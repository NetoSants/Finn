import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def extrato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    mes = None
    ano = None

    if context.args and len(context.args) >= 2:
        try:
            mes = int(context.args[0])
            ano = int(context.args[1])
        except ValueError:
            pass

    if mes and ano and 1 <= mes <= 12:
        rows = repository.listar_transacoes_periodo(user_id, mes, ano)
        titulo = f"Extrato {mes:02d}/{ano}"
    else:
        rows = repository.listar_transacoes(user_id)
        titulo = "Extrato (ultimas 20)"

    if not rows:
        await update.message.reply_text("Nenhuma transacao encontrada.")
        return

    msg = f"{titulo}:\n\n"
    for row in rows:
        tipo, valor, descricao, pagamento, data_transacao, cat_nome, cat_emoji = row
        emoji = "G" if tipo == "gasto" else "R"
        cat = f" {cat_emoji}" if cat_emoji else ""
        pago = f" ({pagamento})" if pagamento else ""
        data_str = data_transacao.strftime('%d/%m') if data_transacao else "??/??"
        msg += f"{emoji} {data_str}: R$ {valor:.2f} — {descricao}{cat}{pago}\n"

    await update.message.reply_text(msg)
