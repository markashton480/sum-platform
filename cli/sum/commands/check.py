from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import click

from cli.sum.utils.environment import ExecutionMode, detect_mode, resolve_project_path
from cli.sum.utils.validation import (
    ProjectValidator,
    ValidationResult,
    ValidationStatus,
)


def _resolve_project_path(project: str | None) -> Path:
    return resolve_project_path(project)


def _format_status(status: ValidationStatus) -> str:
    if status is ValidationStatus.OK:
        return "[OK]"
    if status is ValidationStatus.SKIP:
        return "[SKIP]"
    return "[FAIL]"


def _virtualenv_check(validator: ProjectValidator) -> ValidationResult:
    venv_result = validator.check_venv_exists()
    if venv_result.failed:
        return venv_result

    package_result = validator.check_packages_installed()
    if package_result.failed or package_result.skipped:
        return package_result

    return ValidationResult.ok(".venv exists with required packages")


def run_enhanced_checks(project_path: Path, mode: ExecutionMode) -> None:
    """Run enhanced validation checks."""
    validator = ProjectValidator(project_path, mode)

    checks: list[tuple[str, Callable[[], ValidationResult]]] = [
        ("Virtualenv", lambda: _virtualenv_check(validator)),
        ("Credentials", validator.check_env_local),
        ("Database", validator.check_migrations_applied),
        ("Homepage", validator.check_homepage_exists),
    ]

    has_failures = False

    for name, check_func in checks:
        result = check_func()
        status = _format_status(result.status)
        click.echo(f"{status} {name}: {result.message}")
        if result.failed and result.remediation:
            click.echo(f"      → {result.remediation}")
            has_failures = True
        elif result.failed:
            has_failures = True

    if has_failures:
        click.echo("\n❌ Some checks failed")
        sys.exit(1)

    click.echo("\n✅ All checks passed")


@click.command()
@click.argument("project", required=False)
def check(project: str | None) -> None:
    """Validate project setup."""
    try:
        project_path = _resolve_project_path(project)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    mode = detect_mode(project_path)
    run_enhanced_checks(project_path, mode)
