import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    logger.info(f"Message from {user.id}: {text}")

    from bot.handlers.gasto import gasto_text
    if await gasto_text(update, context):
        return

    from bot.handlers.renda import renda_text
    if await renda_text(update, context):
        return

    from bot.handlers.bancos import banco_text
    if await banco_text(update, context):
        return

    await update.message.reply_text(
        "Use /gasto ou /renda para registrar.\n"
        "Ex: /gasto 50 almoco debito"
    )
