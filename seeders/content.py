"""YAML content loading and validation utilities."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from .exceptions import ContentProfileError, ContentSchemaError


@dataclass(frozen=True)
class ProfileData:
    """Container for loaded profile content."""

    site: dict[str, Any]
    navigation: dict[str, Any]
    pages: dict[str, dict[str, Any]]


class ContentLoader:
    """Load and validate YAML content profiles."""

    _interpolation_pattern = re.compile(r"\$\{([^}]+)\}")

    def __init__(self, content_dir: Path | None = None) -> None:
        self.content_dir = content_dir or Path("content")

    def list_profiles(self) -> list[str]:
        """List available content profiles."""

        if not self.content_dir.exists():
            return []
        if not self.content_dir.is_dir():
            raise ContentProfileError(
                f"Content directory is not a directory: {self.content_dir}"
            )
        profiles = [
            path.name
            for path in self.content_dir.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        ]
        return sorted(profiles)

    def load_profile(self, profile: str) -> ProfileData:
        """Load all content for a profile."""

        profile_dir = self.content_dir / profile
        if not profile_dir.exists() or not profile_dir.is_dir():
            raise ContentProfileError(f"Profile not found: {profile}")

        site = self._load_yaml(profile_dir / "site.yaml")
        navigation = self._load_yaml(profile_dir / "navigation.yaml")
        pages = self._load_pages(profile_dir / "pages")

        self._validate_site(site)
        self._validate_navigation(navigation)
        self._validate_pages(pages)

        context = self._build_context(site=site, navigation=navigation, pages=pages)
        site = cast(dict[str, Any], self._interpolate(site, context))
        navigation = cast(dict[str, Any], self._interpolate(navigation, context))
        pages = {
            name: cast(dict[str, Any], self._interpolate(page, context))
            for name, page in pages.items()
        }

        return ProfileData(site=site, navigation=navigation, pages=pages)

    def _load_pages(self, pages_dir: Path) -> dict[str, dict[str, Any]]:
        if not pages_dir.exists() or not pages_dir.is_dir():
            raise ContentProfileError(f"Pages directory missing: {pages_dir}")

        page_files = sorted(pages_dir.glob("*.yaml")) + sorted(pages_dir.glob("*.yml"))
        pages: dict[str, dict[str, Any]] = {}
        seen_stems: dict[str, Path] = {}
        for page_file in page_files:
            stem = page_file.stem
            if stem in seen_stems:
                first = seen_stems[stem]
                raise ContentProfileError(
                    f"Duplicate page definition for '{stem}': {first} and {page_file}"
                )
            seen_stems[stem] = page_file
            pages[stem] = self._load_yaml(page_file)
        return pages

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists() or not path.is_file():
            raise ContentProfileError(f"Required content file missing: {path}")
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise ContentSchemaError(f"Invalid YAML in {path}") from exc

        if data is None:
            return {}
        if not isinstance(data, dict):
            raise ContentSchemaError(f"YAML root must be a mapping in {path}")
        return cast(dict[str, Any], data)

    def _validate_site(self, site: dict[str, Any]) -> None:
        if not isinstance(site, dict):
            raise ContentSchemaError("Site content must be a mapping")
        if not site:
            raise ContentSchemaError("Site content cannot be empty")

    def _validate_navigation(self, navigation: dict[str, Any]) -> None:
        if not isinstance(navigation, dict):
            raise ContentSchemaError("Navigation content must be a mapping")
        if not navigation:
            raise ContentSchemaError("Navigation content cannot be empty")

    def _validate_pages(self, pages: dict[str, dict[str, Any]]) -> None:
        for name, page in pages.items():
            if not isinstance(page, dict):
                raise ContentSchemaError(f"Page '{name}' must be a mapping")
            slug = page.get("slug")
            title = page.get("title")
            if not isinstance(slug, str) or not slug:
                raise ContentSchemaError(f"Page '{name}' missing valid slug")
            if not isinstance(title, str) or not title:
                raise ContentSchemaError(f"Page '{name}' missing valid title")

    def _build_context(
        self,
        *,
        site: dict[str, Any],
        navigation: dict[str, Any],
        pages: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        context: dict[str, Any] = {
            "site": site,
            "navigation": navigation,
            "pages": pages,
        }
        for key, value in site.items():
            if key not in context:
                context[key] = value
        return context

    def _interpolate(self, data: Any, context: Mapping[str, Any]) -> Any:
        if isinstance(data, str):
            return self._interpolate_string(data, context)
        if isinstance(data, list):
            return [self._interpolate(item, context) for item in data]
        if isinstance(data, dict):
            return {
                key: self._interpolate(value, context) for key, value in data.items()
            }
        return data

    def _interpolate_string(self, value: str, context: Mapping[str, Any]) -> str:
        def replace(match: re.Match[str]) -> str:
            path = match.group(1).strip()
            resolved = self._resolve_path(context, path)
            if isinstance(resolved, str | int | float | bool):
                return str(resolved)
            raise ContentSchemaError(
                f"Interpolation value for '{path}' must be a scalar"
            )

        return self._interpolation_pattern.sub(replace, value)

    def _resolve_path(self, context: Mapping[str, Any], path: str) -> Any:
        current: Any = context
        for segment in path.split("."):
            if not segment:
                continue
            if isinstance(current, Mapping) and segment in current:
                current = current[segment]
            else:
                raise ContentSchemaError(f"Interpolation path not found: {path}")
        return current
