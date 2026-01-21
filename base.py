"""
Base headers module for the scraper's headers package.

Responsibilities:
- Provide a randomized User-Agent pool.
- Provide a default header set for generic HTTP requests.
- Provide helper functions usable by topic-specific header modules.
- Expose a build_headers function to compose headers per topic with optional extras.

Designed to be modular and extensible for future topics.
"""

import random
from typing import Dict, Optional

# Randomized User-Agent pool
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43",
    # Chrome on Android
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Mobile Safari/537.36",
]

# Default headers for generic HTTP requests
DEFAULT_HEADERS: Dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",  # Do Not Track Request Header
    "Upgrade-Insecure-Requests": "1",
}

def get_random_user_agent() -> str:
    """
    Returns a random User-Agent string from the pool.
    """
    return random.choice(USER_AGENTS)

# Topic-specific header presets
# These can be imported from topic modules or defined here for now.
# For example, nba_headers.py can define NBA_HEADERS and import here.
# For now, define a sample NBA preset.
NBA_HEADERS: Dict[str, str] = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
}

# Mapping topic names to their header presets
TOPIC_PRESETS = {
    "nba": NBA_HEADERS,
    # Future topics can be added here, e.g.:
    # "finance": FINANCE_HEADERS,
    # "news": NEWS_HEADERS,
}

def merge_headers(base: Dict[str, str], override: Optional[Dict[str, str]]) -> Dict[str, str]:
    """
    Merge two header dictionaries, with override taking precedence.
    """
    if override is None:
        return base.copy()
    merged = base.copy()
    merged.update(override)
    return merged

def build_headers(url: str, topic: str = "nba", extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Build a headers dictionary for a given URL and topic.

    Args:
        url (str): The URL to be requested (not currently used but kept for extensibility).
        topic (str): The topic preset to use (default 'nba').
        extra (Optional[Dict[str, str]]): Additional headers to merge on top.

    Returns:
        Dict[str, str]: The composed headers dictionary.
    """
    # Start with defaults
    headers = DEFAULT_HEADERS.copy()

    # Merge topic-specific preset if available
    topic_headers = TOPIC_PRESETS.get(topic.lower())
    if topic_headers:
        headers = merge_headers(headers, topic_headers)

    # Add randomized User-Agent
    headers["User-Agent"] = get_random_user_agent()

    # Merge any extra headers passed
    if extra:
        headers = merge_headers(headers, extra)

    return headers

if __name__ == "__main__":
    # Debug entry point: print example headers for realgm.com with nba topic
    example_url = "https://www.realgm.com/"
    example_headers = build_headers(example_url, topic="nba")
    print("Example headers for", example_url)
    for k, v in example_headers.items():
        print(f"{k}: {v}")
