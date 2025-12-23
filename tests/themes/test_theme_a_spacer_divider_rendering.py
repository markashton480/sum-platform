from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from sum_core.pages.models import StandardPage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _get_classes(tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


def _create_standard_page_with_blocks(slug: str, blocks) -> StandardPage:
    root = Page.get_first_root_node()
    homepage = HomePage.objects.first()
    if homepage is None:
        homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
        root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    page = StandardPage(title="Spacer Divider Test", slug=slug)
    page.body = blocks
    homepage.add_child(instance=page)
    page.save_revision().publish()
    return page


def _assert_template_origin(response, template_name: str, theme_active_copy) -> None:
    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]
    assert template_name in template_names

    origin_paths = [
        str(getattr(template.origin, "name", ""))
        for template in templates
        if getattr(template, "name", None) == template_name
    ]
    expected_fragments = (
        str(theme_active_copy),
        "themes/theme_a/templates",
    )
    assert any(
        any(fragment in path for fragment in expected_fragments)
        for path in origin_paths
    )


def _has_div_with_only_class(soup: BeautifulSoup, class_name: str) -> bool:
    for div in soup.find_all("div", class_=class_name):
        if _get_classes(div) == [class_name]:
            return True
    return False


def _has_hr_with_class(soup: BeautifulSoup, class_name: str) -> bool:
    for hr in soup.find_all("hr"):
        if class_name in _get_classes(hr):
            return True
    return False


class TestThemeASpacerDividerRendering:
    def test_spacer_and_divider_rendering(
        self, client: Client, theme_active_copy
    ) -> None:
        spacer_sizes = ["small", "medium", "large", "xlarge"]
        divider_styles = ["muted", "strong", "accent"]

        blocks = [("spacer", {"size": size}) for size in spacer_sizes] + [
            ("divider", {"style": style}) for style in divider_styles
        ]
        page = _create_standard_page_with_blocks("theme-a-spacer-divider", blocks)

        response = client.get(page.url)
        assert response.status_code == 200

        _assert_template_origin(
            response,
            "sum_core/blocks/content_spacer.html",
            theme_active_copy,
        )
        _assert_template_origin(
            response,
            "sum_core/blocks/content_divider.html",
            theme_active_copy,
        )

        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        expected_spacer_classes = {
            "small": "h-6",
            "medium": "h-10",
            "large": "h-16",
            "xlarge": "h-24",
        }
        for size, class_name in expected_spacer_classes.items():
            assert _has_div_with_only_class(
                soup, class_name
            ), f"Missing spacer class for {size}: {class_name}"

        expected_divider_classes = {
            "muted": "border-sage-black/20",
            "strong": "border-sage-black",
            "accent": "border-sage-terra",
        }
        for style, class_name in expected_divider_classes.items():
            assert _has_hr_with_class(
                soup, class_name
            ), f"Missing divider class for {style}: {class_name}"
