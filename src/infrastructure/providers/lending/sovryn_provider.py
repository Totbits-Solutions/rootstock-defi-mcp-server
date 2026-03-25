"""Sovryn lending provider — bZx fork, annualized rates direct."""

from ....domain.lending.models import LendingMarket, PoolMetrics, RateInfo
from ....domain.lending.ports import LendingProvider
from ....domain.shared.exceptions import BlockchainQueryError
from ....domain.shared.models import Protocol
from ....domain.shared.ports import BlockchainGateway
from ...blockchain.contracts import ContractId
from ...blockchain.gateway import Web3BlockchainGateway

# Mapping market name → ContractId
_POOLS: dict[str, ContractId] = {
    "iRBTC": ContractId.I_RBTC,
    "iDOC": ContractId.I_DOC,
    "iUSDT": ContractId.I_USDT,
    "iBPro": ContractId.I_BPRO,
    "iXUSD": ContractId.I_XUSD,
    "iDLLR": ContractId.I_DLLR,
}


class SovrynLendingProvider(LendingProvider):
    """Adapter for Sovryn (bZx fork) lending pools on Rootstock."""

    def __init__(self, gateway: BlockchainGateway) -> None:
        self._gw = gateway

    def supported_markets(self) -> list[str]:
        return list(_POOLS.keys())

    async def get_market(self, market: str) -> LendingMarket:
        contract_id = _POOLS.get(market)
        if contract_id is None:
            raise BlockchainQueryError(f"Unknown Sovryn pool: {market}")
        return await self._fetch_pool(market, contract_id)

    async def get_all_markets(self) -> list[LendingMarket]:
        results: list[LendingMarket] = []
        for name, contract_id in _POOLS.items():
            results.append(await self._fetch_pool(name, contract_id))
        return results

    async def _fetch_pool(self, name: str, contract_id: ContractId) -> LendingMarket:
        fw = Web3BlockchainGateway.from_wei

        raw_supply_rate = await self._gw.call(contract_id, "supplyInterestRate")
        raw_borrow_rate = await self._gw.call(contract_id, "borrowInterestRate")
        raw_total_supply = await self._gw.call(contract_id, "totalAssetSupply")
        raw_total_borrow = await self._gw.call(contract_id, "totalAssetBorrow")

        # Sovryn rates are already annualized: from_wei() gives the percentage directly
        supply_apy = fw(raw_supply_rate)
        borrow_apy = fw(raw_borrow_rate)

        total_supply = fw(raw_total_supply)
        total_borrow = fw(raw_total_borrow)
        liquidity = total_supply - total_borrow

        utilization = (total_borrow / total_supply * 100) if total_supply > 0 else 0.0

        return LendingMarket(
            market=name,
            protocol=Protocol.SOVRYN,
            rates=RateInfo(
                supply_apr=supply_apy,
                supply_apy=supply_apy,
                borrow_apr=borrow_apy,
                borrow_apy=borrow_apy,
            ),
            pool=PoolMetrics(
                total_supply_usd=total_supply,
                total_borrows_usd=total_borrow,
                available_liquidity_usd=liquidity,
                utilization_rate=utilization,
            ),
        )
