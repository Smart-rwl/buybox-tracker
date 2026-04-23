import random
import asyncio
import os
from playwright.async_api import async_playwright

PROXIES = os.getenv("PROXIES", "").split(";") if os.getenv("PROXIES") else []
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
BASE_DELAY_MS = int(os.getenv("BASE_DELAY_MS", 2000))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119 Safari/537.36",
]


def pick_proxy():
    if not PROXIES:
        return None
    return {"server": random.choice(PROXIES)}


async def is_blocked(content):
    content = content.lower()
    return (
        "captcha" in content
        or "validatecaptcha" in content
        or "enter the characters you see below" in content
    )


async def create_context(browser):
    proxy = pick_proxy()

    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        locale="en-IN",
        timezone_id="Asia/Kolkata",
        viewport={
            "width": random.choice([1366, 1440, 1536]),
            "height": random.choice([768, 864, 900]),
        },
        proxy=proxy
    )
    return context


# ------------------ PRODUCT PAGE ------------------
async def scrape_product(page, asin):
    await page.goto(f"https://www.amazon.in/dp/{asin}", timeout=60000)
    await page.wait_for_timeout(random.randint(2000, 4000))

    content = await page.content()

    if await is_blocked(content):
        return None, None, "BLOCKED"

    try:
        seller = await page.locator("#sellerProfileTriggerId").inner_text(timeout=3000)
    except:
        seller = "Unknown"

    try:
        price = await page.locator(".a-price-whole").first.inner_text(timeout=3000)
    except:
        price = "N/A"

    if "See All Buying Options" in content:
        seller = "No Buy Box"

    return seller.strip(), price.strip(), "OK"


# ------------------ OFFER PAGE (FALLBACK) ------------------
async def scrape_offer(page, asin):
    await page.goto(f"https://www.amazon.in/gp/offer-listing/{asin}", timeout=60000)
    await page.wait_for_timeout(random.randint(2000, 4000))

    content = await page.content()

    if await is_blocked(content):
        return None, None, "BLOCKED"

    try:
        seller = await page.locator("h3.olpSellerName").first.inner_text(timeout=3000)
    except:
        seller = "Unknown"

    try:
        price = await page.locator(".olpOfferPrice").first.inner_text(timeout=3000)
    except:
        price = "N/A"

    return seller.strip(), price.strip(), "OK"


# ------------------ RETRY ENGINE ------------------
async def scrape_with_retry(browser, asin):
    for attempt in range(MAX_RETRIES):
        context = await create_context(browser)
        page = await context.new_page()

        try:
            # Step 1: Try product page
            seller, price, status = await scrape_product(page, asin)

            if status == "OK":
                await context.close()
                print(f"✅ {asin} → {seller} | {price}")
                return asin, seller, price, "OK"

            # Step 2: fallback to offer page
            seller, price, status = await scrape_offer(page, asin)

            if status == "OK":
                await context.close()
                print(f"🟡 {asin} (offer) → {seller} | {price}")
                return asin, seller, price, "OK"

        except Exception as e:
            print(f"❌ Error {asin}: {e}")

        await context.close()
        await asyncio.sleep((BASE_DELAY_MS / 1000) * (attempt + 1))

    print(f"🚫 FAILED {asin}")
    return asin, "FAILED", "FAILED", "FAILED"


# ------------------ MAIN RUNNER ------------------
async def run_scraper(asins, concurrency=2, headless=True):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        sem = asyncio.Semaphore(concurrency)

        async def task(a):
            async with sem:
                return await scrape_with_retry(browser, a)

        results = await asyncio.gather(*[task(a) for a in asins])

        await browser.close()

    return results
