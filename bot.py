import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
N8N_URL_FINANCAS = os.getenv("N8N_URL_FINANCAS", "http://n8n:5678/webhook/financas")
N8N_URL_COMANDOS = os.getenv("N8N_URL_COMANDOS", "http://n8n:5678/webhook/comandos")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Sou o TeleTony. Como posso ajudar?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandos disponíveis:\n/start - Iniciar\n/help - Ajuda\n/ping - Testar integração")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                N8N_URL_COMANDOS,
                json={"comando": "ping"}
            )
        
        if response.status_code == 200:
            await update.message.reply_text("✅ Pong! Integração funcionando!")
        else:
            await update.message.reply_text(f"⚠️ Erro ao enviar. Status: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Você disse: {update.message.text}")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Desculpe, não entendi esse comando.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    logger.info("Bot TeleTony iniciado!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()