from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Ensure repo root is on sys.path so 'tests.utils' is importable
# when running `pytest cli/tests` in isolation (sliced runs).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pytest  # noqa: E402

from tests.utils.safe_cleanup import create_filesystem_sandbox  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture(autouse=True)
def cli_filesystem_sandbox(request, tmp_path_factory):
    repo_root = Path(__file__).resolve().parents[2]
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    sandbox = create_filesystem_sandbox(repo_root, tmp_base, request)
    request.node.cli_filesystem_sandbox = sandbox
    return sandbox


def snapshot_theme_state(theme_root: Path) -> dict[str, str]:
    """Return a stable snapshot of files under a theme directory."""
    snapshot: dict[str, str] = {}
    for path in sorted(theme_root.rglob("*")):
        if not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        snapshot[str(path.relative_to(theme_root))] = digest.hexdigest()
    return snapshot


@pytest.fixture
def isolated_theme_env(tmp_path: Path) -> dict[str, str]:
    output_root = tmp_path / "client-output"
    output_root.mkdir(parents=True, exist_ok=True)
    return {
        "SUM_THEME_PATH": str(_REPO_ROOT / "themes"),
        "SUM_BOILERPLATE_PATH": str(_REPO_ROOT / "boilerplate"),
        "SUM_CLIENT_OUTPUT_PATH": str(output_root),
        "SUM_TEST_MODE": "1",
    }


@pytest.fixture
def apply_isolated_theme_env(
    monkeypatch: pytest.MonkeyPatch, isolated_theme_env: dict[str, str]
) -> dict[str, str]:
    for key, value in isolated_theme_env.items():
        monkeypatch.setenv(key, value)
    return isolated_theme_env


@pytest.fixture
def theme_snapshot() -> Callable[[Path], dict[str, str]]:
    return snapshot_theme_state
