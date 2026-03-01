

from typing import Optional, TypeVar, Generic

from core.services.extraction_service import ExtractionService
from core.services.normalization_service import NormalizationService


T = TypeVar("T")  # Extracted type
R = TypeVar("R")  # Normalized type


class HttpClientPort:
    """
    Outbound port responsible for retrieving raw data
    from an external source (HTTP, API, file system, etc.).
    """

    async def fetch(self, url: str, headers: Optional[dict] = None) -> str:
        raise NotImplementedError


class StoragePort(Generic[R]):
    """
    Outbound port responsible for persisting normalized objects.
    """

    async def save(self, items: list[R]) -> None:
        raise NotImplementedError


class ScrapeOrchestrator(Generic[T, R]):
    """
    Application-level orchestration service.

    Coordinates the scraping workflow:

        1. Fetch raw data via HttpClientPort
        2. Extract structured data via ExtractionService
        3. Normalize structured data via NormalizationService
        4. Persist normalized data via StoragePort

    This class:
        - Contains NO domain-specific logic
        - Contains NO infrastructure implementation
        - Depends only on abstract boundaries

    It represents a single executable scrape use-case.
    """

    def __init__(
        self,
        name: str,
        target_url: str,
        http_client: HttpClientPort,
        extractor: ExtractionService,
        normalizer: NormalizationService[T, R],
        storage: StoragePort[R],
        headers: Optional[dict] = None,
    ) -> None:
        self.name = name
        self.target_url = target_url
        self.http_client = http_client
        self.extractor = extractor
        self.normalizer = normalizer
        self.storage = storage
        self.headers = headers or {}

    async def execute(self) -> None:
        """
        Execute the full scraping workflow.
        """

        # 1. Fetch
        raw_data = await self.http_client.fetch(
            self.target_url,
            headers=self.headers,
        )

        # 2. Extract
        extracted = await self.extractor.extract(raw_data)

        # 3. Normalize
        normalized = self.normalizer.normalize(extracted)

        # 4. Persist
        await self.storage.save(list(normalized))