import logging
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from config import N8N_URL_COMANDOS

logger = logging.getLogger(__name__)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Usuário {user.id} ({user.username}) executou /ping")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                N8N_URL_COMANDOS,
                json={"comando": "ping"}
            )

        if response.status_code == 200:
            await update.message.reply_text("✅ Pong! Integração funcionando!")
        else:
            await update.message.reply_text(f"⚠️ Erro ao enviar. Status: {response.status_code}")
    except httpx.TimeoutException:
        await update.message.reply_text("❌ Timeout: O servidor n8n demorou muito para responder.")
    except httpx.ConnectError:
        await update.message.reply_text(f"❌ Erro de conexão: Verifique se o n8n está rodando em {N8N_URL_COMANDOS}")
    except Exception as e:
        logger.error(f"Erro inesperado no comando ping: {e}", exc_info=True)
        await update.message.reply_text("❌ Erro inesperado. Tente novamente mais tarde.")
