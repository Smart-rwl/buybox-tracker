import random
import asyncio
import os
from playwright.async_api import async_playwright

PROXIES = os.getenv("PROXIES", "").split(";") if os.getenv("PROXIES") else []
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
BASE_DELAY_MS = int(os.getenv("BASE_DELAY_MS", 2000))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
]

def pick_proxy():
    if not PROXIES:
        return None
    raw = random.choice(PROXIES)
    # supports http://user:pass@host:port
    return {"server": raw}

async def is_captcha(page):
    html = await page.content()
    return ("captcha" in html.lower()) or ("validatecaptcha" in html.lower())

async def create_context(browser):
    proxy = pick_proxy()

    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        locale="en-IN",
        timezone_id="Asia/Kolkata",
        viewport={"width": random.choice([1366, 1440, 1536]), "height": random.choice([768, 900, 864])},
        proxy=proxy
    )
    return context, proxy

async def scrape_with_retry(browser, asin):
    attempt = 0

    while attempt < MAX_RETRIES:
        attempt += 1
        context, proxy = await create_context(browser)
        page = await context.new_page()

        try:
            await page.goto(f"https://www.amazon.in/dp/{asin}", timeout=60000)
            await page.wait_for_timeout(random.randint(2000, 4000))

            # CAPTCHA detection
            if await is_captcha(page):
                await context.close()
                await asyncio.sleep((BASE_DELAY_MS / 1000) * attempt)
                continue  # retry with different proxy

            content = await page.content()

            # Seller
            try:
                seller = await page.locator("#sellerProfileTriggerId").inner_text(timeout=3000)
            except:
                seller = "Amazon / Unknown"

            # Price
            try:
                price = await page.locator(".a-price-whole").first.inner_text(timeout=3000)
            except:
                price = "N/A"

            if "See All Buying Options" in content:
                seller = "No Buy Box"

            await context.close()
            return asin, seller.strip(), price.strip(), "OK"

        except Exception:
            await context.close()
            await asyncio.sleep((BASE_DELAY_MS / 1000) * attempt)

    return asin, "ERROR", "ERROR", "FAILED"


async def run_scraper(asins, concurrency=2, headless=True):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        sem = asyncio.Semaphore(concurrency)

        async def bound(a):
            async with sem:
                return await scrape_with_retry(browser, a)

        tasks = [bound(a) for a in asins]
        results = await asyncio.gather(*tasks)

        await browser.close()

    return results
