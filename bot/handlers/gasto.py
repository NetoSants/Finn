import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Uso: /gasto [valor] [descricao]\nEx: /gasto 30 almoco")
        return

    try:
        valor = float(context.args[0].replace(',', '.'))
    except ValueError:
        await update.message.reply_text("Valor invalido. Use numeros (ex: 30 ou 30,50)")
        return

    descricao = ' '.join(context.args[1:])
    context.user_data['gasto_valor'] = valor
    context.user_data['gasto_descricao'] = descricao

    keyboard = [
        [
            InlineKeyboardButton("Debito", callback_data="gasto_debito"),
            InlineKeyboardButton("Credito", callback_data="gasto_credito"),
            InlineKeyboardButton("Pix", callback_data="gasto_pix"),
        ]
    ]

    await update.message.reply_text(
        f"Selecione o tipo de pagamento para:\nR$ {valor:.2f} - {descricao}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def gasto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    payment_type = query.data.replace("gasto_", "")
    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    if not valor or not descricao:
        await query.edit_message_text("Erro: dados do gasto nao encontrados. Tente novamente.")
        return

    user = update.effective_user

    try:
        repository.inserir_transacao('gasto', valor, descricao, payment_type, user.id, user.username)
        await query.edit_message_text(f"Gasto de R$ {valor:.2f} registrado: {descricao}\nPagamento: {payment_type}")
    except Exception as e:
        logger.error(f"Erro ao registrar gasto: {e}")
        await query.edit_message_text("Erro ao registrar gasto. Tente novamente.")

    context.user_data.pop('gasto_valor', None)
    context.user_data.pop('gasto_descricao', None)
