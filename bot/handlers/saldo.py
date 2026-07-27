import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        total_gastos = repository.total_gastos(user_id)
        total_rendas = repository.total_rendas(user_id)
        saldo_valor = total_rendas - total_gastos

        await update.message.reply_text(
            f"**Saldo:**\n\n"
            f"Rendas: R$ {total_rendas:.2f}\n"
            f"Gastos: R$ {total_gastos:.2f}\n"
            f"**Saldo Total: R$ {saldo_valor:.2f}**",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Erro ao consultar saldo: {e}")
        await update.message.reply_text("Erro ao consultar saldo. Tente novamente.")
