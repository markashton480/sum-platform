"""
Name: Test Project Theme Wiring Tests
Path: tests/themes/test_test_project_theme_wiring.py
Purpose: Guardrails ensuring the test_project harness is wired to prefer repo-root themes/ per Theme Architecture Spec v1
Family: Themes / Harness wiring
Dependencies: pathlib, pytest
"""

from __future__ import annotations

from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]


def test_repo_root_theme_a_exists() -> None:
    """Repo-root themes/theme_a must exist (canonical source-of-truth)."""
    theme_root = repo_root / "themes" / "theme_a"

    assert (theme_root / "theme.json").is_file()
    assert (theme_root / "templates").is_dir()
    assert (theme_root / "static").is_dir()


def test_test_project_candidates_include_repo_root_theme_a() -> None:
    """
    test_project settings should include repo-root themes/theme_a in its candidates so that
    local dev (non-pytest) prefers canonical repo themes without copying into theme/active.
    """
    expected_templates = repo_root / "themes" / "theme_a" / "templates"
    expected_static = repo_root / "themes" / "theme_a" / "static"

    settings_py = (
        repo_root
        / "core"
        / "sum_core"
        / "test_project"
        / "test_project"
        / "settings.py"
    )
    settings_text = settings_py.read_text(encoding="utf-8")

    # Assert the harness wiring *includes* repo-root themes as candidates.
    assert 'REPO_ROOT / "themes" / "theme_a" / "templates"' in settings_text
    assert 'REPO_ROOT / "themes" / "theme_a" / "static"' in settings_text

    # Also assert those canonical directories exist in this repo checkout.
    assert expected_templates.is_dir()
    assert expected_static.is_dir()
