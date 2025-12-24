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
from sum_core.navigation.models import FooterNavigation
from sum_core.pages import StandardPage
from wagtail.models import Site

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


def _run_seed_command() -> None:
    command_cls = _load_seed_command()
    command = command_cls()
    command.stdout = StringIO()
    command.handle()


@pytest.mark.django_db
def test_seed_showroom_creates_legal_pages_idempotently(
    wagtail_default_site: Site,
) -> None:
    assert wagtail_default_site.is_default_site
    _run_seed_command()

    terms = StandardPage.objects.filter(slug="terms").first()
    privacy = StandardPage.objects.filter(slug="privacy").first()

    assert terms is not None
    assert privacy is not None
    assert terms.get_parent().slug == "showroom-home"
    assert privacy.get_parent().slug == "showroom-home"

    _run_seed_command()

    assert StandardPage.objects.filter(slug="terms").count() == 1
    assert StandardPage.objects.filter(slug="privacy").count() == 1


@pytest.mark.django_db
def test_seed_showroom_serves_legal_pages(
    client: Client, wagtail_default_site: Site
) -> None:
    assert wagtail_default_site.is_default_site
    _run_seed_command()

    terms_response = client.get("/terms/")
    privacy_response = client.get("/privacy/")

    assert terms_response.status_code == 200
    assert privacy_response.status_code == 200

    footer = FooterNavigation.for_site(Site.objects.get(is_default_site=True))
    link_sections = footer.link_sections.get_prep_value()
    link_texts = [
        link.get("link_text")
        for section in link_sections
        for link in section["value"]["links"]
    ]

    assert "Terms" in link_texts
    assert "Privacy" in link_texts
