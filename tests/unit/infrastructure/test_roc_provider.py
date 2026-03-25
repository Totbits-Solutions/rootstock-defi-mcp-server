"""Tests for RoC V2 price provider."""

from unittest.mock import AsyncMock

import pytest

from src.domain.pricing.models import PegStatus
from src.domain.shared.exceptions import BlockchainQueryError
from src.domain.shared.models import Protocol, Token
from src.infrastructure.providers.pricing.roc_price_provider import RoCPriceProvider


def _peek_valid(price_wei: int) -> tuple[bytes, bool]:
    return (price_wei.to_bytes(32, byteorder="big"), True)


def _peek_invalid() -> tuple[bytes, bool]:
    return (b"\x00" * 32, False)


@pytest.fixture
def gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def provider(gateway: AsyncMock) -> RoCPriceProvider:
    return RoCPriceProvider(gateway)


class TestSupportedTokens:
    def test_returns_rif_rifpro_usdrif(self, provider: RoCPriceProvider) -> None:
        assert set(provider.supported_tokens()) == {Token.RIF, Token.RIFPRO, Token.USDRIF}


class TestGetPrice:
    async def test_rif_price(self, provider: RoCPriceProvider, gateway: AsyncMock) -> None:
        rif_price_wei = int(0.03 * 10**18)
        gateway.call.return_value = _peek_valid(rif_price_wei)

        result = await provider.get_price(Token.RIF)
        assert result.token == Token.RIF
        assert abs(result.price_usd - 0.03) < 1e-10
        assert result.protocol == Protocol.ROC_V2

    async def test_rif_invalid_oracle_raises(
        self, provider: RoCPriceProvider, gateway: AsyncMock
    ) -> None:
        gateway.call.return_value = _peek_invalid()
        with pytest.raises(BlockchainQueryError, match="no valid value"):
            await provider.get_price(Token.RIF)

    async def test_rifpro_price_cross_rate(
        self, provider: RoCPriceProvider, gateway: AsyncMock
    ) -> None:
        rif_price_wei = int(0.03 * 10**18)
        rifpro_in_rif = int(1.15 * 10**18)

        gateway.call.side_effect = [
            rifpro_in_rif,
            _peek_valid(rif_price_wei),
        ]

        result = await provider.get_price(Token.RIFPRO)
        assert result.token == Token.RIFPRO
        assert result.price_rif is not None
        assert abs(result.price_rif - 1.15) < 1e-10
        expected_usd = 1.15 * 0.03
        assert abs(result.price_usd - expected_usd) < 1e-10

    async def test_usdrif_price_is_pegged(
        self, provider: RoCPriceProvider, gateway: AsyncMock
    ) -> None:
        result = await provider.get_price(Token.USDRIF)
        assert result.token == Token.USDRIF
        assert result.price_usd == 1.0
        gateway.call.assert_not_called()


class TestGetStablecoinHealth:
    async def test_usdrif_health(
        self, provider: RoCPriceProvider, gateway: AsyncMock
    ) -> None:
        rif_price_wei = int(0.03 * 10**18)
        coverage = int(5.0 * 10**18)
        target = int(3.0 * 10**18)
        liq = int(1.5 * 10**18)
        locked_rif = 10_000_000 * 10**18
        usdrif_supply = 200_000 * 10**18
        rifpro_supply = 5_000_000 * 10**18

        gateway.call.side_effect = [
            _peek_valid(rif_price_wei),
            coverage,
            target,
            liq,
            locked_rif,
            usdrif_supply,
            rifpro_supply,
        ]

        health = await provider.get_stablecoin_health(Token.USDRIF)
        assert health is not None
        assert health.token == Token.USDRIF
        assert health.protocol_price_usd == 1.0
        assert health.market_price_usd is None
        assert health.peg_deviation_pct is None
        assert health.collateral.asset == Token.RIF
        assert health.collateral.locked_amount == 10_000_000.0
        assert health.coverage.current == 5.0
        assert health.status == PegStatus.HEALTHY
        assert "USDRIF" in health.supply
        assert "RIFPRO" in health.supply

    async def test_non_usdrif_returns_none(
        self, provider: RoCPriceProvider, gateway: AsyncMock
    ) -> None:
        result = await provider.get_stablecoin_health(Token.RIF)
        assert result is None
