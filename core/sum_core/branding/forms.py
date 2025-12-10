"""
Name: Branding Admin Forms
Path: core/sum_core/branding/forms.py
Purpose: Provide custom Wagtail admin forms for branding-related settings.
Family: Used by branding.models.SiteSettings via base_form_class.
Dependencies: Django forms, Wagtail admin forms, branding.theme_presets, branding.models.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import forms
from wagtail.admin.forms.models import WagtailAdminModelForm

from sum_core.branding.theme_presets import THEME_PRESETS, get_theme_preset_choices

if TYPE_CHECKING:
    from sum_core.branding.models import SiteSettings


class SiteSettingsAdminForm(WagtailAdminModelForm):
    """Custom admin form for SiteSettings with theme preset support."""

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    class Meta:
        # Import here to avoid circular import at module load time
        from sum_core.branding.models import SiteSettings

        model = SiteSettings
        # Use exclude=[] instead of fields='__all__' to work around a quirk
        # where WagtailAdminModelForm doesn't resolve '__all__' properly for
        # construct_instance, causing form data to not be applied to the instance.
        # With exclude=[], _meta.fields becomes None which is handled correctly.
        exclude = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["theme_preset"].choices = get_theme_preset_choices()

    def save(self, commit: bool = True) -> SiteSettings:
        """Apply theme preset values if one was selected, then save."""
        instance = super().save(commit=False)

        preset_key = self.cleaned_data.get("theme_preset")
        if preset_key and preset_key in THEME_PRESETS:
            preset = THEME_PRESETS[preset_key]
            instance.primary_color = preset.primary_color
            instance.secondary_color = preset.secondary_color
            instance.accent_color = preset.accent_color
            instance.heading_font = preset.heading_font
            instance.body_font = preset.body_font

        if commit:
            instance.save()

        return instance

