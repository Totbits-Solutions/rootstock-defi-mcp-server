"""Value objects for the Pricing bounded context."""

from enum import StrEnum

from pydantic import BaseModel

from ..shared.models import Protocol, Token


class TokenPrice(BaseModel):
    token: Token
    price_usd: float
    price_btc: float | None = None
    price_rif: float | None = None
    source: str
    protocol: Protocol


class PegStatus(StrEnum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    LIQUIDATION_RISK = "LIQUIDATION_RISK"


class CollateralInfo(BaseModel):
    asset: Token
    locked_amount: float
    value_usd: float


class CoverageMetrics(BaseModel):
    current: float
    target: float
    liquidation_threshold: float


class StablecoinHealth(BaseModel):
    token: Token
    protocol_price_usd: float
    market_price_usd: float | None = None
    peg_deviation_pct: float | None = None
    collateral: CollateralInfo
    coverage: CoverageMetrics
    supply: dict[str, float]
    status: PegStatus
    protocol: Protocol
