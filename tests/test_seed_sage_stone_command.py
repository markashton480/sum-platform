"""
Name: Seed Sage & Stone Management Command Tests
Path: tests/test_seed_sage_stone_command.py
Purpose: Verify Sage & Stone seeding creates site root + homepage and supports clear.
Family: seed_sage_stone smoke coverage.
Dependencies: pytest, importlib.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from datetime import date
from importlib import util
from io import StringIO
from typing import Any, cast

import pytest
from home.models import HomePage
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from sum_core.pages.legal import LegalPage
from sum_core.pages.standard import StandardPage
from wagtail.images.models import Image
from wagtail.models import Site

from tests.utils import REPO_ROOT

MODULE_NAME = "seed_sage_stone_command"


def _load_seed_module():
    if MODULE_NAME in sys.modules:
        return sys.modules[MODULE_NAME]
    path = (
        REPO_ROOT
        / "boilerplate/project_name/home/management/commands/seed_sage_stone.py"
    )
    spec = util.spec_from_file_location(MODULE_NAME, path)
    assert spec and spec.loader
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_seed_command():
    return _load_seed_module().Command


def _run_seed_command(clear: bool = False, images_only: bool = False) -> None:
    command_cls = _load_seed_command()
    command = command_cls()
    command.stdout = StringIO()
    command.handle(clear=clear, images_only=images_only)


def _get_brand_config() -> Mapping[str, Any]:
    command_cls = _load_seed_command()
    module = sys.modules[command_cls.__module__]
    return cast(Mapping[str, Any], module.BRAND_CONFIG)


@pytest.mark.django_db
def test_seed_sage_stone_creates_site_and_homepage(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    site = Site.objects.get(hostname="localhost", port=8000)
    assert site.site_name == "Sage & Stone"
    assert site.root_page.slug == "home"
    assert site.is_default_site is True

    home_page = HomePage.objects.get(slug="home")
    assert home_page.live is True


@pytest.mark.django_db
def test_seed_sage_stone_configures_branding(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    site = Site.objects.get(hostname="localhost", port=8000)
    settings = SiteSettings.for_site(site)
    config = _get_brand_config()
    command_cls = _load_seed_command()

    assert settings.company_name == config["company_name"]
    assert settings.primary_color == config["primary_color"]
    assert settings.heading_font == config["heading_font"]
    assert settings.phone_number == config["phone_number"]
    assert settings.instagram_url == config["instagram_url"]
    assert settings.cookie_banner_enabled is config["cookie_banner_enabled"]
    assert settings.header_logo is not None
    assert settings.footer_logo_id == settings.header_logo_id
    assert settings.header_logo.title == f"{command_cls.image_prefix}_LOGO"
    assert settings.favicon is not None
    assert settings.favicon.title == f"{command_cls.image_prefix}_FAVICON"
    assert settings.og_default_image_id is not None


@pytest.mark.django_db
def test_seed_sage_stone_branding_idempotent(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    site = Site.objects.get(hostname="localhost", port=8000)
    settings = SiteSettings.for_site(site)
    logo_id = settings.header_logo_id
    favicon_id = settings.favicon_id
    og_image_id = settings.og_default_image_id

    _run_seed_command()

    settings = SiteSettings.for_site(site)
    assert SiteSettings.objects.filter(site=site).count() == 1
    assert settings.header_logo_id == logo_id
    assert settings.favicon_id == favicon_id
    assert settings.og_default_image_id == og_image_id

    command_cls = _load_seed_command()
    assert Image.objects.filter(title=f"{command_cls.image_prefix}_LOGO").count() == 1
    assert (
        Image.objects.filter(title=f"{command_cls.image_prefix}_FAVICON").count() == 1
    )
    assert (
        Image.objects.filter(title=f"{command_cls.image_prefix}_HERO_IMAGE").count()
        == 1
    )


@pytest.mark.django_db
def test_seed_sage_stone_idempotent(wagtail_default_site: Site) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()
    _run_seed_command()

    assert Site.objects.filter(hostname="localhost", port=8000).count() == 1
    assert HomePage.objects.filter(slug="home").count() == 1


@pytest.mark.django_db
def test_seed_sage_stone_clear_rebuilds_site(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()
    original_home_id = HomePage.objects.get(slug="home").id

    _run_seed_command(clear=True)

    assert HomePage.objects.filter(id=original_home_id).exists() is False
    assert HomePage.objects.filter(slug="home").count() == 1
    assert Site.objects.filter(hostname="localhost", port=8000).count() == 1


@pytest.mark.django_db
def test_placeholder_image_generation(wagtail_default_site: Site) -> None:
    module = _load_seed_module()
    manager = module.ImageManager(prefix=module.IMAGE_PREFIX)

    img = manager.generate("TEST", 800, 600)

    assert img.title == f"{module.IMAGE_PREFIX}_TEST"
    assert img.width == 800
    assert img.height == 600


@pytest.mark.django_db
def test_placeholder_image_generation_idempotent(wagtail_default_site: Site) -> None:
    module = _load_seed_module()
    manager = module.ImageManager(prefix=module.IMAGE_PREFIX)

    first = manager.generate("TEST", 800, 600)
    second = manager.generate("TEST", 800, 600)

    assert first.pk == second.pk


@pytest.mark.django_db
def test_seed_sage_stone_generates_manifest_images(
    wagtail_default_site: Site,
) -> None:
    module = _load_seed_module()
    command_cls = module.Command
    command = command_cls()
    command.stdout = StringIO()

    command.handle(images_only=True)
    command.handle(images_only=True)

    for spec in module.IMAGE_MANIFEST:
        title = f"{module.IMAGE_PREFIX}_{spec['key']}"
        assert Image.objects.filter(title=title).count() == 1
        image = Image.objects.get(title=title)
        assert image.width == spec["width"]
        assert image.height == spec["height"]


@pytest.mark.django_db
def test_terms_page_created(wagtail_default_site: Site) -> None:
    _run_seed_command()

    page = LegalPage.objects.get(slug="terms")
    assert page.title == "Terms of Supply"
    assert page.last_updated == date(2025, 1, 15)
    assert page.live is True


@pytest.mark.django_db
def test_terms_has_sections(wagtail_default_site: Site) -> None:
    _run_seed_command()

    page = LegalPage.objects.get(slug="terms")
    assert len(page.sections) == 6


@pytest.mark.django_db
def test_section_anchors(wagtail_default_site: Site) -> None:
    _run_seed_command()

    page = LegalPage.objects.get(slug="terms")
    anchors = [section.value["anchor"] for section in page.sections]

    assert "definitions" in anchors
    assert "scope" in anchors
    assert "payment" in anchors
    assert "materials" in anchors
    assert "access" in anchors
    assert "guarantee" in anchors


@pytest.mark.django_db
def test_placeholder_pages_created(wagtail_default_site: Site) -> None:
    _run_seed_command()

    assert StandardPage.objects.filter(slug="privacy", live=True).exists()
    assert StandardPage.objects.filter(slug="accessibility", live=True).exists()


@pytest.mark.django_db
def test_seed_sage_stone_configures_header_navigation(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    site = Site.objects.get(hostname="localhost", port=8000)
    header = HeaderNavigation.for_site(site)

    assert header.show_phone_in_header is True
    assert header.header_cta_enabled is True
    assert header.header_cta_text == "Enquire"
    assert header.mobile_cta_enabled is True
    assert header.mobile_cta_phone_enabled is True
    assert header.mobile_cta_button_enabled is True
    assert len(header.menu_items) == 5


@pytest.mark.django_db
def test_seed_sage_stone_kitchens_mega_menu(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    site = Site.objects.get(hostname="localhost", port=8000)
    header = HeaderNavigation.for_site(site)

    kitchens = header.menu_items[0]
    assert kitchens.value["label"] == "Kitchens"
    assert len(kitchens.value["children"]) == 3


@pytest.mark.django_db
def test_seed_sage_stone_configures_footer_navigation(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    site = Site.objects.get(hostname="localhost", port=8000)
    footer = FooterNavigation.for_site(site)

    assert footer.tagline == "Rooms that remember."
    assert len(footer.link_sections) == 3
    assert footer.social_instagram == "https://instagram.com/sageandstone"
    assert footer.copyright_text == "© {year} Sage & Stone Ltd. All rights reserved."


@pytest.mark.django_db
def test_seed_sage_stone_creates_core_pages(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    for slug in ["about", "services", "portfolio", "contact"]:
        assert StandardPage.objects.filter(slug=slug).exists()


@pytest.mark.django_db
def test_seed_sage_stone_core_pages_have_content(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    home = HomePage.objects.get(slug="home")
    assert len(home.body) > 0

    for slug in [
        "about",
        "services",
        "portfolio",
        "contact",
        "privacy",
        "accessibility",
    ]:
        page = StandardPage.objects.get(slug=slug)
        assert len(page.body) > 0


@pytest.mark.django_db
def test_seed_sage_stone_pages_are_children_of_home(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    home = HomePage.objects.get(slug="home")
    for slug in [
        "about",
        "services",
        "portfolio",
        "contact",
        "privacy",
        "accessibility",
    ]:
        page = StandardPage.objects.get(slug=slug)
        assert page.get_parent().id == home.id

    terms = LegalPage.objects.get(slug="terms")
    assert terms.get_parent().id == home.id


@pytest.mark.django_db
def test_seed_sage_stone_categories_created(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    assert Category.objects.count() == 3
    assert Category.objects.filter(slug="material-science").exists()


@pytest.mark.django_db
def test_seed_sage_stone_blog_index_created(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    index = BlogIndexPage.objects.get(slug="journal")
    assert index.title == "The Ledger"
    assert index.posts_per_page == 9


@pytest.mark.django_db
def test_seed_sage_stone_blog_posts_created(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    posts = BlogPostPage.objects.all()
    assert posts.count() == 7


@pytest.mark.django_db
def test_seed_sage_stone_posts_have_categories(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    post = BlogPostPage.objects.get(slug="art-of-seasoning-timber")
    assert post.category.slug == "material-science"


@pytest.mark.django_db
def test_seed_sage_stone_posts_have_content_and_images(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    for post in BlogPostPage.objects.all():
        assert post.featured_image_id is not None
        assert len(post.body) > 0
        assert post.excerpt
        assert post.reading_time >= 1


@pytest.mark.django_db
def test_seed_sage_stone_posts_ordered_by_date(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site

    _run_seed_command()

    posts = list(BlogPostPage.objects.live().order_by("-published_date"))
    assert posts[0].slug == "art-of-seasoning-timber"
