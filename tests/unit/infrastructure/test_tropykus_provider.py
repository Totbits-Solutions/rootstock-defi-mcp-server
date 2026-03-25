"""Tests for Tropykus lending provider."""

from unittest.mock import AsyncMock

import pytest

from src.domain.shared.exceptions import BlockchainQueryError
from src.domain.shared.models import Protocol
from src.infrastructure.providers.lending.tropykus_provider import TropykusLendingProvider


@pytest.fixture
def gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def provider(gateway: AsyncMock) -> TropykusLendingProvider:
    return TropykusLendingProvider(gateway)


class TestSupportedMarkets:
    def test_returns_four_markets(self, provider: TropykusLendingProvider) -> None:
        markets = provider.supported_markets()
        assert len(markets) == 4
        assert set(markets) == {"kRBTC", "kDOC", "kUSDRIF", "kBPRO"}


class TestGetMarket:
    async def test_get_market_returns_lending_market(
        self, provider: TropykusLendingProvider, gateway: AsyncMock
    ) -> None:
        # supply_rate, borrow_rate, cash, borrows, reserves
        gateway.call.side_effect = [
            int(2e13),       # supplyRatePerBlock (~2% APY)
            int(5e13),       # borrowRatePerBlock (~5% APY)
            500 * 10**18,    # getCash
            200 * 10**18,    # totalBorrows
            10 * 10**18,     # totalReserves
        ]

        result = await provider.get_market("kRBTC")
        assert result.market == "kRBTC"
        assert result.protocol == Protocol.TROPYKUS
        assert result.rates.supply_apy > 0
        assert result.rates.supply_apr > 0
        assert result.rates.borrow_apy > result.rates.supply_apy
        assert result.pool.total_borrows_usd == 200.0
        assert result.pool.available_liquidity_usd == 500.0
        assert result.pool.utilization_rate > 0

    async def test_unknown_market_raises(
        self, provider: TropykusLendingProvider, gateway: AsyncMock
    ) -> None:
        with pytest.raises(BlockchainQueryError, match="Unknown Tropykus market"):
            await provider.get_market("kINVALID")

    async def test_utilization_zero_when_denom_zero(
        self, provider: TropykusLendingProvider, gateway: AsyncMock
    ) -> None:
        # cash=0, borrows=0, reserves=0 → denom=0
        gateway.call.side_effect = [
            0,  # supplyRatePerBlock
            0,  # borrowRatePerBlock
            0,  # getCash
            0,  # totalBorrows
            0,  # totalReserves
        ]

        result = await provider.get_market("kDOC")
        assert result.pool.utilization_rate == 0.0


class TestGetAllMarkets:
    async def test_returns_four_markets(
        self, provider: TropykusLendingProvider, gateway: AsyncMock
    ) -> None:
        # 5 calls per market × 4 markets = 20 calls
        gateway.call.side_effect = [
            int(2e13), int(5e13), 500 * 10**18, 200 * 10**18, 10 * 10**18,
            int(1e13), int(3e13), 1000 * 10**18, 300 * 10**18, 20 * 10**18,
            int(3e13), int(7e13), 200 * 10**18, 100 * 10**18, 5 * 10**18,
            int(1e13), int(4e13), 800 * 10**18, 150 * 10**18, 15 * 10**18,
        ]

        results = await provider.get_all_markets()
        assert len(results) == 4
        market_names = {r.market for r in results}
        assert market_names == {"kRBTC", "kDOC", "kUSDRIF", "kBPRO"}
