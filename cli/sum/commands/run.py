from __future__ import annotations

import os
import socket
import subprocess
from pathlib import Path

import click

from cli.sum.setup.venv import VenvManager
from cli.sum.utils.environment import (
    ExecutionMode,
    detect_mode,
    find_monorepo_root,
    get_clients_dir,
)


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError(
        f"No available ports found in range {start_port}-{start_port + max_attempts - 1}"
    )


def resolve_project_path(project: str | None) -> Path:
    """Resolve project path from name or current directory."""
    if project:
        try:
            clients_dir = get_clients_dir()
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc
        project_path = clients_dir / project
        if project_path.exists():
            return project_path
        raise click.ClickException(f"Project not found: {project}")

    cwd = Path.cwd()
    if (cwd / "manage.py").exists():
        return cwd

    raise click.ClickException(
        "Not in a project directory. Either cd into a project or specify project name."
    )


@click.command()
@click.argument("project", required=False)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Development server port (default: 8000)",
)
def run(project: str | None, port: int) -> None:
    """Start development server for a project."""
    project_path = resolve_project_path(project)
    project_name = project_path.name
    mode = detect_mode(project_path)

    venv_manager = VenvManager()
    if not venv_manager.exists(project_path):
        raise click.ClickException(
            f"Virtualenv not found at {project_path / '.venv'}. "
            "Run 'sum init --full' or create manually."
        )

    python_exe = venv_manager.get_python_executable(project_path)

    try:
        actual_port = find_available_port(port)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    if actual_port != port:
        click.echo(f"⚠️  Port {port} in use, using {actual_port} instead")

    click.echo(f"🚀 Starting {project_name}...")
    click.echo()
    click.echo(f"Using virtualenv: {project_path / '.venv'}")
    click.echo(f"Mode: {mode.value}")
    click.echo(f"Python: {python_exe}")
    click.echo()

    env = os.environ.copy()
    if mode is ExecutionMode.MONOREPO:
        repo_root = find_monorepo_root(project_path)
        if repo_root is not None:
            core_path = repo_root / "core"
            existing = env.get("PYTHONPATH", "")
            if existing:
                env["PYTHONPATH"] = f"{core_path}{os.pathsep}{existing}"
            else:
                env["PYTHONPATH"] = str(core_path)

    try:
        subprocess.run(
            [str(python_exe), "manage.py", "runserver", f"127.0.0.1:{actual_port}"],
            cwd=project_path,
            env=env,
        )
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped")
