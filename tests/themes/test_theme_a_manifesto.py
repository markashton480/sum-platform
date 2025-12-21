from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from django.conf import settings
from django.template import engines
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="module", autouse=True)
def active_theme_a(tmp_path_factory, safe_rmtree):
    """
    Install Theme A templates into a simulated client-owned theme/active/templates/
    directory and ensure it is first in template resolution.
    """
    repo_root = Path(__file__).resolve().parents[2]
    source_templates_dir = repo_root / "themes" / "theme_a" / "templates"
    active_root_dir = Path(tmp_path_factory.mktemp("theme-active"))
    active_templates_dir = active_root_dir / "templates"

    original_theme_templates_dir = Path(settings.THEME_TEMPLATES_DIR)
    original_template_dirs = list(settings.TEMPLATES[0]["DIRS"])

    settings.THEME_TEMPLATES_DIR = str(active_templates_dir)
    settings.TEMPLATES[0]["DIRS"] = [
        Path(settings.THEME_TEMPLATES_DIR),
        Path(settings.CLIENT_OVERRIDES_DIR),
    ]

    active_templates_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_templates_dir, active_templates_dir, dirs_exist_ok=True)
    for loader in engines["django"].engine.template_loaders:
        if hasattr(loader, "reset"):
            loader.reset()
    try:
        yield
    finally:
        safe_rmtree(active_root_dir)
        settings.THEME_TEMPLATES_DIR = str(original_theme_templates_dir)
        settings.TEMPLATES[0]["DIRS"] = original_template_dirs
        for loader in engines["django"].engine.template_loaders:
            if hasattr(loader, "reset"):
                loader.reset()


class TestThemeAManifestoBlock:
    """Tests for ManifestoBlock rendering with Theme A."""

    def test_manifesto_block_uses_theme_template(self, client: Client) -> None:
        """Test that ManifestoBlock uses the theme template and renders theme classes."""
        from sum_core.pages.models import StandardPage

        # Create a page
        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Test Home", slug="theme-home-manifesto")
        root.add_child(instance=homepage)

        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        Site.clear_site_root_paths_cache()

        # Create StandardPage with ManifestoBlock
        # We need to constructing the StreamField data correctly
        block_data = [
            {
                "type": "manifesto",
                "value": {
                    "eyebrow": "The Manifesto",
                    "heading": "We believe in quality",
                    "body": "<p>This is the body.</p>",
                    "quote": "A quote",
                },
            }
        ]

        standard = StandardPage(
            title="Manifesto Test", slug="manifesto-test", body=json.dumps(block_data)
        )
        # Note: Direct StreamField assignment via json/list usually works if using compatible data structures,
        # but helper might be safer. For now, testing basic creation.
        # Actually StandardPage.body is a StreamField.
        # Better to assign proper struct:

        standard.body = [
            (
                "manifesto",
                {
                    "eyebrow": "The Manifesto",
                    "heading": "We believe in quality",
                    "body": "<p>This is the body.</p>",
                    "quote": "A quote",
                },
            )
        ]

        homepage.add_child(instance=standard)
        standard.save_revision().publish()

        response = client.get(standard.url)
        content = response.content.decode("utf-8")

        # Check for class specific to Theme A template
        assert "bg-sage-linen" in content
        assert "text-sage-terra" in content
        assert "We believe in quality" in content
