import asyncio
from datetime import datetime
import time

from sheets import init_sheet
from scraper import run_scraper
from notifier import send


def run():
    sheet = init_sheet()
    rows = sheet.get_all_values()

    asins = []
    meta = {}

    for i, row in enumerate(rows[1:], start=2):
        asin = row[0]
        if not asin:
            continue

        asins.append(asin)
        meta[asin] = {
            "row": i,
            "your_name": row[1],
            "old_seller": row[2]
        }

    results = asyncio.run(run_scraper(asins))

    won = lost = unchanged = 0
    lost_items = []

    for asin, new_seller, price, flag in results:
    data = meta[asin]
    row = data["row"]

    if flag == "FAILED":
        sheet.update(f"C{row}:F{row}", [[
            "FAILED",
            "FAILED",
            "Retry Next Run",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ]])
        continue

        if old != new_seller:
            if new_seller.lower() == your.lower():
                status = "Won"
                won += 1
            else:
                status = "Lost"
                lost += 1
                lost_items.append(f"{asin} → {new_seller} ({price})")
        else:
            status = "No Change"
            unchanged += 1

        sheet.update(f"C{row}:F{row}", [[
            new_seller,
            price,
            status,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ]])

        time.sleep(1)

    msg = f"""
📊 Weekly Buy Box Report

Total: {len(asins)}
Won: {won}
Lost: {lost}
No Change: {unchanged}
"""

    

    if lost_items:
    msg += "\n🔻 Lost:\n" + "\n".join(lost_items[:10])

# ✅ ADD THIS (failed ASINs)
failed = [r[0] for r in results if r[3] == "FAILED"]

if failed:
    msg += "\n⚠️ Failed:\n" + "\n".join(failed[:10])

send(msg)


if __name__ == "__main__":
    run()
