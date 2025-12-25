"""
Name: Seed Showroom Management Command Tests
Path: tests/test_seed_showroom_command.py
Purpose: Verify showroom seeding creates required legal pages and exposes them via HTTP + navigation.
Family: seed_showroom smoke coverage.
Dependencies: pytest, Wagtail test client, importlib.
"""

from __future__ import annotations

import sys
from importlib import util
from io import StringIO

import pytest
from django.test import Client
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation
from wagtail.models import Page, Site

from tests.utils import REPO_ROOT


def _load_seed_command():
    path = (
        REPO_ROOT / "boilerplate/project_name/home/management/commands/seed_showroom.py"
    )
    spec = util.spec_from_file_location("seed_showroom_command", path)
    assert spec and spec.loader
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.Command


def _run_seed_command(profile: str = "starter") -> None:
    command_cls = _load_seed_command()
    command = command_cls()
    command.stdout = StringIO()
    command.handle(profile=profile)


@pytest.mark.django_db
def test_seed_showroom_creates_legal_pages_idempotently(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site
    _run_seed_command()

    terms = Page.objects.filter(slug="terms").first()
    privacy = Page.objects.filter(slug="privacy").first()
    cookies = Page.objects.filter(slug="cookies").first()

    assert terms is not None
    assert privacy is not None
    assert cookies is not None
    assert terms.get_parent().slug == "showroom-home"
    assert privacy.get_parent().slug == "showroom-home"
    assert cookies.get_parent().slug == "showroom-home"
    assert terms.specific.live is True
    assert privacy.specific.live is True
    assert cookies.specific.live is True

    for page in (terms, privacy, cookies):
        body = getattr(page.specific, "body", None)
        assert body, f"Missing body stream on {page.slug}"
        block_types = [block.block_type for block in body]
        assert "legal_section" in block_types

    _run_seed_command()

    assert Page.objects.filter(slug="terms").count() == 1
    assert Page.objects.filter(slug="privacy").count() == 1
    assert Page.objects.filter(slug="cookies").count() == 1


@pytest.mark.django_db
def test_seed_showroom_starter_home_has_minimum_blocks(
    client: Client, wagtail_default_site: Site
) -> None:
    assert wagtail_default_site.is_default_site
    _run_seed_command()

    home = Page.objects.filter(slug="showroom-home").first()
    assert home is not None
    body = home.specific.body
    block_types = [block.block_type for block in body]
    assert "hero_image" in block_types
    assert len(block_types) >= 3

    response = client.get("/")
    content = response.content.decode()
    assert "theme_a/css/main.css" in content
    assert "<!-- THEME: theme_a -->" in content


@pytest.mark.django_db
def test_seed_showroom_serves_legal_pages(
    client: Client, wagtail_default_site: Site
) -> None:
    assert wagtail_default_site.is_default_site
    _run_seed_command()

    terms_response = client.get("/terms/")
    privacy_response = client.get("/privacy/")
    cookies_response = client.get("/cookies/")

    assert terms_response.status_code == 200
    assert privacy_response.status_code == 200
    assert cookies_response.status_code == 200

    footer = FooterNavigation.for_site(Site.objects.get(is_default_site=True))
    link_sections = footer.link_sections.get_prep_value()
    link_texts = [
        link.get("link_text")
        for section in link_sections
        for link in section["value"]["links"]
    ]

    assert "Terms" in link_texts
    assert "Privacy" in link_texts
    assert "Cookies" in link_texts

    terms_page = Page.objects.filter(slug="terms").first()
    privacy_page = Page.objects.filter(slug="privacy").first()
    cookies_page = Page.objects.filter(slug="cookies").first()
    settings = SiteSettings.for_site(Site.objects.get(is_default_site=True))
    assert settings.cookie_banner_enabled is True
    assert settings.terms_page_id == terms_page.id
    assert settings.privacy_policy_page_id == privacy_page.id
    assert settings.cookie_policy_page_id == cookies_page.id
