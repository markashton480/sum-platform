from __future__ import annotations

import importlib

from click.testing import CliRunner

from cli.sum.commands.check import check
from cli.sum.utils.validation import ValidationResult

check_module = importlib.import_module("cli.sum.commands.check")


def test_check_command_reports_failures(monkeypatch) -> None:
    class DummyValidator:
        def __init__(self, project_path, mode) -> None:
            self.project_path = project_path
            self.mode = mode

        def check_venv_exists(self) -> ValidationResult:
            return ValidationResult.ok(".venv exists")

        def check_packages_installed(self) -> ValidationResult:
            return ValidationResult.ok("Required packages installed")

        def check_env_local(self) -> ValidationResult:
            return ValidationResult.skip("No .env.local found (superuser not created)")

        def check_migrations_applied(self) -> ValidationResult:
            return ValidationResult.ok("Migrations up to date")

        def check_homepage_exists(self) -> ValidationResult:
            return ValidationResult.fail(
                "Homepage not configured",
                "Run 'python manage.py seed_homepage'",
            )

    monkeypatch.setattr(check_module, "ProjectValidator", DummyValidator)

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("manage.py", "w", encoding="utf-8") as handle:
            handle.write("print('ok')\n")
        result = runner.invoke(check, [])

    assert result.exit_code == 1
    assert "[FAIL] Homepage: Homepage not configured" in result.output
    assert "Some checks failed" in result.output


def test_check_command_passes_with_skips(monkeypatch) -> None:
    class DummyValidator:
        def __init__(self, project_path, mode) -> None:
            self.project_path = project_path
            self.mode = mode

        def check_venv_exists(self) -> ValidationResult:
            return ValidationResult.ok(".venv exists")

        def check_packages_installed(self) -> ValidationResult:
            return ValidationResult.ok("Required packages installed")

        def check_env_local(self) -> ValidationResult:
            return ValidationResult.skip("No .env.local found (superuser not created)")

        def check_migrations_applied(self) -> ValidationResult:
            return ValidationResult.ok("Migrations up to date")

        def check_homepage_exists(self) -> ValidationResult:
            return ValidationResult.ok("Homepage set as site root")

    monkeypatch.setattr(check_module, "ProjectValidator", DummyValidator)

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("manage.py", "w", encoding="utf-8") as handle:
            handle.write("print('ok')\n")
        result = runner.invoke(check, [])

    assert result.exit_code == 0
    assert "[SKIP] Credentials: No .env.local found (superuser not created)" in (
        result.output
    )
    assert "All checks passed" in result.output
