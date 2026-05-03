import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra ajuda sobre os comandos disponíveis."""
    help_text = (
        "📚 **Comandos do TeleTony**\n\n"
        "💸 **Financeiro:**\n"
        "`/gasto [valor] [descrição]` - Registra um gasto\n"
        "  Ex: `/gasto 30 almoço`\n\n"
        "`/renda [valor] [descrição]` - Registra uma renda\n"
        "  Ex: `/renda 500 salário`\n\n"
        "ℹ️ **Outros:**\n"
        "`/start` - Inicia o bot\n"
        "`/help` - Mostra esta ajuda\n\n"
        "🔍 **Processamento:**\n"
        "Todas as mensagens são enviadas para o n8n + Ollama para processamento em linguagem natural."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")
