import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import fazer_requisicao_n8n

logger = logging.getLogger(__name__)


async def gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Registra um gasto: /gasto [valor] [descrição]"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Uso: /gasto [valor] [descrição]\nEx: /gasto 30 almoço")
        return

    try:
        valor = float(context.args[0].replace(',', '.'))
    except ValueError:
        await update.message.reply_text("❌ Valor inválido. Use números (ex: 30 ou 30,50)")
        return

    descricao = ' '.join(context.args[1:])

    # Store in user_data for callback
    context.user_data['gasto_valor'] = valor
    context.user_data['gasto_descricao'] = descricao

    await update.message.reply_text("⏳ Um momento")

    # Create inline buttons for payment type
    keyboard = [
        [
            InlineKeyboardButton("💳 Débito", callback_data="gasto_debito"),
            InlineKeyboardButton("💳 Crédito", callback_data="gasto_credito"),
            InlineKeyboardButton("💰 Pix", callback_data="gasto_pix"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Selecione o tipo de pagamento para:\nR$ {valor:.2f} - {descricao}",
        reply_markup=reply_markup
    )


async def gasto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a seleção do tipo de pagamento do gasto."""
    query = update.callback_query
    await query.answer()

    # Get payment type from callback data
    payment_type = query.data.replace("gasto_", "")

    # Get stored data
    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    if not valor or not descricao:
        await query.edit_message_text("❌ Erro: dados do gasto não encontrados. Tente novamente.")
        return

    from config import N8N_URL_FINANCAS
    from datetime import datetime

    payload = {
        "tipo": "gasto",
        "valor": valor,
        "descricao": descricao,
        "pagamento": payment_type,
        "user_id": update.effective_user.id,
        "username": update.effective_user.username or "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    await query.edit_message_text("⏳ Processando...")

    sucesso, mensagem = await fazer_requisicao_n8n(N8N_URL_FINANCAS, payload)
    if sucesso:
        await query.edit_message_text(f"✅ Gasto de R$ {valor:.2f} registrado: {descricao}\n💳 Pagamento: {payment_type}")
    else:
        logger.error(f"Erro ao registrar gasto: {mensagem}")
        await query.edit_message_text("❌ Erro ao registrar gasto. Tente novamente.")

    # Clear user_data
    context.user_data.pop('gasto_valor', None)
    context.user_data.pop('gasto_descricao', None)
