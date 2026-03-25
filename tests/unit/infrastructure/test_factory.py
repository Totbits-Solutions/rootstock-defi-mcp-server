"""Tests for ProviderFactory."""

from unittest.mock import AsyncMock

from src.domain.shared.models import Protocol
from src.infrastructure.factory import ProviderFactory
from src.infrastructure.providers.lending.sovryn_provider import SovrynLendingProvider
from src.infrastructure.providers.lending.tropykus_provider import TropykusLendingProvider
from src.infrastructure.providers.pricing.moc_price_provider import MoCPriceProvider
from src.infrastructure.providers.pricing.roc_price_provider import RoCPriceProvider


def test_create_price_providers() -> None:
    gateway = AsyncMock()
    factory = ProviderFactory(gateway)
    providers = factory.create_price_providers()

    assert len(providers) == 2
    assert isinstance(providers[0], MoCPriceProvider)
    assert isinstance(providers[1], RoCPriceProvider)


def test_create_lending_providers() -> None:
    gateway = AsyncMock()
    factory = ProviderFactory(gateway)
    providers = factory.create_lending_providers()

    assert len(providers) == 2
    assert Protocol.TROPYKUS in providers
    assert Protocol.SOVRYN in providers
    assert isinstance(providers[Protocol.TROPYKUS], TropykusLendingProvider)
    assert isinstance(providers[Protocol.SOVRYN], SovrynLendingProvider)
