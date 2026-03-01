from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

T = TypeVar("T")


class ExtractionService(ABC, Generic[T]):
    """
    Core extraction service contract.

    This is a domain-facing abstraction that defines the boundary
    between raw external data (HTML, JSON, etc.) and structured
    intermediate representations used by the domain layer.

    IMPORTANT:
        - This file must contain NO infrastructure imports.
        - This file must NOT depend on BeautifulSoup, httpx, Scrapy, etc.
        - Concrete implementations belong in the adapters layer.

    Responsibilities:
        - Define the behavioral contract for extraction.
        - Allow domain-specific extractors to implement structured output.
        - Enable infrastructure adapters to remain swappable.
    """

    @abstractmethod
    async def extract(self, raw_data: str) -> Iterable[T]:
        """
        Transform raw external data into structured intermediate objects.

        Args:
            raw_data: Raw response payload (HTML, JSON, etc.)

        Returns:
            Iterable of structured intermediate objects suitable
            for domain-level normalization.
        """
        raise NotImplementedError
