import time
import random
import requests
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright


# ================= CONFIG =================
SHEET_NAME = "BuyBox Tracker"

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

HEADLESS = True
DELAY_RANGE = (2, 5)
# ==========================================


# -------- Google Sheets Setup --------
def init_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet


# -------- Telegram --------
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })


# -------- Scraper --------
def get_buybox_data(page, asin):
    url = f"https://www.amazon.in/dp/{asin}"
    page.goto(url, timeout=60000)

    time.sleep(random.uniform(2, 4))

    try:
        # Seller
        seller = page.locator("#sellerProfileTriggerId").inner_text(timeout=3000)
    except:
        seller = "Amazon / Unknown"

    try:
        # Price
        price = page.locator(".a-price-whole").first.inner_text(timeout=3000)
    except:
        price = "N/A"

    # Check if Buy Box missing
    if "See All Buying Options" in page.content():
        seller = "No Buy Box"

    return seller.strip(), price.strip()


# -------- Main Logic --------
def run():
    sheet = init_sheet()
    rows = sheet.get_all_values()

    total = len(rows) - 1
    won = 0
    lost = 0
    unchanged = 0

    lost_items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        for i, row in enumerate(rows[1:], start=2):
            asin = row[0]
            your_name = row[1]
            old_seller = row[2]

            if not asin:
                continue

            print(f"Checking {asin}...")

            try:
                new_seller, price = get_buybox_data(page, asin)
            except Exception as e:
                print(f"Error for {asin}: {e}")
                continue

            # Status Logic
            if old_seller != new_seller:
                if new_seller.lower() == your_name.lower():
                    status = "Won"
                    won += 1
                else:
                    status = "Lost"
                    lost += 1
                    lost_items.append(f"{asin} → {new_seller} ({price})")
            else:
                status = "No Change"
                unchanged += 1

            # Update Sheet
            sheet.update(f"C{i}:F{i}", [[
                new_seller,
                price,
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ]])

            # Delay (important)
            time.sleep(random.uniform(*DELAY_RANGE))

        browser.close()

    # -------- Telegram Summary --------
    message = f"""
📊 Weekly Buy Box Report

Total ASINs: {total}
✅ Won: {won}
❌ Lost: {lost}
⚠️ No Change: {unchanged}

"""

    if lost_items:
        message += "🔻 Lost ASINs:\n" + "\n".join(lost_items[:10])

    send_telegram(message)

    print("Done ✅")


if __name__ == "__main__":
    run()
