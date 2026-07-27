import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def extrato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        rows = repository.listar_transacoes(user_id)
    except Exception as e:
        logger.error(f"Erro ao buscar extrato: {e}")
        await update.message.reply_text("Erro ao buscar extrato. Tente novamente.")
        return

    if not rows:
        await update.message.reply_text("Nenhuma transacao encontrada.")
        return

    msg = "**Extrato (ultimas 20):**\n\n"
    for row in rows:
        tipo, valor, descricao, pagamento, data_transacao = row
        emoji = "G" if tipo == "gasto" else "R"
        pago = f" ({pagamento})" if pagamento else ""
        data_str = data_transacao.strftime('%d/%m') if data_transacao else "??/??"
        msg += f"{emoji} {data_str}: R$ {valor:.2f} - {descricao}{pago}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")
