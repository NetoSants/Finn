import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tela de boas-vindas ao chamar /start."""
    welcome_msg = (
        "Olá! Eu sou o **TeleTony**, seu assistente financeiro via Telegram.\n\n"
        "✨ **O que eu faço?**\n"
        "Processo comandos e mensagens em linguagem natural.\n\n"
        "📝 **Comandos disponíveis:**\n"
        "`/gasto [valor] [descrição]` - Registra um gasto\n"
        "`/renda [valor] [descrição]` - Registra uma renda\n"
        "`/saldo` - Consulta saldo\n"
        "`/extrato` - Mostra extrato\n"
        "`/help` - Mostra esta ajuda\n\n"
        "💬 **Linguagem natural:**\n"
        "Envie mensagens como 'Gastei 30 com almoço' para processamento via IA."
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
