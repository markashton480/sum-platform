"""
Name: Theme Discovery Tests
Path: tests/themes/test_theme_discovery.py
Purpose: Unit tests for theme discovery and validation (Theme Architecture Spec v1)
Family: Platform tests
Dependencies: sum_cli.themes_registry, pytest
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.utils import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "cli"))

from sum_cli.themes_registry import (  # noqa: E402
    ThemeManifest,
    ThemeNotFoundError,
    ThemeValidationError,
    discover_themes,
    get_theme,
    list_themes,
    resolve_theme_dir,
)


def test_discover_themes_finds_theme_a(monkeypatch) -> None:
    """Test that theme discovery finds theme_a from repo-root themes/."""
    monkeypatch.chdir(REPO_ROOT)
    themes = discover_themes(REPO_ROOT / "themes")

    assert len(themes) >= 1
    theme_slugs = [t.slug for t in themes]
    assert "theme_a" in theme_slugs


def test_get_theme_returns_valid_manifest(monkeypatch) -> None:
    """Test that get_theme returns a valid ThemeManifest for theme_a."""
    monkeypatch.chdir(REPO_ROOT)
    theme = get_theme("theme_a")

    assert isinstance(theme, ThemeManifest)
    assert theme.slug == "theme_a"
    assert theme.name == "Sage & Stone"
    assert theme.description
    assert theme.version == "1.0.0"


def test_get_theme_raises_on_invalid_slug(monkeypatch) -> None:
    """Test that get_theme raises ThemeNotFoundError for invalid slugs."""
    monkeypatch.chdir(REPO_ROOT)
    with pytest.raises(ThemeNotFoundError, match="not found"):
        get_theme("nonexistent_theme")


def test_list_themes_returns_sorted(monkeypatch) -> None:
    """Test that list_themes returns themes sorted by slug."""
    monkeypatch.chdir(REPO_ROOT)
    themes = list_themes()

    assert len(themes) >= 1
    slugs = [t.slug for t in themes]
    assert slugs == sorted(slugs)


def test_theme_template_dir_exists(monkeypatch) -> None:
    """Theme A templates/ directory must exist."""
    monkeypatch.chdir(REPO_ROOT)
    theme_dir = resolve_theme_dir("theme_a")
    template_dir = theme_dir / "templates"

    assert isinstance(template_dir, Path)
    assert template_dir.exists()
    assert template_dir.is_dir()
    assert template_dir.name == "templates"


def test_theme_static_dir_exists(monkeypatch) -> None:
    """Theme A static/ directory must exist."""
    monkeypatch.chdir(REPO_ROOT)
    theme_dir = resolve_theme_dir("theme_a")
    static_dir = theme_dir / "static"

    assert isinstance(static_dir, Path)
    assert static_dir.exists()
    assert static_dir.is_dir()
    assert static_dir.name == "static"


def test_theme_manifest_validation() -> None:
    """Test ThemeManifest validation logic."""
    # Valid manifest
    valid = ThemeManifest(
        slug="test",
        name="Test Theme",
        description="A test theme",
        version="1.0.0",
    )
    valid.validate()  # Should not raise

    # Empty slug
    invalid_slug = ThemeManifest(
        slug="", name="Test", description="Desc", version="1.0.0"
    )
    with pytest.raises(ValueError, match="slug cannot be empty"):
        invalid_slug.validate()

    # Empty name
    invalid_name = ThemeManifest(
        slug="test", name="", description="Desc", version="1.0.0"
    )
    with pytest.raises(ValueError, match="name cannot be empty"):
        invalid_name.validate()

    # Empty version
    invalid_version = ThemeManifest(
        slug="test", name="Test", description="Desc", version=""
    )
    with pytest.raises(ValueError, match="version cannot be empty"):
        invalid_version.validate()


def test_theme_manifest_from_dict() -> None:
    """Test ThemeManifest creation from dictionary."""
    data = {
        "slug": "custom_theme",
        "name": "Custom Theme",
        "description": "A custom theme",
        "version": "2.0.0",
    }

    manifest = ThemeManifest.from_dict(data)

    assert manifest.slug == "custom_theme"
    assert manifest.name == "Custom Theme"
    assert manifest.description == "A custom theme"
    assert manifest.version == "2.0.0"


def test_get_theme_validates_slug_mismatch(tmp_path: Path, monkeypatch) -> None:
    """Test that get_theme raises error when directory name doesn't match manifest slug."""
    # Create a fake theme directory
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()

    wrong_slug_dir = themes_dir / "wrong_slug"
    wrong_slug_dir.mkdir()

    manifest_data = {
        "slug": "different_slug",  # Mismatch!
        "name": "Test Theme",
        "description": "Test",
        "version": "1.0.0",
    }

    manifest_file = wrong_slug_dir / "theme.json"
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    monkeypatch.setenv("SUM_THEME_PATH", str(themes_dir))
    with pytest.raises(ThemeValidationError, match="slug mismatch"):
        get_theme("wrong_slug")


def test_invalid_json_in_manifest(tmp_path: Path) -> None:
    """Test graceful handling of invalid JSON in manifest during discovery."""
    # Create a fake theme with invalid JSON
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()

    bad_theme_dir = themes_dir / "bad_theme"
    bad_theme_dir.mkdir()

    manifest_file = bad_theme_dir / "theme.json"
    manifest_file.write_text("{ invalid json", encoding="utf-8")

    themes = discover_themes(themes_dir)
    assert themes == []
