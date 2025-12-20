import os

import pytest


def test_no_legacy_theme_directories():
    """
    Guardrail: fail if any directory (other than allowed stubs) exists
    under core/sum_core/themes/.

    Themes must strictly live in repo-root `themes/` to be canonical.
    """
    from pathlib import Path

    import sum_core

    # Robustly find .../core/sum_core/themes
    # sum_core.__file__ is .../core/sum_core/__init__.py
    base_path = Path(sum_core.__file__).parent / "themes"

    if not os.path.exists(base_path):
        # If the directory doesn't exist at all, that's fine too,
        # though we expect __init__.py there.
        return

    # iterate contents
    for name in os.listdir(base_path):
        item_path = os.path.join(base_path, name)

        # We allow __init__.py, __pycache__, and maybe a README if strictly necessary.
        # We do NOT allow 'theme_a', 'theme_b', or any directory that looks like a theme.
        if os.path.isdir(item_path):
            if name == "__pycache__":
                continue

            # Any other directory is a violation
            pytest.fail(
                f"Legacy theme directory found: {item_path}\n"
                f"Themes must live under repo-root `themes/` (e.g. `themes/{name}`).\n"
                "Please delete this legacy copy."
            )
