"""Tests for LendingService domain logic."""

from src.domain.lending.services import LendingService


def test_rate_per_block_to_apy():
    rate_per_block = 0.00000002
    apy = LendingService.rate_per_block_to_apy(rate_per_block)
    assert apy > 0


def test_blocks_per_year():
    assert LendingService.blocks_per_year() == 1_051_200
