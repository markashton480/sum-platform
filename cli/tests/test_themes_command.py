"""
Name: CLI Themes Command Tests
Path: cli/tests/test_themes_command.py
Purpose: Integration tests for sum themes list command
Family: sum_cli tests
Dependencies: sum_cli, sum_core.themes
"""
from __future__ import annotations

from sum_cli.commands.themes import run_themes_list


def test_themes_list_succeeds() -> None:
    """Test that sum themes list command runs successfully."""
    exit_code = run_themes_list()

    assert exit_code == 0


def test_themes_list_finds_theme_a(capsys) -> None:
    """Test that sum themes list outputs theme_a."""
    exit_code = run_themes_list()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "theme_a" in captured.out
    assert "Sage & Stone" in captured.out
