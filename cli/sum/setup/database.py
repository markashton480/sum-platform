"""Database management for CLI setup."""

from __future__ import annotations

from dataclasses import dataclass

from cli.sum.exceptions import MigrationError
from cli.sum.utils.django import DjangoCommandExecutor


@dataclass
class MigrationResult:
    """Result of a migration operation."""

    success: bool
    output: str


class DatabaseManager:
    """Manages database operations."""

    def __init__(self, django_executor: DjangoCommandExecutor) -> None:
        self.django = django_executor

    def migrate(self) -> MigrationResult:
        """Run database migrations.

        Raises:
            MigrationError: If migration fails.

        Returns:
            MigrationResult with success=True and output.
        """
        result = self.django.run_command(["migrate", "--noinput"], check=False)

        if result.returncode != 0:
            raise MigrationError(f"Migration failed: {result.stderr}")

        return MigrationResult(success=True, output=result.stdout)

    def check_migrations(self) -> bool:
        """Check if migrations are up to date.

        Returns:
            True if migrations are up to date, False otherwise.
        """
        result = self.django.run_command(["migrate", "--check"], check=False)
        return result.returncode == 0

    def get_migration_status(self) -> str:
        """Get detailed migration status.

        Returns:
            Output from showmigrations --plan command.
        """
        result = self.django.run_command(["showmigrations", "--plan"], check=False)
        return result.stdout
