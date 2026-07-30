import logging
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.config import BOT_TOKEN
from bot.decorators import restricted
from bot.handlers import COMMANDS, CALLBACKS
from bot.handlers.generic import process_message
from bot.migrations import run_migrations

logger = logging.getLogger(__name__)


async def post_init(application):
    commands = [
        BotCommand("start", "Inicia o bot"),
        BotCommand("help", "Mostra ajuda"),
        BotCommand("gasto", "Registra um gasto"),
        BotCommand("renda", "Registra uma renda"),
        BotCommand("bancos", "Lista bancos cadastrados"),
        BotCommand("saldo", "Consulta saldo"),
        BotCommand("extrato", "Mostra extrato"),
        BotCommand("parcelas", "Lista parcelas"),
        BotCommand("parcelar", "Cadastra parcela"),
        BotCommand("meta", "Define/consulta metas mensais"),
        BotCommand("categorias", "Lista categorias"),
        BotCommand("resumo", "Resumo mensal com insights"),
        BotCommand("exportar", "Exporta transacoes em CSV"),
        BotCommand("ping", "Verifica se o bot esta online"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Finn configured!")


def main():
    run_migrations()

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    for name, handler in COMMANDS.items():
        application.add_handler(CommandHandler(name, restricted(handler)))

    for pattern, callback in CALLBACKS:
        application.add_handler(CallbackQueryHandler(callback, pattern=pattern))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, restricted(process_message)))

    logger.info("Finn started!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, RuntimeError):
        logger.info("Finn stopped!")
