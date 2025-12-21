"""Safe filesystem helpers for pytest sandboxes."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

PROTECTED_PATHS = (
    "themes",
    "boilerplate",
    "core",
    "cli",
    "docs",
    "scripts",
    "infrastructure",
    "clients",
    "design",
    "media",
)


class UnsafeDeleteError(RuntimeError):
    """Raised when a cleanup targets a path we refuse to remove."""


def _resolve_path(value: Path | str) -> Path:
    return Path(value).resolve()


def safe_rmtree(path: Path | str, repo_root: Path, tmp_base: Path) -> None:
    """Remove `path` only when it is safely within the pytest temp tree."""
    resolved_path = _resolve_path(path)
    repo_root_path = _resolve_path(repo_root)
    tmp_root = _resolve_path(tmp_base)

    if resolved_path == repo_root_path:
        raise UnsafeDeleteError(f"Refusing to delete repo root: {resolved_path}")

    if ".git" in resolved_path.parts:
        raise UnsafeDeleteError(
            f"Refusing to delete path containing .git: {resolved_path}"
        )

    if resolved_path.is_relative_to(repo_root_path):
        for protected_name in PROTECTED_PATHS:
            protected_root = repo_root_path / protected_name
            if resolved_path == protected_root or resolved_path.is_relative_to(
                protected_root
            ):
                raise UnsafeDeleteError(
                    "Refusing to delete protected directory: "
                    f"{protected_root} (target={resolved_path})"
                )

    if not resolved_path.is_relative_to(tmp_root):
        raise UnsafeDeleteError(
            "Refusing to delete outside pytest tmp tree: "
            f"{resolved_path} (tmp_base={tmp_root})"
        )

    shutil.rmtree(resolved_path, ignore_errors=False)


def register_cleanup(
    request: pytest.FixtureRequest,
    target: Path | str,
    *,
    repo_root: Path,
    tmp_base: Path,
) -> None:
    """Register a cleanup that uses `safe_rmtree` when the test finishes."""

    def _cleanup() -> None:
        safe_rmtree(target, repo_root=repo_root, tmp_base=tmp_base)

    request.addfinalizer(_cleanup)


class FilesystemSandbox:
    """Convenience wrapper that keeps the repo root and tmp base handy."""

    def __init__(
        self, repo_root: Path, tmp_base: Path, request: pytest.FixtureRequest
    ) -> None:
        self.repo_root = _resolve_path(repo_root)
        self.tmp_base = _resolve_path(tmp_base)
        self._request = request

    def safe_rmtree(self, target: Path | str) -> None:
        safe_rmtree(target, repo_root=self.repo_root, tmp_base=self.tmp_base)

    def register_cleanup(self, target: Path | str) -> None:
        register_cleanup(
            self._request,
            target,
            repo_root=self.repo_root,
            tmp_base=self.tmp_base,
        )


def create_filesystem_sandbox(
    repo_root: Path, tmp_base: Path, request: pytest.FixtureRequest
) -> FilesystemSandbox:
    """Return a sandbox instance configured for the current pytest run."""

    return FilesystemSandbox(repo_root, tmp_base, request)
