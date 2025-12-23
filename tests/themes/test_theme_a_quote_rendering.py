from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _create_standard_page_with_quote(
    slug: str, quote: str, author: str = "", role: str = ""
) -> Page:
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage.objects.first()
    if homepage is None:
        homepage = HomePage(title="Theme Test Home", slug="theme-home-quote")
        root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Quote Test", slug=slug)
    standard.body = [
        (
            "quote",
            {
                "quote": quote,
                "author": author,
                "role": role,
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()

    return standard


class TestThemeAQuoteBlock:
    def test_quote_block_renders_theme_template(self, client: Client, theme_active_copy) -> None:
        page = _create_standard_page_with_quote(
            "quote-theme-a",
            "Quiet craft.\nLoud result.",
            "Ava Hill",
            "Property Owner",
        )

        response = client.get(page.url)
        content = response.content.decode("utf-8")

        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert "sum_core/blocks/content_quote.html" in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None) == "sum_core/blocks/content_quote.html"
        ]
        expected_fragments = (
            str(theme_active_copy),
            "themes/theme_a/templates",
        )
        assert any(
            any(fragment in path for fragment in expected_fragments)
            for path in origin_paths
        )
        assert "Quiet craft." in content
        assert "Ava Hill" in content
        assert "Property Owner" in content
        assert "reveal" in content

    def test_quote_block_author_and_role_are_optional(self, client: Client) -> None:
        author_page = _create_standard_page_with_quote(
            "quote-theme-a-author-only",
            "Measured framing.",
            "Rowan Lee",
            "",
        )
        author_response = client.get(author_page.url)
        author_soup = BeautifulSoup(author_response.content.decode("utf-8"), "html.parser")
        author_caption = author_soup.find("figcaption")
        assert author_caption is not None
        assert "Rowan Lee" in author_caption.get_text()
        assert "Property Owner" not in author_caption.get_text()

        role_page = _create_standard_page_with_quote(
            "quote-theme-a-role-only",
            "Measured framing.",
            "",
            "Property Owner",
        )
        role_response = client.get(role_page.url)
        role_soup = BeautifulSoup(role_response.content.decode("utf-8"), "html.parser")
        role_caption = role_soup.find("figcaption")
        assert role_caption is not None
        assert "Property Owner" in role_caption.get_text()
        assert role_caption.find("cite") is None
