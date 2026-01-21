import asyncio
from playwright.async_api import async_playwright, Error as PlaywrightError
from .headers.nba_headers import get_nba_headers


async def fetch_stats_html(
    url: str,
    wait_for_selector: str = None,
    headless: bool = True,
    retries: int = 3,
    verbose: bool = False
) -> str:
    """
    Fetch rendered HTML for a RealGM stats page using Playwright.

    This function is part of the scraping pipeline and should NOT
    contain print statements or debugging logic.
    """
    attempt = 0
    while attempt < retries:
        try:
            if verbose:
                print(f"Attempt {attempt + 1} to fetch {url}")
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=headless)
                page = await browser.new_page()

                try:
                    await page.set_extra_http_headers(get_nba_headers(url))

                    if verbose:
                        print(f"Navigating to {url}")
                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=60000
                    )

                    if wait_for_selector:
                        if verbose:
                            print(f"Waiting for selector: {wait_for_selector}")
                        await page.wait_for_selector(wait_for_selector, timeout=60000)
                        element = await page.query_selector(wait_for_selector)
                        html = await element.inner_html() if element else ""
                    else:
                        # Temporary: allow JS to finish injecting content (debug/discovery phase)
                        await page.wait_for_timeout(5000)
                        html = await page.content()
                finally:
                    await browser.close()

            return html
        except (PlaywrightError, asyncio.TimeoutError) as e:
            if verbose:
                print(f"Error on attempt {attempt + 1}: {e}")
            attempt += 1
            if attempt >= retries:
                raise
            if verbose:
                print(f"Retrying ({attempt}/{retries})...")


# --- Debug entry point ---
# This block exists ONLY so you can run this file directly
# during development to inspect output. It is not used by
# the rest of the application.
if __name__ == "__main__":
    TEST_URL = "https://basketball.realgm.com/nba/stats"
    html = asyncio.run(fetch_stats_html(TEST_URL, headless=False))
    print(html[:1000])
