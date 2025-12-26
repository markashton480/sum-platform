from __future__ import annotations

from pathlib import Path

import pytest

from cli.sum.utils.environment import (
    ExecutionMode,
    detect_mode,
    find_monorepo_root,
    get_clients_dir,
)


def test_find_monorepo_root_walks_upward(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    nested = repo_root / "a" / "b"
    (repo_root / "core").mkdir(parents=True)
    (repo_root / "boilerplate").mkdir()
    nested.mkdir(parents=True)

    assert find_monorepo_root(nested) == repo_root


def test_find_monorepo_root_handles_file_path(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    nested = repo_root / "a" / "b"
    (repo_root / "core").mkdir(parents=True)
    (repo_root / "boilerplate").mkdir()
    nested.mkdir(parents=True)
    marker = nested / "marker.txt"
    marker.write_text("ok", encoding="utf-8")

    assert find_monorepo_root(marker) == repo_root


def test_find_monorepo_root_defaults_to_cwd(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    (repo_root / "core").mkdir(parents=True)
    (repo_root / "boilerplate").mkdir()
    monkeypatch.chdir(repo_root)

    assert find_monorepo_root() == repo_root


def test_find_monorepo_root_returns_none_when_absent(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    assert find_monorepo_root(project_root) is None


def test_detect_mode_monorepo(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    (repo_root / "core").mkdir(parents=True)
    (repo_root / "boilerplate").mkdir()

    assert detect_mode(repo_root) is ExecutionMode.MONOREPO


def test_detect_mode_standalone(tmp_path: Path) -> None:
    standalone = tmp_path / "project"
    standalone.mkdir()

    assert detect_mode(standalone) is ExecutionMode.STANDALONE


def test_get_clients_dir_monorepo(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    clients_dir = repo_root / "clients"
    (repo_root / "core").mkdir(parents=True)
    (repo_root / "boilerplate").mkdir()
    clients_dir.mkdir()

    assert get_clients_dir(repo_root) == clients_dir


def test_get_clients_dir_standalone(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    clients_dir = project_root / "clients"
    clients_dir.mkdir(parents=True)

    assert get_clients_dir(project_root) == clients_dir


def test_get_clients_dir_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    with pytest.raises(FileNotFoundError, match="Cannot locate clients directory"):
        get_clients_dir(project_root)
