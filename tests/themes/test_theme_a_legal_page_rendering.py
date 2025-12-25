from __future__ import annotations

import datetime as dt

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from sum_core.pages import LegalPage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _build_legal_page(slug: str) -> LegalPage:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    page = LegalPage(
        title="Terms of Service",
        slug=slug,
        last_updated=dt.date(2025, 10, 1),
        sections=[
            (
                "section",
                {
                    "anchor": "definitions",
                    "heading": "Definitions",
                    "body": "<p>Key definitions for the agreement.</p>",
                },
            ),
            (
                "section",
                {
                    "anchor": "scope",
                    "heading": "Scope of Works",
                    "body": "<p>Scope details.</p>",
                },
            ),
        ],
    )
    homepage.add_child(instance=page)
    page.save_revision().publish()
    return page


def test_legal_page_uses_theme_a_template(client: Client, theme_active_copy) -> None:
    page = _build_legal_page("theme-a-legal-page")
    response = client.get(page.url)
    assert response.status_code == 200

    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]
    assert "theme/legal_page.html" in template_names

    origins = [
        str(getattr(template.origin, "name", ""))
        for template in templates
        if getattr(template, "name", None) == "theme/legal_page.html"
    ]
    assert any(
        "themes/theme_a/templates" in path or str(theme_active_copy) in path
        for path in origins
    ), f"Unexpected template origins: {origins}"

    soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
    toggle = soup.find("button", attrs={"id": "mobile-toc-toggle"})
    assert toggle is not None
    assert toggle.get("aria-controls") == "mobile-toc-menu"
    assert toggle.get("aria-expanded") == "false"

    mobile_nav = soup.find("nav", attrs={"id": "mobile-toc-menu"})
    assert mobile_nav is not None
    assert mobile_nav.get("aria-label") == "Mobile Table of Contents"

    toc_links = [link.get("href") for link in mobile_nav.find_all("a")]
    assert "#definitions" in toc_links
    assert "#scope" in toc_links

    section_ids = {
        section.get("id") for section in soup.find_all("article") if section.get("id")
    }
    assert "definitions" in section_ids
    assert "scope" in section_ids

    print_button = soup.find("button", attrs={"onclick": "window.print()"})
    assert print_button is not None
