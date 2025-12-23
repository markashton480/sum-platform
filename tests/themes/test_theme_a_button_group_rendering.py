from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _get_classes(tag: Tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


def _create_standard_page_with_buttons(
    slug: str,
    alignment: str,
    homepage: HomePage | None = None,
):
    from sum_core.pages.models import StandardPage

    if homepage is None:
        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
        root.add_child(instance=homepage)

        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Button Group Test", slug=slug)
    standard.body = [
        (
            "buttons",
            {
                "alignment": alignment,
                "buttons": [
                    {
                        "label": "Book Consultation",
                        "url": "https://example.com/book",
                        "style": "primary",
                    },
                    {
                        "label": "View Project Gallery",
                        "url": "https://example.com/gallery",
                        "style": "secondary",
                    },
                ],
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()

    return standard


def _find_button_group(soup: BeautifulSoup, button_href: str) -> Tag | None:
    button = soup.find("a", href=button_href)
    if not button:
        return None
    return button.find_parent(
        "div",
        class_=lambda value: value
        and {"flex", "gap-4"}.issubset(set(str(value).split())),
    )


def _assert_theme_template_origin(
    response, theme_active_copy, template_name: str
) -> None:
    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]
    assert template_name in template_names

    origin_paths = [
        str(getattr(template.origin, "name", ""))
        for template in templates
        if getattr(template, "name", None) == template_name
    ]
    expected_fragments = (str(theme_active_copy), "themes/theme_a/templates")
    assert any(
        any(fragment in path for fragment in expected_fragments)
        for path in origin_paths
    )


def test_theme_a_button_group_template_and_styles(
    client: Client, theme_active_copy
) -> None:
    standard = _create_standard_page_with_buttons("theme-a-buttons-left", "left")

    response = client.get(standard.url)
    _assert_theme_template_origin(
        response, theme_active_copy, "sum_core/blocks/content_buttons.html"
    )

    soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
    button_group = _find_button_group(soup, "https://example.com/book")
    assert button_group

    primary = button_group.find("a", href="https://example.com/book")
    assert primary
    assert "Book Consultation" in primary.get_text()
    assert "btn-primary" in _get_classes(primary)

    secondary = button_group.find("a", href="https://example.com/gallery")
    assert secondary
    assert "View Project Gallery" in secondary.get_text()
    assert "btn-outline" in _get_classes(secondary)


def test_theme_a_button_group_alignment_classes(client: Client, theme_active_copy):
    cases = [
        ("center", "justify-center"),
        ("right", "justify-end"),
    ]

    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug="theme-home-button-group")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    for alignment, expected_class in cases:
        standard = _create_standard_page_with_buttons(
            f"theme-a-buttons-{alignment}", alignment, homepage=homepage
        )
        response = client.get(standard.url)
        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        button_group = _find_button_group(soup, "https://example.com/book")
        assert button_group
        assert expected_class in _get_classes(button_group)
