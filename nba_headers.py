from typing import Optional, Dict
from .base import build_headers

REALGM_HEADERS: Dict[str, str] = {
    "Referer": "https://basketball.realgm.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

BASKETBALL_REFERENCE_HEADERS: Dict[str, str] = {
    "Referer": "https://www.basketball-reference.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

ESPN_HEADERS: Dict[str, str] = {
    "Referer": "https://www.espn.com/nba/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def get_nba_headers(site_url: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Return headers tailored for NBA stats sites based on the provided site URL.
    Merges the site-specific preset headers with any extra headers provided.

    Args:
        site_url (str): The URL of the NBA stats site.
        extra (Optional[Dict[str, str]]): Additional headers to merge.

    Returns:
        Dict[str, str]: The combined headers dictionary.
    """
    site_url_lower = site_url.lower()
    if "realgm.com" in site_url_lower:
        preset = REALGM_HEADERS.copy()
    elif "basketball-reference.com" in site_url_lower:
        preset = BASKETBALL_REFERENCE_HEADERS.copy()
    elif "espn.com" in site_url_lower and "/nba" in site_url_lower:
        preset = ESPN_HEADERS.copy()
    else:
        # Default to RealGM headers if unknown
        preset = REALGM_HEADERS.copy()

    if extra:
        preset.update(extra)
    return build_headers(url=site_url, topic="nba", extra=preset)


if __name__ == "__main__":
    # Debug example usage for RealGM headers
    example_headers = get_nba_headers("https://basketball.realgm.com/player/1234")
    print("Example RealGM NBA headers:")
    for k, v in example_headers.items():
        print(f"{k}: {v}")
