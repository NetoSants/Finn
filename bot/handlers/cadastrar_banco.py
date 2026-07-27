import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def cadastrar_banco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "Uso: /cadastrar_banco [nome] [vencimento] [limite]\n"
            "Ex: /cadastrar_banco Itau 15 5000"
        )
        return

    try:
        limite = float(context.args[-1].replace(',', '.'))
        vencimento = int(context.args[-2])
        if vencimento < 1 or vencimento > 31:
            await update.message.reply_text("Dia de vencimento deve estar entre 1 e 31.")
            return
    except ValueError:
        await update.message.reply_text("Formato invalido. Use: /cadastrar_banco [nome] [vencimento] [limite]")
        return

    nome_banco = ' '.join(context.args[:-2])

    try:
        repository.inserir_banco(nome_banco, vencimento, limite)
        await update.message.reply_text(f"Banco '{nome_banco}' cadastrado!\nVencimento: dia {vencimento} | Limite: R$ {limite:.2f}")
    except Exception as e:
        logger.error(f"Erro ao cadastrar banco: {e}")
        await update.message.reply_text("Erro ao cadastrar banco. Tente novamente.")
