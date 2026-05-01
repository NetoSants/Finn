import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN não encontrado no arquivo .env!")
    raise ValueError("Token do bot não configurado. Verifique o arquivo .env")

N8N_URL_FINANCAS = os.getenv("N8N_URL_FINANCAS", "http://n8n:5678/webhook/financas")
N8N_URL_COMANDOS = os.getenv("N8N_URL_COMANDOS", "http://n8n:5678/webhook/comandos")
