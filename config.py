import os
import json

GOOGLE_CREDS = json.loads(os.environ["GOOGLE_CREDS_JSON"])
SHEET_NAME = os.environ["SHEET_NAME"]

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", 2))
HEADLESS = os.getenv("HEADLESS", "true") == "true"