import os
import re
import json
import logging
import requests

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

SYSTEM_PROMPT = """Você é um parser de mensagens financeiras em português brasileiro.

IMPORTANTE: Palavras como "torrei", "mandei", "paguei", "comprei", "botti", "gastei" indicam GASTO (tipo: "gasto").
Palavras como "recebi", "ganhei", "me pagaram" indicam RENDA (tipo: "renda").

Retorne APENAS um JSON com:
- "tipo": "gasto" ou "renda"
- "valor": número decimal ou null
- "descricao": texto descritivo
- "pagamento": "debito", "credito", "pix" ou null

Se a mensagem não é sobre registrar gasto/renda, retorne: {"erro": true}

Exemplos:
"gastei 50 no almoço" -> {"tipo": "gasto", "valor": 50, "descricao": "almoço", "pagamento": null}
"torrei 200 no fim de semana" -> {"tipo": "gasto", "valor": 200, "descricao": "fim de semana", "pagamento": null}
"mandei 200 no pix pro joao" -> {"tipo": "gasto", "valor": 200, "descricao": "transferencia para joao", "pagamento": "pix"}
"botti 15 no onibus" -> {"tipo": "gasto", "valor": 15, "descricao": "onibus", "pagamento": null}
"paguei 80 de credito na amazon" -> {"tipo": "gasto", "valor": 80, "descricao": "amazon", "pagamento": "credito"}
"recebi 2000 de salario" -> {"tipo": "renda", "valor": 2000, "descricao": "salário", "pagamento": null}
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
