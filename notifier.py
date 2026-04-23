import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

MESSAGE_THREAD_ID = 1373

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
