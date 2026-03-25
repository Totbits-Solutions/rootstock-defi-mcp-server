"""Shared value objects and enums used across bounded contexts."""

from enum import StrEnum

from pydantic import BaseModel


class Token(StrEnum):
    RBTC = "RBTC"
    BPRO = "BPRO"
    RIF = "RIF"
    RIFPRO = "RIFPRO"
    DOC = "DOC"
    USDRIF = "USDRIF"


class Protocol(StrEnum):
    MOC = "moc"
    ROC_V2 = "roc_v2"
    TROPYKUS = "tropykus"
    SOVRYN = "sovryn"


class ProtocolInfo(BaseModel):
    name: str
    protocol: Protocol
    description: str
