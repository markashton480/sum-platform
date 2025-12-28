from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from cli.sum.utils.environment import ExecutionMode
from cli.sum.utils.validation import ProjectValidator, ValidationStatus


def _create_project(tmp_path: Path) -> Path:
    project_path = tmp_path / "project"
    project_path.mkdir()
    return project_path


def _create_venv(project_path: Path) -> None:
    venv_bin = project_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "python").write_text("", encoding="utf-8")


def test_check_venv_exists(tmp_path: Path) -> None:
    project_path = _create_project(tmp_path)
    validator = ProjectValidator(project_path, ExecutionMode.STANDALONE)

    result = validator.check_venv_exists()
    assert result.status is ValidationStatus.FAIL
    assert result.remediation

    _create_venv(project_path)
    result = validator.check_venv_exists()
    assert result.status is ValidationStatus.OK


def test_check_packages_installed_skips_without_venv(tmp_path: Path) -> None:
    project_path = _create_project(tmp_path)
    validator = ProjectValidator(project_path, ExecutionMode.STANDALONE)

    result = validator.check_packages_installed()
    assert result.status is ValidationStatus.SKIP


def test_check_packages_installed_reports_missing_package(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_path = _create_project(tmp_path)
    _create_venv(project_path)
    validator = ProjectValidator(project_path, ExecutionMode.STANDALONE)

    calls = {"count": 0}

    def fake_run(cmd, capture_output=True, text=True):
        calls["count"] += 1
        return subprocess.CompletedProcess(cmd, 1 if calls["count"] == 2 else 0)

    monkeypatch.setattr("cli.sum.utils.validation.subprocess.run", fake_run)

    result = validator.check_packages_installed()
    assert result.status is ValidationStatus.FAIL
    assert "wagtail" in result.message
    assert result.remediation


def test_check_env_local(tmp_path: Path) -> None:
    project_path = _create_project(tmp_path)
    validator = ProjectValidator(project_path, ExecutionMode.STANDALONE)

    result = validator.check_env_local()
    assert result.status is ValidationStatus.SKIP

    env_local = project_path / ".env.local"
    env_local.write_text("DJANGO_SUPERUSER_USERNAME=admin\n", encoding="utf-8")
    result = validator.check_env_local()
    assert result.status is ValidationStatus.OK


def test_check_migrations_applied(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_path = _create_project(tmp_path)
    _create_venv(project_path)
    validator = ProjectValidator(project_path, ExecutionMode.STANDALONE)

    class DummyExecutor:
        def __init__(self, project_path: Path, mode: ExecutionMode) -> None:
            self.project_path = project_path
            self.mode = mode

        def run_command(self, command, check=False):
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("cli.sum.utils.validation.DjangoCommandExecutor", DummyExecutor)
    result = validator.check_migrations_applied()
    assert result.status is ValidationStatus.OK


def test_check_homepage_exists_reports_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_path = _create_project(tmp_path)
    _create_venv(project_path)
    validator = ProjectValidator(project_path, ExecutionMode.STANDALONE)

    class DummyExecutor:
        def __init__(self, project_path: Path, mode: ExecutionMode) -> None:
            self.project_path = project_path
            self.mode = mode

        def run_command(self, command, check=False):
            return subprocess.CompletedProcess(command, 0, stdout="blog", stderr="")

    monkeypatch.setattr("cli.sum.utils.validation.DjangoCommandExecutor", DummyExecutor)
    result = validator.check_homepage_exists()
    assert result.status is ValidationStatus.FAIL
    assert result.remediation
