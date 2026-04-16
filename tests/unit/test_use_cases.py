"""Tests for application use cases."""

from unittest.mock import AsyncMock, MagicMock

from src.application.get_lending_rates import get_lending_rates
from src.application.get_stablecoin_health import get_stablecoin_health
from src.application.get_token_prices import get_token_prices
from src.domain.lending.models import LendingMarket, PoolMetrics, RateInfo
from src.domain.pricing.models import (
    CollateralInfo,
    CoverageMetrics,
    PegStatus,
    StablecoinHealth,
    TokenPrice,
)
from src.domain.shared.models import Protocol, Token


def _make_token_price(token: Token, price: float) -> TokenPrice:
    return TokenPrice(
        token=token,
        price_usd=price,
        source="test",
        protocol=Protocol.MOC,
    )


def _make_lending_market(market: str, protocol: Protocol = Protocol.TROPYKUS) -> LendingMarket:
    return LendingMarket(
        market=market,
        protocol=protocol,
        rates=RateInfo(
            supply_apr=2.5,
            supply_apy=2.53,
            borrow_apr=5.0,
            borrow_apy=5.12,
        ),
        pool=PoolMetrics(
            total_supply_usd=1_000_000.0,
            total_borrows_usd=400_000.0,
            available_liquidity_usd=600_000.0,
            utilization_rate=0.4,
        ),
    )


def _make_stablecoin_health(token: Token, protocol: Protocol = Protocol.MOC) -> StablecoinHealth:
    return StablecoinHealth(
        token=token,
        protocol_price_usd=1.0,
        collateral=CollateralInfo(
            asset=Token.RBTC,
            locked_amount=10.0,
            value_usd=670_000.0,
        ),
        coverage=CoverageMetrics(
            current=4.0,
            target=2.1,
            liquidation_threshold=1.5,
        ),
        supply={"stablecoin": 1_000_000.0, "leveraged": 5_000.0},
        status=PegStatus.HEALTHY,
        protocol=protocol,
    )


class TestGetTokenPrices:
    async def test_returns_all_prices(self) -> None:
        mock_service = MagicMock()
        mock_service.get_prices = AsyncMock(
            return_value={
                Token.RBTC: _make_token_price(Token.RBTC, 67000.0),
                Token.BPRO: _make_token_price(Token.BPRO, 150.0),
            }
        )

        result = await get_token_prices(mock_service)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, dict) for item in result)
        assert result[0]["token"] == "RBTC"
        assert result[0]["price_usd"] == 67000.0

    async def test_filtered_by_token(self) -> None:
        mock_service = MagicMock()
        mock_service.get_prices = AsyncMock(
            return_value={
                Token.RBTC: _make_token_price(Token.RBTC, 67000.0),
            }
        )

        result = await get_token_prices(mock_service, tokens=[Token.RBTC])

        mock_service.get_prices.assert_called_once_with([Token.RBTC])
        assert len(result) == 1
        assert result[0]["token"] == "RBTC"

    async def test_empty_result(self) -> None:
        mock_service = MagicMock()
        mock_service.get_prices = AsyncMock(return_value={})

        result = await get_token_prices(mock_service)
        assert result == []


class TestGetStablecoinHealth:
    async def test_returns_all_stablecoin_health(self) -> None:
        mock_service = MagicMock()
        mock_service.get_stablecoin_health = AsyncMock(
            return_value={
                Token.DOC: _make_stablecoin_health(Token.DOC, Protocol.MOC),
                Token.USDRIF: _make_stablecoin_health(Token.USDRIF, Protocol.ROC_V2),
            }
        )

        result = await get_stablecoin_health(mock_service)

        mock_service.get_stablecoin_health.assert_called_once_with(None)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, dict) for item in result)
        tokens = {item["token"] for item in result}
        assert tokens == {"DOC", "USDRIF"}
        assert result[0]["status"] == "HEALTHY"
        assert result[0]["collateral"]["asset"] == "RBTC"
        assert result[0]["coverage"]["current"] == 4.0

    async def test_filtered_by_token(self) -> None:
        mock_service = MagicMock()
        mock_service.get_stablecoin_health = AsyncMock(
            return_value={
                Token.DOC: _make_stablecoin_health(Token.DOC, Protocol.MOC),
            }
        )

        result = await get_stablecoin_health(mock_service, tokens=[Token.DOC])

        mock_service.get_stablecoin_health.assert_called_once_with([Token.DOC])
        assert len(result) == 1
        assert result[0]["token"] == "DOC"

    async def test_empty_result(self) -> None:
        mock_service = MagicMock()
        mock_service.get_stablecoin_health = AsyncMock(return_value={})

        result = await get_stablecoin_health(mock_service)
        assert result == []


class TestGetLendingRates:
    async def test_returns_all_rates(self) -> None:
        mock_service = MagicMock()
        mock_service.get_all_rates = AsyncMock(
            return_value=[
                _make_lending_market("kDOC", Protocol.TROPYKUS),
                _make_lending_market("iDOC", Protocol.SOVRYN),
            ]
        )

        result = await get_lending_rates(mock_service)

        mock_service.get_all_rates.assert_called_once_with()
        assert isinstance(result, list)
        assert len(result) == 2
        markets = {item["market"] for item in result}
        assert markets == {"kDOC", "iDOC"}

    async def test_filtered_by_protocol(self) -> None:
        mock_service = MagicMock()
        mock_service.get_rates_by_protocol = AsyncMock(
            return_value=[
                _make_lending_market("kDOC", Protocol.TROPYKUS),
                _make_lending_market("kRBTC", Protocol.TROPYKUS),
            ]
        )

        result = await get_lending_rates(mock_service, protocol=Protocol.TROPYKUS)

        mock_service.get_rates_by_protocol.assert_called_once_with(Protocol.TROPYKUS)
        assert len(result) == 2
        assert all(item["protocol"] == "tropykus" for item in result)

    async def test_filtered_by_protocol_and_market(self) -> None:
        mock_service = MagicMock()
        mock_service.get_market = AsyncMock(
            return_value=_make_lending_market("kDOC", Protocol.TROPYKUS),
        )

        result = await get_lending_rates(mock_service, protocol=Protocol.TROPYKUS, market="kDOC")

        mock_service.get_market.assert_called_once_with(Protocol.TROPYKUS, "kDOC")
        assert len(result) == 1
        assert result[0]["market"] == "kDOC"
        assert result[0]["protocol"] == "tropykus"

    async def test_empty_result(self) -> None:
        mock_service = MagicMock()
        mock_service.get_all_rates = AsyncMock(return_value=[])

        result = await get_lending_rates(mock_service)
        assert result == []
