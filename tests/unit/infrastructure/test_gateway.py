"""Tests for Web3BlockchainGateway."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.shared.exceptions import BlockchainQueryError
from src.infrastructure.blockchain.contracts import ContractId
from src.infrastructure.blockchain.gateway import Web3BlockchainGateway


@pytest.fixture
def gateway() -> Web3BlockchainGateway:
    with patch(
        "src.infrastructure.blockchain.gateway.AsyncWeb3"
    ) as mock_web3_cls:
        mock_w3 = MagicMock()
        mock_web3_cls.return_value = mock_w3
        mock_web3_cls.from_wei = lambda v, unit: v / 10**18 if unit == "ether" else v
        gw = Web3BlockchainGateway(rsk_node_url="https://fake-node.example.com")
        gw._mock_w3 = mock_w3  # type: ignore[attr-defined]
        return gw


class TestCall:
    async def test_call_returns_value(self, gateway: Web3BlockchainGateway) -> None:
        mock_contract = MagicMock()
        mock_fn = AsyncMock(return_value=100_000)
        mock_contract.functions.__getitem__.return_value = lambda *a: MagicMock(
            call=mock_fn
        )

        gateway._contracts[ContractId.BTC_USD_ORACLE] = mock_contract

        result = await gateway.call(ContractId.BTC_USD_ORACLE, "getPrice")
        assert result == 100_000

    async def test_call_wraps_exception_in_blockchain_query_error(
        self, gateway: Web3BlockchainGateway
    ) -> None:
        mock_contract = MagicMock()
        mock_fn = AsyncMock(side_effect=ConnectionError("node down"))
        mock_contract.functions.__getitem__.return_value = lambda *a: MagicMock(
            call=mock_fn
        )

        gateway._contracts[ContractId.MOC_STATE] = mock_contract

        with pytest.raises(BlockchainQueryError, match="node down"):
            await gateway.call(ContractId.MOC_STATE, "getBitcoinPrice")

    async def test_call_with_unknown_contract_raises(
        self, gateway: Web3BlockchainGateway
    ) -> None:
        with pytest.raises(BlockchainQueryError, match="Unknown contract"):
            await gateway.call("nonexistent_contract", "someFunction")


class TestIsConnected:
    async def test_is_connected_delegates(
        self, gateway: Web3BlockchainGateway
    ) -> None:
        gateway._w3.is_connected = AsyncMock(return_value=True)
        assert await gateway.is_connected() is True

    async def test_is_connected_returns_false_on_error(
        self, gateway: Web3BlockchainGateway
    ) -> None:
        gateway._w3.is_connected = AsyncMock(side_effect=Exception("timeout"))
        assert await gateway.is_connected() is False


class TestGetBlockNumber:
    async def test_get_block_number_delegates(
        self, gateway: Web3BlockchainGateway
    ) -> None:
        gateway._w3.eth.get_block_number = AsyncMock(return_value=6_500_000)
        result = await gateway.get_block_number()
        assert result == 6_500_000

    async def test_get_block_number_raises_on_error(
        self, gateway: Web3BlockchainGateway
    ) -> None:
        gateway._w3.eth.get_block_number = AsyncMock(
            side_effect=Exception("connection lost")
        )
        with pytest.raises(BlockchainQueryError, match="Failed to get block number"):
            await gateway.get_block_number()


class TestContractCache:
    async def test_contract_is_cached_after_first_call(
        self, gateway: Web3BlockchainGateway
    ) -> None:
        mock_contract = MagicMock()
        mock_fn = AsyncMock(return_value=42)
        mock_contract.functions.__getitem__.return_value = lambda *a: MagicMock(
            call=mock_fn
        )
        gateway._w3.eth.contract = MagicMock(return_value=mock_contract)

        await gateway.call(ContractId.K_RBTC, "supplyRatePerBlock")
        await gateway.call(ContractId.K_RBTC, "borrowRatePerBlock")

        # contract() should only have been called once (cached on second call)
        gateway._w3.eth.contract.assert_called_once()


class TestFromWei:
    def test_from_wei_converts_correctly(self) -> None:
        assert Web3BlockchainGateway.from_wei(10**18) == 1.0

    def test_from_wei_zero(self) -> None:
        assert Web3BlockchainGateway.from_wei(0) == 0.0

    def test_from_wei_small_value(self) -> None:
        result = Web3BlockchainGateway.from_wei(10**15)
        assert abs(result - 0.001) < 1e-10
