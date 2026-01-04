"""Setup orchestration for CLI project initialization."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from cli.sum.config import SetupConfig
from cli.sum.exceptions import SetupError
from cli.sum.setup.auth import SuperuserManager
from cli.sum.setup.database import DatabaseManager
from cli.sum.setup.deps import DependencyManager
from cli.sum.setup.scaffold import scaffold_project, validate_project_structure
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


class SetupStep(str, Enum):
    """Ordered, typed identifiers for setup steps."""

    SCAFFOLD = "Scaffolding structure"
    VALIDATE = "Validating structure"
    CREATE_VENV = "Creating virtualenv"
    INSTALL_DEPS = "Installing dependencies"
    MIGRATE = "Running migrations"
    SEED = "Seeding homepage"
    CREATE_SUPERUSER = "Creating superuser"
    START_SERVER = "Starting server"


StepFunction = Callable[[SetupConfig], Path | None]
StepDefinition = tuple[SetupStep, StepFunction]


class SetupOrchestrator:
    """Orchestrates the full project setup flow.

    Owns ALL 8 steps — init command is a thin wrapper around this.
    """

    def __init__(self, project_path: Path, mode: ExecutionMode) -> None:
        self.project_path = project_path
        self.mode = mode

        # Initialize components (reused across setup steps)
        self.venv_manager = VenvManager()
        self.deps_manager = DependencyManager(venv_manager=self.venv_manager)
        self.django_executor: DjangoCommandExecutor | None = None

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
            self._show_progress(step_num, total_steps, step_name.value, "⏳")
            try:
                result = step_func(config)
                if step_name is SetupStep.CREATE_SUPERUSER and result:
                    credentials_path = result
                self._show_progress(step_num, total_steps, step_name.value, "✅")
            except SetupError:
                self._show_progress(step_num, total_steps, step_name.value, "❌")
                raise
            except Exception as e:
                # Wrap unexpected exceptions
                self._show_progress(step_num, total_steps, step_name.value, "❌")
                raise SetupError(f"Unexpected error in '{step_name.value}': {e}") from e

        return SetupResult(
            success=True,
            project_path=self.project_path,
            credentials_path=credentials_path,
            url=f"http://127.0.0.1:{config.port}/",
        )

    def _build_step_list(self, config: SetupConfig) -> list[StepDefinition]:
        """Build list of steps to execute based on config.

        Args:
            config: The setup configuration with flags and options.

        Returns:
            List of (step_name, step_function) tuples to execute.
        """
        # Always include scaffold and validate
        steps: list[StepDefinition] = [
            (SetupStep.SCAFFOLD, self._scaffold),
            (SetupStep.VALIDATE, self._validate),
        ]

        # Venv and deps (unless skipped)
        if not config.skip_venv:
            steps.append((SetupStep.CREATE_VENV, self._setup_venv))
            steps.append((SetupStep.INSTALL_DEPS, self._install_deps))

        # Quick mode stops here
        if config.quick:
            return steps

        # DB operations
        if not config.skip_migrations:
            steps.append((SetupStep.MIGRATE, self._migrate))

        if not config.skip_seed:
            steps.append((SetupStep.SEED, self._seed_content))

        if not config.skip_superuser:
            steps.append((SetupStep.CREATE_SUPERUSER, self._create_superuser))

        # Server (only if requested)
        if config.run_server:
            steps.append((SetupStep.START_SERVER, self._start_server))

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

    def _get_django_executor(self) -> DjangoCommandExecutor:
        """Get or create the Django command executor (lazy initialization).

        Returns:
            The DjangoCommandExecutor instance.
        """
        if self.django_executor is None:
            self.django_executor = DjangoCommandExecutor(self.project_path, self.mode)
        return self.django_executor

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
        db_manager = DatabaseManager(self._get_django_executor())
        db_manager.migrate()

    def _seed_content(self, config: SetupConfig) -> None:
        """Seed site content.

        Args:
            config: The setup configuration.
        """
        seeder = ContentSeeder(self._get_django_executor())
        if config.seed_site:
            seed_site = config.seed_site.lower()
            if seed_site == "sage-and-stone":
                seeder.seed_profile("sage-stone")
                return
            raise SetupError(f"Unknown seed site: {config.seed_site}")
        seeder.seed_homepage(preset=config.seed_preset)

    def _create_superuser(self, config: SetupConfig) -> Path:
        """Create superuser and return credentials path.

        Args:
            config: The setup configuration.

        Returns:
            Path to the credentials file (.env.local).
        """
        auth_manager = SuperuserManager(self._get_django_executor(), self.project_path)
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
        """
        scaffold_project(
            # project_path name should be the validated project slug from init.
            project_name=self.project_path.name,
            clients_dir=self.project_path.parent,
            theme_slug=config.theme_slug,
        )

    def _validate(self, config: SetupConfig) -> None:
        """Validate project structure.

        Args:
            config: The setup configuration.
        """
        validate_project_structure(self.project_path)

    def _start_server(self, config: SetupConfig) -> None:
        """Start development server in background.

        Args:
            config: The setup configuration.

        Note:
            If venv was skipped (skip_venv=True), falls back to sys.executable.
            This allows server start to work even without a virtualenv.
        """
        import sys

        # Use venv python if available, otherwise fall back to system python
        if self.venv_manager.exists(self.project_path):
            python = self.venv_manager.get_python_executable(self.project_path)
        else:
            python = Path(sys.executable)

        # Start server as background process
        subprocess.Popen(
            [str(python), "manage.py", "runserver", f"127.0.0.1:{config.port}"],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
