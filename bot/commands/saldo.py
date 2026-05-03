import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import fazer_requisicao_n8n
from config import N8N_URL_COMANDOS
from datetime import datetime

logger = logging.getLogger(__name__)


async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta saldo via webhook comandos."""
    user = update.effective_user
    logger.info(f"Saldo solicitado por {user.id}")

    await update.message.reply_text("⏳ Um momento")

    payload = {
        "intent": "saldo",
        "user_id": user.id,
        "username": user.username or "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    sucesso, mensagem = await fazer_requisicao_n8n(N8N_URL_COMANDOS, payload)
    if sucesso:
        await update.message.reply_text(mensagem)
    else:
        logger.error(f"Erro ao consultar saldo: {mensagem}")
        await update.message.reply_text("❌ Erro ao consultar saldo. Tente novamente.")
