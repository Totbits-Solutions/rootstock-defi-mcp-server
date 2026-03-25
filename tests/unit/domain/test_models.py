"""Tests for domain value objects and enums."""

from src.domain.shared.models import Protocol, Token


def test_token_enum_values():
    assert Token.RBTC == "RBTC"
    assert Token.DOC == "DOC"
    assert Token.USDRIF == "USDRIF"


def test_protocol_enum_values():
    assert Protocol.MOC == "moc"
    assert Protocol.TROPYKUS == "tropykus"
    assert Protocol.SOVRYN == "sovryn"
