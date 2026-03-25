"""MCP tool: get_token_prices — query on-chain token prices."""

from fastmcp import Context
from fastmcp.exceptions import ToolError

from ..application.get_token_prices import get_token_prices as get_token_prices_uc
from ..dependencies import get_pricing_service
from ..domain.shared.exceptions import DomainError
from ..domain.shared.models import Token
from ..server import mcp


@mcp.tool(
    tags={"defi", "pricing"},
    annotations={"readOnlyHint": True, "idempotentHint": True},
    description=(
        "Get current token prices from Rootstock on-chain oracles. "
        "Returns prices for RBTC, BPRO, RIF, RIFPRO, DOC, and USDRIF. "
        "Optionally filter by specific tokens."
    ),
)
async def get_token_prices(
    tokens: list[str] | None = None,
    ctx: Context | None = None,
) -> list[dict]:
    """Query on-chain token prices from MoC and RoC V2 oracles."""
    service = get_pricing_service()

    try:
        parsed_tokens = [Token(t) for t in tokens] if tokens else None
    except ValueError as e:
        valid = [t.value for t in Token]
        raise ToolError(f"Invalid token: {e}. Valid tokens: {valid}") from e

    try:
        result = await get_token_prices_uc(service, parsed_tokens)
    except DomainError as e:
        raise ToolError(str(e)) from e

    if ctx:
        count = len(result)
        await ctx.info(f"Returned {count} token price(s)")

    return result
