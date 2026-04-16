"""Use case: lending data (all / by protocol / by market)."""

from typing import Any

from ..domain.lending.services import LendingService
from ..domain.shared.models import Protocol


async def get_lending_rates(
    service: LendingService,
    protocol: Protocol | None = None,
    market: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch lending markets and return serializable results.

    Args:
        service: LendingService instance (injected from tool layer).
        protocol: Optional filter — restrict to a single protocol.
        market: Optional filter — restrict to a single market (requires
            `protocol`; that validation belongs to the tool layer).

    Returns:
        List of LendingMarket dicts ready for MCP response.
    """
    if protocol and market:
        single = await service.get_market(protocol, market)
        return [single.model_dump()]
    if protocol:
        markets = await service.get_rates_by_protocol(protocol)
    else:
        markets = await service.get_all_rates()
    return [m.model_dump() for m in markets]
