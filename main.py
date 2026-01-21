"""
Project entry point.

This file is intentionally kept thin. It delegates all real work to the
`scrape` package so imports remain stable and testable.
"""

import asyncio
from src.scrape.fetcher import fetch
from src.scrape.parse import parse_realgm_stats
from src.scrape.normalize import normalize_realgm_stats
from src.scrape.storage import insert_rows
from src.scrape.headers.nba_headers import get_nba_headers


async def run() -> None:
    """
    Orchestrates the full scraping pipeline:

    1. Fetch RealGM stats page HTML (HTTP or Playwright).
    2. Parse the HTML into structured rows.
    3. Normalize the rows into a consistent schema.
    4. Persist the normalized rows to storage.
    """

    headers = get_nba_headers("https://basketball.realgm.com/nba/stats")

    html = await fetch(
        url="https://basketball.realgm.com/nba/stats",
        use_playwright=True,
    )

    rows = parse_realgm_stats(html)
    normalized_rows = normalize_realgm_stats(rows)

    insert_rows(normalized_rows)

    # Lightweight verification output
    print(f"Inserted {len(normalized_rows)} rows.")
    for row in normalized_rows[:3]:
        print(row)


def main() -> None:
    """
    Synchronous entry point for CLI execution.
    """
    asyncio.run(run())


if __name__ == "__main__":
    main()
