from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from cli.sum.exceptions import DependencyError
from cli.sum.setup.deps import DependencyManager


def _create_requirements(project_path: Path) -> Path:
    requirements = project_path / "requirements.txt"
    requirements.write_text("Django==5.0\nWagtail==6.2\n", encoding="utf-8")
    return requirements


def test_install_runs_pip_with_venv_python(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / ".venv").mkdir()
    requirements = _create_requirements(project_path)

    captured: dict[str, object] = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    manager = DependencyManager()
    manager.install(project_path)

    assert captured["args"] == [
        str(project_path / ".venv" / "bin" / "python"),
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements),
    ]
    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["check"] is True
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True


def test_install_raises_dependency_error_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / ".venv").mkdir()
    _create_requirements(project_path)

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0], stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    manager = DependencyManager()
    with pytest.raises(DependencyError, match="pip install failed"):
        manager.install(project_path)


def test_install_raises_when_requirements_missing(tmp_path: Path) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / ".venv").mkdir()

    manager = DependencyManager()
    with pytest.raises(DependencyError, match="requirements.txt not found"):
        manager.install(project_path)


def test_install_raises_when_venv_missing(tmp_path: Path) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()
    _create_requirements(project_path)

    manager = DependencyManager()
    with pytest.raises(DependencyError, match="Virtualenv not found"):
        manager.install(project_path)


def test_verify_returns_true_when_packages_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / ".venv").mkdir()

    call_count = {"count": 0}

    def fake_run(*args, **kwargs):
        call_count["count"] += 1
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    manager = DependencyManager()
    assert manager.verify(project_path) is True
    assert call_count["count"] == 2


def test_verify_returns_false_when_package_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / ".venv").mkdir()

    def fake_run(args, **kwargs):
        if "import django" in args:
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="missing")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    manager = DependencyManager()
    assert manager.verify(project_path) is False


def test_verify_raises_when_venv_missing(tmp_path: Path) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()

    manager = DependencyManager()
    with pytest.raises(DependencyError, match="Virtualenv not found"):
        manager.verify(project_path)
