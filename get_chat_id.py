import requests
import time

BOT_TOKEN = "8696560682:AAFMIJ8DMqiyS8s2BSYsNpJvGujihmUb50Q"

print("👉 Send a message to your bot in Telegram (type anything)...")
time.sleep(5)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
res = requests.get(url).json()

if not res["result"]:
    print("❌ No messages found. Send a message to your bot first.")
    exit()

# Get latest message
last_msg = res["result"][-1]
chat = last_msg["message"]["chat"]

chat_id = chat["id"]
chat_type = chat["type"]

print("\n✅ Chat ID Found!")
print(f"Chat ID: {chat_id}")
print(f"Type: {chat_type}")