"""Tropykus lending provider — Compound v2 fork, per-block rate conversion."""

from ....domain.lending.models import LendingMarket, PoolMetrics, RateInfo
from ....domain.lending.ports import LendingProvider
from ....domain.lending.services import LendingService
from ....domain.shared.exceptions import BlockchainQueryError
from ....domain.shared.models import Protocol
from ....domain.shared.ports import BlockchainGateway
from ...blockchain.constants import BLOCKS_PER_YEAR
from ...blockchain.contracts import ContractId
from ...blockchain.gateway import Web3BlockchainGateway

# Mapping market name → ContractId
_MARKETS: dict[str, ContractId] = {
    "kRBTC": ContractId.K_RBTC,
    "kDOC": ContractId.K_DOC,
    "kUSDRIF": ContractId.K_USDRIF,
    "kBPRO": ContractId.K_BPRO,
}


class TropykusLendingProvider(LendingProvider):
    """Adapter for Tropykus (Compound v2 fork) lending markets on Rootstock."""

    def __init__(self, gateway: BlockchainGateway) -> None:
        self._gw = gateway

    def supported_markets(self) -> list[str]:
        return list(_MARKETS.keys())

    async def get_market(self, market: str) -> LendingMarket:
        contract_id = _MARKETS.get(market)
        if contract_id is None:
            raise BlockchainQueryError(f"Unknown Tropykus market: {market}")
        return await self._fetch_market(market, contract_id)

    async def get_all_markets(self) -> list[LendingMarket]:
        results: list[LendingMarket] = []
        for name, contract_id in _MARKETS.items():
            results.append(await self._fetch_market(name, contract_id))
        return results

    async def _fetch_market(self, name: str, contract_id: ContractId) -> LendingMarket:
        fw = Web3BlockchainGateway.from_wei

        raw_supply_rate = await self._gw.call(contract_id, "supplyRatePerBlock")
        raw_borrow_rate = await self._gw.call(contract_id, "borrowRatePerBlock")
        raw_cash = await self._gw.call(contract_id, "getCash")
        raw_borrows = await self._gw.call(contract_id, "totalBorrows")
        raw_reserves = await self._gw.call(contract_id, "totalReserves")

        supply_rate = fw(raw_supply_rate)
        borrow_rate = fw(raw_borrow_rate)
        cash = fw(raw_cash)
        borrows = fw(raw_borrows)
        reserves = fw(raw_reserves)

        # APY (compound interest)
        supply_apy = LendingService.rate_per_block_to_apy(supply_rate)
        borrow_apy = LendingService.rate_per_block_to_apy(borrow_rate)

        # APR (simple interest)
        supply_apr = supply_rate * BLOCKS_PER_YEAR * 100
        borrow_apr = borrow_rate * BLOCKS_PER_YEAR * 100

        # Utilization
        denom = cash + borrows - reserves
        utilization = (borrows / denom * 100) if denom > 0 else 0.0

        return LendingMarket(
            market=name,
            protocol=Protocol.TROPYKUS,
            rates=RateInfo(
                supply_apr=supply_apr,
                supply_apy=supply_apy,
                borrow_apr=borrow_apr,
                borrow_apy=borrow_apy,
            ),
            pool=PoolMetrics(
                total_supply_usd=cash + borrows,
                total_borrows_usd=borrows,
                available_liquidity_usd=cash,
                utilization_rate=utilization,
            ),
        )
