from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tests.utils.safe_cleanup import UnsafeDeleteError, safe_rmtree

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_safe_rmtree_deletes_tmp_tree(tmp_path_factory) -> None:
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    target = tmp_path_factory.mktemp("safe-delete")
    (target / "marker.txt").write_text("x", encoding="utf-8")

    safe_rmtree(target, repo_root=REPO_ROOT, tmp_base=tmp_base)

    assert not target.exists()


def test_safe_rmtree_rejects_repo_root(tmp_path_factory) -> None:
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()

    with pytest.raises(UnsafeDeleteError, match="repo root"):
        safe_rmtree(REPO_ROOT, repo_root=REPO_ROOT, tmp_base=tmp_base)


def test_safe_rmtree_rejects_protected_dirs(tmp_path_factory) -> None:
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    protected_root = REPO_ROOT / "themes" / "theme_a"

    with pytest.raises(UnsafeDeleteError, match="protected directory"):
        safe_rmtree(protected_root, repo_root=REPO_ROOT, tmp_base=tmp_base)


def test_safe_rmtree_rejects_outside_tmp_base(tmp_path_factory) -> None:
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    outside = tmp_base.parent / "outside-sandbox"
    outside.mkdir(exist_ok=True, parents=True)

    try:
        with pytest.raises(UnsafeDeleteError, match="outside pytest tmp tree"):
            safe_rmtree(outside, repo_root=REPO_ROOT, tmp_base=tmp_base)
    finally:
        shutil.rmtree(outside, ignore_errors=True)


def test_safe_rmtree_rejects_git_fragments(tmp_path_factory) -> None:
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    git_dir = tmp_base / ".git"
    git_dir.mkdir(exist_ok=True)

    try:
        with pytest.raises(UnsafeDeleteError, match=r"containing \.git"):
            safe_rmtree(git_dir, repo_root=REPO_ROOT, tmp_base=tmp_base)
    finally:
        shutil.rmtree(git_dir, ignore_errors=True)
