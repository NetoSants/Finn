import os
import re
import json
import logging
import requests

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

SYSTEM_PROMPT = """Analise a mensagem do usuario e retorne APENAS um JSON valido, sem nenhum texto adicional.

O JSON deve ter exatamente estes campos:
- "tipo": "gasto" (se gasta dinheiro) ou "renda" (se recebe dinheiro)
- "valor": o valor numerico (sem R$) ou null se nao mencionado
- "descricao": o que foi comprado ou de onde veio o dinheiro
- "pagamento": "debito", "credito", "pix" ou null se nao mencionado

IMPORTANTE: Se a mensagem NAO for sobre registrar um gasto ou renda (ex: "bom dia", "obrigado", "ajuda"), retorne EXATAMENTE: {"erro": true}

Exemplos:
"gastei 50 no almoço" -> {"tipo": "gasto", "valor": 50, "descricao": "almoço", "pagamento": null}
"recebi 2000 de salario" -> {"tipo": "renda", "valor": 2000, "descricao": "salário", "pagamento": null}
"paguei 35 no uber de credito" -> {"tipo": "gasto", "valor": 35, "descricao": "uber", "pagamento": "credito"}
"gastei 20 no pix" -> {"tipo": "gasto", "valor": 20, "descricao": "pix", "pagamento": "pix"}
"bom dia" -> {"erro": true}"""

TERMOS_FINANCEIROS = [
    "gastei", "gasto", "paguei", "pago", "comprei", "compra",
    "recebi", "recebo", "ganhei", "ganho", "renda", "salario", "salário",
    "freelance", "cashback", "estorno", "reembolso", "bonus", "bônus",
    "debito", "débito", "credito", "crédito", "pix", "transferi",
    "deposito", "depósito", "saque", "troco",
    "conta", "fatura", "boleto", "parcela",
]


def _tem_termo_financeiro(texto: str) -> bool:
    texto_lower = texto.lower()
    return any(termo in texto_lower for termo in TERMOS_FINANCEIROS)


def _tem_numero(texto: str) -> bool:
    return bool(re.search(r"\d", texto))


def interpretar_mensagem(texto: str) -> dict | None:
    texto = texto.strip()

    if len(texto.split()) < 2:
        return None

    if not _tem_termo_financeiro(texto) and not _tem_numero(texto):
        return None

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": texto,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200},
            },
            timeout=30,
        )
        resp.raise_for_status()
        resultado = resp.json().get("response", "").strip()

        if resultado.startswith("```"):
            resultado = resultado.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        dados = json.loads(resultado)

        if dados.get("erro"):
            return None

        if not all(k in dados for k in ("tipo", "valor", "descricao")):
            return None

        if dados["valor"] is None:
            return None

        dados["valor"] = float(dados["valor"])

        if dados["valor"] <= 0:
            return None

        if dados["tipo"] not in ("gasto", "renda"):
            return None

        if dados["tipo"] == "renda":
            dados["pagamento"] = None
        elif dados.get("pagamento") not in ("debito", "credito", "pix", None):
            dados["pagamento"] = None

        return dados

    except (json.JSONDecodeError, KeyError, ValueError, requests.RequestException) as e:
        logger.warning(f"Erro ao interpretar mensagem: {e}")
        return None
