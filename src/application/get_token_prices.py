"""Use case: query token prices (all or filtered by token)."""

from ..domain.pricing.services import PricingService
from ..domain.shared.models import Token


async def get_token_prices(
    service: PricingService,
    tokens: list[Token] | None = None,
) -> list[dict]:
    """Fetch token prices and return serializable results.

    Args:
        service: PricingService instance (injected from tool layer).
        tokens: Optional filter — query only these tokens.

    Returns:
        List of TokenPrice dicts ready for MCP response.
    """
    prices = await service.get_prices(tokens)
    return [price.model_dump() for price in prices.values()]
