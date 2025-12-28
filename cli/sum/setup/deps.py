from __future__ import annotations

import subprocess
from pathlib import Path

from cli.sum.exceptions import DependencyError
from cli.sum.setup.venv import VenvManager
from cli.sum.utils.output import OutputFormatter


class DependencyManager:
    """Manage dependency installation for CLI projects."""

    def __init__(self, venv_manager: VenvManager | None = None) -> None:
        self.venv_manager = venv_manager or VenvManager()

    def install(self, project_path: Path) -> None:
        """Install dependencies from requirements.txt using the venv pip."""
        requirements = project_path / "requirements.txt"
        OutputFormatter.progress(1, 1, f"Installing dependencies for {project_path}")

        if not requirements.exists():
            OutputFormatter.error(f"requirements.txt not found at {requirements}")
            raise DependencyError(f"requirements.txt not found at {requirements}")

        if not self.venv_manager.exists(project_path):
            OutputFormatter.error("Virtualenv not found for dependency install")
            raise DependencyError(f"Virtualenv not found at {project_path / '.venv'}")

        python = self.venv_manager.get_python_executable(project_path)
        try:
            subprocess.run(
                [str(python), "-m", "pip", "install", "-r", str(requirements)],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            OutputFormatter.error("Virtualenv python not found for pip install")
            raise DependencyError(f"Virtualenv python not found at {python}") from exc
        except subprocess.CalledProcessError as exc:
            OutputFormatter.error("pip install failed")
            details = exc.stderr or exc.stdout or "Unknown error"
            raise DependencyError(f"pip install failed: {details}") from exc

        OutputFormatter.success("Dependencies installed")

    def verify(self, project_path: Path) -> bool:
        """Verify key dependencies are installed in the virtualenv."""
        OutputFormatter.progress(1, 1, f"Verifying dependencies for {project_path}")

        if not self.venv_manager.exists(project_path):
            OutputFormatter.error("Virtualenv not found for dependency verification")
            raise DependencyError(f"Virtualenv not found at {project_path / '.venv'}")

        python = self.venv_manager.get_python_executable(project_path)
        required = ["django", "wagtail"]
        missing: list[str] = []
        for package in required:
            result = subprocess.run(
                [str(python), "-c", f"import {package}"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                missing.append(package)

        if missing:
            OutputFormatter.error(f"Missing packages: {', '.join(sorted(missing))}")
            return False

        OutputFormatter.success("Dependencies verified")
        return True
