import logging
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import BOT_TOKEN, N8N_URL_NLP, ALLOWED_USER_IDS
from commands import start, help_command, gasto, gasto_callback, renda, saldo, extrato, ping
from utils import fazer_requisicao_n8n, fazer_requisicao_n8n_sem_resposta

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def restricted(handler):
    """Decorator to restrict access to allowed user IDs only."""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user and user.id in ALLOWED_USER_IDS:
            return await handler(update, context)
        else:
            logger.warning(f"Acesso negado para usuário {user.id if user else 'None'}")
            if update.message:
                await update.message.reply_text("❌ Acesso restrito.")
            return
    return wrapped


async def post_init(application):
    """Configura comandos do bot."""
    commands = [
        BotCommand("start", "Inicia o bot"),
        BotCommand("help", "Mostra ajuda"),
        BotCommand("gasto", "Registra um gasto"),
        BotCommand("renda", "Registra uma renda"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot TeleTony configurado!")


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto via webhook NLP."""
    user = update.effective_user
    text = update.message.text
    logger.info(f"NLP: mensagem recebida de {user.id}: {text}")

    await update.message.reply_text("⏳ Um momento")

    payload = {
        "text": text,
        "user_id": user.id,
        "username": user.username or "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    await fazer_requisicao_n8n_sem_resposta(N8N_URL_NLP, payload)


def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Comandos locais
    application.add_handler(CommandHandler("start", restricted(start)))
    application.add_handler(CommandHandler("help", restricted(help_command)))
    application.add_handler(CommandHandler("gasto", restricted(gasto)))
    application.add_handler(CommandHandler("renda", restricted(renda)))
    application.add_handler(CommandHandler("saldo", restricted(saldo)))
    application.add_handler(CommandHandler("extrato", restricted(extrato)))
    application.add_handler(CommandHandler("ping", restricted(ping)))

    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(gasto_callback, pattern="^gasto_"))

    # Mensagens de texto (linguagem natural) vão para NLP
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, restricted(process_message)))

    logger.info("Bot TeleTony iniciado!")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
