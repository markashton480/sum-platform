"""
Name: Smoke Tests
Path: tests/test_smoke.py
Purpose: Basic smoke tests to validate pytest wiring
Family: pytest test suite
Dependencies: pytest, standard library
"""

import sys


def test_python_version() -> None:
    """Test that we're running Python 3.12+."""
    assert sys.version_info >= (3, 12), f"Expected Python 3.12+, got {sys.version_info}"


def test_import_standard_library() -> None:
    """Test that standard library imports work."""
    import os
    import pathlib

    assert os is not None
    assert pathlib is not None


def test_basic_assertion() -> None:
    """Test that basic assertions work."""
    assert True


