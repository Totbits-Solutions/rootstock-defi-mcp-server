"""Tests for the get_stablecoin_health MCP tool."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp.exceptions import ToolError

from src.domain.shared.exceptions import DomainError
from src.tools.stablecoin_health import get_stablecoin_health


@pytest.fixture
def mock_service():
    with patch("src.tools.stablecoin_health.get_pricing_service") as mock:
        mock.return_value = AsyncMock()
        yield mock.return_value


@pytest.fixture
def mock_use_case():
    with patch("src.tools.stablecoin_health.get_stablecoin_health_uc") as mock:
        yield mock


class TestGetStablecoinHealthTool:
    async def test_returns_health_for_all_stablecoins(self, mock_service, mock_use_case) -> None:
        mock_use_case.return_value = [
            {"token": "DOC", "status": "HEALTHY"},
            {"token": "USDRIF", "status": "HEALTHY"},
        ]

        result = await get_stablecoin_health()

        mock_use_case.assert_called_once_with(mock_service, None)
        assert len(result) == 2
        assert result[0]["token"] == "DOC"

    async def test_filtered_by_token(self, mock_service, mock_use_case) -> None:
        mock_use_case.return_value = [{"token": "DOC", "status": "HEALTHY"}]

        result = await get_stablecoin_health(tokens=["DOC"])

        assert len(result) == 1
        assert result[0]["token"] == "DOC"

    async def test_invalid_token_raises_tool_error(self, mock_service, mock_use_case) -> None:
        with pytest.raises(ToolError, match="Invalid token"):
            await get_stablecoin_health(tokens=["INVALID"])

    async def test_non_stablecoin_raises_tool_error(self, mock_service, mock_use_case) -> None:
        with pytest.raises(ToolError, match="is not a stablecoin"):
            await get_stablecoin_health(tokens=["RBTC"])

    async def test_domain_error_raises_tool_error(self, mock_service, mock_use_case) -> None:
        mock_use_case.side_effect = DomainError("provider timeout")

        with pytest.raises(ToolError, match="provider timeout"):
            await get_stablecoin_health()
