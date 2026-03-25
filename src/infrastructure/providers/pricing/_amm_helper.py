"""Helper para consultas de precio de mercado via Sovryn AMM SwapNetwork."""

from ....domain.shared.ports import BlockchainGateway
from ...blockchain.contracts import ContractId
from ...blockchain.gateway import Web3BlockchainGateway

# Cantidad de tokens para la consulta AMM (1000 unidades en wei para mayor precisión)
_AMM_QUERY_AMOUNT = 1000 * 10**18
_AMM_QUERY_UNITS = 1000


async def get_amm_market_price(
    gateway: BlockchainGateway,
    source_token_address: str,
    target_token_address: str,
    reference_price_usd: float,
) -> float | None:
    """Calcula el precio de mercado de un token via Sovryn AMM.

    Consulta conversionPath y rateByPath del SwapNetwork para obtener
    la tasa de cambio real en el AMM. Retorna None si no hay ruta disponible.

    Args:
        gateway: Blockchain gateway para llamadas on-chain.
        source_token_address: Dirección checksum del token origen (ej: DOC).
        target_token_address: Dirección checksum del token destino (ej: WRBTC).
        reference_price_usd: Precio USD del token destino (ej: BTC price).

    Returns:
        Precio de mercado en USD del token origen, o None si no hay AMM pool.
    """
    try:
        path = await gateway.call(
            ContractId.SOVRYN_SWAP_NETWORK,
            "conversionPath",
            source_token_address,
            target_token_address,
        )
    except Exception:
        return None

    if not path:
        return None

    try:
        rate_output = await gateway.call(
            ContractId.SOVRYN_SWAP_NETWORK,
            "rateByPath",
            path,
            _AMM_QUERY_AMOUNT,
        )
    except Exception:
        return None

    rate_in_target = Web3BlockchainGateway.from_wei(rate_output) / _AMM_QUERY_UNITS
    return rate_in_target * reference_price_usd
