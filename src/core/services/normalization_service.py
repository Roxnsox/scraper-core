

from typing import Iterable, Any, TypeVar, Generic
from abc import ABC, abstractmethod


T = TypeVar("T")
R = TypeVar("R")


class NormalizationService(ABC, Generic[T, R]):
    """
    Abstract normalization service contract.

    Responsible for transforming extracted data into
    normalized, domain-ready objects.

    This layer is where:
        - Type coercion happens
        - Validation rules are applied
        - Domain invariants are enforced
        - Raw dictionaries become domain entities

    This class defines the behavioral boundary used by the
    core orchestrator.
    """

    @abstractmethod
    def normalize(self, data: Iterable[T]) -> Iterable[R]:
        """
        Transform extracted data into normalized objects.
        """
        pass


class PassThroughNormalizationService(NormalizationService[T, T]):
    """
    Generic infrastructural implementation.

    Performs no transformation and simply returns
    the incoming data unchanged.

    Useful when:
        - Extraction already returns domain objects
        - You want to bypass normalization temporarily
        - You are testing pipeline wiring
    """

    def normalize(self, data: Iterable[T]) -> Iterable[T]:
        return data