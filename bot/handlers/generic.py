import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    logger.info(f"Message from {user.id}: {text}")
    await update.message.reply_text(
        "Use os comandos:\n"
        "/gasto [valor] [desc]\n"
        "/renda [valor] [desc]\n"
        "/parcelar [valor] [parc] [dia] [desc]"
    )
