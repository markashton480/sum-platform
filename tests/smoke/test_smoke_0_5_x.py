"""
Name: Legacy 0.5.x Smoke Tests
Path: tests/smoke/test_smoke_0_5_x.py
Purpose: Provide stable smoke coverage for the frozen 0.5.x line.
Family: Smoke tests
Dependencies: pytest, sum_core test_project settings
"""

from __future__ import annotations

import importlib
import re

import pytest

pytestmark = pytest.mark.legacy_only


def test_sum_core_version_is_exposed() -> None:
    import sum_core

    version = getattr(sum_core, "__version__", "")
    assert isinstance(version, str)
    assert version.strip() != ""


def test_sum_core_version_has_major_minor() -> None:
    import sum_core

    version = str(getattr(sum_core, "__version__", ""))
    assert re.match(
        r"^\d+\.\d+\.\d+", version
    ), f"Expected semantic version 'MAJOR.MINOR.PATCH', got {version!r}"


def test_settings_module_importable() -> None:
    settings_module = importlib.import_module(
        "sum_core.test_project.test_project.settings"
    )
    assert hasattr(settings_module, "INSTALLED_APPS")
    assert hasattr(settings_module, "ROOT_URLCONF")
