"""
Name: CLI Safety Regression Tests
Path: cli/tests/test_cli_safety.py
Purpose: Explicit regression tests for CLI safety boundaries and immutability
Family: sum_cli tests
Dependencies: sum_cli
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sum_cli.commands.init import run_init

from tests.utils.safe_cleanup import UnsafeDeleteError

pytestmark = pytest.mark.regression


def _assert_output_boundary(project_root: Path, output_root: Path) -> None:
    assert project_root.is_relative_to(
        output_root
    ), "Project must be created under SUM_CLIENT_OUTPUT_PATH"


def _assert_source_theme_present(theme_root: Path) -> None:
    assert theme_root.exists(), "Source theme directory must exist"
    assert (theme_root / "theme.json").exists(), "Source theme.json must exist"


def test_init_output_boundary_and_source_immutability(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env, theme_snapshot
) -> None:
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    boilerplate_root = Path(isolated_theme_env["SUM_BOILERPLATE_PATH"])

    theme_before = theme_snapshot(theme_root)
    boilerplate_before = theme_snapshot(boilerplate_root)

    project_name = "cli-safety-init"
    monkeypatch.chdir(output_root)
    assert run_init(project_name, theme_slug="theme_a") == 0

    project_root = output_root / "clients" / project_name
    _assert_output_boundary(project_root, output_root)
    assert project_root.exists()
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == theme_before
    assert theme_snapshot(boilerplate_root) == boilerplate_before


def test_cleanup_guard_refuses_source_paths(request, isolated_theme_env) -> None:
    sandbox = request.node.cli_filesystem_sandbox
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    boilerplate_root = Path(isolated_theme_env["SUM_BOILERPLATE_PATH"])

    with pytest.raises(UnsafeDeleteError):
        sandbox.safe_rmtree(theme_root)
    with pytest.raises(UnsafeDeleteError):
        sandbox.safe_rmtree(boilerplate_root)


def test_repeated_inits_do_not_corrupt_sources(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env, theme_snapshot
) -> None:
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    boilerplate_root = Path(isolated_theme_env["SUM_BOILERPLATE_PATH"])

    theme_before = theme_snapshot(theme_root)
    boilerplate_before = theme_snapshot(boilerplate_root)

    monkeypatch.chdir(output_root)
    first_project = "cli-safety-repeat-1"
    second_project = "cli-safety-repeat-2"

    assert run_init(first_project, theme_slug="theme_a") == 0
    assert run_init(second_project, theme_slug="theme_a") == 0

    first_root = output_root / "clients" / first_project
    second_root = output_root / "clients" / second_project

    _assert_output_boundary(first_root, output_root)
    _assert_output_boundary(second_root, output_root)
    assert first_root.exists()
    assert second_root.exists()
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == theme_before
    assert theme_snapshot(boilerplate_root) == boilerplate_before
