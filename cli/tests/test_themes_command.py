"""
Name: CLI Themes Command Tests
Path: cli/tests/test_themes_command.py
Purpose: Integration tests for sum themes list command
Family: sum_cli tests
Dependencies: sum_cli
"""

from __future__ import annotations

from pathlib import Path

from sum_cli.commands.themes import run_themes_list


def test_themes_list_succeeds(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env
) -> None:
    """Test that sum themes list command runs successfully."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    monkeypatch.chdir(output_root)
    exit_code = run_themes_list()

    assert exit_code == 0


def test_themes_list_finds_theme_a(
    monkeypatch, capsys, isolated_theme_env, apply_isolated_theme_env
) -> None:
    """Test that sum themes list outputs theme_a."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    monkeypatch.chdir(output_root)
    exit_code = run_themes_list()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "theme_a" in captured.out
    assert "Sage & Stone" in captured.out
