from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from cli.sum.exceptions import VenvError
from cli.sum.setup.venv import VenvManager


def test_create_idempotent_returns_existing_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    venv_path = tmp_path / ".venv"
    venv_path.mkdir()

    called = {"count": 0}

    def fake_run(*args, **kwargs):
        called["count"] += 1
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    manager = VenvManager()
    result = manager.create(tmp_path)

    assert result == venv_path
    assert called["count"] == 0


def test_create_runs_venv_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    manager = VenvManager()
    result = manager.create(tmp_path)

    assert result == tmp_path / ".venv"
    assert captured["args"] == [
        sys.executable,
        "-m",
        "venv",
        str(tmp_path / ".venv"),
    ]
    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["check"] is True
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True


def test_create_raises_venv_error_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0], stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    manager = VenvManager()
    with pytest.raises(VenvError, match="Failed to create virtualenv"):
        manager.create(tmp_path)


def test_get_python_executable_returns_expected_path(tmp_path: Path) -> None:
    manager = VenvManager()
    python = manager.get_python_executable(tmp_path)
    assert python == tmp_path / ".venv" / "bin" / "python"


def test_is_activated_detects_virtual_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = VenvManager()
    monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / ".venv"))
    assert manager.is_activated() is True


def test_exists_returns_true_when_directory_present(tmp_path: Path) -> None:
    manager = VenvManager()
    (tmp_path / ".venv").mkdir()
    assert manager.exists(tmp_path) is True


@pytest.mark.slow
def test_create_integration_creates_real_venv(tmp_path: Path) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()

    manager = VenvManager()
    venv_path = manager.create(project_path)

    assert venv_path.is_dir()
    assert manager.get_python_executable(project_path).exists()
