"""
Name: Themes Command
Path: cli/sum_cli/commands/themes.py
Purpose: List available themes from the theme registry (spec v1)
Family: sum_cli commands
Dependencies: sum_cli.themes_registry
"""

from __future__ import annotations

import sys

from sum_cli.themes_registry import list_themes


def run_themes_list() -> int:
    """
    List all available themes.

    Returns:
        0 on success, 1 on failure
    """
    try:
        themes = list_themes()

        if not themes:
            print("No themes available.")
            return 0

        print("Available themes:")
        print()
        for theme in themes:
            print(f"  {theme.slug}")
            print(f"    Name: {theme.name}")
            print(f"    Description: {theme.description}")
            print(f"    Version: {theme.version}")
            print()

        return 0
    except Exception as e:
        print(f"[FAIL] Failed to list themes: {e}", file=sys.stderr)
        return 1
