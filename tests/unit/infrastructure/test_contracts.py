"""Tests for the contract registry and ABI definitions."""

import pytest
from web3 import Web3

from src.infrastructure.blockchain.contracts import (
    CONTRACT_REGISTRY,
    ContractId,
)


class TestContractId:
    def test_all_ids_have_registry_entry(self) -> None:
        for cid in ContractId:
            assert cid in CONTRACT_REGISTRY, f"{cid} missing from CONTRACT_REGISTRY"

    def test_registry_has_no_extra_entries(self) -> None:
        for key in CONTRACT_REGISTRY:
            assert key in ContractId, f"Unknown key in CONTRACT_REGISTRY: {key}"


class TestContractRegistry:
    @pytest.mark.parametrize("contract_id", list(ContractId))
    def test_address_is_valid_checksum(self, contract_id: ContractId) -> None:
        info = CONTRACT_REGISTRY[contract_id]
        assert Web3.is_checksum_address(info.address), (
            f"{contract_id}: {info.address} is not a valid checksum address"
        )

    @pytest.mark.parametrize("contract_id", list(ContractId))
    def test_abi_has_at_least_one_function(self, contract_id: ContractId) -> None:
        info = CONTRACT_REGISTRY[contract_id]
        functions = [entry for entry in info.abi if entry.get("type") == "function"]
        assert len(functions) >= 1, f"{contract_id}: ABI has no functions"

    @pytest.mark.parametrize("contract_id", list(ContractId))
    def test_abi_functions_have_name(self, contract_id: ContractId) -> None:
        info = CONTRACT_REGISTRY[contract_id]
        for entry in info.abi:
            if entry.get("type") == "function":
                assert "name" in entry, f"{contract_id}: ABI function missing 'name'"
                assert isinstance(entry["name"], str)

    def test_no_duplicate_addresses(self) -> None:
        addresses = [info.address for info in CONTRACT_REGISTRY.values()]
        assert len(addresses) == len(set(addresses)), "Duplicate addresses found"
