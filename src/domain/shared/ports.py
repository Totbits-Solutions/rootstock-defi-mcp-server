"""Domain ports — abstract gateways that infrastructure must implement."""

from abc import ABC, abstractmethod
from typing import Any


class BlockchainGateway(ABC):
    """Port for blockchain read-only interactions.

    Infrastructure adapters implement this to decouple domain/providers
    from Web3 or any specific blockchain library.
    """

    @abstractmethod
    async def call(self, contract_id: str, function_name: str, *args: Any) -> Any:
        """Execute a read-only call on a smart contract function."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check connectivity with the blockchain node."""
        ...

    @abstractmethod
    async def get_block_number(self) -> int:
        """Return the current block number."""
        ...
