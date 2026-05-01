import logging
from telegram import Update, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, N8N_URL_FINANCAS, N8N_URL_COMANDOS
from commands import start, help_command, ping, gasto, renda, saldo, extrato

logger = logging.getLogger(__name__)


async def post_init(application):
    """Configura os comandos do bot após inicialização."""
    commands = [
        BotCommand("start", "Inicia o bot"),
        BotCommand("help", "Mostra ajuda"),
        BotCommand("ping", "Testa integração"),
        BotCommand("gasto", "Registra um gasto"),
        BotCommand("renda", "Registra uma renda"),
        BotCommand("saldo", "Consulta saldo"),
        BotCommand("extrato", "Mostra extrato"),
    ]

    await application.bot.set_my_commands(
        commands,
        scope=BotCommandScopeAllPrivateChats()
    )

    group_commands = [
        BotCommand("start", "Inicia o bot"),
        BotCommand("help", "Mostra ajuda"),
        BotCommand("gasto", "Registra um gasto"),
    ]
    await application.bot.set_my_commands(
        group_commands,
        scope=BotCommandScopeAllGroupChats()
    )

    logger.info("Comandos do bot configurados com sucesso!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Você disse: {update.message.text}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Desculpe, não entendi esse comando.")


def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("gasto", gasto))
    application.add_handler(CommandHandler("renda", renda))
    application.add_handler(CommandHandler("saldo", saldo))
    application.add_handler(CommandHandler("extrato", extrato))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Bot TeleTony iniciado!")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
