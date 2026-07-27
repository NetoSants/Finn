import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ALLOWED_USER_IDS

logger = logging.getLogger(__name__)


def restricted(handler):
    @wraps(handler)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user and user.id in ALLOWED_USER_IDS:
            return await handler(update, context)
        logger.warning(f"Access denied for user {user.id if user else 'None'}")
        if update.message:
            await update.message.reply_text("Acesso restrito.")
    return wrapped
