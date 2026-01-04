"""
Name: Content Loader Tests
Path: tests/seeders/test_content_loader.py
Purpose: Verify YAML content loading, validation, and interpolation.
"""

from __future__ import annotations

import pytest

from seeders.content import ContentLoader
from seeders.exceptions import ContentSchemaError


def test_content_loader_lists_profiles(tmp_path) -> None:
    content_dir = tmp_path / "content"
    (content_dir / "alpha").mkdir(parents=True)
    (content_dir / "beta").mkdir()
    (content_dir / ".hidden").mkdir()

    loader = ContentLoader(content_dir=content_dir)

    assert loader.list_profiles() == ["alpha", "beta"]


def test_content_loader_loads_and_interpolates(tmp_path) -> None:
    content_dir = tmp_path / "content"
    profile_dir = content_dir / "sage-stone"
    pages_dir = profile_dir / "pages"
    pages_dir.mkdir(parents=True)

    (profile_dir / "site.yaml").write_text(
        'brand:\n  company_name: "Sage & Stone"\n',
        encoding="utf-8",
    )
    (profile_dir / "navigation.yaml").write_text(
        'footer:\n  tagline: "${brand.company_name}"\n',
        encoding="utf-8",
    )
    (pages_dir / "home.yaml").write_text(
        'title: "Welcome to ${brand.company_name}"\nslug: "home"\n',
        encoding="utf-8",
    )

    loader = ContentLoader(content_dir=content_dir)
    data = loader.load_profile("sage-stone")

    assert data.site["brand"]["company_name"] == "Sage & Stone"
    assert data.navigation["footer"]["tagline"] == "Sage & Stone"
    assert data.pages["home"]["title"] == "Welcome to Sage & Stone"


def test_content_loader_validates_page_schema(tmp_path) -> None:
    content_dir = tmp_path / "content"
    profile_dir = content_dir / "invalid"
    pages_dir = profile_dir / "pages"
    pages_dir.mkdir(parents=True)

    (profile_dir / "site.yaml").write_text("brand:\n  company_name: Test\n")
    (profile_dir / "navigation.yaml").write_text("footer: {}\n")
    (pages_dir / "home.yaml").write_text('title: "Missing slug"\n')

    loader = ContentLoader(content_dir=content_dir)

    with pytest.raises(ContentSchemaError):
        loader.load_profile("invalid")
