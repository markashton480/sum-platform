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
from wagtail.images.models import Image
from wagtail.models import Site

from tests.utils import REPO_ROOT


def _load_seed_module():
    path = (
        REPO_ROOT
        / "boilerplate/project_name/home/management/commands/seed_sage_stone.py"
    )
    spec = util.spec_from_file_location("seed_sage_stone_command", path)
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


@pytest.mark.django_db
def test_placeholder_image_generation(wagtail_default_site: Site) -> None:
    module = _load_seed_module()
    generator = module.PlaceholderImageGenerator()

    img = generator.generate_image("TEST", 800, 600)

    assert img.title == f"{module.IMAGE_PREFIX}_TEST"
    assert img.width == 800
    assert img.height == 600


@pytest.mark.django_db
def test_placeholder_image_generation_idempotent(wagtail_default_site: Site) -> None:
    module = _load_seed_module()
    generator = module.PlaceholderImageGenerator()

    first = generator.generate_image("TEST", 800, 600)
    second = generator.generate_image("TEST", 800, 600)

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
