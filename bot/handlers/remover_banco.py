import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def remover_banco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Uso: /remover_banco [nome]\n"
            "Ex: /remover_banco Itau"
        )
        return

    nome_banco = ' '.join(context.args)

    try:
        repository.remover_banco(nome_banco)
        await update.message.reply_text(f"Banco '{nome_banco}' removido!")
    except Exception as e:
        logger.error(f"Erro ao remover banco: {e}")
        await update.message.reply_text("Erro ao remover banco. Tente novamente.")
