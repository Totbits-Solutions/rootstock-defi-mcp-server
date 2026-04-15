"""Use case: stablecoin analysis (all or filtered)."""

from typing import Any

from ..domain.pricing.services import PricingService
from ..domain.shared.models import Token


async def get_stablecoin_health(
    service: PricingService,
    tokens: list[Token] | None = None,
) -> list[dict[str, Any]]:
    """Fetch stablecoin health metrics and return serializable results.

    Args:
        service: PricingService instance (injected from tool layer).
        tokens: Optional filter — restrict to these stablecoins. Token
            validation (stablecoin-only) belongs to the tool layer.

    Returns:
        List of StablecoinHealth dicts ready for MCP response.
    """
    health = await service.get_stablecoin_health(tokens)
    return [item.model_dump() for item in health.values()]
