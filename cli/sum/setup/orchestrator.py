"""Setup orchestration for CLI project initialization."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from cli.sum.config import SetupConfig
from cli.sum.exceptions import SetupError
from cli.sum.setup.auth import SuperuserManager
from cli.sum.setup.database import DatabaseManager
from cli.sum.setup.deps import DependencyManager
from cli.sum.setup.seed import ContentSeeder
from cli.sum.setup.venv import VenvManager
from cli.sum.utils.django import DjangoCommandExecutor
from cli.sum.utils.environment import ExecutionMode
from cli.sum.utils.output import OutputFormatter


@dataclass
class SetupResult:
    """Result of a setup operation."""

    success: bool
    project_path: Path
    credentials_path: Path | None = None
    url: str = "http://127.0.0.1:8000/"


class SetupOrchestrator:
    """Orchestrates the full project setup flow.

    Owns ALL 8 steps — init command is a thin wrapper around this.
    """

    def __init__(self, project_path: Path, mode: ExecutionMode) -> None:
        self.project_path = project_path
        self.mode = mode

        # Initialize components
        self.venv_manager = VenvManager()
        self.deps_manager = DependencyManager(venv_manager=self.venv_manager)

    def run_full_setup(self, config: SetupConfig) -> SetupResult:
        """Run complete setup based on configuration.

        Args:
            config: The setup configuration with flags and options.

        Raises:
            SetupError: If any setup step fails.

        Returns:
            SetupResult with success=True, project path, and optional credentials path.
        """
        # Build step list dynamically based on config
        steps = self._build_step_list(config)
        total_steps = len(steps)

        credentials_path: Path | None = None

        for step_num, (step_name, step_func) in enumerate(steps, 1):
            self._show_progress(step_num, total_steps, step_name, "⏳")
            try:
                result = step_func(config)
                if step_name == "Creating superuser" and result:
                    credentials_path = result
                self._show_progress(step_num, total_steps, step_name, "✅")
            except SetupError:
                self._show_progress(step_num, total_steps, step_name, "❌")
                raise
            except Exception as e:
                # Wrap unexpected exceptions
                self._show_progress(step_num, total_steps, step_name, "❌")
                raise SetupError(f"Unexpected error in '{step_name}': {e}") from e

        return SetupResult(
            success=True,
            project_path=self.project_path,
            credentials_path=credentials_path,
            url=f"http://127.0.0.1:{config.port}/",
        )

    def _build_step_list(
        self, config: SetupConfig
    ) -> list[tuple[str, Callable[[SetupConfig], Path | None]]]:
        """Build list of steps to execute based on config.

        Args:
            config: The setup configuration with flags and options.

        Returns:
            List of (step_name, step_function) tuples to execute.
        """
        # Always include scaffold and validate
        steps: list[tuple[str, Callable[[SetupConfig], Path | None]]] = [
            ("Scaffolding structure", self._scaffold),
            ("Validating structure", self._validate),
        ]

        # Venv and deps (unless skipped)
        if not config.skip_venv:
            steps.append(("Creating virtualenv", self._setup_venv))
            steps.append(("Installing dependencies", self._install_deps))

        # Quick mode stops here
        if config.quick:
            return steps

        # DB operations
        if not config.skip_migrations:
            steps.append(("Running migrations", self._migrate))

        if not config.skip_seed:
            steps.append(("Seeding homepage", self._seed_content))

        if not config.skip_superuser:
            steps.append(("Creating superuser", self._create_superuser))

        # Server (only if requested)
        if config.run_server:
            steps.append(("Starting server", self._start_server))

        return steps

    def _show_progress(self, step: int, total: int, message: str, status: str) -> None:
        """Display progress indicator.

        Args:
            step: Current step number (1-indexed).
            total: Total number of steps.
            message: The step description.
            status: Status emoji (⏳, ✅, ❌).
        """
        OutputFormatter.progress(step, total, message, status)

    def _setup_venv(self, config: SetupConfig) -> None:
        """Create virtualenv.

        Args:
            config: The setup configuration.
        """
        self.venv_manager.create(self.project_path)

    def _install_deps(self, config: SetupConfig) -> None:
        """Install dependencies.

        Args:
            config: The setup configuration.
        """
        self.deps_manager.install(self.project_path)

    def _migrate(self, config: SetupConfig) -> None:
        """Run database migrations.

        Args:
            config: The setup configuration.
        """
        executor = DjangoCommandExecutor(self.project_path, self.mode)
        db_manager = DatabaseManager(executor)
        db_manager.migrate()

    def _seed_content(self, config: SetupConfig) -> None:
        """Seed homepage content.

        Args:
            config: The setup configuration.
        """
        executor = DjangoCommandExecutor(self.project_path, self.mode)
        seeder = ContentSeeder(executor)
        seeder.seed_homepage(preset=config.seed_preset)

    def _create_superuser(self, config: SetupConfig) -> Path:
        """Create superuser and return credentials path.

        Args:
            config: The setup configuration.

        Returns:
            Path to the credentials file (.env.local).
        """
        executor = DjangoCommandExecutor(self.project_path, self.mode)
        auth_manager = SuperuserManager(executor, self.project_path)
        result = auth_manager.create(
            username=config.superuser_username,
            email=config.superuser_email,
            password=config.superuser_password,
        )
        return result.credentials_path

    def _scaffold(self, config: SetupConfig) -> None:
        """Scaffold project structure.

        Args:
            config: The setup configuration.

        Note:
            This is a placeholder for scaffolding logic to be integrated from init command.
        """
        # TODO: Implementation to be integrated from existing init command
        pass

    def _validate(self, config: SetupConfig) -> None:
        """Validate project structure.

        Args:
            config: The setup configuration.

        Note:
            This is a placeholder for validation logic to be integrated from init command.
        """
        # TODO: Implementation to be integrated from existing init command
        pass

    def _start_server(self, config: SetupConfig) -> None:
        """Start development server in background.

        Args:
            config: The setup configuration.
        """
        python = self.venv_manager.get_python_executable(self.project_path)

        # Start server as background process
        subprocess.Popen(
            [str(python), "manage.py", "runserver", f"127.0.0.1:{config.port}"],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
