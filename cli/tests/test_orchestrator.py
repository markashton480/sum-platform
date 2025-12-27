"""Tests for setup orchestration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cli.sum.config import SetupConfig
from cli.sum.exceptions import SetupError
from cli.sum.setup.orchestrator import SetupOrchestrator, SetupResult
from cli.sum.utils.environment import ExecutionMode


@pytest.fixture
def tmp_project_path(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    project_path = tmp_path / "test_project"
    project_path.mkdir()
    return project_path


@pytest.fixture
def orchestrator(tmp_project_path: Path) -> SetupOrchestrator:
    """Create a SetupOrchestrator instance."""
    return SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)


def test_build_step_list_full_setup(tmp_project_path: Path) -> None:
    """Test step list includes all steps for full setup."""
    config = SetupConfig(full=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    steps = orchestrator._build_step_list(config)
    step_names = [name.value for name, _ in steps]

    assert "Scaffolding structure" in step_names
    assert "Validating structure" in step_names
    assert "Creating virtualenv" in step_names
    assert "Installing dependencies" in step_names
    assert "Running migrations" in step_names
    assert "Seeding homepage" in step_names
    assert "Creating superuser" in step_names
    assert "Starting server" not in step_names  # Not included unless run_server=True


def test_build_step_list_quick_mode(tmp_project_path: Path) -> None:
    """Test step list only includes first 4 steps in quick mode."""
    config = SetupConfig(quick=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    steps = orchestrator._build_step_list(config)
    step_names = [name.value for name, _ in steps]

    assert len(steps) == 4
    assert "Scaffolding structure" in step_names
    assert "Validating structure" in step_names
    assert "Creating virtualenv" in step_names
    assert "Installing dependencies" in step_names
    assert "Running migrations" not in step_names
    assert "Seeding homepage" not in step_names
    assert "Creating superuser" not in step_names


def test_build_step_list_skip_venv(tmp_project_path: Path) -> None:
    """Test step list excludes venv steps when skip_venv=True."""
    config = SetupConfig(skip_venv=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    steps = orchestrator._build_step_list(config)
    step_names = [name.value for name, _ in steps]

    assert "Creating virtualenv" not in step_names
    assert "Installing dependencies" not in step_names
    assert "Running migrations" in step_names


def test_build_step_list_skip_migrations(tmp_project_path: Path) -> None:
    """Test step list excludes migrations when skip_migrations=True."""
    config = SetupConfig(skip_migrations=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    steps = orchestrator._build_step_list(config)
    step_names = [name.value for name, _ in steps]

    assert "Running migrations" not in step_names
    assert "Creating virtualenv" in step_names
    assert "Seeding homepage" in step_names


def test_build_step_list_skip_seed(tmp_project_path: Path) -> None:
    """Test step list excludes seeding when skip_seed=True."""
    config = SetupConfig(skip_seed=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    steps = orchestrator._build_step_list(config)
    step_names = [name.value for name, _ in steps]

    assert "Seeding homepage" not in step_names
    assert "Running migrations" in step_names
    assert "Creating superuser" in step_names


def test_build_step_list_skip_superuser(tmp_project_path: Path) -> None:
    """Test step list excludes superuser when skip_superuser=True."""
    config = SetupConfig(skip_superuser=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    steps = orchestrator._build_step_list(config)
    step_names = [name.value for name, _ in steps]

    assert "Creating superuser" not in step_names
    assert "Seeding homepage" in step_names


def test_build_step_list_with_server(tmp_project_path: Path) -> None:
    """Test step list includes server start when run_server=True."""
    config = SetupConfig(run_server=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    steps = orchestrator._build_step_list(config)
    step_names = [name.value for name, _ in steps]

    assert "Starting server" in step_names
    assert step_names[-1] == "Starting server"  # Should be last step


@patch("cli.sum.setup.orchestrator.OutputFormatter.progress")
@patch.object(SetupOrchestrator, "_scaffold")
@patch.object(SetupOrchestrator, "_validate")
@patch.object(SetupOrchestrator, "_setup_venv")
@patch.object(SetupOrchestrator, "_install_deps")
def test_run_full_setup_success(
    mock_install_deps: MagicMock,
    mock_setup_venv: MagicMock,
    mock_validate: MagicMock,
    mock_scaffold: MagicMock,
    mock_progress: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test successful full setup execution."""
    config = SetupConfig(quick=True)  # Only 4 steps
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    result = orchestrator.run_full_setup(config)

    assert isinstance(result, SetupResult)
    assert result.success is True
    assert result.project_path == tmp_project_path
    assert result.credentials_path is None  # Quick mode doesn't create superuser

    # Verify all steps were called
    mock_scaffold.assert_called_once()
    mock_validate.assert_called_once()
    mock_setup_venv.assert_called_once()
    mock_install_deps.assert_called_once()

    # Verify progress was shown for each step (twice per step: start and complete)
    assert mock_progress.call_count == 8  # 4 steps * 2 (start + complete)


