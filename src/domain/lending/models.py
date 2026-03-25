"""Value objects for the Lending bounded context."""

from pydantic import BaseModel

from ..shared.models import Protocol


class RateInfo(BaseModel):
    supply_apr: float
    supply_apy: float
    borrow_apr: float
    borrow_apy: float


class PoolMetrics(BaseModel):
    total_supply_usd: float
    total_borrows_usd: float
    available_liquidity_usd: float
    utilization_rate: float


class LendingMarket(BaseModel):
    market: str
    protocol: Protocol
    rates: RateInfo
    pool: PoolMetrics
