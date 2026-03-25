"""Tests for application use cases."""

from unittest.mock import AsyncMock, MagicMock

from src.application.get_token_prices import get_token_prices
from src.domain.pricing.models import TokenPrice
from src.domain.shared.models import Protocol, Token


def _make_token_price(token: Token, price: float) -> TokenPrice:
    return TokenPrice(
        token=token,
        price_usd=price,
        source="test",
        protocol=Protocol.MOC,
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
