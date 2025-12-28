"""
Pytest fixtures for E2E tests using Playwright.

These tests validate that the generated Sage & Stone site works for end users,
not just that database records exist.

E2E tests require:
1. A running Django server (python manage.py runserver)
2. A seeded database (python manage.py seed_sage_stone)

Run with:
    pytest tests/e2e/ -p no:django --base-url http://localhost:8000
"""

from __future__ import annotations

import os

import pytest


def pytest_configure(config):
    """Set default base URL if not provided."""
    if not config.option.base_url:
        config.option.base_url = os.environ.get("E2E_BASE_URL", "http://localhost:8000")


# Override autouse fixtures from parent conftest.py to disable them for E2E tests
# These fixtures depend on Django which we disable for E2E tests


@pytest.fixture(autouse=True)
def _isolate_django_media_root():
    """Override parent fixture - not needed for E2E tests."""
    pass


@pytest.fixture(autouse=True)
def _reset_homepage_between_tests():
    """Override parent fixture - not needed for E2E tests."""
    pass


@pytest.fixture(scope="session")
def _session_media_root(tmp_path_factory):
    """Override parent fixture - not needed for E2E tests."""
    return tmp_path_factory.mktemp("e2e-media")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-GB",
    }


@pytest.fixture(scope="function")
def seeded_database():
    """
    Marker fixture indicating tests expect a pre-seeded database.

    E2E tests require the Sage & Stone site to be seeded and a server running.

    Setup before running E2E tests:
    1. cd core/sum_core/test_project
    2. python manage.py migrate
    3. python manage.py seed_sage_stone
    4. python manage.py runserver 8765 &
    5. cd ../../..
    6. pytest tests/e2e/ -p no:django --base-url http://localhost:8765
    """
    # This is a marker fixture - actual seeding happens outside test session
    pass
