from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from cli.sum.setup.venv import VenvManager
from cli.sum.utils.django import DjangoCommandExecutor
from cli.sum.utils.environment import ExecutionMode


class ValidationStatus(str, Enum):
    OK = "ok"
    FAIL = "fail"
    SKIP = "skip"


@dataclass(frozen=True)
class ValidationResult:
    status: ValidationStatus
    message: str
    remediation: str | None = None

    @property
    def passed(self) -> bool:
        return self.status is ValidationStatus.OK

    @property
    def failed(self) -> bool:
        return self.status is ValidationStatus.FAIL

    @property
    def skipped(self) -> bool:
        return self.status is ValidationStatus.SKIP

    @classmethod
    def ok(cls, message: str) -> ValidationResult:
        return cls(ValidationStatus.OK, message)

    @classmethod
    def fail(cls, message: str, remediation: str | None = None) -> ValidationResult:
        return cls(ValidationStatus.FAIL, message, remediation)

    @classmethod
    def skip(cls, message: str) -> ValidationResult:
        return cls(ValidationStatus.SKIP, message)


class ProjectValidator:
    """Validates project setup state."""

    def __init__(self, project_path: Path, mode: ExecutionMode) -> None:
        self.project_path = project_path
        self.mode = mode
        self.venv_manager = VenvManager()

    def check_venv_exists(self) -> ValidationResult:
        """Check if virtualenv exists."""
        venv_path = self.project_path / ".venv"
        if venv_path.is_dir():
            return ValidationResult.ok(".venv exists")
        return ValidationResult.fail(
            ".venv not found",
            "Run 'sum init --full' or 'python -m venv .venv'",
        )

    def check_packages_installed(self) -> ValidationResult:
        """Check if key packages are installed in venv."""
        if not self.venv_manager.exists(self.project_path):
            return ValidationResult.skip("Virtualenv missing; skipping package checks")

        python = self.venv_manager.get_python_executable(self.project_path)
        for package in ("django", "wagtail"):
            result = subprocess.run(
                [str(python), "-c", f"import {package}"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return ValidationResult.fail(
                    f"Package '{package}' not installed",
                    "Run 'pip install -r requirements.txt'",
                )

        return ValidationResult.ok("Required packages installed")

    def check_env_local(self) -> ValidationResult:
        """Check if .env.local exists."""
        env_local = self.project_path / ".env.local"
        if env_local.is_file():
            return ValidationResult.ok(".env.local found")
        return ValidationResult.skip("No .env.local found (superuser not created)")

    def check_migrations_applied(self) -> ValidationResult:
        """Check if migrations are up to date."""
        if not self.venv_manager.exists(self.project_path):
            return ValidationResult.skip("Virtualenv missing; skipping migration check")
        try:
            executor = DjangoCommandExecutor(self.project_path, self.mode)
            result = executor.run_command(["migrate", "--check"], check=False)
        except Exception as exc:
            return ValidationResult.fail(f"Migration check failed: {exc}")

        if result.returncode == 0:
            return ValidationResult.ok("Migrations up to date")
        return ValidationResult.fail(
            "Pending migrations",
            "Run 'python manage.py migrate'",
        )

    def check_homepage_exists(self) -> ValidationResult:
        """Check if homepage is set as site root."""
        if not self.venv_manager.exists(self.project_path):
            return ValidationResult.skip("Virtualenv missing; skipping homepage check")
        try:
            executor = DjangoCommandExecutor(self.project_path, self.mode)
            result = executor.run_command(
                [
                    "shell",
                    "-c",
                    "from wagtail.models import Site; "
                    "site = Site.objects.get(is_default_site=True); "
                    "print(site.root_page.slug)",
                ],
                check=False,
            )
        except Exception as exc:
            return ValidationResult.fail(f"Homepage check failed: {exc}")

        if result.returncode == 0 and result.stdout.strip() == "home":
            return ValidationResult.ok("Homepage set as site root")
        return ValidationResult.fail(
            "Homepage not configured",
            "Run 'python manage.py seed_homepage'",
        )
