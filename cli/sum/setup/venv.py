from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from cli.sum.exceptions import VenvError
from cli.sum.utils.output import OutputFormatter


class VenvManager:
    """Manage Python virtual environments for CLI projects."""

    def create(self, project_path: Path) -> Path:
        """Create a .venv in the project path if it does not exist."""
        venv_path = project_path / ".venv"
        if venv_path.is_dir():
            OutputFormatter.info(f"Virtualenv already exists at {venv_path}")
            return venv_path

        OutputFormatter.progress(1, 1, f"Creating virtualenv at {venv_path}")
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            OutputFormatter.error("Failed to create virtualenv")
            raise VenvError(
                f"Failed to create virtualenv at {venv_path}: {exc.stderr}"
            ) from exc

        OutputFormatter.success(f"Virtualenv created at {venv_path}")
        return venv_path

    def get_python_executable(self, project_path: Path) -> Path:
        """Return the Python executable inside the project virtualenv."""
        python_path = project_path / ".venv" / "bin" / "python"
        return python_path

    def is_activated(self) -> bool:
        """Return True when running inside a virtualenv."""
        active = bool(os.environ.get("VIRTUAL_ENV")) or sys.prefix != sys.base_prefix
        return active

    def exists(self, project_path: Path) -> bool:
        """Return True when the project virtualenv exists."""
        venv_path = project_path / ".venv"
        exists = venv_path.is_dir()
        return exists
