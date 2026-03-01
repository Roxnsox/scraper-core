from typing import Iterable, Any, Dict, List
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class ExtractionService(ABC):
    """
    Abstract extraction service contract.

    Domain-specific extraction services (e.g., NBAExtractionService)
    should inherit from this class and implement `extract`.

    This defines the behavioral boundary used by the core orchestrator.
    """

    @abstractmethod
    async def extract(self, raw_data: str) -> Iterable[Any]:
        """
        Transform raw input data into structured intermediate objects.
        """
        pass


class GenericHTMLExtractionService(ExtractionService):
    """
    Generic infrastructural HTML extraction implementation.

    This service:
        - Parses raw HTML
        - Applies configurable selectors
        - Returns structured dictionaries

    It contains:
        - NO domain logic
        - NO business rules
        - NO source-specific assumptions

    It is reusable infrastructure.
    """

    def __init__(self, row_selector: str, field_selectors: Dict[str, str]) -> None:
        """
        Args:
            row_selector: CSS selector identifying each data row.
            field_selectors: Mapping of field name -> CSS selector (relative to row).
        """
        self.row_selector = row_selector
        self.field_selectors = field_selectors

    async def extract(self, raw_data: str) -> Iterable[Dict[str, Any]]:
        soup = BeautifulSoup(raw_data, "html.parser")

        rows = soup.select(self.row_selector)

        extracted_items: List[Dict[str, Any]] = []

        for row in rows:
            item: Dict[str, Any] = {}

            for field_name, selector in self.field_selectors.items():
                element = row.select_one(selector)
                item[field_name] = (
                    element.get_text(strip=True) if element else None
                )

            extracted_items.append(item)

        return extracted_items
