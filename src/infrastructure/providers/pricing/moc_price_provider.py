"""Money on Chain price provider — RBTC, BPRO prices + DOC health."""

from ....domain.pricing.models import (
    CollateralInfo,
    CoverageMetrics,
    StablecoinHealth,
    TokenPrice,
)
from ....domain.pricing.ports import PriceProvider
from ....domain.pricing.services import PricingService
from ....domain.shared.exceptions import BlockchainQueryError, TokenNotSupportedError
from ....domain.shared.models import Protocol, Token
from ....domain.shared.ports import BlockchainGateway
from ...blockchain.contracts import CONTRACT_REGISTRY, ContractId
from ...blockchain.gateway import Web3BlockchainGateway
from ._amm_helper import get_amm_market_price


class MoCPriceProvider(PriceProvider):
    """Adapter for Money on Chain — RBTC, BPRO prices and DOC stablecoin health."""

    def __init__(self, gateway: BlockchainGateway) -> None:
        self._gw = gateway

    def supported_tokens(self) -> list[Token]:
        return [Token.RBTC, Token.BPRO, Token.DOC]

    async def get_price(self, token: Token) -> TokenPrice:
        if token == Token.RBTC:
            return await self._get_rbtc_price()
        if token == Token.BPRO:
            return await self._get_bpro_price()
        if token == Token.DOC:
            return TokenPrice(
                token=Token.DOC,
                price_usd=1.0,
                source="MoC protocol (pegged)",
                protocol=Protocol.MOC,
            )
        raise TokenNotSupportedError(f"MoCPriceProvider does not support {token}")

    async def get_stablecoin_health(self, token: Token) -> StablecoinHealth | None:
        if token != Token.DOC:
            return None
        return await self._get_doc_health()

    # --- Private helpers ---

    async def _get_rbtc_price(self) -> TokenPrice:
        """RBTC price from OMoC BTC/USD oracle via peek()."""
        result = await self._gw.call(ContractId.BTC_USD_ORACLE, "peek")
        raw_bytes, valid = result[0], result[1]
        if not valid:
            raise BlockchainQueryError("BTC/USD oracle has no valid value")
        price_usd = Web3BlockchainGateway.from_wei(int.from_bytes(raw_bytes, byteorder="big"))
        return TokenPrice(
            token=Token.RBTC,
            price_usd=price_usd,
            source="OMoC BTC/USD oracle",
            protocol=Protocol.MOC,
        )

    async def _get_bpro_price(self) -> TokenPrice:
        """BPRO price from MoCState."""
        raw_usd = await self._gw.call(ContractId.MOC_STATE, "bproUsdPrice")
        raw_btc = await self._gw.call(ContractId.MOC_STATE, "bproTecPrice")
        return TokenPrice(
            token=Token.BPRO,
            price_usd=Web3BlockchainGateway.from_wei(raw_usd),
            price_btc=Web3BlockchainGateway.from_wei(raw_btc),
            source="MoCState",
            protocol=Protocol.MOC,
        )

    async def _get_doc_health(self) -> StablecoinHealth:
        """DOC stablecoin health from MoCState + Sovryn AMM market price."""
        fw = Web3BlockchainGateway.from_wei

        raw_btc_price = await self._gw.call(ContractId.MOC_STATE, "getBitcoinPrice")
        btc_price_usd = fw(raw_btc_price)

        raw_coverage = await self._gw.call(ContractId.MOC_STATE, "globalCoverage")
        raw_doc_supply = await self._gw.call(ContractId.MOC_STATE, "docTotalSupply")
        raw_bpro_supply = await self._gw.call(ContractId.MOC_STATE, "bproTotalSupply")
        raw_locked_btc = await self._gw.call(ContractId.MOC_STATE, "globalLockedBitcoin")
        raw_target = await self._gw.call(ContractId.MOC_STATE, "cobj")
        raw_liq = await self._gw.call(ContractId.MOC_STATE, "liq")

        coverage = fw(raw_coverage)
        doc_supply = fw(raw_doc_supply)
        bpro_supply = fw(raw_bpro_supply)
        locked_btc = fw(raw_locked_btc)
        target = fw(raw_target)
        liq_threshold = fw(raw_liq)

        # Market price via Sovryn AMM
        doc_address = CONTRACT_REGISTRY[ContractId.DOC_TOKEN].address
        wrbtc_address = CONTRACT_REGISTRY[ContractId.WRBTC_TOKEN].address

        market_price = await get_amm_market_price(
            gateway=self._gw,
            source_token_address=doc_address,
            target_token_address=wrbtc_address,
            reference_price_usd=btc_price_usd,
        )

        peg_deviation = (
            PricingService.calculate_peg_deviation(market_price)
            if market_price is not None
            else None
        )

        status = PricingService.evaluate_coverage_status(coverage, target, liq_threshold)

        return StablecoinHealth(
            token=Token.DOC,
            protocol_price_usd=1.0,
            market_price_usd=market_price,
            peg_deviation_pct=peg_deviation,
            collateral=CollateralInfo(
                asset=Token.RBTC,
                locked_amount=locked_btc,
                value_usd=locked_btc * btc_price_usd,
            ),
            coverage=CoverageMetrics(
                current=coverage,
                target=target,
                liquidation_threshold=liq_threshold,
            ),
            supply={"DOC": doc_supply, "BPRO": bpro_supply},
            status=status,
            protocol=Protocol.MOC,
        )
