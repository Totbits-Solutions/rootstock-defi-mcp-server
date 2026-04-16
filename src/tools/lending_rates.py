"""MCP tool: get_lending_rates — query supply/borrow rates per market."""

from typing import Annotated, Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from ..application.get_lending_rates import (
    get_lending_rates as get_lending_rates_uc,
)
from ..dependencies import get_lending_service
from ..domain.shared.exceptions import DomainError
from ..domain.shared.models import Protocol
from ..server import mcp

LENDING_PROTOCOLS: frozenset[Protocol] = frozenset({Protocol.TROPYKUS, Protocol.SOVRYN})
_PROTOCOL_NAMES = ", ".join(sorted(p.value for p in LENDING_PROTOCOLS))


@mcp.tool(
    tags={"defi", "lending"},
    annotations={"readOnlyHint": True, "idempotentHint": True},
    description=(
        "Get supply and borrow rates (APR/APY) for lending markets on Rootstock. "
        "Returns rates and pool metrics (total supply/borrows, liquidity, "
        "utilization) per market. Filter by protocol, or by protocol + market "
        "for a single market. Only Tropykus and Sovryn are supported."
    ),
)
async def get_lending_rates(
    protocol: Annotated[
        str | None,
        Field(
            description=(
                "Lending protocol to query. Omit for all supported protocols. Valid values: tropykus, sovryn."
            ),
            examples=["tropykus", "sovryn"],
        ),
    ] = None,
    market: Annotated[
        str | None,
        Field(
            description=(
                "Market name (e.g. 'kDOC', 'kRBTC' for Tropykus; 'iDOC', "
                "'iRBTC' for Sovryn). Requires 'protocol' to be set. "
                "Case-sensitive."
            ),
            examples=["kDOC", "iRBTC"],
        ),
    ] = None,
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """Query lending markets from Tropykus and Sovryn."""
    service = get_lending_service()

    parsed_protocol: Protocol | None = None
    if protocol is not None:
        try:
            parsed_protocol = Protocol(protocol)
        except ValueError as e:
            raise ToolError(
                f"Invalid protocol: {e}. Only the following lending protocols are supported: {_PROTOCOL_NAMES}."
            ) from e

        if parsed_protocol not in LENDING_PROTOCOLS:
            raise ToolError(
                f"{parsed_protocol.value} is not a lending protocol. "
                f"Only the following lending protocols are supported: "
                f"{_PROTOCOL_NAMES}."
            )

    if market is not None and parsed_protocol is None:
        raise ToolError(f"Parameter 'market' requires 'protocol' to be set (valid protocols: {_PROTOCOL_NAMES}).")

    try:
        result = await get_lending_rates_uc(service, parsed_protocol, market)
    except DomainError as e:
        raise ToolError(str(e)) from e

    if ctx:
        await ctx.info(f"Returned {len(result)} lending market(s)")

    return result
