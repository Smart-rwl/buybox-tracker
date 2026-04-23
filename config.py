import os
from dotenv import load_dotenv

load_dotenv()

SHEET_NAME = os.getenv("SHEET_NAME")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", 2))
HEADLESS = os.getenv("HEADLESS", "true") == "true"