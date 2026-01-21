from typing import List, Dict, Any
import re


def _to_snake_case(name: str) -> str:
    """
    Normalize column names like 'FG%' or '3PA' into snake_case keys.
    """
    name = name.lower()
    name = re.sub(r"%", "_pct", name)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def _coerce_value(value: str) -> Any:
    """
    Convert scraped string values into int / float where possible.
    """
    if value == "":
        return None

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def normalize_realgm_stats(
    rows: List[Dict[str, str]],
    source_url: str = "https://basketball.realgm.com/nba/stats"
) -> List[Dict[str, Any]]:
    """
    Normalize parsed RealGM stat rows into model-ready dictionaries.
    """
    normalized: List[Dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue
        clean_row: Dict[str, Any] = {
            "source": source_url
        }

        for key, value in row.items():
            norm_key = _to_snake_case(key)
            if norm_key == "":
                norm_key = "rank"
            clean_row[norm_key] = _coerce_value(value)

        normalized.append(clean_row)

    return normalized


if __name__ == "__main__":
    example_rows = [
        {"Player": "LeBron James", "FG%": "52.3", "3PA": "8", "Team": "LAL"},
        {"Player": "Stephen Curry", "FG%": "48.1", "3PA": "10", "Team": "GSW"},
    ]
    normalized = normalize_realgm_stats(example_rows)
    for row in normalized:
        print(row)