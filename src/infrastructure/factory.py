"""Provider factory — registry and creation of protocol providers."""

from ..domain.lending.ports import LendingProvider
from ..domain.pricing.ports import PriceProvider
from ..domain.shared.models import Protocol
from ..domain.shared.ports import BlockchainGateway
from .providers.lending.sovryn_provider import SovrynLendingProvider
from .providers.lending.tropykus_provider import TropykusLendingProvider
from .providers.pricing.moc_price_provider import MoCPriceProvider
from .providers.pricing.roc_price_provider import RoCPriceProvider


class ProviderFactory:
    """Creates and groups all protocol providers."""

    def __init__(self, gateway: BlockchainGateway) -> None:
        self._gateway = gateway

    def create_price_providers(self) -> list[PriceProvider]:
        return [
            MoCPriceProvider(self._gateway),
            RoCPriceProvider(self._gateway),
        ]

    def create_lending_providers(self) -> dict[Protocol, LendingProvider]:
        return {
            Protocol.TROPYKUS: TropykusLendingProvider(self._gateway),
            Protocol.SOVRYN: SovrynLendingProvider(self._gateway),
        }
