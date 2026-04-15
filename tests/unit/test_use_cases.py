"""Tests for application use cases."""

from unittest.mock import AsyncMock, MagicMock

from src.application.get_stablecoin_health import get_stablecoin_health
from src.application.get_token_prices import get_token_prices
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


def _make_stablecoin_health(
    token: Token, protocol: Protocol = Protocol.MOC
) -> StablecoinHealth:
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
