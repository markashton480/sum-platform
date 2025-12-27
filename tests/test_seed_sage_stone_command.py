"""
Name: Seed Sage & Stone Management Command Tests
Path: tests/test_seed_sage_stone_command.py
Purpose: Verify Sage & Stone seeding creates site root + homepage and supports clear.
Family: seed_sage_stone smoke coverage.
Dependencies: pytest, importlib.
"""

from __future__ import annotations

import sys
from importlib import util
from io import StringIO

import pytest
from home.models import HomePage
from wagtail.models import Site

from tests.utils import REPO_ROOT


def _load_seed_command():
    path = (
        REPO_ROOT
        / "boilerplate/project_name/home/management/commands/seed_sage_stone.py"
    )
    spec = util.spec_from_file_location("seed_sage_stone_command", path)
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
