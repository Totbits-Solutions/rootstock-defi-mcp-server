"""Ports (strategy interfaces) for the Pricing bounded context."""

from abc import ABC, abstractmethod

from ..shared.models import Token
from .models import StablecoinHealth, TokenPrice


class PriceProvider(ABC):
    """Port: each protocol implements this interface."""

    @abstractmethod
    def supported_tokens(self) -> list[Token]:
        """Return the list of tokens this provider can price."""
        ...

    @abstractmethod
    async def get_price(self, token: Token) -> TokenPrice:
        """Get the current price for a token."""
        ...

    @abstractmethod
    async def get_stablecoin_health(self, token: Token) -> StablecoinHealth | None:
        """Return stablecoin health or None if not applicable."""
        ...
