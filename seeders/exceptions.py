"""Seeder-specific exceptions."""


class SeederError(Exception):
    """Base exception for seeder failures."""


class SeederRegistryError(SeederError):
    """Raised when the seeder registry encounters an error."""


class SeederRegistrationError(SeederRegistryError):
    """Raised when a seeder cannot be registered."""


class SeederNotFoundError(SeederRegistryError):
    """Raised when a seeder cannot be found."""


class SeederPageError(SeederError):
    """Raised when page creation or lookup fails."""


class SeederSlugError(SeederError):
    """Raised when slug generation fails."""


class SeederContentError(SeederError):
    """Raised when content loading or validation fails."""


class ContentProfileError(SeederContentError):
    """Raised when a content profile is missing or invalid."""


class ContentSchemaError(SeederContentError):
    """Raised when content does not match expected structure."""
