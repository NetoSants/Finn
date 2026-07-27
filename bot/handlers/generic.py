import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import ai, repository

logger = logging.getLogger(__name__)


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    logger.info(f"Message from {user.id}: {text}")

    dados = ai.interpretar_mensagem(text)

    if not dados:
        await update.message.reply_text(
            "Nao entendi. Tente algo como:\n"
            "\"gastei 50 no almoço\"\n"
            "\"recebi 2000 de salario\"\n"
            "\"paguei 35 no uber de credito\""
        )
        return

    context.user_data["ai_dados"] = dados

    tipo = "Gasto" if dados["tipo"] == "gasto" else "Renda"
    pagamento = dados.get("pagamento", "debito")

    texto = f"*{tipo}*\n"
    texto += f"Valor: R$ {dados['valor']:.2f}\n"
    texto += f"Descricao: {dados['descricao']}\n"

    if dados["tipo"] == "gasto":
        texto += f"Pagamento: {pagamento}\n"

    keyboard = [
        [
            InlineKeyboardButton("Confirmar", callback_data="ai_confirmar"),
            InlineKeyboardButton("Cancelar", callback_data="ai_cancelar"),
        ]
    ]

    await update.message.reply_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def ai_confirmar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dados = context.user_data.get("ai_dados")
    if not dados:
        await query.edit_message_text("Dados expirados. Envie a mensagem novamente.")
        return

    user = update.effective_user

    try:
        if dados["tipo"] == "gasto":
            repository.inserir_transacao(
                dados["tipo"], dados["valor"], dados["descricao"],
                dados.get("pagamento", "debito"), user.id, user.username,
            )
            await query.edit_message_text(
                f"Gasto de R$ {dados['valor']:.2f} registrado: {dados['descricao']}\n"
                f"Pagamento: {dados.get('pagamento', 'debito')}"
            )
        else:
            repository.inserir_renda(
                dados["valor"], dados["descricao"], user.id, user.username,
            )
            await query.edit_message_text(
                f"Renda de R$ {dados['valor']:.2f} registrada: {dados['descricao']}"
            )
    except Exception as e:
        logger.error(f"Erro ao registrar transacao via IA: {e}")
        await query.edit_message_text("Erro ao registrar. Tente novamente.")

    context.user_data.pop("ai_dados", None)


async def ai_cancelar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("ai_dados", None)
    await query.edit_message_text("Cancelado.")
