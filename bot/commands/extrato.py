import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import fazer_requisicao_n8n
from config import N8N_URL_COMANDOS
from datetime import datetime

logger = logging.getLogger(__name__)


async def extrato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra extrato via webhook comandos."""
    user = update.effective_user
    logger.info(f"Extrato solicitado por {user.id}")

    await update.message.reply_text("⏳ Um momento")

    payload = {
        "intent": "extrato",
        "user_id": user.id,
        "username": user.username or "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    sucesso, mensagem = await fazer_requisicao_n8n(N8N_URL_COMANDOS, payload)
    if sucesso:
        await update.message.reply_text(mensagem)
    else:
        logger.error(f"Erro ao consultar extrato: {mensagem}")
        await update.message.reply_text("❌ Erro ao consultar extrato. Tente novamente.")
