from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is on sys.path so 'tests.utils' is importable
# when running `pytest cli/tests` in isolation (sliced runs).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pytest  # noqa: E402

from tests.utils.safe_cleanup import create_filesystem_sandbox  # noqa: E402


@pytest.fixture(autouse=True)
def cli_filesystem_sandbox(request, tmp_path_factory):
    repo_root = Path(__file__).resolve().parents[2]
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    sandbox = create_filesystem_sandbox(repo_root, tmp_base, request)
    request.node.cli_filesystem_sandbox = sandbox
    return sandbox
