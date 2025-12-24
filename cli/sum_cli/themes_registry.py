"""
Name: Theme Registry & Discovery (CLI)
Path: cli/sum_cli/themes_registry.py
Purpose: Discover and validate themes for `sum init --theme` and `sum themes`.
Family: sum_cli
Dependencies: stdlib only
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ThemeNotFoundError(Exception):
    """Raised when a requested theme slug cannot be found."""


class ThemeValidationError(ValueError):
    """Raised when a theme exists but is invalid (bad manifest or missing files)."""


@dataclass(frozen=True, slots=True)
class ThemeManifest:
    """Type-safe theme metadata loaded from theme.json."""

    slug: str
    name: str
    description: str
    version: str

    def validate(self) -> None:
        if not self.slug:
            raise ValueError("slug cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.version:
            raise ValueError("version cannot be empty")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThemeManifest:
        return cls(
            slug=str(data.get("slug", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            version=str(data.get("version", "")).strip(),
        )


def _read_manifest(theme_dir: Path) -> ThemeManifest:
    manifest_path = theme_dir / "theme.json"
    if not manifest_path.is_file():
        raise ThemeValidationError(f"Missing theme manifest: {manifest_path}")

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ThemeValidationError(
            f"Invalid JSON in theme manifest: {manifest_path} ({e})"
        ) from e

    if not isinstance(data, dict):
        raise ThemeValidationError(f"Theme manifest must be an object: {manifest_path}")

    manifest = ThemeManifest.from_dict(data)
    manifest.validate()

    # Hard validation: directory name must match manifest slug
    if manifest.slug != theme_dir.name:
        raise ThemeValidationError(
            f"Theme slug mismatch: dir='{theme_dir.name}' manifest='{manifest.slug}'"
        )

    return manifest


def _resolve_theme_dir_from_env(slug: str) -> Path | None:
    """
    Resolve a theme dir from SUM_THEME_PATH.

    Spec v1 supports setting SUM_THEME_PATH to a single theme directory like:
      SUM_THEME_PATH=/path/to/themes/theme_a

    For developer ergonomics we also support pointing at a themes root like:
      SUM_THEME_PATH=/path/to/themes
    """
    env = os.getenv("SUM_THEME_PATH")
    if not env:
        return None

    p = Path(env).expanduser().resolve()
    if not p.exists():
        raise ThemeNotFoundError(f"SUM_THEME_PATH does not exist: {p}")

    # If SUM_THEME_PATH points at a theme root (contains theme.json), use it directly.
    if (p / "theme.json").is_file():
        return p

    # Otherwise treat it as a themes root containing subdirectories by slug.
    candidate = p / slug
    if candidate.is_dir():
        return candidate

    raise ThemeNotFoundError(f"Theme '{slug}' not found under SUM_THEME_PATH: {p}")


def resolve_theme_dir(slug: str) -> Path:
    """
    Resolve a theme directory using Theme Architecture Spec v1 order:

    1) SUM_THEME_PATH (dev override)
    2) repo-local canonical: ./themes/<slug> (relative to current working dir)
    3) bundled themes inside CLI package (optional, later)
    """
    slug = slug.strip()
    if not slug:
        raise ThemeNotFoundError("Theme slug cannot be empty")

    env_dir = _resolve_theme_dir_from_env(slug)
    if env_dir is not None:
        return env_dir

    repo_local = (Path.cwd() / "themes" / slug).resolve()
    if repo_local.is_dir():
        return repo_local

    # Bundled themes inside CLI package: optional later (not implemented yet).
    raise ThemeNotFoundError(
        f"Theme '{slug}' not found. Looked in SUM_THEME_PATH (if set) and "
        f"{repo_local.parent}"
    )


def get_theme(slug: str) -> ThemeManifest:
    """Return a validated ThemeManifest for the theme slug."""
    theme_dir = resolve_theme_dir(slug)
    try:
        return _read_manifest(theme_dir)
    except ThemeValidationError as e:
        # Keep a stable exception type for callers (CLI/tests).
        raise ThemeValidationError(str(e)) from e


def list_themes() -> list[ThemeManifest]:
    """
    List themes from the best available registry in this environment.

    - If SUM_THEME_PATH points to a single theme dir, return that one theme.
    - If SUM_THEME_PATH points to a themes root, scan that root.
    - Else scan ./themes (repo-local canonical).
    """
    env = os.getenv("SUM_THEME_PATH")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "theme.json").is_file():
            return [_read_manifest(p)]
        if p.is_dir():
            return discover_themes(p)

    repo_local_root = (Path.cwd() / "themes").resolve()
    return discover_themes(repo_local_root)


def discover_themes(themes_root: Path) -> list[ThemeManifest]:
    """Discover themes by scanning `<themes_root>/*/theme.json`."""
    if not themes_root.exists():
        return []

    manifests: list[ThemeManifest] = []
    for theme_dir in sorted(p for p in themes_root.iterdir() if p.is_dir()):
        if theme_dir.name.startswith("__"):
            continue
        try:
            manifests.append(_read_manifest(theme_dir))
        except ThemeValidationError:
            # Discovery is tolerant by design: invalid themes are ignored.
            continue
    return sorted(manifests, key=lambda t: t.slug)


__all__ = [
    "ThemeManifest",
    "ThemeNotFoundError",
    "ThemeValidationError",
    "discover_themes",
    "get_theme",
    "list_themes",
    "resolve_theme_dir",
]
