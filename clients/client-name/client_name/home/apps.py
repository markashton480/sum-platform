"""
Django AppConfig for the client home app.

Replace 'client_name' with your actual project name after copying.
Both 'name' and 'label' must be updated.
"""
from __future__ import annotations

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """Configuration for the client home app."""

    default_auto_field = "django.db.models.BigAutoField"
    # Update these after renaming client_name:
    name = "client_name.home"
    label = "client_name_home"
    verbose_name = "Home"
