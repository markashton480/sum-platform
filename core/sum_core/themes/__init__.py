"""
Name: Theme System
Path: core/sum_core/themes/__init__.py
Purpose: Theme discovery, validation, and registry for SUM Platform theme system v1
Family: sum_core themes
Dependencies: sum_core, pathlib, json
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Directory containing all themes
THEMES_DIR: Final[Path] = Path(__file__).parent


@dataclass(frozen=True)
class ThemeManifest:
    """
    Type-safe representation of a theme's manifest.

    Attributes:
        slug: Unique identifier for the theme (filesystem-safe)
        name: Human-readable theme name
        description: Brief description of the theme's purpose
        version: Semantic version string
    """

    slug: str
    name: str
    description: str
    version: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ThemeManifest:
        """Create ThemeManifest from parsed JSON dictionary."""
        return cls(
            slug=data["slug"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
        )

    def validate(self) -> None:
        """
        Validate manifest data.

        Raises:
            ValueError: If any required field is missing or invalid
        """
        if not self.slug:
            raise ValueError("Theme slug cannot be empty")
        if not self.name:
            raise ValueError("Theme name cannot be empty")
        if not self.version:
            raise ValueError("Theme version cannot be empty")


class ThemeNotFoundError(Exception):
    """Raised when a requested theme does not exist."""

    pass


class ThemeValidationError(Exception):
    """Raised when a theme manifest is invalid."""

    pass


def discover_themes() -> list[ThemeManifest]:
    """
    Discover all valid themes in the themes directory.

    Returns:
        List of ThemeManifest objects for all valid themes

    A theme is valid if:
    - It's a subdirectory of THEMES_DIR
    - It contains a theme.json manifest
    - The manifest is valid JSON with required fields
    """
    themes: list[ThemeManifest] = []

    if not THEMES_DIR.exists() or not THEMES_DIR.is_dir():
        return themes

    for theme_dir in THEMES_DIR.iterdir():
        if not theme_dir.is_dir():
            continue

        manifest_path = theme_dir / "theme.json"
        if not manifest_path.exists():
            continue

        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            manifest = ThemeManifest.from_dict(data)
            manifest.validate()
            themes.append(manifest)
        except (json.JSONDecodeError, KeyError, ValueError):
            # Skip invalid themes during discovery
            continue

    return themes


def get_theme(slug: str) -> ThemeManifest:
    """
    Get a specific theme by slug.

    Args:
        slug: Theme identifier

    Returns:
        ThemeManifest for the requested theme

    Raises:
        ThemeNotFoundError: If theme does not exist
        ThemeValidationError: If theme manifest is invalid
    """
    theme_dir = THEMES_DIR / slug

    if not theme_dir.exists() or not theme_dir.is_dir():
        raise ThemeNotFoundError(f"Theme '{slug}' not found")

    manifest_path = theme_dir / "theme.json"
    if not manifest_path.exists():
        raise ThemeValidationError(f"Theme '{slug}' is missing theme.json manifest")

    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        manifest = ThemeManifest.from_dict(data)
        manifest.validate()

        # Ensure slug in manifest matches directory name
        if manifest.slug != slug:
            raise ThemeValidationError(
                f"Theme slug mismatch: directory '{slug}' but manifest says '{manifest.slug}'"
            )

        return manifest
    except json.JSONDecodeError as e:
        raise ThemeValidationError(f"Invalid JSON in theme manifest: {e}")
    except KeyError as e:
        raise ThemeValidationError(f"Missing required field in theme manifest: {e}")
    except ValueError as e:
        raise ThemeValidationError(f"Theme validation failed: {e}")


def list_themes() -> list[ThemeManifest]:
    """
    List all available themes.

    Returns:
        List of ThemeManifest objects, sorted by slug
    """
    themes = discover_themes()
    return sorted(themes, key=lambda t: t.slug)


def get_theme_template_dir(slug: str) -> Path:
    """
    Get the template directory path for a theme.

    Args:
        slug: Theme identifier

    Returns:
        Absolute path to theme's templates directory

    Raises:
        ThemeNotFoundError: If theme does not exist
    """
    # Validate theme exists
    get_theme(slug)

    return THEMES_DIR / slug / "templates"


def get_theme_static_dir(slug: str) -> Path:
    """
    Get the static files directory path for a theme.

    Args:
        slug: Theme identifier

    Returns:
        Absolute path to theme's static directory

    Raises:
        ThemeNotFoundError: If theme does not exist
    """
    # Validate theme exists
    get_theme(slug)

    return THEMES_DIR / slug / "static"


def get_theme_dir(slug: str) -> Path:
    """
    Get the root directory path for a theme.

    This is used by the CLI to copy theme files into the client project
    during `sum init`.

    Args:
        slug: Theme identifier

    Returns:
        Absolute path to theme's root directory

    Raises:
        ThemeNotFoundError: If theme does not exist
    """
    # Validate theme exists
    get_theme(slug)

    return THEMES_DIR / slug


__all__ = [
    "ThemeManifest",
    "ThemeNotFoundError",
    "ThemeValidationError",
    "discover_themes",
    "get_theme",
    "list_themes",
    "get_theme_template_dir",
    "get_theme_static_dir",
    "get_theme_dir",
]
