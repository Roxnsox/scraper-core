"""
Scrapy integration layer.

This module wires Scrapy into the existing scraping pipeline without
duplicating fetch / parse / normalize / storage logic.

Scrapy is used ONLY for:
- crawl orchestration
- request scheduling
- retries / throttling
- future multi-page expansion

All data processing is delegated to the existing pipeline.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Iterable

import scrapy
from scrapy.crawler import CrawlerProcess

from .fetch_playwright import fetch_stats_html
from .headers.nba_headers import get_nba_headers
from .parse import parse_realgm_stats
from .normalize import normalize_realgm_stats
from .storage import insert_rows


class RealGMSpider(scrapy.Spider):
    """
    Scrapy spider that delegates page rendering to Playwright
    and data processing to the existing pipeline.
    """

    name = "realgm_stats"
    allowed_domains = ["basketball.realgm.com"]
    start_urls = ["https://basketball.realgm.com/nba/stats"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "LOG_LEVEL": "INFO",
    }

    def parse(self, response: scrapy.http.Response) -> Iterable:
        """
        Scrapy callback.

        Scrapy fetches the URL, but we intentionally ignore its body
        and re-fetch via Playwright for JS-complete HTML.

        Note:
            Headers are applied via the new NBA headers package inside Playwright.
        """

        self.logger.info("Delegating render to Playwright")

        try:
            # Use wait_for_selector to ensure main table is loaded
            html = asyncio.run(fetch_stats_html(response.url, wait_for_selector="table"))
        except Exception as e:
            self.logger.error("Exception during Playwright fetch: %s", e, exc_info=True)
            return []

        self.logger.info("Fetched HTML length: %d", len(html))
        self.logger.debug("Fetched HTML preview: %s", html[:500])

        if os.getenv("DEBUG_HTML"):
            try:
                debug_path = "debug_realgm_stats.html"
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(html)
                self.logger.info("Saved debug HTML to %s", debug_path)
            except Exception as e:
                self.logger.error("Failed to save debug HTML: %s", e, exc_info=True)

        try:
            rows = parse_realgm_stats(html)
            normalized = normalize_realgm_stats(rows)
        except Exception as e:
            self.logger.error("Exception during parse/normalize: %s", e, exc_info=True)
            return []

        try:
            insert_rows(normalized)
        except Exception as e:
            self.logger.error("Exception during insert_rows: %s", e, exc_info=True)
            return []

        self.logger.info("Stored %d rows", len(normalized))

        # Scrapy expects an iterable
        return []


def run_scrapy() -> None:
    """
    Entry point for running the Scrapy pipeline programmatically.

    This allows Scrapy to be invoked from main.run() or any other
    orchestration layer without CLI usage.
    """

    process = CrawlerProcess()
    process.crawl(RealGMSpider)
    process.start()
