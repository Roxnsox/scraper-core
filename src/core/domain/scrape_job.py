from typing import Any, Iterable, Protocol


class ExtractionService(Protocol):
    async def extract(self, raw_data: str) -> Iterable[Any]:
        ...


class NormalizationService(Protocol):
    def normalize(self, data: Iterable[Any]) -> Iterable[Any]:
        ...


class HttpClientPort(Protocol):
    async def fetch(self, url: str, headers: dict | None = None) -> str:
        ...


class StoragePort(Protocol):
    async def save(self, items: Iterable[Any]) -> None:
        ...


class ScrapeJob:
    """
    Represents a single scraping operation.

    Coordinates:
        - Fetching raw data
        - Extracting structured domain objects
        - Normalizing data
        - Persisting results

    This class contains NO framework or infrastructure logic.
    """

    def __init__(
        self,
        name: str,
        target_url: str,
        http_client: HttpClientPort,
        extraction_service: ExtractionService,
        normalization_service: NormalizationService,
        storage: StoragePort,
        headers: dict | None = None,
    ) -> None:
        self.name = name
        self.target_url = target_url
        self.http_client = http_client
        self.extraction_service = extraction_service
        self.normalization_service = normalization_service
        self.storage = storage
        self.headers = headers or {}

    async def execute(self) -> None:
        """
        Executes the scraping workflow.
        """
        raw_data = await self.http_client.fetch(
            self.target_url,
            headers=self.headers,
        )

        extracted_items = await self.extraction_service.extract(raw_data)

        normalized_items = self.normalization_service.normalize(extracted_items)

        await self.storage.save(normalized_items)