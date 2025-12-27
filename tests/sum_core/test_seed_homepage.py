"""
Name: Seed Homepage Management Command Tests
Path: tests/sum_core/test_seed_homepage.py
Purpose: Verify seed_homepage creates and manages the default HomePage.
Family: sum_core management command tests.
Dependencies: pytest, Django call_command, Wagtail Site/Page, HomePage model.
"""

from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command
from home.models import HomePage
from wagtail.models import Page, Site


@pytest.mark.django_db
def test_seed_homepage_creates_published_homepage(wagtail_default_site: Site) -> None:
    out = StringIO()
    call_command("seed_homepage", stdout=out)

    homepage = HomePage.objects.get(slug="home")
    root = Page.get_first_root_node()
    site = Site.objects.get(is_default_site=True)

    assert homepage.title == "Welcome"
    assert homepage.seo_title == "Home"
    assert homepage.search_description == "Welcome to our website"
    assert homepage.live is True
    assert homepage.get_parent().id == root.id
    assert site.root_page_id == homepage.id

    output = out.getvalue()
    assert "✅ Homepage created successfully (ID:" in output
    assert "URL: http://127.0.0.1:8000/" in output

    body = homepage.body
    block_types = [block.block_type for block in body]
    assert "hero_gradient" in block_types
    assert "rich_text" in block_types

    hero_block = next(block for block in body if block.block_type == "hero_gradient")
    assert "Welcome to Your New Site" in str(hero_block.value["headline"])
    assert (
        hero_block.value["subheadline"]
        == "Your professional website is ready to customize."
    )

    rich_text_block = next(block for block in body if block.block_type == "rich_text")
    assert "Edit this content in the Wagtail admin." in str(rich_text_block.value)


@pytest.mark.django_db
def test_seed_homepage_is_idempotent_without_force(
    wagtail_default_site: Site,
) -> None:
    call_command("seed_homepage")

    out = StringIO()
    call_command("seed_homepage", stdout=out)

    assert "Homepage already exists" in out.getvalue()
    assert HomePage.objects.count() == 1


@pytest.mark.django_db
def test_seed_homepage_force_recreates_homepage(wagtail_default_site: Site) -> None:
    call_command("seed_homepage")
    original = HomePage.objects.get(slug="home")

    out = StringIO()
    call_command("seed_homepage", force=True, stdout=out)

    assert HomePage.objects.filter(id=original.id).exists() is False
    new_homepage = HomePage.objects.get(slug="home")
    assert new_homepage.id != original.id

    site = Site.objects.get(is_default_site=True)
    assert site.root_page_id == new_homepage.id


@pytest.mark.django_db
def test_seed_homepage_accepts_preset_arg(wagtail_default_site: Site) -> None:
    call_command("seed_homepage", preset="starter")

    assert HomePage.objects.filter(slug="home").exists()
