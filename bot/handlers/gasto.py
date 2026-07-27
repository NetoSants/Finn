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

    categorias = repository.listar_categorias()

    if not categorias:
        await update.message.reply_text(
            f"Selecione o tipo de pagamento para:\nR$ {valor:.2f} - {descricao}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Debito", callback_data="gasto_debito"),
                InlineKeyboardButton("Credito", callback_data="gasto_credito"),
                InlineKeyboardButton("Pix", callback_data="gasto_pix"),
            ]])
        )
        return

    keyboard = []
    row = []
    for cat in categorias:
        label = f"{cat[2]} {cat[1]}" if cat[2] else cat[1]
        row.append(InlineKeyboardButton(label, callback_data=f"gasto_cat_{cat[0]}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    await update.message.reply_text(
        f"R$ {valor:.2f} - {descricao}\n\nSelecione a categoria:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def gasto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    if not valor or not descricao:
        await query.edit_message_text("Erro: dados do gasto nao encontrados. Tente novamente.")
        return

    if data.startswith("gasto_cat_"):
        categoria_id = int(data.replace("gasto_cat_", ""))
        context.user_data['gasto_categoria_id'] = categoria_id

        keyboard = [
            [
                InlineKeyboardButton("Debito", callback_data="gasto_debito"),
                InlineKeyboardButton("Credito", callback_data="gasto_credito"),
                InlineKeyboardButton("Pix", callback_data="gasto_pix"),
            ]
        ]

        await query.edit_message_text(
            f"R$ {valor:.2f} - {descricao}\n\nSelecione o tipo de pagamento:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    payment_type = data.replace("gasto_", "")
    categoria_id = context.user_data.pop('gasto_categoria_id', None)

    user = update.effective_user

    try:
        repository.inserir_transacao(
            'gasto', valor, descricao, payment_type,
            user.id, user.username, categoria_id
        )
        await query.edit_message_text(f"Gasto de R$ {valor:.2f} registrado: {descricao}\nPagamento: {payment_type}")
    except Exception as e:
        logger.error(f"Erro ao registrar gasto: {e}")
        await query.edit_message_text("Erro ao registrar gasto. Tente novamente.")

    context.user_data.pop('gasto_valor', None)
    context.user_data.pop('gasto_descricao', None)