@patch("cli.sum.setup.orchestrator.OutputFormatter.progress")
@patch.object(SetupOrchestrator, "_scaffold")
@patch.object(SetupOrchestrator, "_validate")
@patch.object(SetupOrchestrator, "_setup_venv")
@patch.object(SetupOrchestrator, "_install_deps")
@patch.object(SetupOrchestrator, "_migrate")
@patch.object(SetupOrchestrator, "_seed_content")
@patch.object(SetupOrchestrator, "_create_superuser")
def test_run_full_setup_with_superuser(
    mock_create_superuser: MagicMock,
    mock_seed_content: MagicMock,
    mock_migrate: MagicMock,
    mock_install_deps: MagicMock,
    mock_setup_venv: MagicMock,
    mock_validate: MagicMock,
    mock_scaffold: MagicMock,
    mock_progress: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test setup with superuser creation returns credentials path."""
    credentials_path = tmp_project_path / ".env.local"
    mock_create_superuser.return_value = credentials_path

    config = SetupConfig(full=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    result = orchestrator.run_full_setup(config)

    assert result.success is True
    assert result.credentials_path == credentials_path
    mock_create_superuser.assert_called_once()


@patch("cli.sum.setup.orchestrator.OutputFormatter.progress")
@patch.object(SetupOrchestrator, "_scaffold")
@patch.object(SetupOrchestrator, "_validate")
def test_run_full_setup_handles_setup_error(
    mock_validate: MagicMock,
    mock_scaffold: MagicMock,
    mock_progress: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test that SetupError is re-raised without wrapping."""
    mock_validate.side_effect = SetupError("Validation failed")

    config = SetupConfig(quick=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    with pytest.raises(SetupError, match="Validation failed"):
        orchestrator.run_full_setup(config)


@patch("cli.sum.setup.orchestrator.OutputFormatter.progress")
@patch.object(SetupOrchestrator, "_scaffold")
@patch.object(SetupOrchestrator, "_validate")
def test_run_full_setup_wraps_unexpected_error(
    mock_validate: MagicMock,
    mock_scaffold: MagicMock,
    mock_progress: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test that unexpected exceptions are wrapped in SetupError."""
    mock_validate.side_effect = ValueError("Unexpected error")

    config = SetupConfig(quick=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    with pytest.raises(SetupError, match="Unexpected error in 'Validating structure'"):
        orchestrator.run_full_setup(config)


@patch("cli.sum.setup.orchestrator.VenvManager.create")
def test_setup_venv_calls_venv_manager(
    mock_create: MagicMock, tmp_project_path: Path
) -> None:
    """Test _setup_venv calls VenvManager.create."""
    config = SetupConfig()
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    orchestrator._setup_venv(config)

    mock_create.assert_called_once_with(tmp_project_path)


@patch("cli.sum.setup.orchestrator.DependencyManager.install")
def test_install_deps_calls_dependency_manager(
    mock_install: MagicMock, tmp_project_path: Path
) -> None:
    """Test _install_deps calls DependencyManager.install."""
    config = SetupConfig()
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    orchestrator._install_deps(config)

    mock_install.assert_called_once_with(tmp_project_path)


@patch("cli.sum.setup.orchestrator.DatabaseManager.migrate")
@patch("cli.sum.setup.orchestrator.DjangoCommandExecutor")
def test_migrate_calls_database_manager(
    mock_executor_class: MagicMock,
    mock_migrate: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test _migrate calls DatabaseManager.migrate."""
    config = SetupConfig()
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    orchestrator._migrate(config)

    mock_executor_class.assert_called_once_with(
        tmp_project_path, ExecutionMode.STANDALONE
    )
    mock_migrate.assert_called_once()


@patch("cli.sum.setup.orchestrator.ContentSeeder.seed_homepage")
@patch("cli.sum.setup.orchestrator.DjangoCommandExecutor")
def test_seed_content_calls_content_seeder(
    mock_executor_class: MagicMock,
    mock_seed_homepage: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test _seed_content calls ContentSeeder.seed_homepage."""
    config = SetupConfig(seed_preset="theme-x")
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    orchestrator._seed_content(config)

    mock_executor_class.assert_called_once_with(
        tmp_project_path, ExecutionMode.STANDALONE
    )
    mock_seed_homepage.assert_called_once_with(preset="theme-x")


@patch("cli.sum.setup.orchestrator.SuperuserManager.create")
@patch("cli.sum.setup.orchestrator.DjangoCommandExecutor")
def test_create_superuser_calls_superuser_manager(
    mock_executor_class: MagicMock,
    mock_create: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test _create_superuser calls SuperuserManager.create."""
    credentials_path = tmp_project_path / ".env.local"
    mock_result = MagicMock(credentials_path=credentials_path)
    mock_create.return_value = mock_result

    config = SetupConfig(
        superuser_username="testadmin",
        superuser_email="test@example.com",
        superuser_password="testpass",
    )
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    result = orchestrator._create_superuser(config)

    assert result == credentials_path
    mock_executor_class.assert_called_once_with(
        tmp_project_path, ExecutionMode.STANDALONE
    )
    mock_create.assert_called_once_with(
        username="testadmin", email="test@example.com", password="testpass"
    )


@patch("cli.sum.setup.orchestrator.subprocess.Popen")
@patch("cli.sum.setup.orchestrator.VenvManager.exists")
@patch("cli.sum.setup.orchestrator.VenvManager.get_python_executable")
def test_start_server_calls_subprocess(
    mock_get_python: MagicMock,
    mock_venv_exists: MagicMock,
    mock_popen: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test _start_server starts Django dev server with venv."""
    python_path = tmp_project_path / ".venv" / "bin" / "python"
    mock_venv_exists.return_value = True
    mock_get_python.return_value = python_path

    config = SetupConfig(port=8080)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    orchestrator._start_server(config)

    mock_venv_exists.assert_called_once_with(tmp_project_path)
    mock_get_python.assert_called_once_with(tmp_project_path)
    mock_popen.assert_called_once()
    call_args = mock_popen.call_args

    # Verify command
    assert call_args[0][0] == [
        str(python_path),
        "manage.py",
        "runserver",
        "127.0.0.1:8080",
    ]

    # Verify working directory
    assert call_args[1]["cwd"] == tmp_project_path


@patch("cli.sum.setup.orchestrator.subprocess.Popen")
@patch("cli.sum.setup.orchestrator.VenvManager.exists")
def test_start_server_without_venv_uses_system_python(
    mock_venv_exists: MagicMock,
    mock_popen: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test _start_server falls back to sys.executable when venv doesn't exist."""
    import sys

    mock_venv_exists.return_value = False

    config = SetupConfig(port=8080, skip_venv=True, run_server=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    orchestrator._start_server(config)

    mock_venv_exists.assert_called_once_with(tmp_project_path)
    mock_popen.assert_called_once()
    call_args = mock_popen.call_args

    # Verify command uses system python (sys.executable)
    assert call_args[0][0][0] == sys.executable
    assert call_args[0][0][1:] == [
        "manage.py",
        "runserver",
        "127.0.0.1:8080",
    ]

    # Verify working directory
    assert call_args[1]["cwd"] == tmp_project_path


def test_orchestrator_uses_correct_mode(tmp_project_path: Path) -> None:
    """Test that orchestrator stores and uses the provided execution mode."""
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.MONOREPO)

    assert orchestrator.mode == ExecutionMode.MONOREPO
    assert orchestrator.project_path == tmp_project_path


def test_setup_result_default_url(tmp_project_path: Path) -> None:
    """Test SetupResult default URL."""
    result = SetupResult(success=True, project_path=tmp_project_path)

    assert result.url == "http://127.0.0.1:8000/"


def test_setup_result_custom_url(tmp_project_path: Path) -> None:
    """Test SetupResult with custom URL."""
    result = SetupResult(
        success=True, project_path=tmp_project_path, url="http://127.0.0.1:9000/"
    )

    assert result.url == "http://127.0.0.1:9000/"


@patch("cli.sum.setup.orchestrator.OutputFormatter.progress")
@patch.object(SetupOrchestrator, "_scaffold")
@patch.object(SetupOrchestrator, "_validate")
@patch.object(SetupOrchestrator, "_setup_venv")
@patch.object(SetupOrchestrator, "_install_deps")
def test_progress_shows_correct_step_count(
    mock_install_deps: MagicMock,
    mock_setup_venv: MagicMock,
    mock_validate: MagicMock,
    mock_scaffold: MagicMock,
    mock_progress: MagicMock,
    tmp_project_path: Path,
) -> None:
    """Test progress displays correct step numbers for quick mode."""
    config = SetupConfig(quick=True)
    orchestrator = SetupOrchestrator(tmp_project_path, ExecutionMode.STANDALONE)

    orchestrator.run_full_setup(config)

    # Check progress calls show [1/4], [2/4], [3/4], [4/4] not [1/8], etc.
    progress_calls = [call[0] for call in mock_progress.call_args_list]

    # Extract step and total from progress calls (step, total, message, status)
    step_totals = [(call[0], call[1]) for call in progress_calls]

    # We get 2 calls per step (start and complete), so 8 total calls
    assert step_totals == [
        (1, 4),
        (1, 4),  # Scaffolding start and complete
        (2, 4),
        (2, 4),  # Validating start and complete
        (3, 4),
        (3, 4),  # Creating venv start and complete
        (4, 4),
        (4, 4),  # Installing deps start and complete
    ]
