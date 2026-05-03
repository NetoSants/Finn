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
    raise ValueError("Token do bot não configurado.")

# NLP Webhook (linguagem natural - Ollama processa tudo)
N8N_URL_NLP = os.getenv("N8N_URL_NLP")
if not N8N_URL_NLP:
    n8n_host = os.getenv("N8N_HOST", "n8n")
    n8n_port = os.getenv("N8N_PORT", "5678")
    n8n_webhook_path = os.getenv("N8N_WEBHOOK_PATH", "webhook-test")
    N8N_URL_NLP = f"http://{n8n_host}:{n8n_port}/{n8n_webhook_path}/nlp"

# Finanças (gasto/renda via webhook)
N8N_URL_FINANCAS = os.getenv("N8N_URL_FINANCAS")
if not N8N_URL_FINANCAS:
    n8n_host = os.getenv("N8N_HOST", "n8n")
    n8n_port = os.getenv("N8N_PORT", "5678")
    n8n_webhook_path = os.getenv("N8N_WEBHOOK_PATH", "webhook-test")
    N8N_URL_FINANCAS = f"http://{n8n_host}:{n8n_port}/{n8n_webhook_path}/financas"

# Comandos (saldo/extrato/ping via webhook)
N8N_URL_COMANDOS = os.getenv("N8N_URL_COMANDOS")
if not N8N_URL_COMANDOS:
    n8n_host = os.getenv("N8N_HOST", "n8n")
    n8n_port = os.getenv("N8N_PORT", "5678")
    n8n_webhook_path = os.getenv("N8N_WEBHOOK_PATH", "webhook-test")
    N8N_URL_COMANDOS = f"http://{n8n_host}:{n8n_port}/{n8n_webhook_path}/comandos"

# Restrição de acesso
allowed_ids_str = os.getenv("ALLOWED_USER_IDS", "1401845586")
ALLOWED_USER_IDS = set()
for id_str in allowed_ids_str.split(","):
    id_str = id_str.strip()
    if id_str:
        try:
            ALLOWED_USER_IDS.add(int(id_str))
        except ValueError:
            logger.warning(f"ID inválido em ALLOWED_USER_IDS: {id_str}")
