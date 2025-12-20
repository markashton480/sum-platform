"""
Django AppConfig for the client home app.

Replace 'test_project_2' with your actual project name after copying.
Both 'name' and 'label' must be updated.
"""
from __future__ import annotations

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """Configuration for the client home app."""

    default_auto_field = "django.db.models.BigAutoField"
    # Update these after renaming test_project_2:
    name = "test_project_2.home"
    label = "test_project_2_home"
    verbose_name = "Home"
