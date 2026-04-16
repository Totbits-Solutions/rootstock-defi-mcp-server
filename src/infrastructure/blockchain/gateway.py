"""Web3 blockchain gateway — AsyncWeb3 implementation."""

from typing import Any

from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.contract import AsyncContract

from ...domain.shared.exceptions import BlockchainQueryError
from ...domain.shared.ports import BlockchainGateway
from .contracts import CONTRACT_REGISTRY, ContractId


class Web3BlockchainGateway(BlockchainGateway):
    """Infrastructure adapter that wraps AsyncWeb3 for blockchain calls.

    Implements the BlockchainGateway port so that domain providers
    remain decoupled from the Web3 library.
    """

    def __init__(self, rsk_node_url: str) -> None:
        self._w3 = AsyncWeb3(AsyncHTTPProvider(rsk_node_url))
        self._contracts: dict[str, AsyncContract] = {}

    # --- Port implementation ---

    async def call(self, contract_id: str, function_name: str, *args: Any) -> Any:
        """Execute a read-only call on a smart contract function."""
        contract = self._get_or_create_contract(contract_id)
        try:
            fn = contract.functions[function_name](*args)
            return await fn.call()
        except BlockchainQueryError:
            raise
        except Exception as e:
            raise BlockchainQueryError(f"Call to {contract_id}.{function_name} failed: {e}") from e

    async def is_connected(self) -> bool:
        """Check connectivity with the RSK node."""
        try:
            return await self._w3.is_connected()
        except Exception:
            return False

    async def get_block_number(self) -> int:
        """Return the current block number."""
        try:
            return await self._w3.eth.get_block_number()
        except Exception as e:
            raise BlockchainQueryError(f"Failed to get block number: {e}") from e

    # --- Helpers ---

    def _get_or_create_contract(self, contract_id: str) -> AsyncContract:
        """Retrieve a cached contract or instantiate from the registry."""
        if contract_id in self._contracts:
            return self._contracts[contract_id]

        try:
            cid = ContractId(contract_id)
        except ValueError as e:
            raise BlockchainQueryError(f"Unknown contract: {contract_id}") from e

        info = CONTRACT_REGISTRY[cid]
        contract = self._w3.eth.contract(address=info.address, abi=info.abi)
        self._contracts[contract_id] = contract
        return contract

    @staticmethod
    def from_wei(value: int) -> float:
        """Convert a wei-scaled value (1e18) to float."""
        return float(AsyncWeb3.from_wei(value, "ether"))
