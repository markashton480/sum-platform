"""
Name: Pytest Django Configuration
Path: tests/conftest.py
Purpose: Configure Django/Wagtail settings and test database for pytest runs.
Family: Shared fixtures for the test suite.
Dependencies: Django test utilities, pytest.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from collections.abc import Generator

import django
import pytest
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = ROOT_DIR / "core"
TEST_PROJECT_DIR = CORE_DIR / "sum_core" / "test_project"

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sum_core.test_project.test_project.settings")
django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_environment() -> Generator[None, None, None]:
    """Set up Django and the test database for the test session."""

    setup_test_environment()
    db_config = setup_databases(verbosity=0, interactive=False, keepdb=False)
    try:
        yield
    finally:
        teardown_databases(db_config, verbosity=0)
        teardown_test_environment()
