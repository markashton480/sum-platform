from __future__ import annotations

from enum import Enum
from pathlib import Path


class ExecutionMode(str, Enum):
    MONOREPO = "monorepo"
    STANDALONE = "standalone"


def _normalize_start_path(start_path: Path | None) -> Path:
    """Return a directory path from a file path or default to the current cwd."""
    path = start_path or Path.cwd()
    if path.is_file():
        return path.parent
    return path


def find_monorepo_root(start_path: Path | None = None) -> Path | None:
    """Walk upward to find monorepo root (contains core/ and boilerplate/)."""
    search_path = _normalize_start_path(start_path)

    for parent in [search_path, *search_path.parents]:
        if (parent / "core").is_dir() and (parent / "boilerplate").is_dir():
            return parent

    return None


def detect_mode(path: Path | None = None) -> ExecutionMode:
    """Detect execution mode based on directory structure."""
    if find_monorepo_root(path) is not None:
        return ExecutionMode.MONOREPO
    return ExecutionMode.STANDALONE


def get_clients_dir(start_path: Path | None = None) -> Path:
    """Resolve the clients directory for monorepo or standalone mode."""
    repo_root = find_monorepo_root(start_path)
    if repo_root is not None:
        return repo_root / "clients"

    search_path = _normalize_start_path(start_path)
    standalone_clients = search_path / "clients"
    if standalone_clients.is_dir():
        return standalone_clients

    raise FileNotFoundError(
        "Cannot locate clients directory. Ensure you're running inside the monorepo "
        "or from a standalone project root that contains a 'clients' folder."
    )
