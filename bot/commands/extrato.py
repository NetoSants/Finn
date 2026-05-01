import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import fazer_requisicao_n8n
from config import N8N_URL_COMANDOS

logger = logging.getLogger(__name__)


async def extrato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra o extrato de transações."""
    logger.info(f"Usuário {update.effective_user.id} executou /extrato")

    sucesso, resposta = await fazer_requisicao_n8n(
        N8N_URL_COMANDOS,
        {"comando": "extrato"}
    )

    if sucesso:
        await update.message.reply_text(f"📄 Extrato:\n{resposta}")
    else:
        await update.message.reply_text("❌ Erro ao consultar extrato.")
