from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from sum_core.blocks.content import EditorialHeaderBlock
from sum_core.pages.standard import StandardPage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _get_classes(tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


def _build_page_with_editorial_header(slug: str, block_value) -> StandardPage:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    page = StandardPage(title="Editorial Header Test", slug=slug)
    page.body = [("editorial_header", block_value)]
    homepage.add_child(instance=page)
    page.save_revision().publish()
    return page


def test_editorial_header_uses_theme_a_override(
    client: Client, theme_active_copy
) -> None:
    block_value = {
        "eyebrow": "Ledger",
        "heading": "<p>Article Heading</p>",
        "align": "left",
    }
    template_name = "sum_core/blocks/content_editorial_header.html"
    page = _build_page_with_editorial_header("theme-a-editorial-header", block_value)

    response = client.get(page.url)
    assert response.status_code == 200

    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]
    assert template_name in template_names

    origins: list[str] = []
    for template in templates:
        name = getattr(template, "name", None)
        if name == template_name:
            origins.append(str(getattr(template.origin, "name", "")))
    assert any(
        "themes/theme_a/templates" in path or str(theme_active_copy) in path
        for path in origins
    ), f"Unexpected template origins: {origins}"

    content = response.content.decode("utf-8")
    assert "bg-sage-black" in content
    assert "text-sage-linen" in content
    soup = BeautifulSoup(content, "html.parser")
    section = soup.find(
        "section",
        class_=lambda value: value and "section--hero" in str(value).split(),
    )
    assert section is not None


def test_editorial_header_alignment_and_richtext() -> None:
    block = EditorialHeaderBlock()

    centered_html = block.render(
        block.to_python(
            {
                "eyebrow": "Centered Eyebrow",
                "heading": "<p>Centered <em>Heading</em></p>",
                "align": "center",
            }
        )
    )
    centered = BeautifulSoup(centered_html, "html.parser")
    centered_wrapper = centered.find("div", class_="space-y-4")
    assert centered_wrapper is not None
    centered_classes = _get_classes(centered_wrapper)
    assert "text-center" in centered_classes
    assert "mx-auto" in centered_classes
    assert "max-w-3xl" in centered_classes

    heading = centered.find("div", class_="font-display")
    assert heading is not None
    assert heading.find("em") is not None

    left_html = block.render(
        block.to_python({"heading": "<p>Left Heading</p>", "align": "left"})
    )
    left = BeautifulSoup(left_html, "html.parser")
    left_wrapper = left.find("div", class_="space-y-4")
    assert left_wrapper is not None
    left_classes = _get_classes(left_wrapper)
    assert "text-left" in left_classes
    assert "mx-auto" not in left_classes
    assert "max-w-4xl" in left_classes


def test_editorial_header_eyebrow_optional() -> None:
    block = EditorialHeaderBlock()

    html_with = block.render(
        block.to_python({"heading": "<p>With Eyebrow</p>", "eyebrow": "Meta Label"})
    )
    soup_with = BeautifulSoup(html_with, "html.parser")
    eyebrow = soup_with.find("span", class_="text-sage-terra")
    assert eyebrow is not None
    assert "Meta Label" in eyebrow.get_text()

    html_without = block.render(block.to_python({"heading": "<p>No Eyebrow</p>"}))
    soup_without = BeautifulSoup(html_without, "html.parser")
    assert soup_without.find("span", class_="text-sage-terra") is None
