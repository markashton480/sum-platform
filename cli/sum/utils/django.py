from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from pathlib import Path

from cli.sum.exceptions import VenvError
from cli.sum.utils.environment import ExecutionMode, find_monorepo_root


class DjangoCommandExecutor:
    """Executes Django management commands."""

    def __init__(self, project_path: Path, mode: ExecutionMode) -> None:
        self.project_path = project_path
        self.mode = mode

    def run_command(
        self,
        command: list[str],
        env: Mapping[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Run a Django management command."""
        python = self._get_python_executable()
        full_command = [str(python), "manage.py", *command]

        command_env = os.environ.copy()
        if env:
            command_env.update(env)

        if self.mode is ExecutionMode.MONOREPO:
            core_path = self._get_core_path()
            existing = command_env.get("PYTHONPATH", "")
            if existing:
                command_env["PYTHONPATH"] = f"{existing}{os.pathsep}{core_path}"
            else:
                command_env["PYTHONPATH"] = str(core_path)

        return subprocess.run(
            full_command,
            cwd=self.project_path,
            env=command_env,
            capture_output=True,
            text=True,
            check=check,
        )

    def _get_python_executable(self) -> Path:
        """Return the project virtualenv's Python executable."""
        venv_python = self.project_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            raise VenvError(
                f"Virtualenv not found at {self.project_path / '.venv'}. "
                "Run 'sum init --full' or create manually with 'python -m venv .venv'"
            )
        return venv_python

    def _get_core_path(self) -> Path:
        """Get the monorepo core path for PYTHONPATH injection."""
        repo_root = find_monorepo_root(self.project_path)
        if repo_root is not None:
            return repo_root / "core"
        raise ValueError("Cannot determine core path - not in monorepo")
