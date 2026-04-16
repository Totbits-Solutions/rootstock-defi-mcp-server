"""Tests for PricingService domain logic."""

from src.domain.pricing.models import PegStatus
from src.domain.pricing.services import PricingService


def test_calculate_peg_deviation_at_peg():
    assert PricingService.calculate_peg_deviation(1.0) == 0.0


def test_calculate_peg_deviation_above():
    deviation = PricingService.calculate_peg_deviation(1.02)
    assert abs(deviation - 2.0) < 0.01


def test_calculate_peg_deviation_below():
    deviation = PricingService.calculate_peg_deviation(0.95)
    assert abs(deviation - (-5.0)) < 0.01


def test_evaluate_coverage_healthy():
    status = PricingService.evaluate_coverage_status(coverage=4.0, target=3.0, liq_threshold=1.5)
    assert status == PegStatus.HEALTHY


def test_evaluate_coverage_warning():
    status = PricingService.evaluate_coverage_status(coverage=2.0, target=3.0, liq_threshold=1.5)
    assert status == PegStatus.WARNING


def test_evaluate_coverage_liquidation_risk():
    status = PricingService.evaluate_coverage_status(coverage=1.2, target=3.0, liq_threshold=1.5)
    assert status == PegStatus.LIQUIDATION_RISK
