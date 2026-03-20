import logging
import os
from datetime import datetime

# Ensure storage directory exists
os.makedirs("storage", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("storage/logs.txt", mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("kai_bot")

def log_event(message):
    logger.info(message)

def log_error(message):
    logger.error(message)
