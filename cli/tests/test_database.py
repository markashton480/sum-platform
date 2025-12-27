"""Tests for database management."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cli.sum.exceptions import MigrationError
from cli.sum.setup.database import DatabaseManager, MigrationResult
from cli.sum.utils.django import DjangoCommandExecutor
from cli.sum.utils.environment import ExecutionMode


@pytest.fixture
def mock_executor(tmp_path: Path) -> MagicMock:
    """Create a mocked DjangoCommandExecutor."""
    executor = MagicMock(spec=DjangoCommandExecutor)
    executor.project_path = tmp_path
    executor.mode = ExecutionMode.STANDALONE
    return executor


def test_migrate_success(mock_executor: MagicMock) -> None:
    """Test successful migration."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "migrate", "--noinput"],
        returncode=0,
        stdout="Operations to perform:\n  Apply all migrations\nRunning migrations:\n  No migrations to apply.",
        stderr="",
    )

    manager = DatabaseManager(mock_executor)
    result = manager.migrate()

    assert isinstance(result, MigrationResult)
    assert result.success is True
    assert "No migrations to apply" in result.output
    mock_executor.run_command.assert_called_once_with(
        ["migrate", "--noinput"], check=False
    )


def test_migrate_failure(mock_executor: MagicMock) -> None:
    """Test migration failure raises MigrationError."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "migrate", "--noinput"],
        returncode=1,
        stdout="",
        stderr="django.db.utils.OperationalError: no such table: auth_user",
    )

    manager = DatabaseManager(mock_executor)

    with pytest.raises(MigrationError, match="Migration failed"):
        manager.migrate()

    mock_executor.run_command.assert_called_once_with(
        ["migrate", "--noinput"], check=False
    )


def test_check_migrations_up_to_date(mock_executor: MagicMock) -> None:
    """Test check_migrations returns True when migrations are up to date."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "migrate", "--check"],
        returncode=0,
        stdout="",
        stderr="",
    )

    manager = DatabaseManager(mock_executor)
    result = manager.check_migrations()

    assert result is True
    mock_executor.run_command.assert_called_once_with(
        ["migrate", "--check"], check=False
    )


def test_check_migrations_pending(mock_executor: MagicMock) -> None:
    """Test check_migrations returns False when migrations are pending."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "migrate", "--check"],
        returncode=1,
        stdout="",
        stderr="",
    )

    manager = DatabaseManager(mock_executor)
    result = manager.check_migrations()

    assert result is False
    mock_executor.run_command.assert_called_once_with(
        ["migrate", "--check"], check=False
    )


def test_get_migration_status(mock_executor: MagicMock) -> None:
    """Test get_migration_status returns detailed migration plan."""
    migration_output = """
    auth.0001_initial
    auth.0002_alter_permission_name_max_length
    contenttypes.0001_initial
    [X] wagtailcore.0001_initial
    [ ] wagtailcore.0002_initial_data
    """
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "showmigrations", "--plan"],
        returncode=0,
        stdout=migration_output,
        stderr="",
    )

    manager = DatabaseManager(mock_executor)
    result = manager.get_migration_status()

    assert "wagtailcore.0001_initial" in result
    assert "[ ] wagtailcore.0002_initial_data" in result
    mock_executor.run_command.assert_called_once_with(
        ["showmigrations", "--plan"], check=False
    )


def test_database_manager_uses_provided_executor(tmp_path: Path) -> None:
    """Test that DatabaseManager uses the provided executor instance."""
    executor = MagicMock(spec=DjangoCommandExecutor)
    executor.project_path = tmp_path

    manager = DatabaseManager(executor)

    assert manager.django is executor


def test_migrate_error_handles_empty_stderr(mock_executor: MagicMock) -> None:
    """Test that migration error handles empty stderr gracefully."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "migrate", "--noinput"],
        returncode=1,
        stdout="Error in stdout",
        stderr="",
    )

    manager = DatabaseManager(mock_executor)

    with pytest.raises(MigrationError, match="Migration failed: Error in stdout"):
        manager.migrate()
