"""
Name: Legal Page Rendering Tests
Path: tests/templates/test_legal_page_rendering.py
Purpose: Validate LegalPage template rendering and TOC structure.
Family: Part of the template test suite exercising page rendering.
Dependencies: Django test client, Wagtail models, sum_core.pages.LegalPage.
"""

from __future__ import annotations

import datetime as dt

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from sum_core.pages import LegalPage
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_legal_page_renders_toc_and_sections() -> None:
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = LegalPage(
        title="Privacy Policy",
        slug="privacy-policy",
        last_updated=dt.date(2025, 10, 1),
        sections=[
            (
                "section",
                {
                    "anchor": "introduction",
                    "heading": "Introduction",
                    "body": "<p>Welcome to our policy.</p>",
                },
            )
        ],
    )
    root.add_child(instance=page)
    page.save_revision().publish()

    client = Client()
    response = client.get(page.url)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
    toggle = soup.find("button", attrs={"id": "mobile-toc-toggle"})
    assert toggle is not None
    assert toggle.get("aria-controls") == "mobile-toc-menu"
    assert toggle.get("aria-expanded") == "false"

    mobile_nav = soup.find("nav", attrs={"id": "mobile-toc-menu"})
    assert mobile_nav is not None
    assert mobile_nav.get("aria-label") == "Mobile Table of Contents"

    toc_links = [link.get("href") for link in mobile_nav.find_all("a")]
    assert "#introduction" in toc_links

    section = soup.find("article", attrs={"id": "introduction"})
    assert section is not None

    print_button = soup.find("button", attrs={"onclick": "window.print()"})
    assert print_button is not None
