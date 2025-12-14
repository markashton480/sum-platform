"""
Name: Pytest Django Configuration
Path: tests/conftest.py
Purpose: Configure Django/Wagtail settings and test database for pytest runs.
Family: Shared fixtures for the test suite.
Dependencies: Django test utilities, pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = ROOT_DIR / "core"
TEST_PROJECT_DIR = CORE_DIR / "sum_core" / "test_project"

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))


@pytest.fixture()
def wagtail_default_site(db):
    """
    Return a deterministic default Wagtail Site for tests that use HTTP routing.

    Why: this repo's test DB is session-scoped (see `django_test_environment`),
    so other tests can mutate `Site` and Wagtail's internal site-root-path cache.
    Rendering tests that call `client.get(page.url)` should not depend on test order.
    """
    from wagtail.models import Page, Site

    # Ensure Wagtail's computed site root paths cache can't go stale across tests.
    Site.clear_site_root_paths_cache()

    root = Page.get_first_root_node()
    site = Site.objects.filter(is_default_site=True).first()

    if site is None:
        site = Site.objects.create(
            hostname="testserver",
            port=80,
            root_page=root,
            is_default_site=True,
        )
    else:
        changed = False
        if site.hostname != "testserver":
            site.hostname = "testserver"
            changed = True
        if site.port != 80:
            site.port = 80
            changed = True
        if site.root_page_id != root.id:
            site.root_page = root
            changed = True
        if not site.is_default_site:
            site.is_default_site = True
            changed = True
        if changed:
            site.save()

    Site.clear_site_root_paths_cache()
    return site


@pytest.fixture(autouse=True)
def _reset_homepage_between_tests(db) -> None:
    """
    Ensure HomePage tests remain isolated.

    The test DB is session-scoped (see `django_test_environment`), so without
    cleanup, a HomePage created in one test would prevent other tests from
    creating one because HomePage enforces a single-instance constraint.
    """
    from home.models import HomePage
    from wagtail.models import Page, Site

    # If any Site is currently pointing at a HomePage, reset it back to the root node
    # before deleting HomePages to avoid dangling references/caches.
    root = Page.get_first_root_node()
    for site in Site.objects.all():
        if HomePage.objects.filter(pk=site.root_page_id).exists():
            site.root_page = root
            site.save()

    HomePage.objects.all().delete()
    Site.clear_site_root_paths_cache()
