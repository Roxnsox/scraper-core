import asyncio
from .fetch_http import fetch_html
from .fetch_playwright import fetch_stats_html
from .headers.nba_headers import get_nba_headers

async def fetch(url: str, use_playwright: bool = False) -> str:
    """
    Fetch HTML content from a URL using either HTTP or Playwright.

    Args:
        url (str): The URL to fetch.
        use_playwright (bool): Whether to use Playwright for fetching. Defaults to False.

    Returns:
        str: The fetched HTML content.
    """
    if use_playwright:
        return await fetch_stats_html(url)
    else:
        headers = get_nba_headers(url)
        return await fetch_html(url, headers=headers)

if __name__ == "__main__":
    async def main():
        test_url = "https://basketball.realgm.com/nba/stats"
        print("Fetching using HTTP...")
        html_http = await fetch(test_url, use_playwright=False)
        print(f"HTTP fetch length: {len(html_http)}")

        print("Fetching using Playwright...")
        html_playwright = await fetch(test_url, use_playwright=True)
        print(f"Playwright fetch length: {len(html_playwright)}")

    asyncio.run(main())
