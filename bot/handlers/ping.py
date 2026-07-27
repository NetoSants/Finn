import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        count_transacoes = repository.contar_transacoes(user_id)
        count_bancos = repository.contar_bancos()

        await update.message.reply_text(
            f"Finn online!\n\n"
            f"Transacoes: {count_transacoes}\n"
            f"Bancos: {count_bancos}"
        )
    except Exception as e:
        logger.error(f"Erro no ping: {e}")
        await update.message.reply_text("Erro ao conectar no banco de dados.")
