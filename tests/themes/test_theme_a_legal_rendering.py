from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from sum_core.pages.standard import StandardPage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _build_legal_page(slug: str) -> StandardPage:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    page = StandardPage(title="Legal Blocks Test", slug=slug)
    page.body = [
        (
            "table_of_contents",
            {
                "items": [
                    {"label": "Scope of Works", "anchor": "scope-of-works"},
                    {"label": "Payments", "anchor": "payments"},
                ]
            },
        ),
        (
            "legal_section",
            {
                "anchor": "scope-of-works",
                "heading": "Scope of Works",
                "body": (
                    "<p>We deliver the services agreed in the proposal.</p>"
                    "<ul><li>Defined scope only.</li>"
                    "<li>Changes require written approval.</li></ul>"
                ),
            },
        ),
        (
            "legal_section",
            {
                "anchor": "payments",
                "heading": "Payments",
                "body": (
                    "<p>Invoices are due on the schedule agreed.</p>"
                    "<p><strong>Late fees</strong> may apply.</p>"
                ),
            },
        ),
    ]
    homepage.add_child(instance=page)
    page.save_revision().publish()
    return page


def test_legal_blocks_render_with_theme_a_templates(
    client: Client, theme_active_copy
) -> None:
    page = _build_legal_page("theme-a-legal")
    response = client.get(page.url)
    assert response.status_code == 200

    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]
    assert "sum_core/blocks/table_of_contents.html" in template_names
    assert "sum_core/blocks/legal_section.html" in template_names

    origins: dict[str, list[str]] = {
        "sum_core/blocks/table_of_contents.html": [],
        "sum_core/blocks/legal_section.html": [],
    }
    for template in templates:
        name = getattr(template, "name", None)
        if name in origins:
            origins[name].append(str(getattr(template.origin, "name", "")))

    for paths in origins.values():
        assert any(
            "themes/theme_a/templates" in path or str(theme_active_copy) in path
            for path in paths
        ), f"Unexpected template origins: {paths}"

    soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
    toc_nav = soup.find("nav", attrs={"aria-label": "Table of Contents"})
    assert toc_nav is not None
    hrefs = [link.get("href") for link in toc_nav.find_all("a")]
    assert "#scope-of-works" in hrefs
    assert "#payments" in hrefs

    section_ids = {
        section.get("id") for section in soup.find_all("section") if section.get("id")
    }
    assert "scope-of-works" in section_ids
    assert "payments" in section_ids
