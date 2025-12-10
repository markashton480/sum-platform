"""
Name: SumCoreConfig
Path: core/sum_core/apps.py
Purpose: Django application configuration for the sum_core shared core app.
Family: Referenced by INSTALLED_APPS in client projects and sum_core.test_project.
Dependencies: django.apps.AppConfig
"""

from django.apps import AppConfig


class SumCoreConfig(AppConfig):
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "sum_core"

    def ready(self) -> None:
        """Wire up custom admin forms after all models are loaded."""
        from sum_core.branding.forms import SiteSettingsAdminForm
        from sum_core.branding.models import SiteSettings

        SiteSettings.base_form_class = SiteSettingsAdminForm
