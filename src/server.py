"""FastMCP server entry point with async lifespan"""

from collections.abc import AsyncIterator
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.lifespan import Lifespan

from .config import Settings
from .domain.lending.services import LendingService
from .domain.pricing.services import PricingService
from .infrastructure.blockchain.gateway import Web3BlockchainGateway
from .infrastructure.factory import ProviderFactory


async def _app_lifespan(_server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Initialize all services at startup, tear down on shutdown."""
    settings = Settings()

    gateway = Web3BlockchainGateway(settings.rsk_node_url)
    factory = ProviderFactory(gateway)

    pricing_service = PricingService(factory.create_price_providers())
    lending_service = LendingService(factory.create_lending_providers())

    yield {
        "settings": settings,
        "gateway": gateway,
        "pricing_service": pricing_service,
        "lending_service": lending_service,
    }


mcp = FastMCP(
    name="rootstock-defi-mcp",
    instructions=(
        "MCP server for on-chain DeFi analysis on Rootstock (RSK). "
        "Query token prices, stablecoin health, and lending rates "
        "from MoC, RoC V2, Tropykus, and Sovryn protocols."
    ),
    lifespan=Lifespan(_app_lifespan),
)

# Register tools — import triggers @mcp.tool() decoration
from .tools import lending_rates as _lending_rates  # noqa: E402, F401
from .tools import stablecoin_health as _stablecoin_health  # noqa: E402, F401
from .tools import token_prices as _token_prices  # noqa: E402, F401


def main() -> None:
    """Entry point for the rootstock-mcp CLI command."""
    mcp.run()
