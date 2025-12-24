"""
Name: Theme A CSS Contract Tests
Path: tests/themes/test_theme_a_css_contract.py
Purpose: Guard Theme A Tailwind content coverage and custom utility presence.
Family: Themes / Toolchain
Dependencies: Django staticfiles, pathlib
"""

from __future__ import annotations

from pathlib import Path

from django.contrib.staticfiles import finders


def test_theme_a_css_is_discoverable() -> None:
    """Theme A compiled CSS should resolve via staticfiles."""
    css_path = finders.find("theme_a/css/main.css")
    assert css_path, "Theme A compiled CSS not found via staticfiles"
    assert Path(css_path).exists(), f"Theme A CSS missing at {css_path}"


def test_theme_a_css_contains_reference_sentinels() -> None:
    """Compiled CSS should include key utilities and palette outputs."""
    css_path = finders.find("theme_a/css/main.css")
    assert css_path, "Theme A compiled CSS not found via staticfiles"
    content = Path(css_path).read_text()

    sentinels = [
        ".no-scrollbar",
        ".reveal",
        ".hero--gradient-primary",
        ".bg-sage-linen",
        ".text-sage-terra",
    ]

    missing = [selector for selector in sentinels if selector not in content]
    assert not missing, f"Missing CSS sentinels: {', '.join(missing)}"


def test_tailwind_content_includes_reference_html() -> None:
    """Tailwind config must scan the compiled reference HTML."""
    repo_root = Path(__file__).resolve().parents[2]
    config_path = repo_root / "themes" / "theme_a" / "tailwind" / "tailwind.config.js"
    content = config_path.read_text()

    assert (
        "docs/dev/design/wireframes/sage-and-stone/compiled/*.html" in content
    ), "Tailwind content globs missing compiled reference HTML"
