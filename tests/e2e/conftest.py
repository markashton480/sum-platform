"""
Pytest fixtures for E2E tests using Playwright.

These tests validate that the generated Sage & Stone site works for end users,
not just that database records exist.
"""

from __future__ import annotations

import sys
from importlib import util
from io import StringIO

import pytest

from tests.utils import REPO_ROOT

MODULE_NAME = "seed_sage_stone_command_e2e"


def _load_seed_module():
    """Load the seed_sage_stone module from the boilerplate."""
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
    """Load the Command class from the seed module."""
    return _load_seed_module().Command


def _run_seed_command(
    clear: bool = False,
    images_only: bool = False,
    hostname: str = "localhost",
    port: int = 8000,
) -> None:
    """Run the seed_sage_stone management command."""
    command_cls = _load_seed_command()
    command = command_cls()
    command.stdout = StringIO()
    command.handle(
        clear=clear,
        images_only=images_only,
        hostname=hostname,
        port=port,
    )


@pytest.fixture(scope="session")
def seeded_database(django_db_setup, django_db_blocker):
    """Seed Sage & Stone site once for all E2E tests in session."""
    with django_db_blocker.unblock():
        # Seed fresh site for E2E tests
        _run_seed_command(clear=True)
        _run_seed_command()


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-GB",
    }


@pytest.fixture(scope="function")
def mobile_browser_context_args(browser_context_args):
    """Configure mobile browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 375, "height": 667},
        "locale": "en-GB",
        "is_mobile": True,
    }
