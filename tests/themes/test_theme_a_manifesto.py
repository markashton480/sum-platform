from __future__ import annotations

import json

import pytest
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


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
