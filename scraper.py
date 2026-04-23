import random
import asyncio
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...Chrome/120",
    "Mozilla/5.0 (Macintosh)...Safari/537.36",
]

async def scrape_one(context, asin):
    page = await context.new_page()

    try:
        await page.goto(f"https://www.amazon.in/dp/{asin}", timeout=60000)
        await page.wait_for_timeout(random.randint(2000, 4000))

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

        return asin, seller.strip(), price.strip()

    except Exception as e:
        return asin, "ERROR", "ERROR"

    finally:
        await page.close()


async def run_scraper(asins, concurrency=2, headless=True):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS)
        )

        sem = asyncio.Semaphore(concurrency)

        async def bound_task(asin):
            async with sem:
                return await scrape_one(context, asin)

        tasks = [bound_task(a) for a in asins]
        results = await asyncio.gather(*tasks)

        await browser.close()

    return results
