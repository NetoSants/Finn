import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from utils import fazer_requisicao_n8n
from config import N8N_URL_FINANCAS

logger = logging.getLogger(__name__)


async def renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Registra uma renda."""
    user = update.effective_user
    logger.info(f"Usuário {user.id} ({user.username}) executou /renda com args: {context.args}")

    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Use: /renda [valor] [descrição]\nEx: /renda 1500.00 salário")
        return

    try:
        valor = float(args[0])
        descricao = " ".join(args[1:])

        sucesso, mensagem = await fazer_requisicao_n8n(
            N8N_URL_FINANCAS,
            {
                "tipo": "renda",
                "valor": valor,
                "descricao": descricao,
                "timestamp": datetime.now().isoformat()
            }
        )

        if sucesso:
            await update.message.reply_text(f"✅ Renda registrada! R$ {valor:.2f} - {descricao}")
        else:
            await update.message.reply_text(mensagem)

    except ValueError:
        await update.message.reply_text("⚠️ Valor inválido. Use número decimal.\nEx: /renda 1500.00")
