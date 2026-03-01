from __future__ import annotations
import random
import time
import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    # Only for typing, not runtime
    from typing import Callable

__all__ = ["RequestPolicy", "SimpleRequestPolicy", "RateLimitExceeded"]


class RateLimitExceeded(Exception):
    """Raised when a request should be delayed due to rate limiting."""
    pass


class RequestPolicy(ABC):
    """
    Abstract policy defining how HTTP requests should be issued.

    This exists at the infrastructural/core boundary.
    It contains:
      - no domain logic
      - no parser logic
      - no framework logic
    """

    @abstractmethod
    def before_request(self, url: str) -> None:
        """
        Called immediately before each outgoing request.

        Implementers can raise RateLimitExceeded to signal
        that the caller should retry later.
        """
        ...

    @abstractmethod
    def after_response(self, url: str, status_code: int, elapsed: float) -> None:
        """
        Called immediately after receiving a response.

        This allows:
          - dynamic backoff
          - throttling
          - detecting soft blocks (429, 503, captcha, etc.)
        """
        ...


class SimpleRequestPolicy(RequestPolicy):
    """
    A simple but practical default policy.

    Features:
      - fixed delay between requests
      - optional random jitter
      - simple retry/backoff support
      - basic status-code based soft block detection
    """

    def __init__(
        self,
        delay_seconds: float = 0.0,
        jitter: float = 0.0,
        backoff_multiplier: float = 1.5,
        max_backoff: float = 10.0,
        adaptive: bool = True,
    ) -> None:
        self.delay = delay_seconds
        self.jitter = jitter
        self.backoff_multiplier = backoff_multiplier
        self.max_backoff = max_backoff
        self._current_backoff = delay_seconds
        self.adaptive = adaptive
        self._last_request_time: Optional[float] = None

    def _sleep(self) -> None:
        """
        Delay according to policy before next request.
        """
        interval = self._current_backoff
        if self.jitter > 0:
            # Add random jitter so it's not perfectly steady
            interval += random.uniform(-self.jitter, self.jitter)

        time.sleep(max(0.0, interval))

    def before_request(self, url: str) -> None:
        """
        Optionally block immediately before a request.
        """
        if self._last_request_time is not None:
            # Time since last request
            elapsed = time.time() - self._last_request_time
            if elapsed < self._current_backoff:
                raise RateLimitExceeded(
                    f"Rate limit: must wait {self._current_backoff - elapsed:.2f}s"
                )

        # Apply the delay before calling out
        self._sleep()

    def after_response(self, url: str, status_code: int, elapsed: float) -> None:
        """
        Adapt policy based on response status or time.
        """
        # Update last request timestamp
        self._last_request_time = time.time()

        # If adaptive backoff is enabled and we see throttling or slow responses,
        # increase the delay (up to max_backoff).
        if self.adaptive:
            if status_code in (429, 503):
                self._current_backoff = min(
                    self._current_backoff * self.backoff_multiplier,
                    self.max_backoff,
                )


# Async version helpers

class AsyncRequestPolicy(RequestPolicy):
    """Same contract, async friendly."""

    @abstractmethod
    async def before_request(self, url: str) -> None:
        ...

    @abstractmethod
    async def after_response(self, url: str, status_code: int, elapsed: float) -> None:
        ...


class AsyncSimpleRequestPolicy(AsyncRequestPolicy):
    """
    Async equivalent of SimpleRequestPolicy with asyncio.sleep.
    """

    def __init__(
        self,
        delay: float = 0.0,
        jitter: float = 0.0,
        backoff_multiplier: float = 1.5,
        max_backoff: float = 10.0,
        adaptive: bool = True,
    ) -> None:
        self.delay = delay
        self.jitter = jitter
        self.backoff_multiplier = backoff_multiplier
        self.max_backoff = max_backoff
        self.adaptive = adaptive
        self._current_backoff = delay
        self._last_request_time: float | None = None

    async def before_request(self, url: str) -> None:
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._current_backoff:
                raise RateLimitExceeded(
                    f"Rate limit: must wait {self._current_backoff - elapsed:.2f}s"
                )

        # Use asyncio.sleep for async delays
        wait_for = self._current_backoff
        if self.jitter:
            wait_for += random.uniform(-self.jitter, self.jitter)

        await asyncio.sleep(max(0.0, wait_for))

    async def after_response(self, url: str, status_code: int, elapsed: float) -> None:
        self._last_request_time = time.time()
        if self.adaptive and status_code in (429, 503):
            self._current_backoff = min(
                self._current_backoff * self.backoff_multiplier,
                self.max_backoff,
            )