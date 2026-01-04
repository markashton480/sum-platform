"""
Name: Site Seeder Tests
Path: tests/seeders/test_site_seeder.py
Purpose: Verify site seeding for branding, navigation, and clear behavior.
"""

from __future__ import annotations

from typing import Any

import pytest
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.pages.standard import StandardPage
from wagtail.images.models import Image
from wagtail.models import Page, Site

from seeders.content import ContentLoader
from seeders.exceptions import SeederContentError, SeederPageError
from seeders.images import ImageManager
from seeders.site import SiteSeeder


def _create_standard_page(parent: Page, slug: str, title: str) -> StandardPage:
    """Create and publish a StandardPage under the given parent."""
    page = StandardPage(title=title, slug=slug)
    parent.add_child(instance=page)
    page.save_revision().publish()
    return page


@pytest.mark.django_db
def test_site_seeder_seed_profile_populates_site_data(
    wagtail_default_site: Site, tmp_path
) -> None:
    root = Page.get_first_root_node()
    about_page = _create_standard_page(root, "about", "About")
    contact_page = _create_standard_page(root, "contact", "Contact")

    pages: dict[str, Any] = {
        "about": about_page,
        "contact": contact_page,
    }

    content_dir = tmp_path / "content"
    profile_dir = content_dir / "demo"
    pages_dir = profile_dir / "pages"
    pages_dir.mkdir(parents=True)

    (profile_dir / "site.yaml").write_text(
        "\n".join(
            [
                'company_name: "Test Co"',
                'primary_color: "#123456"',
                'text_light_color: "#ffffff"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (profile_dir / "navigation.yaml").write_text(
        "\n".join(
            [
                "header:",
                "  show_phone_in_header: true",
                '  header_cta_text: "Contact"',
                "  header_cta_enabled: true",
                "  header_cta_link:",
                '    - type: "link"',
                "      value:",
                '        link_type: "page"',
                '        page: "contact"',
                '        link_text: "Contact"',
                "  mobile_cta_enabled: true",
                "  mobile_cta_phone_enabled: true",
                "  mobile_cta_button_enabled: true",
                '  mobile_cta_button_text: "Contact"',
                "  mobile_cta_button_link:",
                '    - type: "link"',
                "      value:",
                '        link_type: "page"',
                '        page: "contact"',
                '        link_text: "Contact"',
                "  menu_items:",
                '    - type: "item"',
                "      value:",
                '        label: "About"',
                "        link:",
                '          link_type: "page"',
                '          page: "about"',
                '          link_text: "About"',
                "        children: []",
                "footer:",
                '  tagline: "Test tagline"',
                "  auto_service_areas: false",
                '  social_instagram: ""',
                '  social_facebook: ""',
                '  social_linkedin: ""',
                '  social_youtube: ""',
                '  social_x: ""',
                '  copyright_text: "Copyright"',
                "  link_sections:",
                '    - type: "section"',
                "      value:",
                '        title: "Explore"',
                "        links:",
                '          - link_type: "page"',
                '            page: "about"',
                '            link_text: "About"',
                '    - type: "section"',
                "      value:",
                '        title: "Contact"',
                "        links:",
                '          - link_type: "page"',
                '            page: "contact"',
                '            link_text: "Contact"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (pages_dir / "about.yaml").write_text('title: "About"\nslug: "about"\n')

    loader = ContentLoader(content_dir=content_dir)
    seeder = SiteSeeder(
        hostname="testserver",
        port=80,
        root_page=root,
        pages=pages,
        content_loader=loader,
        image_manager=ImageManager(prefix="TESTSITE"),
    )

    seeder.seed_profile("demo", pages=pages)

    site = Site.objects.get(hostname="testserver", port=80)
    assert site.root_page_id == root.id
    assert site.site_name == "Test Co"

    settings = SiteSettings.for_site(site)
    assert settings.company_name == "Test Co"
    assert settings.primary_color == "#123456"
    assert settings.header_logo.title == "TESTSITE_LOGO"
    assert settings.favicon.title == "TESTSITE_FAVICON"
    assert settings.og_default_image.title == "TESTSITE_HERO_IMAGE"

    header = HeaderNavigation.for_site(site)
    assert len(header.menu_items) == 1
    menu_page = header.menu_items[0].value["link"]["page"]
    assert getattr(menu_page, "id", menu_page) == about_page.id

    footer = FooterNavigation.for_site(site)
    assert len(footer.link_sections) == 2
    footer_page = footer.link_sections[0].value["links"][0]["page"]
    assert getattr(footer_page, "id", footer_page) == about_page.id


@pytest.mark.django_db
def test_site_seeder_clear_removes_seeded_state(
    wagtail_default_site: Site,
) -> None:
    root = Page.get_first_root_node()
    about_page = _create_standard_page(root, "about", "About")
    contact_page = _create_standard_page(root, "contact", "Contact")

    pages: dict[str, Any] = {
        "about": about_page,
        "contact": contact_page,
    }

    content = {
        "site": {
            "company_name": "Clear Test",
            "primary_color": "#111111",
            "text_light_color": "#ffffff",
        },
        "navigation": {
            "header": {
                "show_phone_in_header": True,
                "header_cta_enabled": True,
                "header_cta_text": "Contact",
                "header_cta_link": [
                    {
                        "type": "link",
                        "value": {
                            "link_type": "page",
                            "page": "contact",
                            "link_text": "Contact",
                        },
                    }
                ],
                "mobile_cta_enabled": True,
                "mobile_cta_phone_enabled": True,
                "mobile_cta_button_enabled": True,
                "mobile_cta_button_text": "Contact",
                "mobile_cta_button_link": [
                    {
                        "type": "link",
                        "value": {
                            "link_type": "page",
                            "page": "contact",
                            "link_text": "Contact",
                        },
                    }
                ],
                "menu_items": [
                    {
                        "type": "item",
                        "value": {
                            "label": "About",
                            "link": {
                                "link_type": "page",
                                "page": "about",
                                "link_text": "About",
                            },
                            "children": [],
                        },
                    }
                ],
            },
            "footer": {
                "tagline": "Clear Test",
                "auto_service_areas": False,
                "social_instagram": "",
                "social_facebook": "",
                "social_linkedin": "",
                "social_youtube": "",
                "social_x": "",
                "copyright_text": "Copyright",
                "link_sections": [
                    {
                        "type": "section",
                        "value": {
                            "title": "Explore",
                            "links": [
                                {
                                    "link_type": "page",
                                    "page": "about",
                                    "link_text": "About",
                                }
                            ],
                        },
                    },
                    {
                        "type": "section",
                        "value": {
                            "title": "Contact",
                            "links": [
                                {
                                    "link_type": "page",
                                    "page": "contact",
                                    "link_text": "Contact",
                                }
                            ],
                        },
                    },
                ],
            },
        },
        "pages": pages,
    }

    seeder = SiteSeeder(
        hostname="testserver",
        port=80,
        root_page=root,
        pages=pages,
        image_manager=ImageManager(prefix="TESTCLEAR"),
    )
    seeder.seed(content)
    seeder.clear()

    site = Site.objects.get(hostname="testserver", port=80)
    assert SiteSettings.objects.filter(site=site).exists() is False
    assert HeaderNavigation.objects.filter(site=site).exists() is False
    assert FooterNavigation.objects.filter(site=site).exists() is False
    assert Image.objects.filter(title__startswith="TESTCLEAR_").exists() is False


@pytest.mark.django_db
def test_site_seeder_rejects_non_mapping_site_content(
    wagtail_default_site: Site,
) -> None:
    root = Page.get_first_root_node()
    seeder = SiteSeeder(root_page=root)

    with pytest.raises(SeederContentError):
        seeder.seed({"site": "invalid"})


@pytest.mark.django_db
def test_site_seeder_rejects_non_mapping_navigation_content(
    wagtail_default_site: Site,
) -> None:
    root = Page.get_first_root_node()
    seeder = SiteSeeder(root_page=root)

    content = {
        "site": {"company_name": "Test Co"},
        "navigation": ["invalid"],
    }

    with pytest.raises(SeederContentError):
        seeder.seed(content)


@pytest.mark.django_db
def test_site_seeder_rejects_non_mapping_pages(
    wagtail_default_site: Site,
) -> None:
    root = Page.get_first_root_node()
    seeder = SiteSeeder(root_page=root)

    content = {
        "site": {"company_name": "Test Co"},
        "navigation": {},
        "pages": ["invalid"],
    }

    with pytest.raises(SeederContentError):
        seeder.seed(content)


@pytest.mark.django_db
def test_site_seeder_requires_root_page(
    wagtail_default_site: Site,
) -> None:
    seeder = SiteSeeder()

    content = {
        "site": {"company_name": "Test Co"},
        "navigation": {},
    }

    with pytest.raises(SeederPageError):
        seeder.seed(content)


@pytest.mark.django_db
def test_site_seeder_raises_for_missing_page_setting(
    wagtail_default_site: Site,
) -> None:
    root = Page.get_first_root_node()
    seeder = SiteSeeder(root_page=root)

    content = {
        "site": {
            "company_name": "Test Co",
            "privacy_policy_page": "missing",
        },
        "navigation": {},
    }

    with pytest.raises(SeederContentError):
        seeder.seed(content)


@pytest.mark.django_db
def test_site_seeder_raises_for_invalid_navigation_page_reference(
    wagtail_default_site: Site,
) -> None:
    root = Page.get_first_root_node()
    seeder = SiteSeeder(root_page=root)

    content = {
        "site": {"company_name": "Test Co"},
        "navigation": {
            "header": {
                "menu_items": [
                    {
                        "type": "item",
                        "value": {
                            "label": "Broken",
                            "link": {
                                "link_type": "page",
                                "page": object(),
                                "link_text": "Broken",
                            },
                            "children": [],
                        },
                    }
                ],
            },
            "footer": {},
        },
    }

    with pytest.raises(SeederContentError):
        seeder.seed(content)
