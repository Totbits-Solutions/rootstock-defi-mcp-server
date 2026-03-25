"""Ports (strategy interfaces) for the Lending bounded context."""

from abc import ABC, abstractmethod

from .models import LendingMarket


class LendingProvider(ABC):
    """Port: each lending protocol implements this interface."""

    @abstractmethod
    def supported_markets(self) -> list[str]:
        """Return the list of market identifiers this provider supports."""
        ...

    @abstractmethod
    async def get_market(self, market: str) -> LendingMarket:
        """Get lending data for a specific market."""
        ...

    @abstractmethod
    async def get_all_markets(self) -> list[LendingMarket]:
        """Get lending data for all supported markets."""
        ...
