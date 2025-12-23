from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _create_standard_page_with_quote_request_form(
    slug: str, show_compact_meta: bool
) -> Page:
    from sum_core.pages.models import StandardPage

    homepage = HomePage.objects.first()
    if homepage is None:
        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Test Home", slug="theme-home-quote")
        root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Quote Request Test", slug=slug)
    standard.body = [
        (
            "quote_request_form",
            {
                "eyebrow": "Project Application",
                "heading": "Discuss your project",
                "intro": "Tell us about your timeline and scope.",
                "show_compact_meta": show_compact_meta,
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()

    return standard


def test_quote_request_form_uses_theme_a_template(
    client: Client, theme_active_copy
) -> None:
    page = _create_standard_page_with_quote_request_form(
        "quote-request-theme-a", show_compact_meta=True
    )
    response = client.get(page.url)
    content = response.content.decode("utf-8")

    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]
    assert "sum_core/blocks/quote_request_form.html" in template_names

    origin_paths = [
        str(getattr(template.origin, "name", ""))
        for template in templates
        if getattr(template, "name", None) == "sum_core/blocks/quote_request_form.html"
    ]
    expected_fragments = (str(theme_active_copy), "themes/theme_a/templates")
    assert any(
        any(fragment in path for fragment in expected_fragments)
        for path in origin_paths
    )

    assert "Discuss your project" in content


def test_quote_request_form_compact_meta_toggle(client: Client) -> None:
    compact_page = _create_standard_page_with_quote_request_form(
        "quote-request-compact", show_compact_meta=True
    )
    compact_response = client.get(compact_page.url)
    compact_soup = BeautifulSoup(
        compact_response.content.decode("utf-8"), "html.parser"
    )
    assert compact_soup.select_one("[data-compact-meta]") is not None

    non_compact_page = _create_standard_page_with_quote_request_form(
        "quote-request-standard", show_compact_meta=False
    )
    non_compact_response = client.get(non_compact_page.url)
    non_compact_soup = BeautifulSoup(
        non_compact_response.content.decode("utf-8"), "html.parser"
    )
    assert non_compact_soup.select_one("[data-compact-meta]") is None
