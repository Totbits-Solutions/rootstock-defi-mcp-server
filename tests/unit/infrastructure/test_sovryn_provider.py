"""Tests for Sovryn lending provider."""

from unittest.mock import AsyncMock

import pytest

from src.domain.shared.exceptions import BlockchainQueryError
from src.domain.shared.models import Protocol
from src.infrastructure.providers.lending.sovryn_provider import SovrynLendingProvider


@pytest.fixture
def gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def provider(gateway: AsyncMock) -> SovrynLendingProvider:
    return SovrynLendingProvider(gateway)


class TestSupportedMarkets:
    def test_returns_six_pools(self, provider: SovrynLendingProvider) -> None:
        markets = provider.supported_markets()
        assert len(markets) == 6
        assert set(markets) == {"iRBTC", "iDOC", "iUSDT", "iBPro", "iXUSD", "iDLLR"}


class TestGetMarket:
    async def test_get_market_returns_lending_market(self, provider: SovrynLendingProvider, gateway: AsyncMock) -> None:
        # Sovryn rates are already annualized: 3% = 3 * 1e18
        gateway.call.side_effect = [
            (3 * 10**18),  # supplyInterestRate (3% APY)
            (8 * 10**18),  # borrowInterestRate (8% APY)
            1000 * 10**18,  # totalAssetSupply
            400 * 10**18,  # totalAssetBorrow
        ]

        result = await provider.get_market("iRBTC")
        assert result.market == "iRBTC"
        assert result.protocol == Protocol.SOVRYN
        assert result.rates.supply_apy == 3.0
        assert result.rates.borrow_apy == 8.0
        # APR == APY for Sovryn (simplification)
        assert result.rates.supply_apr == result.rates.supply_apy
        assert result.pool.total_supply_usd == 1000.0
        assert result.pool.total_borrows_usd == 400.0
        assert result.pool.available_liquidity_usd == 600.0
        assert result.pool.utilization_rate == 40.0

    async def test_unknown_pool_raises(self, provider: SovrynLendingProvider, gateway: AsyncMock) -> None:
        with pytest.raises(BlockchainQueryError, match="Unknown Sovryn pool"):
            await provider.get_market("iINVALID")

    async def test_utilization_zero_when_supply_zero(self, provider: SovrynLendingProvider, gateway: AsyncMock) -> None:
        gateway.call.side_effect = [
            0,  # supplyInterestRate
            0,  # borrowInterestRate
            0,  # totalAssetSupply
            0,  # totalAssetBorrow
        ]

        result = await provider.get_market("iDOC")
        assert result.pool.utilization_rate == 0.0


class TestGetAllMarkets:
    async def test_returns_six_pools(self, provider: SovrynLendingProvider, gateway: AsyncMock) -> None:
        # 4 calls per pool x 6 pools = 24 calls
        pool_data = [(2 * 10**18), (5 * 10**18), 500 * 10**18, 200 * 10**18]
        gateway.call.side_effect = pool_data * 6

        results = await provider.get_all_markets()
        assert len(results) == 6
        market_names = {r.market for r in results}
        assert market_names == {"iRBTC", "iDOC", "iUSDT", "iBPro", "iXUSD", "iDLLR"}
