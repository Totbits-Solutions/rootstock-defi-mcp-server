"""RIF on Chain V2 price provider — RIF, RIFPRO prices + USDRIF health."""

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
from ...blockchain.contracts import ContractId
from ...blockchain.gateway import Web3BlockchainGateway


class RoCPriceProvider(PriceProvider):
    """Adapter for RIF on Chain V2 — RIF, RIFPRO prices and USDRIF stablecoin health."""

    def __init__(self, gateway: BlockchainGateway) -> None:
        self._gw = gateway

    def supported_tokens(self) -> list[Token]:
        return [Token.RIF, Token.RIFPRO, Token.USDRIF]

    async def get_price(self, token: Token) -> TokenPrice:
        if token == Token.RIF:
            return await self._get_rif_price()
        if token == Token.RIFPRO:
            return await self._get_rifpro_price()
        if token == Token.USDRIF:
            return TokenPrice(
                token=Token.USDRIF,
                price_usd=1.0,
                source="RoC V2 protocol (pegged)",
                protocol=Protocol.ROC_V2,
            )
        raise TokenNotSupportedError(f"RoCPriceProvider does not support {token}")

    async def get_stablecoin_health(self, token: Token) -> StablecoinHealth | None:
        if token != Token.USDRIF:
            return None
        return await self._get_usdrif_health()

    # --- Private helpers ---

    async def _get_rif_price(self) -> TokenPrice:
        """RIF price from RIF/USD price provider via peek()."""
        result = await self._gw.call(ContractId.RIF_USD_PRICE_PROVIDER, "peek")
        raw_bytes, valid = result[0], result[1]
        if not valid:
            raise BlockchainQueryError("RIF/USD oracle has no valid value")
        price_usd = Web3BlockchainGateway.from_wei(int.from_bytes(raw_bytes, byteorder="big"))
        return TokenPrice(
            token=Token.RIF,
            price_usd=price_usd,
            source="RIF/USD price provider",
            protocol=Protocol.ROC_V2,
        )

    async def _get_rifpro_price(self) -> TokenPrice:
        """RIFPRO price derived from RoC V2 getPTCac() * RIF/USD."""
        raw_ptcac = await self._gw.call(ContractId.ROC_V2_PROXY, "getPTCac")
        rifpro_in_rif = Web3BlockchainGateway.from_wei(raw_ptcac)

        rif_price = await self._get_rif_price()
        rifpro_usd = rifpro_in_rif * rif_price.price_usd

        return TokenPrice(
            token=Token.RIFPRO,
            price_usd=rifpro_usd,
            price_rif=rifpro_in_rif,
            source="RoC V2 getPTCac + RIF/USD oracle",
            protocol=Protocol.ROC_V2,
        )

    async def _get_usdrif_health(self) -> StablecoinHealth:
        """USDRIF stablecoin health from RoC V2 state."""
        fw = Web3BlockchainGateway.from_wei

        rif_price = await self._get_rif_price()
        rif_usd = rif_price.price_usd

        raw_coverage = await self._gw.call(ContractId.ROC_V2_PROXY, "getCglb")
        raw_target = await self._gw.call(ContractId.ROC_V2_PROXY, "calcCtargemaCA")
        raw_liq = await self._gw.call(ContractId.ROC_V2_PROXY, "liqThrld")
        raw_locked_rif = await self._gw.call(ContractId.ROC_V2_PROXY, "nACcb")

        raw_usdrif_supply = await self._gw.call(ContractId.USDRIF_TOKEN, "totalSupply")
        raw_rifpro_supply = await self._gw.call(ContractId.RIFPRO_TOKEN, "totalSupply")

        coverage = fw(raw_coverage)
        target = fw(raw_target)
        liq_threshold = fw(raw_liq)
        locked_rif = fw(raw_locked_rif)
        usdrif_supply = fw(raw_usdrif_supply)
        rifpro_supply = fw(raw_rifpro_supply)

        status = PricingService.evaluate_coverage_status(coverage, target, liq_threshold)

        return StablecoinHealth(
            token=Token.USDRIF,
            protocol_price_usd=1.0,
            market_price_usd=None,
            peg_deviation_pct=None,
            collateral=CollateralInfo(
                asset=Token.RIF,
                locked_amount=locked_rif,
                value_usd=locked_rif * rif_usd,
            ),
            coverage=CoverageMetrics(
                current=coverage,
                target=target,
                liquidation_threshold=liq_threshold,
            ),
            supply={"USDRIF": usdrif_supply, "RIFPRO": rifpro_supply},
            status=status,
            protocol=Protocol.ROC_V2,
        )
