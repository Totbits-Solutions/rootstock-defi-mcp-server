"""Tests for MoC price provider."""

from unittest.mock import AsyncMock

import pytest

from src.domain.pricing.models import PegStatus
from src.domain.shared.exceptions import BlockchainQueryError
from src.domain.shared.models import Protocol, Token
from src.infrastructure.blockchain.contracts import ContractId
from src.infrastructure.providers.pricing.moc_price_provider import MoCPriceProvider


def _make_gateway() -> AsyncMock:
    return AsyncMock()


def _btc_price_wei() -> int:
    return 67_000 * 10**18


def _peek_valid(price_wei: int) -> tuple[bytes, bool]:
    return (price_wei.to_bytes(32, byteorder="big"), True)


def _peek_invalid() -> tuple[bytes, bool]:
    return (b"\x00" * 32, False)


@pytest.fixture
def gateway() -> AsyncMock:
    return _make_gateway()


@pytest.fixture
def provider(gateway: AsyncMock) -> MoCPriceProvider:
    return MoCPriceProvider(gateway)


class TestSupportedTokens:
    def test_returns_rbtc_bpro_doc(self, provider: MoCPriceProvider) -> None:
        assert set(provider.supported_tokens()) == {Token.RBTC, Token.BPRO, Token.DOC}


class TestGetPrice:
    async def test_rbtc_price(self, provider: MoCPriceProvider, gateway: AsyncMock) -> None:
        gateway.call.return_value = _peek_valid(_btc_price_wei())
        result = await provider.get_price(Token.RBTC)

        assert result.token == Token.RBTC
        assert result.price_usd == 67_000.0
        assert result.protocol == Protocol.MOC
        gateway.call.assert_called_once_with(ContractId.BTC_USD_ORACLE, "peek")

    async def test_rbtc_invalid_oracle_raises(
        self, provider: MoCPriceProvider, gateway: AsyncMock
    ) -> None:
        gateway.call.return_value = _peek_invalid()
        with pytest.raises(BlockchainQueryError, match="no valid value"):
            await provider.get_price(Token.RBTC)

    async def test_bpro_price(self, provider: MoCPriceProvider, gateway: AsyncMock) -> None:
        gateway.call.side_effect = [
            150 * 10**18,   # bproUsdPrice
            0.002 * 10**18,  # bproTecPrice (in BTC, as int)
        ]
        # Fix: side_effect needs int values
        gateway.call.side_effect = [
            int(150 * 10**18),
            int(0.002 * 10**18),
        ]
        result = await provider.get_price(Token.BPRO)

        assert result.token == Token.BPRO
        assert result.price_usd == 150.0
        assert result.price_btc is not None
        assert result.protocol == Protocol.MOC

    async def test_doc_price_is_pegged(
        self, provider: MoCPriceProvider, gateway: AsyncMock
    ) -> None:
        result = await provider.get_price(Token.DOC)
        assert result.token == Token.DOC
        assert result.price_usd == 1.0
        gateway.call.assert_not_called()

    async def test_unsupported_token_raises(self, provider: MoCPriceProvider) -> None:
        from src.domain.shared.exceptions import TokenNotSupportedError

        with pytest.raises(TokenNotSupportedError):
            await provider.get_price(Token.RIF)


class TestGetStablecoinHealth:
    async def test_doc_health(self, provider: MoCPriceProvider, gateway: AsyncMock) -> None:
        btc_price = 67_000 * 10**18
        coverage = int(4.5 * 10**18)
        doc_supply = 1_000_000 * 10**18
        bpro_supply = 500 * 10**18
        locked_btc = 100 * 10**18
        target = int(3.0 * 10**18)
        liq = int(1.5 * 10**18)

        # Calls: getBitcoinPrice, globalCoverage, docTotalSupply, bproTotalSupply,
        #        globalLockedBitcoin, cobj, liq, then AMM conversionPath
        gateway.call.side_effect = [
            btc_price,
            coverage,
            doc_supply,
            bpro_supply,
            locked_btc,
            target,
            liq,
            [],  # conversionPath returns empty → no AMM
        ]

        health = await provider.get_stablecoin_health(Token.DOC)
        assert health is not None
        assert health.token == Token.DOC
        assert health.protocol_price_usd == 1.0
        assert health.market_price_usd is None
        assert health.peg_deviation_pct is None
        assert health.coverage.current == 4.5
        assert health.coverage.target == 3.0
        assert health.coverage.liquidation_threshold == 1.5
        assert health.collateral.asset == Token.RBTC
        assert health.collateral.locked_amount == 100.0
        assert health.status == PegStatus.HEALTHY

    async def test_doc_health_with_amm_price(
        self, provider: MoCPriceProvider, gateway: AsyncMock
    ) -> None:
        btc_price = 67_000 * 10**18
        coverage = int(2.0 * 10**18)
        doc_supply = 1_000_000 * 10**18
        bpro_supply = 500 * 10**18
        locked_btc = 50 * 10**18
        target = int(3.0 * 10**18)
        liq = int(1.5 * 10**18)

        # AMM returns a rate for 1000 DOC → WRBTC
        # 1000 DOC ≈ 0.01489 WRBTC → 1 DOC ≈ 0.00001489 BTC → ~0.9976 USD
        amm_rate = int(0.01489 * 10**18)

        amm_path = ["0xAddr1", "0xAddr2", "0xAddr3"]

        gateway.call.side_effect = [
            btc_price, coverage, doc_supply, bpro_supply,
            locked_btc, target, liq,
            amm_path,  # conversionPath
            amm_rate,  # rateByPath
        ]

        health = await provider.get_stablecoin_health(Token.DOC)
        assert health is not None
        assert health.market_price_usd is not None
        assert health.peg_deviation_pct is not None
        assert health.status == PegStatus.WARNING  # coverage 2.0 < target 3.0

    async def test_non_doc_returns_none(
        self, provider: MoCPriceProvider, gateway: AsyncMock
    ) -> None:
        result = await provider.get_stablecoin_health(Token.RBTC)
        assert result is None
