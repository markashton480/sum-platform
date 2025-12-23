from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _create_standard_page_with_richtext(slug: str, align: str) -> Page:
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Rich Text Test", slug=slug)
    standard.body = [
        (
            "content",
            {
                "align": align,
                "body": (
                    "<h2>Section Heading</h2>"
                    '<p>Some <a href="#link">linked text</a> in a paragraph.</p>'
                    "<ul><li>First item</li></ul>"
                ),
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()

    return standard


class TestThemeARichTextContentBlock:
    def test_richtext_block_renders_theme_template_and_alignment(
        self, client: Client, theme_active_copy
    ) -> None:
        standard = _create_standard_page_with_richtext(
            "richtext-theme-a-center", "center"
        )

        response = client.get(standard.url)
        content = response.content.decode("utf-8")

        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert "sum_core/blocks/content_richtext.html" in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None)
            == "sum_core/blocks/content_richtext.html"
        ]
        expected_fragments = (
            str(theme_active_copy),
            "themes/theme_a/templates",
        )
        assert any(
            any(fragment in path for fragment in expected_fragments)
            for path in origin_paths
        )
        assert "max-w-3xl mx-auto" in content
        assert "prose-headings:text-center" in content
        assert "<h2>Section Heading</h2>" in content
        assert "<ul>" in content
        assert '<a href="#link"' in content
        soup = BeautifulSoup(content, "html.parser")
        prose = soup.find(
            "div",
            class_=lambda value: value and "prose-sage" in str(value).split(),
        )
        assert prose is not None
        wrapper = prose.find_parent(
            "section",
            class_=lambda value: value and "section" in str(value).split(),
        )
        assert wrapper is not None
