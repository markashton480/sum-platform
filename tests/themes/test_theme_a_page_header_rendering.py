from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from sum_core.pages.standard import StandardPage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _build_page_with_page_header(slug: str, block_value: dict) -> StandardPage:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    page = StandardPage(title="Page Header Test", slug=slug)
    page.body = [("page_header", block_value)]
    homepage.add_child(instance=page)
    page.save_revision().publish()
    return page


def test_page_header_uses_theme_a_override(client: Client, theme_active_copy) -> None:
    block_value = {
        "eyebrow": "Insights",
        "heading": "<p>Interior <em>Heading</em></p>",
        "intro": "Short intro text for the page header.",
    }
    template_name = "sum_core/blocks/page_header.html"
    page = _build_page_with_page_header("theme-a-page-header", block_value)

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
    assert "Interior" in content
    soup = BeautifulSoup(content, "html.parser")
    nav = soup.find("nav", attrs={"aria-label": "Breadcrumb"})
    assert nav is not None
    assert nav.find("ol") is not None
    assert nav.find(attrs={"aria-current": "page"}) is not None
    assert nav.find("a") is not None


def test_page_header_falls_back_to_page_title(client: Client) -> None:
    page = _build_page_with_page_header(
        "theme-a-page-header-fallback", {"intro": "Fallback intro"}
    )

    response = client.get(page.url)
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert page.title in content
