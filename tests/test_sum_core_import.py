"""
Name: sum_core Import Tests
Path: tests/test_sum_core_import.py
Purpose: Basic sanity checks that sum_core is importable and exposes __version__.
Family: Part of the root test suite validating core package wiring.
Dependencies: sum_core
"""

from sum_core import __version__


def test_sum_core_has_version() -> None:
    assert isinstance(__version__, str)
    assert __version__
