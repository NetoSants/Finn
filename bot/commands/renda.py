import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import fazer_requisicao_n8n

logger = logging.getLogger(__name__)


async def renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Registra uma renda: /renda [valor] [descrição]"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Uso: /renda [valor] [descrição]\nEx: /renda 500 salário")
        return

    try:
        valor = float(context.args[0].replace(',', '.'))
    except ValueError:
        await update.message.reply_text("❌ Valor inválido. Use números (ex: 500 ou 500,50)")
        return

    descricao = ' '.join(context.args[1:])

    from config import N8N_URL_FINANCAS
    from datetime import datetime

    payload = {
        "tipo": "renda",
        "valor": valor,
        "descricao": descricao,
        "user_id": update.effective_user.id,
        "username": update.effective_user.username or "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    await update.message.reply_text("⏳ Um momento")

    sucesso, mensagem = await fazer_requisicao_n8n(N8N_URL_FINANCAS, payload)
    if sucesso:
        await update.message.reply_text(f"✅ Renda de R$ {valor:.2f} registrada: {descricao}")
    else:
        logger.error(f"Erro ao registrar renda: {mensagem}")
        await update.message.reply_text("❌ Erro ao registrar renda. Tente novamente.")
