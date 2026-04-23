import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

MESSAGE_THREAD_ID = 1373  # your topic ID

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "message_thread_id": MESSAGE_THREAD_ID
    }

    requests.post(url, data=payload)
