"""Tests for the get_lending_rates MCP tool."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp.exceptions import ToolError

from src.domain.shared.exceptions import DomainError
from src.tools.lending_rates import get_lending_rates


@pytest.fixture
def mock_service():
    with patch("src.tools.lending_rates.get_lending_service") as mock:
        mock.return_value = AsyncMock()
        yield mock.return_value


@pytest.fixture
def mock_use_case():
    with patch("src.tools.lending_rates.get_lending_rates_uc") as mock:
        yield mock


class TestGetLendingRatesTool:
    async def test_returns_all_rates(self, mock_service, mock_use_case) -> None:
        mock_use_case.return_value = [
            {"market": "kDOC", "protocol": "tropykus"},
            {"market": "iDOC", "protocol": "sovryn"},
        ]

        result = await get_lending_rates()

        mock_use_case.assert_called_once_with(mock_service, None, None)
        assert len(result) == 2

    async def test_filtered_by_protocol(self, mock_service, mock_use_case) -> None:
        mock_use_case.return_value = [{"market": "kDOC", "protocol": "tropykus"}]

        result = await get_lending_rates(protocol="tropykus")

        assert len(result) == 1
        assert result[0]["protocol"] == "tropykus"

    async def test_invalid_protocol_raises_tool_error(self, mock_service, mock_use_case) -> None:
        with pytest.raises(ToolError, match="Invalid protocol"):
            await get_lending_rates(protocol="INVALID")

    async def test_non_lending_protocol_raises_tool_error(self, mock_service, mock_use_case) -> None:
        with pytest.raises(ToolError, match="is not a lending protocol"):
            await get_lending_rates(protocol="moc")

    async def test_market_without_protocol_raises_tool_error(self, mock_service, mock_use_case) -> None:
        with pytest.raises(ToolError, match="requires 'protocol'"):
            await get_lending_rates(market="kDOC")

    async def test_domain_error_raises_tool_error(self, mock_service, mock_use_case) -> None:
        mock_use_case.side_effect = DomainError("provider timeout")

        with pytest.raises(ToolError, match="provider timeout"):
            await get_lending_rates()
