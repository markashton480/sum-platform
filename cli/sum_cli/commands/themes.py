"""
Name: Themes Command
Path: cli/sum_cli/commands/themes.py
Purpose: List available themes from sum_core
Family: sum_cli commands
Dependencies: sum_core.themes
"""

from __future__ import annotations

import sys


def run_themes_list() -> int:
    """
    List all available themes from sum_core.

    Returns:
        0 on success, 1 on failure
    """
    try:
        # Import here to allow CLI to work in standalone mode
        # (won't fail immediately if sum_core not installed)
        import sum_core.themes
    except ImportError:
        print("[FAIL] sum_core is not installed or not importable.", file=sys.stderr)
        print(
            "       Install sum_core: pip install -e ./core",
            file=sys.stderr,
        )
        return 1

    try:
        themes = sum_core.themes.list_themes()

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
