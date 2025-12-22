"""Test utilities package.

Provides shared fixtures and safe cleanup helpers for test isolation.
"""

from __future__ import annotations

from tests.utils.fixtures import (
    REPO_ROOT,
    assert_protected_paths_unchanged,
    get_protected_absolute_paths,
    get_protected_paths,
)
from tests.utils.safe_cleanup import (
    PROTECTED_PATHS,
    FilesystemSandbox,
    UnsafeDeleteError,
    create_filesystem_sandbox,
    register_cleanup,
    safe_rmtree,
)

__all__ = [
    # From fixtures
    "REPO_ROOT",
    "get_protected_paths",
    "get_protected_absolute_paths",
    "assert_protected_paths_unchanged",
    # From safe_cleanup
    "PROTECTED_PATHS",
    "UnsafeDeleteError",
    "safe_rmtree",
    "register_cleanup",
    "FilesystemSandbox",
    "create_filesystem_sandbox",
]
