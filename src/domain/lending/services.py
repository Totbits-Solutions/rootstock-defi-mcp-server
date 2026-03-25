"""Domain service for the Lending bounded context."""

from ..shared.exceptions import ProtocolNotSupportedError
from ..shared.models import Protocol
from .models import LendingMarket
from .ports import LendingProvider


class LendingService:
    """Orchestrates multiple LendingProviders using the Strategy pattern."""

    def __init__(self, providers: dict[Protocol, LendingProvider]) -> None:
        self._providers = providers

    async def get_all_rates(self) -> list[LendingMarket]:
        results: list[LendingMarket] = []
        for provider in self._providers.values():
            results.extend(await provider.get_all_markets())
        return results

    async def get_rates_by_protocol(self, protocol: Protocol) -> list[LendingMarket]:
        provider = self._providers.get(protocol)
        if not provider:
            raise ProtocolNotSupportedError(f"No provider for {protocol}")
        return await provider.get_all_markets()

    async def get_market(self, protocol: Protocol, market: str) -> LendingMarket:
        provider = self._providers.get(protocol)
        if not provider:
            raise ProtocolNotSupportedError(f"No provider for {protocol}")
        return await provider.get_market(market)

    @staticmethod
    def blocks_per_year() -> int:
        return 1_051_200

    @staticmethod
    def rate_per_block_to_apy(rate_per_block: float, blocks_per_year: int = 1_051_200) -> float:
        return ((1 + rate_per_block) ** blocks_per_year - 1) * 100
