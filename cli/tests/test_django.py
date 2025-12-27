from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from cli.sum.exceptions import VenvError
from cli.sum.utils.django import DjangoCommandExecutor
from cli.sum.utils.environment import ExecutionMode


def _create_venv_python(project_root: Path) -> Path:
    venv_python = project_root / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True, exist_ok=True)
    venv_python.write_text("", encoding="utf-8")
    return venv_python


def test_executor_initializes(tmp_path: Path) -> None:
    executor = DjangoCommandExecutor(tmp_path, ExecutionMode.STANDALONE)
    assert executor.project_path == tmp_path
    assert executor.mode is ExecutionMode.STANDALONE


def test_get_python_executable_raises_when_missing(tmp_path: Path) -> None:
    executor = DjangoCommandExecutor(tmp_path, ExecutionMode.STANDALONE)

    with pytest.raises(VenvError, match="Virtualenv not found"):
        executor._get_python_executable()


def test_run_command_monorepo_appends_core_path_and_env(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path / "repo"
    project_root = repo_root / "clients" / "demo"
    (repo_root / "core").mkdir(parents=True)
    (repo_root / "boilerplate").mkdir()
    project_root.mkdir(parents=True)
    venv_python = _create_venv_python(project_root)

    monkeypatch.setenv("PYTHONPATH", "existing")

    captured: dict[str, object] = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    executor = DjangoCommandExecutor(project_root, ExecutionMode.MONOREPO)
    result = executor.run_command(
        ["migrate", "--noinput"],
        env={"DJANGO_SETTINGS_MODULE": "demo.settings"},
        check=False,
    )

    assert result.returncode == 0
    assert captured["args"] == [
        str(venv_python),
        "manage.py",
        "migrate",
        "--noinput",
    ]
    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["cwd"] == project_root
    assert kwargs["check"] is False
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True

    env = kwargs["env"]
    assert isinstance(env, dict)
    assert env["DJANGO_SETTINGS_MODULE"] == "demo.settings"
    core_path = repo_root / "core"
    assert env["PYTHONPATH"] == f"existing{os.pathsep}{core_path}"


def test_run_command_standalone_preserves_pythonpath(
    tmp_path: Path, monkeypatch
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    _create_venv_python(project_root)

    monkeypatch.setenv("PYTHONPATH", "existing")

    captured: dict[str, object] = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    executor = DjangoCommandExecutor(project_root, ExecutionMode.STANDALONE)
    executor.run_command(["check"])

    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    env = kwargs["env"]
    assert isinstance(env, dict)
    assert env["PYTHONPATH"] == "existing"
