"""Shared test fixtures and path utilities.

This module provides a single source of truth for:
- Repository root path resolution
- Protected paths list (synchronized with safe_cleanup.py)
- Assertion helpers for verifying protected paths remain unchanged
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tests.utils.safe_cleanup import PROTECTED_PATHS

if TYPE_CHECKING:
    from collections.abc import Callable

# Single source of truth for repository root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]


def get_protected_paths() -> tuple[str, ...]:
    """Return canonical list of protected repo directory names.

    These are directories that tests must never modify or delete.
    Re-exports from safe_cleanup for consistency.
    """
    return PROTECTED_PATHS


def get_protected_absolute_paths() -> tuple[Path, ...]:
    """Return absolute paths to all protected directories."""
    return tuple(REPO_ROOT / name for name in PROTECTED_PATHS)


def assert_protected_paths_unchanged(
    *,
    baseline_mtimes: dict[Path, float | None] | None = None,
    on_error: Callable[[str], None] | None = None,
) -> dict[Path, float | None]:
    """Check that protected paths haven't been modified.

    Args:
        baseline_mtimes: Optional dict of {path: mtime} from a previous call.
            If provided, compares current mtimes against baseline.
            If None, returns current mtimes for use as a baseline.
        on_error: Optional callback invoked with error message if mismatch found.
            Defaults to raising AssertionError.

    Returns:
        Current mtimes dict (for chaining or baseline capture).

    Raises:
        AssertionError: If baseline provided and any mtime changed (and no on_error).
    """
    current_mtimes: dict[Path, float | None] = {}

    for protected_path in get_protected_absolute_paths():
        if protected_path.exists():
            current_mtimes[protected_path] = protected_path.stat().st_mtime
        else:
            current_mtimes[protected_path] = None

    if baseline_mtimes is not None:
        for path, baseline_mtime in baseline_mtimes.items():
            current_mtime = current_mtimes.get(path)
            if current_mtime != baseline_mtime:
                error_msg = (
                    f"Protected path modified: {path}\n"
                    f"  baseline mtime: {baseline_mtime}\n"
                    f"  current mtime:  {current_mtime}"
                )
                if on_error:
                    on_error(error_msg)
                else:
                    raise AssertionError(error_msg)

    return current_mtimes
