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

    # Read sheet
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

    # Run scraper
    results = asyncio.run(run_scraper(asins))

    won = 0
    lost = 0
    unchanged = 0
    lost_items = []

    # Process results
    for asin, new_seller, price, flag in results:
        data = meta[asin]
        row = data["row"]
        old = data["old_seller"]
        your = data["your_name"]

        # Handle failed cases
        if flag == "FAILED":
            sheet.update(
                values=[[
                    "FAILED",
                    "FAILED",
                    "Retry Next Run",
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ]],
                range_name=f"C{row}:F{row}"
            )
            continue

        # Status logic
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

        # Update sheet
        sheet.update(
            values=[[
                new_seller,
                price,
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ]],
            range_name=f"C{row}:F{row}"
        )

        time.sleep(1)

    # Prepare Telegram message
    msg = f"""
📊 Weekly Buy Box Report

Total: {len(asins)}
Won: {won}
Lost: {lost}
No Change: {unchanged}
"""

    if lost_items:
        msg += "\n🔻 Lost:\n" + "\n".join(lost_items[:10])

    # Failed ASINs
    failed = [r[0] for r in results if r[3] == "FAILED"]

    if failed:
        msg += "\n⚠️ Failed:\n" + "\n".join(failed[:10])

    # Send notification
    send(msg)


if __name__ == "__main__":
    run()