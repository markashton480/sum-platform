from __future__ import annotations

import importlib
import os
import subprocess
from pathlib import Path

from click.testing import CliRunner

from cli.sum.commands.run import run

run_module = importlib.import_module("cli.sum.commands.run")


def _create_monorepo_project(tmp_path: Path, name: str = "acme-kitchens") -> Path:
    repo_root = tmp_path / "repo"
    (repo_root / "core").mkdir(parents=True)
    (repo_root / "boilerplate").mkdir()
    clients_dir = repo_root / "clients"
    clients_dir.mkdir()

    project_path = clients_dir / name
    project_path.mkdir()
    (project_path / "manage.py").write_text("print('ok')\n", encoding="utf-8")

    venv_bin = project_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "python").write_text("", encoding="utf-8")
    return project_path


def test_run_command_starts_server(monkeypatch, tmp_path: Path) -> None:
    project_path = _create_monorepo_project(tmp_path)
    monkeypatch.chdir(project_path.parents[1])

    captured_cmd: list[str] | None = None
    captured_cwd: Path | None = None
    captured_env: dict[str, str] | None = None

    def fake_run(cmd, cwd=None, env=None, **kwargs):
        nonlocal captured_cmd, captured_cwd, captured_env
        captured_cmd = cmd
        captured_cwd = cwd
        captured_env = env
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setenv("PYTHONPATH", "/existing")
    monkeypatch.setattr(run_module.subprocess, "run", fake_run)
    monkeypatch.setattr(run_module, "find_available_port", lambda port: port)

    runner = CliRunner()
    result = runner.invoke(run, [project_path.name])

    assert result.exit_code == 0
    assert f"🚀 Starting {project_path.name}..." in result.output
    assert f"Using virtualenv: {project_path / '.venv'}" in result.output
    assert "Mode: monorepo" in result.output
    assert f"Python: {project_path / '.venv' / 'bin' / 'python'}" in result.output

    assert captured_cwd == project_path
    assert captured_cmd == [
        str(project_path / ".venv" / "bin" / "python"),
        "manage.py",
        "runserver",
        "127.0.0.1:8000",
    ]
    assert captured_env is not None
    expected_core = project_path.parents[1] / "core"
    assert captured_env["PYTHONPATH"] == f"/existing{os.pathsep}{expected_core}"


def test_run_command_warns_on_port_conflict(monkeypatch, tmp_path: Path) -> None:
    project_path = _create_monorepo_project(tmp_path, name="acme-gardens")
    monkeypatch.chdir(project_path.parents[1])

    captured_cmd: list[str] | None = None

    def fake_run(cmd, cwd=None, env=None, **kwargs):
        nonlocal captured_cmd
        captured_cmd = cmd
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(run_module.subprocess, "run", fake_run)
    monkeypatch.setattr(run_module, "find_available_port", lambda port: port + 1)

    runner = CliRunner()
    result = runner.invoke(run, [project_path.name, "--port", "8000"])

    assert result.exit_code == 0
    assert "Port 8000 in use, using 8001 instead" in result.output
    assert captured_cmd is not None
    assert captured_cmd[-1] == "127.0.0.1:8001"
