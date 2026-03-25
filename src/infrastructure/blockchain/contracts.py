"""ABI registry and contract addresses for Rootstock protocols.

Migrated from poc_analysis_on_chain_rootstock/shared.py.
Single source of truth for all contract addresses and ABIs.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from web3 import Web3
from web3.types import ChecksumAddress

# =============================================================================
# Contract identifier enum
# =============================================================================


class ContractId(StrEnum):
    """Type-safe identifier for every contract used by the server."""

    # Tokens
    DOC_TOKEN = "doc_token"
    USDRIF_TOKEN = "usdrif_token"
    BPRO_TOKEN = "bpro_token"
    RIF_TOKEN = "rif_token"
    WRBTC_TOKEN = "wrbtc_token"
    RIFPRO_TOKEN = "rifpro_token"

    # Oracles
    BTC_USD_ORACLE = "btc_usd_oracle"
    RIF_USD_PRICE_PROVIDER = "rif_usd_price_provider"

    # Protocols
    MOC_STATE = "moc_state"
    ROC_V2_PROXY = "roc_v2_proxy"
    SOVRYN_SWAP_NETWORK = "sovryn_swap_network"

    # Tropykus markets (Compound v2 fork — kTokens)
    K_RBTC = "k_rbtc"
    K_DOC = "k_doc"
    K_USDRIF = "k_usdrif"
    K_BPRO = "k_bpro"

    # Sovryn pools (bZx fork — iTokens)
    I_RBTC = "i_rbtc"
    I_DOC = "i_doc"
    I_USDT = "i_usdt"
    I_BPRO = "i_bpro"
    I_XUSD = "i_xusd"
    I_DLLR = "i_dllr"


@dataclass(frozen=True)
class ContractInfo:
    """Immutable pair of checksum address + ABI for a contract."""

    address: ChecksumAddress
    abi: list[dict[str, Any]]


# =============================================================================
# Helper
# =============================================================================

_cs = Web3.to_checksum_address


# =============================================================================
# ABIs
# =============================================================================

# IPriceProvider / CoinPairPrice — peek() returns (bytes32 price, bool valid)
PRICE_PROVIDER_ABI: list[dict[str, Any]] = [
    {
        "constant": True,
        "inputs": [],
        "name": "peek",
        "outputs": [
            {"name": "", "type": "bytes32"},
            {"name": "", "type": "bool"},
        ],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "getPrice",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]

# MoCState — Money on Chain (DOC/BPRO, collateral: RBTC)
MOC_STATE_ABI: list[dict[str, Any]] = [
    {
        "constant": True,
        "inputs": [],
        "name": "getBitcoinPrice",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "bproUsdPrice",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "bproTecPrice",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "globalCoverage",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "docTotalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "bproTotalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "globalLockedBitcoin",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "cobj",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "liq",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]

# Sovryn SwapNetwork — for market price queries via AMM
SWAP_NETWORK_ABI: list[dict[str, Any]] = [
    {
        "constant": True,
        "inputs": [
            {"name": "_sourceToken", "type": "address"},
            {"name": "_targetToken", "type": "address"},
        ],
        "name": "conversionPath",
        "outputs": [{"name": "", "type": "address[]"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_path", "type": "address[]"},
            {"name": "_amount", "type": "uint256"},
        ],
        "name": "rateByPath",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]

# RoC V2 proxy — MoC V2 interface (USDRIF/RIFPRO, collateral: RIF)
ROC_V2_ABI: list[dict[str, Any]] = [
    {
        "constant": True,
        "inputs": [],
        "name": "getCglb",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "getPTCac",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "calcCtargemaCA",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "liqThrld",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "protThrld",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "nACcb",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "nTCcb",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]

# ERC20 minimal ABI
ERC20_ABI: list[dict[str, Any]] = [
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]

# Tropykus cToken ABI (Compound v2 fork)
CTOKEN_ABI: list[dict[str, Any]] = [
    {
        "constant": True,
        "inputs": [],
        "name": "supplyRatePerBlock",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "borrowRatePerBlock",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalBorrows",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalReserves",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "getCash",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "exchangeRateStored",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]

# Sovryn iToken ABI (bZx fork)
ITOKEN_ABI: list[dict[str, Any]] = [
    {
        "constant": True,
        "inputs": [],
        "name": "supplyInterestRate",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "borrowInterestRate",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "avgBorrowInterestRate",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalAssetSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalAssetBorrow",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "tokenPrice",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]


# =============================================================================
# Contract Registry — single source of truth
# =============================================================================

CONTRACT_REGISTRY: dict[ContractId, ContractInfo] = {
    # --- Tokens ---
    ContractId.DOC_TOKEN: ContractInfo(
        address=_cs("0xe700691dA7b9851F2F35f8b8182c69c53CcaD9Db"),
        abi=ERC20_ABI,
    ),
    ContractId.USDRIF_TOKEN: ContractInfo(
        address=_cs("0x2d919F19D4892381D58edeBeca66D5642Cef1a1f"),
        abi=ERC20_ABI,
    ),
    ContractId.BPRO_TOKEN: ContractInfo(
        address=_cs("0x440CD83C160De5C96Ddb20246815eA44C7ABBCa8"),
        abi=ERC20_ABI,
    ),
    ContractId.RIF_TOKEN: ContractInfo(
        address=_cs("0x2AcC95758f8b5F583470ba265EB685a8F45fC9D5"),
        abi=ERC20_ABI,
    ),
    ContractId.WRBTC_TOKEN: ContractInfo(
        address=_cs("0x542fDA317318eBF1d3DEAf76E0b632741A7e677d"),
        abi=ERC20_ABI,
    ),
    ContractId.RIFPRO_TOKEN: ContractInfo(
        address=_cs("0xf4d27c56595Ed59B66cC7F03CFF5193e4bd74a61"),
        abi=ERC20_ABI,
    ),
    # --- Oracles ---
    ContractId.BTC_USD_ORACLE: ContractInfo(
        address=_cs("0xe2927A0620b82A66D67F678FC9b826B0E01B1bFD"),
        abi=PRICE_PROVIDER_ABI,
    ),
    ContractId.RIF_USD_PRICE_PROVIDER: ContractInfo(
        address=_cs("0x504EfCadFB020d6bBaeC8a5c5BB21453719d0E00"),
        abi=PRICE_PROVIDER_ABI,
    ),
    # --- Protocols ---
    ContractId.MOC_STATE: ContractInfo(
        address=_cs("0xb9C42EFc8ec54490a37cA91c423F7285Fa01e257"),
        abi=MOC_STATE_ABI,
    ),
    ContractId.ROC_V2_PROXY: ContractInfo(
        address=_cs("0xA27024Ed70035E46dba712609fc2Afa1c97aA36A"),
        abi=ROC_V2_ABI,
    ),
    ContractId.SOVRYN_SWAP_NETWORK: ContractInfo(
        address=_cs("0x98aCE08D2b759a265ae326F010496bcD63C15afc"),
        abi=SWAP_NETWORK_ABI,
    ),
    # --- Tropykus markets (kTokens) ---
    ContractId.K_RBTC: ContractInfo(
        address=_cs("0x0AeAdB9d4c6A80462a47E87E76e487Fa8B9a37D7"),
        abi=CTOKEN_ABI,
    ),
    ContractId.K_DOC: ContractInfo(
        address=_cs("0x544eB90E766B405134b3b3f62b6B4c23fCd5FDA2"),
        abi=CTOKEN_ABI,
    ),
    ContractId.K_USDRIF: ContractInfo(
        address=_cs("0xDdf3CE45fcf080DF61ee61dac5Ddefef7ED4F46C"),
        abi=CTOKEN_ABI,
    ),
    ContractId.K_BPRO: ContractInfo(
        address=_cs("0x405062731d8656af5950ef952be9fa110878036b"),
        abi=CTOKEN_ABI,
    ),
    # --- Sovryn pools (iTokens) ---
    ContractId.I_RBTC: ContractInfo(
        address=_cs("0xa9DcDC63eaBb8a2b6f39D7fF9429d88340044a7A"),
        abi=ITOKEN_ABI,
    ),
    ContractId.I_DOC: ContractInfo(
        address=_cs("0xd8D25f03EBbA94E15Df2eD4d6D38276B595593c1"),
        abi=ITOKEN_ABI,
    ),
    ContractId.I_USDT: ContractInfo(
        address=_cs("0x849C47f9C259E9D62F289BF1b2729039698D8387"),
        abi=ITOKEN_ABI,
    ),
    ContractId.I_BPRO: ContractInfo(
        address=_cs("0x6E2fb26a60dA535732F8149b25018C9c0823a715"),
        abi=ITOKEN_ABI,
    ),
    ContractId.I_XUSD: ContractInfo(
        address=_cs("0x8F77ecf69711a4b346f23109c40416BE3dC7f129"),
        abi=ITOKEN_ABI,
    ),
    ContractId.I_DLLR: ContractInfo(
        address=_cs("0x077FCB01cAb070a30bC14b44559C96F529eE017F"),
        abi=ITOKEN_ABI,
    ),
}
