import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import fazer_requisicao_n8n
from config import N8N_URL_COMANDOS

logger = logging.getLogger(__name__)


async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta o saldo atual."""
    logger.info(f"Usuário {update.effective_user.id} executou /saldo")

    sucesso, resposta = await fazer_requisicao_n8n(
        N8N_URL_COMANDOS,
        {"comando": "saldo"}
    )

    if sucesso:
        await update.message.reply_text(f"💰 Saldo atual: R$ {resposta}")
    else:
        await update.message.reply_text("❌ Erro ao consultar saldo.")
