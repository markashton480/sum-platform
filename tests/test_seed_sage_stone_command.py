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
from importlib import util
from io import StringIO
from typing import Any, cast

import pytest
from home.models import HomePage
from sum_core.branding.models import SiteSettings
from wagtail.images.models import Image
from wagtail.models import Site

from tests.utils import REPO_ROOT

MODULE_NAME = "seed_sage_stone_command"


def _load_seed_command():
    if MODULE_NAME in sys.modules:
        command_cls = getattr(sys.modules[MODULE_NAME], "Command", None)
        if command_cls:
            return command_cls

    path = (
        REPO_ROOT
        / "boilerplate/project_name/home/management/commands/seed_sage_stone.py"
    )
    spec = util.spec_from_file_location(MODULE_NAME, path)
    assert spec and spec.loader
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.Command


def _run_seed_command(clear: bool = False) -> None:
    command_cls = _load_seed_command()
    command = command_cls()
    command.stdout = StringIO()
    command.handle(clear=clear)


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
    assert settings.header_logo.title == f"{command_cls.image_prefix}LOGO"
    assert settings.favicon is not None
    assert settings.favicon.title == f"{command_cls.image_prefix}FAVICON"
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
    assert Image.objects.filter(title=f"{command_cls.image_prefix}LOGO").count() == 1
    assert Image.objects.filter(title=f"{command_cls.image_prefix}FAVICON").count() == 1
    assert (
        Image.objects.filter(title=f"{command_cls.image_prefix}HERO_IMAGE").count() == 1
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
