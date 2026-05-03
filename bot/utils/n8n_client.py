import logging
import httpx

logger = logging.getLogger(__name__)


async def fazer_requisicao_n8n(url: str, dados: dict) -> tuple[bool, str]:
    """Requisição ao n8n que aguarda resposta (para comandos)."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=dados)

        if response.status_code == 200:
            try:
                data = response.json()
                return True, data.get("message", str(data))
            except Exception:
                return True, response.text
        else:
            return False, f"⚠️ Erro no servidor. Status: {response.status_code}"

    except httpx.TimeoutException:
        return False, "❌ Timeout: Servidor demorou para responder."
    except httpx.ConnectError:
        return False, "❌ Erro de conexão: Verifique se o n8n está rodando."
    except Exception as e:
        logger.error(f"Erro na requisição: {e}", exc_info=True)
        return False, f"❌ Erro inesperado: {str(e)}"


async def fazer_requisicao_n8n_sem_resposta(url: str, dados: dict):
    """Envia requisição ao n8n sem aguardar resposta (fire-and-forget)."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=dados)
            logger.info(f"Requisição enviada para {url}")
    except Exception as e:
        logger.error(f"Erro ao enviar para n8n: {e}")
