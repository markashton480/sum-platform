"""CLI-specific exception hierarchy."""


class SumCliError(Exception):
    """Base exception for SUM CLI failures."""


class SetupError(SumCliError):
    """Raised when initial setup steps fail."""


class VenvError(SumCliError):
    """Raised when virtual environment operations fail."""


class DependencyError(SumCliError):
    """Raised when dependency installation or resolution fails."""


class MigrationError(SumCliError):
    """Raised when database migrations fail."""


class SeedError(SumCliError):
    """Raised when seed data operations fail."""


class SuperuserError(SumCliError):
    """Raised when superuser creation fails."""
