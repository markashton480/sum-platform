"""Tests for content seeding."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cli.sum.exceptions import SeedError
from cli.sum.setup.seed import ContentSeeder, SeedResult
from cli.sum.utils.django import DjangoCommandExecutor
from cli.sum.utils.environment import ExecutionMode


@pytest.fixture
def mock_executor(tmp_path: Path) -> MagicMock:
    """Create a mocked DjangoCommandExecutor."""
    executor = MagicMock(spec=DjangoCommandExecutor)
    executor.project_path = tmp_path
    executor.mode = ExecutionMode.STANDALONE
    return executor


def test_seed_homepage_success(mock_executor: MagicMock) -> None:
    """Test successful homepage seeding."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "seed_homepage"],
        returncode=0,
        stdout="Successfully created homepage with ID: 3",
        stderr="",
    )

    seeder = ContentSeeder(mock_executor)
    result = seeder.seed_homepage()

    assert isinstance(result, SeedResult)
    assert result.success is True
    assert result.page_id == 3
    mock_executor.run_command.assert_called_once_with(["seed_homepage"], check=False)


def test_seed_homepage_with_preset(mock_executor: MagicMock) -> None:
    """Test homepage seeding with a theme preset."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "seed_homepage", "--preset", "theme-x"],
        returncode=0,
        stdout="Successfully created homepage with ID: 5",
        stderr="",
    )

    seeder = ContentSeeder(mock_executor)
    result = seeder.seed_homepage(preset="theme-x")

    assert isinstance(result, SeedResult)
    assert result.success is True
    assert result.page_id == 5
    mock_executor.run_command.assert_called_once_with(
        ["seed_homepage", "--preset", "theme-x"], check=False
    )


def test_seed_homepage_already_exists(mock_executor: MagicMock) -> None:
    """Test seeding when homepage already exists."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "seed_homepage"],
        returncode=1,
        stdout="Homepage already exists",
        stderr="",
    )

    seeder = ContentSeeder(mock_executor)
    result = seeder.seed_homepage()

    assert isinstance(result, SeedResult)
    assert result.success is True
    assert result.page_id is None


def test_seed_homepage_failure(mock_executor: MagicMock) -> None:
    """Test seeding failure raises SeedError."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "seed_homepage"],
        returncode=1,
        stdout="",
        stderr="Error: Invalid preset configuration",
    )

    seeder = ContentSeeder(mock_executor)

    with pytest.raises(SeedError, match="Seeding failed"):
        seeder.seed_homepage()

    mock_executor.run_command.assert_called_once_with(["seed_homepage"], check=False)


def test_seed_homepage_no_page_id_in_output(mock_executor: MagicMock) -> None:
    """Test seeding when output doesn't contain page ID."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=["python", "manage.py", "seed_homepage"],
        returncode=0,
        stdout="Successfully created homepage",
        stderr="",
    )

    seeder = ContentSeeder(mock_executor)
    result = seeder.seed_homepage()

    assert isinstance(result, SeedResult)
    assert result.success is True
    assert result.page_id is None


def test_check_homepage_exists_true(mock_executor: MagicMock) -> None:
    """Test check_homepage_exists returns True when homepage exists."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=[
            "python",
            "manage.py",
            "shell",
            "-c",
            "from home.models import HomePage; print(HomePage.objects.filter(slug='home').exists())",
        ],
        returncode=0,
        stdout="True\n",
        stderr="",
    )

    seeder = ContentSeeder(mock_executor)
    result = seeder.check_homepage_exists()

    assert result is True
    mock_executor.run_command.assert_called_once_with(
        [
            "shell",
            "-c",
            (
                "from home.models import HomePage; "
                "print(HomePage.objects.filter(slug='home').exists())"
            ),
        ],
        check=False,
    )


def test_check_homepage_exists_false(mock_executor: MagicMock) -> None:
    """Test check_homepage_exists returns False when homepage doesn't exist."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=[
            "python",
            "manage.py",
            "shell",
            "-c",
            "from home.models import HomePage; print(HomePage.objects.filter(slug='home').exists())",
        ],
        returncode=0,
        stdout="False\n",
        stderr="",
    )

    seeder = ContentSeeder(mock_executor)
    result = seeder.check_homepage_exists()

    assert result is False


def test_content_seeder_uses_provided_executor(tmp_path: Path) -> None:
    """Test that ContentSeeder uses the provided executor instance."""
    executor = MagicMock(spec=DjangoCommandExecutor)
    executor.project_path = tmp_path

    seeder = ContentSeeder(executor)

    assert seeder.django is executor


def test_extract_page_id_with_various_formats(mock_executor: MagicMock) -> None:
    """Test page ID extraction from various output formats."""
    test_cases = [
        ("Created page with ID: 42", 42),
        ("Successfully created homepage with ID: 999", 999),
        ("ID: 1", 1),
        ("No ID here", None),
        ("", None),
    ]

    seeder = ContentSeeder(mock_executor)

    for output, expected_id in test_cases:
        mock_executor.run_command.return_value = subprocess.CompletedProcess(
            args=["python", "manage.py", "seed_homepage"],
            returncode=0,
            stdout=output,
            stderr="",
        )
        result = seeder.seed_homepage()
        assert result.page_id == expected_id


def test_check_homepage_exists_raises_on_import_error(
    mock_executor: MagicMock,
) -> None:
    """Test check_homepage_exists raises SeedError on ImportError."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=[
            "python",
            "manage.py",
            "shell",
            "-c",
            "from home.models import HomePage; print(HomePage.objects.filter(slug='home').exists())",
        ],
        returncode=1,
        stdout="",
        stderr="ImportError: No module named 'home'",
    )

    seeder = ContentSeeder(mock_executor)

    with pytest.raises(SeedError, match="Failed to check homepage existence"):
        seeder.check_homepage_exists()


def test_check_homepage_exists_raises_on_database_error(
    mock_executor: MagicMock,
) -> None:
    """Test check_homepage_exists raises SeedError on database connection issues."""
    mock_executor.run_command.return_value = subprocess.CompletedProcess(
        args=[
            "python",
            "manage.py",
            "shell",
            "-c",
            "from home.models import HomePage; print(HomePage.objects.filter(slug='home').exists())",
        ],
        returncode=1,
        stdout="",
        stderr="django.db.utils.OperationalError: could not connect to server",
    )

    seeder = ContentSeeder(mock_executor)

    with pytest.raises(
        SeedError,
        match="Failed to check homepage existence.*could not connect to server",
    ):
        seeder.check_homepage_exists()
