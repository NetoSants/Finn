import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Uso: /renda [valor] [descricao]\nEx: /renda 500 salario")
        return

    try:
        valor = float(context.args[0].replace(',', '.'))
    except ValueError:
        await update.message.reply_text("Valor invalido. Use numeros (ex: 500 ou 500,50)")
        return

    descricao = ' '.join(context.args[1:])
    user = update.effective_user

    try:
        repository.inserir_renda(valor, descricao, user.id, user.username)
        await update.message.reply_text(f"Renda de R$ {valor:.2f} registrada: {descricao}")
    except Exception as e:
        logger.error(f"Erro ao registrar renda: {e}")
        await update.message.reply_text("Erro ao registrar renda. Tente novamente.")
