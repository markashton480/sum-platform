"""
Name: Smoke Consumer Home App Config
Path: clients/_smoke_consumer/smoke_consumer/home/apps.py
Purpose: Django AppConfig for the smoke consumer home app.
Family: Validation/proof project for sum_core consumability.
Dependencies: django.apps.AppConfig
"""

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """Configuration for the smoke consumer home app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "smoke_consumer.home"
    label = "smoke_consumer_home"
    verbose_name = "Home"
