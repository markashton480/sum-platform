"""
Name: SUM Client Home App Config
Path: clients/sum_client/sum_client/home/apps.py
Purpose: Django AppConfig for the sum_client home app.
Family: Client project consuming sum_core.
Dependencies: django.apps.AppConfig
"""
from __future__ import annotations

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """Configuration for the sum_client home app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "sum_client.home"
    label = "sum_client_home"
    verbose_name = "Home"
