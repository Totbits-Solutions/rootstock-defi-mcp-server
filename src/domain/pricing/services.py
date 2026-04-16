"""Domain service for the Pricing bounded context."""

from ..shared.exceptions import TokenNotSupportedError
from ..shared.models import Token
from .models import PegStatus, StablecoinHealth, TokenPrice
from .ports import PriceProvider


class PricingService:
    """Orchestrates multiple PriceProviders using the Strategy pattern."""

    def __init__(self, providers: list[PriceProvider]) -> None:
        self._token_to_provider: dict[Token, PriceProvider] = {}
        for provider in providers:
            for token in provider.supported_tokens():
                self._token_to_provider[token] = provider

    async def get_prices(self, tokens: list[Token] | None = None) -> dict[Token, TokenPrice]:
        target = tokens or list(self._token_to_provider.keys())
        results: dict[Token, TokenPrice] = {}
        for token in target:
            provider = self._token_to_provider.get(token)
            if not provider:
                raise TokenNotSupportedError(f"No provider registered for {token}")
            results[token] = await provider.get_price(token)
        return results

    async def get_stablecoin_health(self, tokens: list[Token] | None = None) -> dict[Token, StablecoinHealth]:
        stablecoins = tokens or [Token.DOC, Token.USDRIF]
        results: dict[Token, StablecoinHealth] = {}
        for token in stablecoins:
            provider = self._token_to_provider.get(token)
            if not provider:
                raise TokenNotSupportedError(f"No provider registered for {token}")
            health = await provider.get_stablecoin_health(token)
            if health:
                results[token] = health
        return results

    @staticmethod
    def calculate_peg_deviation(market_price: float, peg: float = 1.0) -> float:
        return ((market_price - peg) / peg) * 100

    @staticmethod
    def evaluate_coverage_status(coverage: float, target: float, liq_threshold: float) -> PegStatus:
        if coverage > target:
            return PegStatus.HEALTHY
        if coverage > liq_threshold:
            return PegStatus.WARNING
        return PegStatus.LIQUIDATION_RISK
