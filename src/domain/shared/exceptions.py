"""Domain exceptions."""


class DomainError(Exception):
    """Base domain exception."""


class ProviderNotFoundError(DomainError):
    """No provider registered for the requested resource."""


class BlockchainQueryError(DomainError):
    """A blockchain query failed."""


class TokenNotSupportedError(DomainError):
    """The requested token is not supported by any provider."""


class ProtocolNotSupportedError(DomainError):
    """The requested protocol is not registered."""
