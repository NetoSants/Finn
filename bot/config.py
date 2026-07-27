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
    logger.error("BOT_TOKEN not found in .env")
    raise ValueError("BOT_TOKEN not configured")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "finn")
DB_USER = os.getenv("DB_USER", "finn")
DB_PASSWORD = os.getenv("DB_PASSWORD", "finn")

allowed_ids_str = os.getenv("ALLOWED_USER_IDS", "1401845586")
ALLOWED_USER_IDS = set()
for id_str in allowed_ids_str.split(","):
    id_str = id_str.strip()
    if id_str:
        try:
            ALLOWED_USER_IDS.add(int(id_str))
        except ValueError:
            logger.warning(f"Invalid ID in ALLOWED_USER_IDS: {id_str}")
