"""Application configuration via Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .infrastructure.blockchain.constants import RSK_PUBLIC_NODE


class Settings(BaseSettings):
    """Server configuration loaded from environment / .env file.

    All env vars use the ``MCP_`` prefix and ``__`` nested delimiter.
    Example: ``MCP_RSK_NODE_URL=https://public-node.rsk.co``
    """

    rsk_node_url: str = Field(default=RSK_PUBLIC_NODE)
    log_level: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MCP_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )
