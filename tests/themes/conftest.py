from __future__ import annotations

from pathlib import Path

import pytest

from tests.utils.safe_cleanup import create_filesystem_sandbox


@pytest.fixture(autouse=True)
def theme_filesystem_sandbox(request, tmp_path_factory):
    repo_root = Path(__file__).resolve().parents[2]
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    sandbox = create_filesystem_sandbox(repo_root, tmp_base, request)
    request.node.theme_filesystem_sandbox = sandbox
    return sandbox
