"""Dependency injection — getter functions for services from lifespan context."""

from fastmcp.server.dependencies import get_context

from .config import Settings
from .domain.pricing.services import PricingService
from .domain.shared.ports import BlockchainGateway


def get_settings() -> Settings:
    ctx = get_context()
    return ctx.lifespan_context["settings"]


def get_gateway() -> BlockchainGateway:
    ctx = get_context()
    return ctx.lifespan_context["gateway"]


def get_pricing_service() -> PricingService:
    ctx = get_context()
    return ctx.lifespan_context["pricing_service"]
