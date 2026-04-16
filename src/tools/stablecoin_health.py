"""MCP tool: get_stablecoin_health — query stablecoin peg and coverage health."""

from typing import Annotated, Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from ..application.get_stablecoin_health import (
    get_stablecoin_health as get_stablecoin_health_uc,
)
from ..dependencies import get_pricing_service
from ..domain.shared.exceptions import DomainError
from ..domain.shared.models import Token
from ..server import mcp

STABLECOIN_TOKENS: frozenset[Token] = frozenset({Token.DOC, Token.USDRIF})
_STABLECOIN_NAMES = ", ".join(sorted(t.value for t in STABLECOIN_TOKENS))


@mcp.tool(
    tags={"defi", "stablecoin"},
    annotations={"readOnlyHint": True, "idempotentHint": True},
    description=(
        "Analyze stablecoin peg health and protocol coverage on Rootstock. "
        "Returns protocol price, market price (when available), peg deviation, "
        "collateral info, coverage ratio vs target/liquidation thresholds, "
        "supply, and status. "
        "Only DOC and USDRIF are supported."
    ),
)
async def get_stablecoin_health(
    tokens: Annotated[
        list[str] | None,
        Field(
            description=(
                "Stablecoins to query. Omit or pass null for all supported stablecoins. Valid values: DOC, USDRIF."
            ),
            examples=[["DOC"], ["DOC", "USDRIF"]],
        ),
    ] = None,
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """Query stablecoin health metrics from MoC (DOC) and RoC V2 (USDRIF)."""
    service = get_pricing_service()

    try:
        parsed = [Token(t) for t in tokens] if tokens else None
    except ValueError as e:
        raise ToolError(
            f"Invalid token: {e}. Only the following stablecoins are supported: {_STABLECOIN_NAMES}."
        ) from e

    if parsed:
        invalid = [t.value for t in parsed if t not in STABLECOIN_TOKENS]
        if invalid:
            raise ToolError(
                f"{', '.join(invalid)} is not a stablecoin. "
                f"Only the following stablecoins are supported: {_STABLECOIN_NAMES}."
            )

    try:
        result = await get_stablecoin_health_uc(service, parsed)
    except DomainError as e:
        raise ToolError(str(e)) from e

    if ctx:
        await ctx.info(f"Returned health for {len(result)} stablecoin(s)")

    return result
