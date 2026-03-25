"""Tests for application configuration."""

from src.config import Settings
from src.infrastructure.blockchain.constants import RSK_PUBLIC_NODE


class TestSettings:
    def test_defaults(self) -> None:
        settings = Settings(_env_file=None)
        assert settings.rsk_node_url == RSK_PUBLIC_NODE
        assert settings.log_level == "INFO"

    def test_env_override(self, monkeypatch) -> None:
        monkeypatch.setenv("MCP_RSK_NODE_URL", "https://custom-node.example.com")
        monkeypatch.setenv("MCP_LOG_LEVEL", "DEBUG")

        settings = Settings(_env_file=None)
        assert settings.rsk_node_url == "https://custom-node.example.com"
        assert settings.log_level == "DEBUG"
