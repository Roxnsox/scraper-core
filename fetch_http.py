import aiohttp
import asyncio
from typing import Optional, Dict
from .headers.nba_headers import get_nba_headers

async def fetch_html(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Fetch the HTML content of a webpage using aiohttp.

    Args:
        url (str): The URL to fetch.
        headers (Optional[Dict[str, str]]): Optional HTTP headers.

    Returns:
        str: The full HTML content of the response.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
    """
    if headers is None:
        headers = get_nba_headers(url)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, timeout=20) as response:
            response.raise_for_status()
            return await response.text()


# --- Debug entry point ---
if __name__ == "__main__":
    TEST_URL = "https://basketball.realgm.com/nba/stats"
    
    async def main():
        html = await fetch_html(TEST_URL)
        print(html[:1000])
    
    asyncio.run(main())