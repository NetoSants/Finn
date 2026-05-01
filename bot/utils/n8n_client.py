import logging
import httpx

logger = logging.getLogger(__name__)


async def fazer_requisicao_n8n(url: str, dados: dict, mensagem_erro: str = "Erro na requisição") -> tuple[bool, str]:
    """Função auxiliar para fazer requisições ao n8n."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=dados)

        if response.status_code == 200:
            return True, "✅ Operação realizada com sucesso!"
        else:
            return False, f"⚠️ Erro no servidor. Status: {response.status_code}"

    except httpx.TimeoutException:
        return False, "❌ Timeout: Servidor demorou para responder."
    except httpx.ConnectError:
        return False, "❌ Erro de conexão: Verifique se o n8n está rodando."
    except Exception as e:
        logger.error(f"Erro na requisição: {e}", exc_info=True)
        return False, f"❌ Erro inesperado: {str(e)}"
