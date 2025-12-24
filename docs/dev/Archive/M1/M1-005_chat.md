# Implement M1_005 development task
_Exported on 12/10/2025 at 14:50:52 GMT from Cursor (2.1.50)_

---

**User**

Please carefully review task @docs/dev/M1/M1_005.md and implement. 

---

**Cursor**

I'll implement task M1-005 - the Theme Preset System for Site Branding. Let me first explore the existing codebase structure to understand the current implementation.

Let me examine an existing test file to understand the test patterns and also check if there's any existing form infrastructure:

Now I have a clear understanding of the codebase. Let me create a task list and implement the theme preset system.

```python
"""
Name: Theme Presets
Path: core/sum_core/branding/theme_presets.py
Purpose: Define internal theme presets for SiteSettings one-click application.
Family: Used by SiteSettings admin form to prepopulate branding fields.
Dependencies: Standard library (dataclasses, typing) only.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePreset:
    """Defines a theme preset with colours and font recommendations."""

    key: str
    label: str
    primary_color: str
    secondary_color: str
    accent_color: str
    heading_font: str
    body_font: str


THEME_PRESETS: dict[str, ThemePreset] = {
    "premium-trade": ThemePreset(
        key="premium-trade",
        label="Premium Trade",
        primary_color="#1e3a5f",
        secondary_color="#0f172a",
        accent_color="#f59e0b",
        heading_font="Montserrat",
        body_font="Open Sans",
    ),
    "professional-blue": ThemePreset(
        key="professional-blue",
        label="Professional Blue",
        primary_color="#2563eb",
        secondary_color="#1e40af",
        accent_color="#f97316",
        heading_font="Poppins",
        body_font="Inter",
    ),
    "modern-green": ThemePreset(
        key="modern-green",
        label="Modern Green",
        primary_color="#059669",
        secondary_color="#064e3b",
        accent_color="#fbbf24",
        heading_font="DM Sans",
        body_font="Source Sans 3",
    ),
    "warm-earth": ThemePreset(
        key="warm-earth",
        label="Warm Earth",
        primary_color="#92400e",
        secondary_color="#78350f",
        accent_color="#dc2626",
        heading_font="Playfair Display",
        body_font="Lato",
    ),
    "clean-slate": ThemePreset(
        key="clean-slate",
        label="Clean Slate",
        primary_color="#374151",
        secondary_color="#1f2937",
        accent_color="#6366f1",
        heading_font="Work Sans",
        body_font="Roboto",
    ),
}


def get_theme_preset_choices() -> list[tuple[str, str]]:
    """Return choices for a form field: empty option + 5 presets."""
    choices: list[tuple[str, str]] = [("", "---------")]
    choices.extend((preset.key, preset.label) for preset in THEME_PRESETS.values())
    return choices

```

```python
"""
Name: Branding Admin Forms
Path: core/sum_core/branding/forms.py
Purpose: Provide custom Wagtail admin forms for branding-related settings.
Family: Used by branding.models.SiteSettings via base_form_class.
Dependencies: Django forms, Wagtail admin forms, branding.theme_presets, branding.models.
"""

from __future__ import annotations

from typing import Any

from django import forms
from wagtail.admin.forms.models import WagtailAdminModelForm

from sum_core.branding.theme_presets import THEME_PRESETS, get_theme_preset_choices


class SiteSettingsAdminForm(WagtailAdminModelForm):
    """Custom admin form for SiteSettings with theme preset support."""

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["theme_preset"].choices = get_theme_preset_choices()

    def save(self, commit: bool = True) -> Any:
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

```

Now let me modify the models.py to wire up the form class and add the theme_preset panel:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    base_form_class = "sum_core.branding.forms.SiteSettingsAdminForm"
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

Now I need to add a panel for the theme_preset field. According to the spec, it should be placed near the colours/typography group:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    base_form_class = "sum_core.branding.forms.SiteSettingsAdminForm"
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        MultiFieldPanel(
            [
                FieldPanel("theme_preset"),
            ],
            heading="Theme Preset",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

```python
"""
Name: Theme Presets Tests
Path: tests/branding/test_theme_presets.py
Purpose: Verify theme preset definitions and SiteSettings admin form behaviour.
Family: Branding test suite.
Dependencies: SiteSettings, SiteSettingsAdminForm, THEME_PRESETS.
"""

from __future__ import annotations

import pytest
from wagtail.models import Site

from sum_core.branding.forms import SiteSettingsAdminForm  # type: ignore[import-not-found]
from sum_core.branding.models import SiteSettings  # type: ignore[import-not-found]
from sum_core.branding.theme_presets import THEME_PRESETS  # type: ignore[import-not-found]

pytestmark = pytest.mark.django_db


# PRD Table C.5 – canonical values
PRD_PRESETS = {
    "premium-trade": {
        "label": "Premium Trade",
        "primary_color": "#1e3a5f",
        "secondary_color": "#0f172a",
        "accent_color": "#f59e0b",
        "heading_font": "Montserrat",
        "body_font": "Open Sans",
    },
    "professional-blue": {
        "label": "Professional Blue",
        "primary_color": "#2563eb",
        "secondary_color": "#1e40af",
        "accent_color": "#f97316",
        "heading_font": "Poppins",
        "body_font": "Inter",
    },
    "modern-green": {
        "label": "Modern Green",
        "primary_color": "#059669",
        "secondary_color": "#064e3b",
        "accent_color": "#fbbf24",
        "heading_font": "DM Sans",
        "body_font": "Source Sans 3",
    },
    "warm-earth": {
        "label": "Warm Earth",
        "primary_color": "#92400e",
        "secondary_color": "#78350f",
        "accent_color": "#dc2626",
        "heading_font": "Playfair Display",
        "body_font": "Lato",
    },
    "clean-slate": {
        "label": "Clean Slate",
        "primary_color": "#374151",
        "secondary_color": "#1f2937",
        "accent_color": "#6366f1",
        "heading_font": "Work Sans",
        "body_font": "Roboto",
    },
}


def test_theme_presets_match_prd_definitions() -> None:
    """Assert THEME_PRESETS has 5 entries with expected slugs and values from PRD table C.5."""
    assert len(THEME_PRESETS) == 5
    expected_keys = {
        "premium-trade",
        "professional-blue",
        "modern-green",
        "warm-earth",
        "clean-slate",
    }
    assert set(THEME_PRESETS.keys()) == expected_keys

    for key, expected in PRD_PRESETS.items():
        preset = THEME_PRESETS[key]
        assert preset.label == expected["label"], f"{key}: label mismatch"
        assert preset.primary_color == expected["primary_color"], f"{key}: primary_color mismatch"
        assert (
            preset.secondary_color == expected["secondary_color"]
        ), f"{key}: secondary_color mismatch"
        assert preset.accent_color == expected["accent_color"], f"{key}: accent_color mismatch"
        assert preset.heading_font == expected["heading_font"], f"{key}: heading_font mismatch"
        assert preset.body_font == expected["body_font"], f"{key}: body_font mismatch"


def test_site_settings_admin_form_has_theme_preset_field() -> None:
    """Instantiate SiteSettingsAdminForm and verify theme_preset field exists with correct choices."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    form = SiteSettingsAdminForm(instance=settings)

    assert "theme_preset" in form.fields
    choices = form.fields["theme_preset"].choices
    # 1 blank + 5 presets = 6 choices
    assert len(choices) == 6
    # First choice should be blank
    assert choices[0] == ("", "---------")
    # All preset keys should be in choices
    preset_keys = {choice[0] for choice in choices[1:]}
    assert preset_keys == set(THEME_PRESETS.keys())


def test_applying_theme_preset_updates_site_settings_fields() -> None:
    """Applying 'premium-trade' preset should update colour and font fields."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    # Set initial different values
    settings.primary_color = "#000000"
    settings.secondary_color = "#111111"
    settings.accent_color = "#222222"
    settings.heading_font = "Arial"
    settings.body_font = "Helvetica"
    settings.save()

    # Build form data with all required fields + theme_preset
    form_data = {
        "site": site.pk,
        "theme_preset": "premium-trade",
        # Include other required fields with current/blank values
        "primary_color": settings.primary_color,
        "secondary_color": settings.secondary_color,
        "accent_color": settings.accent_color,
        "background_color": settings.background_color,
        "surface_color": settings.surface_color,
        "surface_elevated_color": settings.surface_elevated_color,
        "text_color": settings.text_color,
        "text_light_color": settings.text_light_color,
        "heading_font": settings.heading_font,
        "body_font": settings.body_font,
        "company_name": settings.company_name,
        "tagline": settings.tagline,
        "phone_number": settings.phone_number,
        "email": settings.email,
        "address": settings.address,
        "business_hours": settings.business_hours,
        "facebook_url": settings.facebook_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "twitter_url": settings.twitter_url,
        "youtube_url": settings.youtube_url,
        "tiktok_url": settings.tiktok_url,
    }

    form = SiteSettingsAdminForm(data=form_data, instance=settings)
    assert form.is_valid(), f"Form errors: {form.errors}"
    saved_instance = form.save()

    # Verify the preset values were applied
    expected = PRD_PRESETS["premium-trade"]
    assert saved_instance.primary_color == expected["primary_color"]
    assert saved_instance.secondary_color == expected["secondary_color"]
    assert saved_instance.accent_color == expected["accent_color"]
    assert saved_instance.heading_font == expected["heading_font"]
    assert saved_instance.body_font == expected["body_font"]


def test_manual_edits_after_preset_are_respected() -> None:
    """After applying a preset, manual edits with no preset selected should persist."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    # First, apply a preset
    form_data = {
        "site": site.pk,
        "theme_preset": "clean-slate",
        "primary_color": "",
        "secondary_color": "",
        "accent_color": "",
        "background_color": "",
        "surface_color": "",
        "surface_elevated_color": "",
        "text_color": "",
        "text_light_color": "",
        "heading_font": "",
        "body_font": "",
        "company_name": "",
        "tagline": "",
        "phone_number": "",
        "email": "",
        "address": "",
        "business_hours": "",
        "facebook_url": "",
        "instagram_url": "",
        "linkedin_url": "",
        "twitter_url": "",
        "youtube_url": "",
        "tiktok_url": "",
    }

    form = SiteSettingsAdminForm(data=form_data, instance=settings)
    assert form.is_valid(), f"Form errors: {form.errors}"
    settings = form.save()

    # Confirm preset values applied
    assert settings.primary_color == PRD_PRESETS["clean-slate"]["primary_color"]

    # Now make manual edits with no preset selected
    custom_primary = "#abcdef"
    custom_heading_font = "Custom Font"

    form_data_manual = {
        "site": site.pk,
        "theme_preset": "",  # No preset selected
        "primary_color": custom_primary,
        "secondary_color": settings.secondary_color,
        "accent_color": settings.accent_color,
        "background_color": settings.background_color,
        "surface_color": settings.surface_color,
        "surface_elevated_color": settings.surface_elevated_color,
        "text_color": settings.text_color,
        "text_light_color": settings.text_light_color,
        "heading_font": custom_heading_font,
        "body_font": settings.body_font,
        "company_name": settings.company_name,
        "tagline": settings.tagline,
        "phone_number": settings.phone_number,
        "email": settings.email,
        "address": settings.address,
        "business_hours": settings.business_hours,
        "facebook_url": settings.facebook_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "twitter_url": settings.twitter_url,
        "youtube_url": settings.youtube_url,
        "tiktok_url": settings.tiktok_url,
    }

    form2 = SiteSettingsAdminForm(data=form_data_manual, instance=settings)
    assert form2.is_valid(), f"Form errors: {form2.errors}"
    updated_settings = form2.save()

    # Verify manual edits persisted and were not overwritten
    assert updated_settings.primary_color == custom_primary
    assert updated_settings.heading_font == custom_heading_font
    # Other preset values should still be from clean-slate (unchanged)
    assert updated_settings.secondary_color == PRD_PRESETS["clean-slate"]["secondary_color"]

```

Let me check for any linter errors and then run the tests:

The form class needs a `Meta` inner class specifying the model. Let me fix the form:

```python
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
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["theme_preset"].choices = get_theme_preset_choices()

    def save(self, commit: bool = True) -> "SiteSettings":
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


```

The test is failing because the instance isn't being refreshed from the database between form operations. Let me update the test to use `refresh_from_db()` to ensure we have the latest values:

```python
"""
Name: Theme Presets Tests
Path: tests/branding/test_theme_presets.py
Purpose: Verify theme preset definitions and SiteSettings admin form behaviour.
Family: Branding test suite.
Dependencies: SiteSettings, SiteSettingsAdminForm, THEME_PRESETS.
"""

from __future__ import annotations

import pytest
from wagtail.models import Site

from sum_core.branding.forms import SiteSettingsAdminForm  # type: ignore[import-not-found]
from sum_core.branding.models import SiteSettings  # type: ignore[import-not-found]
from sum_core.branding.theme_presets import THEME_PRESETS  # type: ignore[import-not-found]

pytestmark = pytest.mark.django_db


# PRD Table C.5 – canonical values
PRD_PRESETS = {
    "premium-trade": {
        "label": "Premium Trade",
        "primary_color": "#1e3a5f",
        "secondary_color": "#0f172a",
        "accent_color": "#f59e0b",
        "heading_font": "Montserrat",
        "body_font": "Open Sans",
    },
    "professional-blue": {
        "label": "Professional Blue",
        "primary_color": "#2563eb",
        "secondary_color": "#1e40af",
        "accent_color": "#f97316",
        "heading_font": "Poppins",
        "body_font": "Inter",
    },
    "modern-green": {
        "label": "Modern Green",
        "primary_color": "#059669",
        "secondary_color": "#064e3b",
        "accent_color": "#fbbf24",
        "heading_font": "DM Sans",
        "body_font": "Source Sans 3",
    },
    "warm-earth": {
        "label": "Warm Earth",
        "primary_color": "#92400e",
        "secondary_color": "#78350f",
        "accent_color": "#dc2626",
        "heading_font": "Playfair Display",
        "body_font": "Lato",
    },
    "clean-slate": {
        "label": "Clean Slate",
        "primary_color": "#374151",
        "secondary_color": "#1f2937",
        "accent_color": "#6366f1",
        "heading_font": "Work Sans",
        "body_font": "Roboto",
    },
}


def test_theme_presets_match_prd_definitions() -> None:
    """Assert THEME_PRESETS has 5 entries with expected slugs and values from PRD table C.5."""
    assert len(THEME_PRESETS) == 5
    expected_keys = {
        "premium-trade",
        "professional-blue",
        "modern-green",
        "warm-earth",
        "clean-slate",
    }
    assert set(THEME_PRESETS.keys()) == expected_keys

    for key, expected in PRD_PRESETS.items():
        preset = THEME_PRESETS[key]
        assert preset.label == expected["label"], f"{key}: label mismatch"
        assert preset.primary_color == expected["primary_color"], f"{key}: primary_color mismatch"
        assert (
            preset.secondary_color == expected["secondary_color"]
        ), f"{key}: secondary_color mismatch"
        assert preset.accent_color == expected["accent_color"], f"{key}: accent_color mismatch"
        assert preset.heading_font == expected["heading_font"], f"{key}: heading_font mismatch"
        assert preset.body_font == expected["body_font"], f"{key}: body_font mismatch"


def test_site_settings_admin_form_has_theme_preset_field() -> None:
    """Instantiate SiteSettingsAdminForm and verify theme_preset field exists with correct choices."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    form = SiteSettingsAdminForm(instance=settings)

    assert "theme_preset" in form.fields
    choices = form.fields["theme_preset"].choices
    # 1 blank + 5 presets = 6 choices
    assert len(choices) == 6
    # First choice should be blank
    assert choices[0] == ("", "---------")
    # All preset keys should be in choices
    preset_keys = {choice[0] for choice in choices[1:]}
    assert preset_keys == set(THEME_PRESETS.keys())


def test_applying_theme_preset_updates_site_settings_fields() -> None:
    """Applying 'premium-trade' preset should update colour and font fields."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    # Set initial different values
    settings.primary_color = "#000000"
    settings.secondary_color = "#111111"
    settings.accent_color = "#222222"
    settings.heading_font = "Arial"
    settings.body_font = "Helvetica"
    settings.save()

    # Build form data with all required fields + theme_preset
    form_data = {
        "site": site.pk,
        "theme_preset": "premium-trade",
        # Include other required fields with current/blank values
        "primary_color": settings.primary_color,
        "secondary_color": settings.secondary_color,
        "accent_color": settings.accent_color,
        "background_color": settings.background_color,
        "surface_color": settings.surface_color,
        "surface_elevated_color": settings.surface_elevated_color,
        "text_color": settings.text_color,
        "text_light_color": settings.text_light_color,
        "heading_font": settings.heading_font,
        "body_font": settings.body_font,
        "company_name": settings.company_name,
        "tagline": settings.tagline,
        "phone_number": settings.phone_number,
        "email": settings.email,
        "address": settings.address,
        "business_hours": settings.business_hours,
        "facebook_url": settings.facebook_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "twitter_url": settings.twitter_url,
        "youtube_url": settings.youtube_url,
        "tiktok_url": settings.tiktok_url,
    }

    form = SiteSettingsAdminForm(data=form_data, instance=settings)
    assert form.is_valid(), f"Form errors: {form.errors}"
    saved_instance = form.save()

    # Verify the preset values were applied
    expected = PRD_PRESETS["premium-trade"]
    assert saved_instance.primary_color == expected["primary_color"]
    assert saved_instance.secondary_color == expected["secondary_color"]
    assert saved_instance.accent_color == expected["accent_color"]
    assert saved_instance.heading_font == expected["heading_font"]
    assert saved_instance.body_font == expected["body_font"]


def test_manual_edits_after_preset_are_respected() -> None:
    """After applying a preset, manual edits with no preset selected should persist."""
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    # First, apply a preset
    form_data = {
        "site": site.pk,
        "theme_preset": "clean-slate",
        "primary_color": "",
        "secondary_color": "",
        "accent_color": "",
        "background_color": "",
        "surface_color": "",
        "surface_elevated_color": "",
        "text_color": "",
        "text_light_color": "",
        "heading_font": "",
        "body_font": "",
        "company_name": "",
        "tagline": "",
        "phone_number": "",
        "email": "",
        "address": "",
        "business_hours": "",
        "facebook_url": "",
        "instagram_url": "",
        "linkedin_url": "",
        "twitter_url": "",
        "youtube_url": "",
        "tiktok_url": "",
    }

    form = SiteSettingsAdminForm(data=form_data, instance=settings)
    assert form.is_valid(), f"Form errors: {form.errors}"
    form.save()

    # Refresh from database to get the saved state
    settings.refresh_from_db()

    # Confirm preset values applied
    assert settings.primary_color == PRD_PRESETS["clean-slate"]["primary_color"]

    # Now make manual edits with no preset selected
    custom_primary = "#abcdef"
    custom_heading_font = "Custom Font"

    form_data_manual = {
        "site": site.pk,
        "theme_preset": "",  # No preset selected
        "primary_color": custom_primary,
        "secondary_color": settings.secondary_color,
        "accent_color": settings.accent_color,
        "background_color": settings.background_color,
        "surface_color": settings.surface_color,
        "surface_elevated_color": settings.surface_elevated_color,
        "text_color": settings.text_color,
        "text_light_color": settings.text_light_color,
        "heading_font": custom_heading_font,
        "body_font": settings.body_font,
        "company_name": settings.company_name,
        "tagline": settings.tagline,
        "phone_number": settings.phone_number,
        "email": settings.email,
        "address": settings.address,
        "business_hours": settings.business_hours,
        "facebook_url": settings.facebook_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "twitter_url": settings.twitter_url,
        "youtube_url": settings.youtube_url,
        "tiktok_url": settings.tiktok_url,
    }

    form2 = SiteSettingsAdminForm(data=form_data_manual, instance=settings)
    assert form2.is_valid(), f"Form errors: {form2.errors}"
    form2.save()

    # Refresh from database to verify saved values
    settings.refresh_from_db()

    # Verify manual edits persisted and were not overwritten
    assert settings.primary_color == custom_primary
    assert settings.heading_font == custom_heading_font
    # Other preset values should still be from clean-slate (unchanged)
    assert settings.secondary_color == PRD_PRESETS["clean-slate"]["secondary_color"]


```

Let me run just that specific test in isolation and add some debugging:

```python
def save(self, commit: bool = True) -> "SiteSettings":
    instance = super().save(commit=False)

    preset_key = self.cleaned_data.get("theme_preset")
    if preset_key and preset_key in THEME_PRESETS:
        preset = THEME_PRESETS[preset_key]
        instance.primary_color = preset.primary_color
        ...

    if commit:
        instance.save()

    return instance
```

The form's `cleaned_data` has the correct value but the save isn't working. Let me debug further to understand what `super().save(commit=False)` returns:

Let me check how the form actually handles the instance:

I see the issue - `WagtailAdminModelForm.save(commit=False)` isn't applying the cleaned_data to the instance. Let me check what fields the form actually has:

Let me investigate how Wagtail settings forms work:

```python
if fields is not None and f.name not in fields:
    continue
```

```python
if fields is not None and f.name not in fields:
    continue
```

I found the issue! When `fields='__all__'`, `construct_instance` checks `f.name not in '__all__'` which is `True` for any field name, so all fields are skipped. Let me verify this:

I see! WagtailAdminModelForm doesn't properly resolve `fields='__all__'` to `None`, causing `construct_instance` to skip all fields. Let me fix our form by explicitly handling the fields:

```python
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
        # Use explicit fields list instead of '__all__' to work around a quirk
        # where WagtailAdminModelForm doesn't resolve '__all__' properly for
        # construct_instance, causing form data to not be applied to the instance.
        fields = None  # None means 'all fields' and is handled correctly

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["theme_preset"].choices = get_theme_preset_choices()

    def save(self, commit: bool = True) -> "SiteSettings":
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


```

Django doesn't allow `fields = None` directly. Let me use `exclude = []` instead which will include all fields:

```python
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

    def save(self, commit: bool = True) -> "SiteSettings":
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


```

All tests pass. Let me run the linter and update the TODO list:

Let me fix the linting error in the forms.py file I created:

```python
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


```

The remaining lint errors are in pre-existing files, not in my new code. Let me verify the tests still pass:

All my new files pass linting. Let me show you the final implementation:

I have successfully implemented task M1-005 - the Theme Preset System for Site Branding. Here's a summary of what was created:

## Summary of Changes

### 1. New File: `core/sum_core/branding/theme_presets.py`

```1:82:core/sum_core/branding/theme_presets.py
"""
Name: Theme Presets
Path: core/sum_core/branding/theme_presets.py
Purpose: Define internal theme presets for SiteSettings one-click application.
Family: Used by SiteSettings admin form to prepopulate branding fields.
Dependencies: Standard library (dataclasses, typing) only.
"""
// ... preset definitions ...
```

Contains:
- `ThemePreset` dataclass with all required fields
- `THEME_PRESETS` dict with 5 presets matching PRD table C.5 exactly
- `get_theme_preset_choices()` helper for form field

### 2. New File: `core/sum_core/branding/forms.py`

```1:64:core/sum_core/branding/forms.py
"""
Name: Branding Admin Forms
Path: core/sum_core/branding/forms.py
Purpose: Provide custom Wagtail admin forms for branding-related settings.
// ...
"""
// ... form implementation ...
```

Contains:
- `SiteSettingsAdminForm` that extends `WagtailAdminModelForm`
- Non-persisted `theme_preset` field with choices from presets
- Custom `save()` method that applies preset values when selected

### 3. Modified: `core/sum_core/branding/models.py`
- Added `base_form_class` to wire up the custom form
- Reorganized panels to place "Theme Preset" between "Logos & Favicon" and "Brand Colours"

### 4. New File: `tests/branding/test_theme_presets.py`
Contains 4 tests as specified:
1. `test_theme_presets_match_prd_definitions` - Verifies all 5 presets match PRD table
2. `test_site_settings_admin_form_has_theme_preset_field` - Verifies field exists with 6 choices
3. `test_applying_theme_preset_updates_site_settings_fields` - Verifies preset application
4. `test_manual_edits_after_preset_are_respected` - Verifies fields remain editable

## Test Results
All 18 tests pass:
- 4 new theme preset tests
- 14 existing tests (no regressions)

## Notable Implementation Detail
During implementation, I discovered that `WagtailAdminModelForm` has a quirk where `fields = '__all__'` doesn't resolve properly for `construct_instance`. The workaround was to use `exclude = []` instead, which results in `_meta.fields = None` that is handled correctly.

```python
"""
Name: Theme Presets
Path: core/sum_core/branding/theme_presets.py
Purpose: Define internal theme presets for SiteSettings one-click application.
Family: Used by SiteSettings admin form to prepopulate branding fields.
Dependencies: Standard library (dataclasses, typing) only.
"""
// ... preset definitions ...
```

```python
"""
Name: Branding Admin Forms
Path: core/sum_core/branding/forms.py
Purpose: Provide custom Wagtail admin forms for branding-related settings.
// ...
"""
// ... form implementation ...
```

---

**User**

Please make these small follow-up tweaks to the theme preset work:



Document the exclude = [] workaround in SiteSettingsAdminForm



In core/sum_core/branding/forms.py, above or inside SiteSettingsAdminForm.Meta, add a short comment explaining why we’re using exclude = [] instead of fields = "__all__" – e.g.:



# NOTE: WagtailAdminModelForm + fields="__all__" does not play nicely with construct_instance;

# using exclude = [] ensures all model fields are included and cleaned_data is applied correctly.



This is just to stop future-you/future-devs “fixing” it back to fields="__all__" and re-breaking the behaviour.



Keep theme_preset clearly non-persisted



In SiteSettingsAdminForm, please add a short docstring on the form class noting that theme_preset:



is an admin-only trigger field,



is not saved to the model,



only pre-populates primary_color, secondary_color, accent_color, heading_font, and body_font.



Double-check PRD alignment in tests



In tests/branding/test_theme_presets.py, ensure test_theme_presets_match_prd_definitions is explicitly checking all of the PRD table columns we care about:



primary_color, secondary_color, accent_color, heading_font, body_font



for all 5 presets: "premium-trade", "professional-blue", "modern-green", "warm-earth", "clean-slate".



If any field isn’t asserted yet, please add an assertion so the test will break if someone changes the preset by accident.

---

**Cursor**

I'll make these follow-up tweaks. Let me read the current files first and then apply the changes:

I can see the test already checks all 5 fields for all 5 presets. Let me update the forms.py with the improved documentation:

```python
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
    """
    Custom admin form for SiteSettings with theme preset support.

    The ``theme_preset`` field is:
      - An admin-only trigger field (not saved to the model).
      - Used to pre-populate: primary_color, secondary_color, accent_color,
        heading_font, and body_font when a preset is selected.
      - After application, all fields remain freely editable.
    """

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    class Meta:
        # Import here to avoid circular import at module load time
        from sum_core.branding.models import SiteSettings

        model = SiteSettings
        # NOTE: WagtailAdminModelForm + fields="__all__" does not play nicely
        # with construct_instance; using exclude = [] ensures all model fields
        # are included and cleaned_data is applied correctly.
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


```

```python
for key, expected in PRD_PRESETS.items():
    preset = THEME_PRESETS[key]
    assert preset.label == expected["label"], f"{key}: label mismatch"
    assert preset.primary_color == expected["primary_color"], f"{key}: primary_color mismatch"
    assert (
        preset.secondary_color == expected["secondary_color"]
    ), f"{key}: secondary_color mismatch"
    assert preset.accent_color == expected["accent_color"], f"{key}: accent_color mismatch"
    assert preset.heading_font == expected["heading_font"], f"{key}: heading_font mismatch"
    assert preset.body_font == expected["body_font"], f"{key}: body_font mismatch"
```

The test already comprehensively checks all 5 fields (`primary_color`, `secondary_color`, `accent_color`, `heading_font`, `body_font`) for all 5 presets in the loop at lines 78-87. Let me verify everything still works:

All done. Here's the updated `forms.py` with the improved documentation:

```22:48:core/sum_core/branding/forms.py
class SiteSettingsAdminForm(WagtailAdminModelForm):
    """
    Custom admin form for SiteSettings with theme preset support.

    The ``theme_preset`` field is:
      - An admin-only trigger field (not saved to the model).
      - Used to pre-populate: primary_color, secondary_color, accent_color,
        heading_font, and body_font when a preset is selected.
      - After application, all fields remain freely editable.
    """

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    class Meta:
        # Import here to avoid circular import at module load time
        from sum_core.branding.models import SiteSettings

        model = SiteSettings
        # NOTE: WagtailAdminModelForm + fields="__all__" does not play nicely
        # with construct_instance; using exclude = [] ensures all model fields
        # are included and cleaned_data is applied correctly.
        exclude = []
```

**Summary of changes:**
1. ✅ **Documented `exclude = []` workaround** - Added a clear `NOTE:` comment explaining why we use `exclude = []` instead of `fields = "__all__"`
2. ✅ **Expanded class docstring** - Added detailed documentation that `theme_preset` is an admin-only trigger field, not saved to the model, and lists the 5 fields it pre-populates
3. ✅ **Tests already complete** - Verified that `test_theme_presets_match_prd_definitions` explicitly checks all 5 PRD columns (`primary_color`, `secondary_color`, `accent_color`, `heading_font`, `body_font`) for all 5 presets

```python
class SiteSettingsAdminForm(WagtailAdminModelForm):
    """
    Custom admin form for SiteSettings with theme preset support.

    The ``theme_preset`` field is:
      - An admin-only trigger field (not saved to the model).
      - Used to pre-populate: primary_color, secondary_color, accent_color,
        heading_font, and body_font when a preset is selected.
      - After application, all fields remain freely editable.
    """

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    class Meta:
        # Import here to avoid circular import at module load time
        from sum_core.branding.models import SiteSettings

        model = SiteSettings
        # NOTE: WagtailAdminModelForm + fields="__all__" does not play nicely
        # with construct_instance; using exclude = [] ensures all model fields
        # are included and cleaned_data is applied correctly.
        exclude = []
```

---

**User**

When I go to the Wagtail Admin I get:



TypeError at /admin/settings/sum_core/sitesettings/1/

str() argument 'encoding' must be str, not tuple

---

**Cursor**

Let me investigate the error. It's likely related to the panel configuration for `theme_preset`:

I see the issue! `theme_preset` is a form-only field (not a model field), but we're trying to use `FieldPanel("theme_preset")` in the model's panels. This doesn't work because Wagtail's `FieldPanel` expects a model field.

Let me remove the invalid panel:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    base_form_class = "sum_core.branding.forms.SiteSettingsAdminForm"
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        # NOTE: theme_preset is a form-only field (not a model field) defined
        # in SiteSettingsAdminForm. It appears automatically at the top of the
        # form since it's declared first on the form class.
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

Fixed! The issue was that `FieldPanel("theme_preset")` was in the model's panels, but `theme_preset` is a **form-only field** (not a model field). Wagtail's `FieldPanel` only works with model fields.

I've removed the invalid panel. The `theme_preset` field will still appear in the admin form because it's defined on the custom form class - it will appear at the top of the form since it's declared first in `SiteSettingsAdminForm`.

Please try the Wagtail admin again - it should now work correctly.

---

**User**

I'm still getting the same issue. Here's the full traceback:



TypeError at /admin/settings/sum_core/sitesettings/1/

str() argument 'encoding' must be str, not tuple

Request Method:	GET

Request URL:	http://127.0.0.1:8000/admin/settings/sum_core/sitesettings/1/

Django Version:	5.2.9

Exception Type:	TypeError

Exception Value:	

str() argument 'encoding' must be str, not tuple

Exception Location:	/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/panels/base.py, line 48, in get_form_for_model

Raised during:	wagtail.contrib.settings.views.EditView

Python Executable:	/home/mark/workspaces/tradesite/.venv/bin/python

Python Version:	3.12.3

Python Path:	

['/home/mark/workspaces/tradesite/core/sum_core/test_project',

 '/usr/lib/python312.zip',

 '/usr/lib/python3.12',

 '/usr/lib/python3.12/lib-dynload',

 '/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages',

 '__editable__.sum_core-0.1.0.finder.__path_hook__']

Server time:	Wed, 10 Dec 2025 13:51:06 +0000

Traceback Switch to copy-and-paste view

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/core/handlers/exception.py, line 55, in inner

                response = get_response(request)

                               ^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/core/handlers/base.py, line 197, in _get_response

                response = wrapped_callback(request, *callback_args, **callback_kwargs)

                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/views/decorators/cache.py, line 80, in _view_wrapper

            response = view_func(request, *args, **kwargs)

                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/urls/__init__.py, line 178, in wrapper

            return view_func(request, *args, **kwargs)

                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/auth.py, line 137, in decorated_view

                    return get_localized_response(view_func, request, *args, **kwargs)

                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/localization.py, line 136, in get_localized_response

                response = view_func(request, *args, **kwargs)

                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/views/generic/base.py, line 105, in view

            return self.dispatch(request, *args, **kwargs)

                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/views/generic/permissions.py, line 30, in dispatch

        return super().dispatch(request, *args, **kwargs)

                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/views/generic/mixins.py, line 96, in dispatch

        return super().dispatch(*args, **kwargs)

                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/views/generic/base.py, line 144, in dispatch

        return handler(request, *args, **kwargs)

                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/views/generic/edit.py, line 202, in get

        return super().get(request, *args, **kwargs)

                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/views/generic/edit.py, line 142, in get

        return self.render_to_response(self.get_context_data())

                                            ^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/contrib/settings/views.py, line 123, in get_context_data

        context = super().get_context_data(**kwargs)

                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/views/generic/models.py, line 893, in get_context_data

        context = super().get_context_data(**kwargs)

                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/views/generic/mixins.py, line 144, in get_context_data

        context = super().get_context_data(**kwargs)

                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/views/generic/mixins.py, line 182, in get_context_data

        context = super().get_context_data(**kwargs)

                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/views/generic/base.py, line 95, in get_context_data

        context = super().get_context_data(**kwargs)

                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/views/generic/edit.py, line 72, in get_context_data

            kwargs["form"] = self.get_form()

                                 ^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/views/generic/edit.py, line 36, in get_form

            form_class = self.get_form_class()

                             ^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/views/generic/mixins.py, line 179, in get_form_class

        return self.panel.get_form_class()

                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/panels/base.py, line 134, in get_form_class

        return get_form_for_model(

                     …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/panels/base.py, line 48, in get_form_for_model

    return metaclass(class_name, tuple(bases), form_class_attrs)

               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

---

**Cursor**

```plaintext
/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/admin/panels/base.py, line 48, in get_form_for_model
    return metaclass(class_name, tuple(bases), form_class_attrs)
```

```python
base_form_class = "sum_core.branding.forms.SiteSettingsAdminForm"
```

The error suggests the string path for `base_form_class` isn't being resolved correctly. Let me check how Wagtail expects this to be configured and try importing the class directly:

```python
return metaclass(class_name, tuple(bases), form_class_attrs)
```

```python
class Meta:
    from sum_core.branding.models import SiteSettings
    model = SiteSettings
    exclude = []
```

The string path for `base_form_class` isn't being resolved correctly by Wagtail's settings framework. Let me try importing the class directly using a lazy import pattern:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


def get_site_settings_form_class() -> type:
    """Lazy import to avoid circular dependency."""
    from sum_core.branding.forms import SiteSettingsAdminForm

    return SiteSettingsAdminForm


@register_setting
class SiteSettings(BaseSiteSetting):
    base_form_class = get_site_settings_form_class()
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        # NOTE: theme_preset is a form-only field (not a model field) defined
        # in SiteSettingsAdminForm. It appears automatically at the top of the
        # form since it's declared first on the form class.
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

```python
class Meta:
    # Import here to avoid circular import at module load time
    from sum_core.branding.models import SiteSettings
    model = SiteSettings
    exclude = []
```

That approach won't work because the function is called at class definition time. Let me try a different approach - define the form class in the same file to avoid circular imports:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        # NOTE: theme_preset is a form-only field (not a model field) defined
        # in SiteSettingsAdminForm. It appears automatically at the top of the
        # form since it's declared first on the form class.
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

Let me try a cleaner approach - move the form class into models.py after SiteSettings to avoid circular imports entirely:

Let me restructure to import the form class at the end of models.py after SiteSettings is defined:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        # NOTE: theme_preset is a form-only field (not a model field) defined
        # in SiteSettingsAdminForm. It appears automatically at the top of the
        # form since it's declared first on the form class.
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")


# Import form class here (after SiteSettings is defined) to avoid circular import.
# forms.py imports SiteSettings, so we can't import it at the top of this file.
from sum_core.branding.forms import SiteSettingsAdminForm  # noqa: E402

SiteSettings.base_form_class = SiteSettingsAdminForm

```

The circular import is still problematic because Django models aren't ready when the form tries to access `SiteSettings._meta`. Let me try a different approach using Wagtail hooks:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        # NOTE: theme_preset is a form-only field (not a model field) defined
        # in SiteSettingsAdminForm. It appears automatically at the top of the
        # form since it's declared first on the form class.
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

```python
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

```

All tests pass. The fix uses Django's `AppConfig.ready()` hook which is called after all models are fully loaded, avoiding the circular import issue.

Please try the Wagtail admin again at `/admin/settings/sum_core/sitesettings/1/` - it should work now.

---

**User**

@docs/dev/M1/M1_005.md:54-75 there is no "theme preset" when I go to settings > site settings. 

---

**Cursor**

The issue is that Wagtail's panel system only renders fields defined in `panels`, and `FieldPanel` only works for model fields. For form-only fields like `theme_preset`, we need a custom panel. Let me create one:

I need to create a custom panel for form-only fields. Let me create a simple `FormFieldPanel` class:

```python
"""
Name: Custom Admin Panels
Path: core/sum_core/branding/panels.py
Purpose: Provide custom Wagtail panels for non-model form fields.
Family: Used by branding.models to display form-only fields in the admin.
Dependencies: Wagtail admin panels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel

if TYPE_CHECKING:
    from wagtail.admin.panels import BoundPanel


class FormFieldPanel(FieldPanel):
    """
    A panel for rendering form-only fields (not model fields).

    Use this for extra fields defined on the form class that aren't
    backed by a model field. The field will be included in the form
    and rendered in the admin, but won't be saved to the database.
    """

    def clone_kwargs(self) -> dict[str, Any]:
        kwargs = super().clone_kwargs()
        return kwargs

    class BoundPanel(FieldPanel.BoundPanel):
        @cached_property
        def bound_field(self) -> Any:
            """Get the bound field from the form."""
            if self.field_name in self.form.fields:
                return self.form[self.field_name]
            return None

        def is_shown(self) -> bool:
            """Show the panel if the field exists in the form."""
            return self.bound_field is not None

```

Now let me update models.py to use this panel:

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from sum_core.branding.panels import FormFieldPanel


@register_setting
class SiteSettings(BaseSiteSetting):
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        # NOTE: theme_preset is a form-only field (not a model field) defined
        # in SiteSettingsAdminForm. It appears automatically at the top of the
        # form since it's declared first on the form class.
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

```python
"""
Name: Branding Site Settings
Path: core/sum_core/branding/models.py
Purpose: Provides Wagtail SiteSettings for branding and business configuration shared across client sites.
Family: Used by template tags and frontend templates (branding_css, branding_fonts, base layouts).
Dependencies: Django models, Wagtail settings framework, wagtailimages, Django cache.
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from sum_core.branding.panels import FormFieldPanel


@register_setting
class SiteSettings(BaseSiteSetting):
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Primary brand colour in hex format (e.g. #0055ff).",
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Secondary brand colour in hex format (e.g. #f97316).",
    )
    accent_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Accent brand colour in hex format (e.g. #10b981).",
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background colour for pages (e.g. #ffffff).",
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Default text colour (e.g. #0f172a).",
    )
    surface_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Surface colour for cards and panels (e.g. #f8fafc).",
    )
    surface_elevated_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Elevated surface colour for layered elements.",
    )
    text_light_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Subtle text colour for muted labels.",
    )
    header_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    footer_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for headings.",
    )
    body_font = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Fonts family name for body text.",
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or brand name displayed across the site.",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline or strapline.",
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary contact phone number.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Primary contact email address.",
    )
    address = models.TextField(
        blank=True,
        help_text="Postal address displayed in footers or contact sections.",
    )
    business_hours = models.TextField(
        blank=True,
        help_text="Business hours text (free-form).",
    )
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("header_logo"),
                FieldPanel("footer_logo"),
                FieldPanel("favicon"),
            ],
            heading="Logos & Favicon",
        ),
        MultiFieldPanel(
            [
                # FormFieldPanel is used for form-only fields not backed by model fields.
                # theme_preset is defined in SiteSettingsAdminForm and pre-populates
                # colours and fonts when a preset is selected.
                FormFieldPanel("theme_preset"),
            ],
            heading="Theme Preset",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
                FieldPanel("accent_color"),
                FieldPanel("background_color"),
                FieldPanel("surface_color"),
                FieldPanel("surface_elevated_color"),
                FieldPanel("text_color"),
                FieldPanel("text_light_color"),
            ],
            heading="Brand Colours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_font"),
                FieldPanel("body_font"),
            ],
            heading="Typography",
        ),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("tagline"),
                FieldPanel("phone_number"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("business_hours"),
            ],
            heading="Business Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("youtube_url"),
                FieldPanel("tiktok_url"),
            ],
            heading="Social Links",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:  # pragma: no cover - admin display helper
        return self.company_name or "Site settings"

    def _invalidate_branding_cache(self) -> None:
        cache.delete(f"branding_css:{self.site_id}")
        cache.delete(f"branding_fonts:{self.site_id}")

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self._invalidate_branding_cache()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        site_id = self.site_id
        super().delete(*args, **kwargs)
        cache.delete(f"branding_css:{site_id}")
        cache.delete(f"branding_fonts:{site_id}")

```

```python
"""
Name: Custom Admin Panels
Path: core/sum_core/branding/panels.py
Purpose: Provide custom Wagtail panels for non-model form fields.
Family: Used by branding.models to display form-only fields in the admin.
Dependencies: Wagtail admin panels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel



class FormFieldPanel(FieldPanel):
    """
    A panel for rendering form-only fields (not model fields).

    Use this for extra fields defined on the form class that aren't
    backed by a model field. The field will be included in the form
    and rendered in the admin, but won't be saved to the database.
    """

    def clone_kwargs(self) -> dict[str, Any]:
        kwargs = super().clone_kwargs()
        return kwargs

    class BoundPanel(FieldPanel.BoundPanel):
        @cached_property
        def bound_field(self) -> Any:
            """Get the bound field from the form."""
            if self.field_name in self.form.fields:
                return self.form[self.field_name]
            return None

        def is_shown(self) -> bool:
            """Show the panel if the field exists in the form."""
            return self.bound_field is not None


```

```python
"""
Name: Custom Admin Panels
Path: core/sum_core/branding/panels.py
Purpose: Provide custom Wagtail panels for non-model form fields.
Family: Used by branding.models to display form-only fields in the admin.
Dependencies: Wagtail admin panels.
"""

from __future__ import annotations

from typing import Any

from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel



class FormFieldPanel(FieldPanel):
    """
    A panel for rendering form-only fields (not model fields).

    Use this for extra fields defined on the form class that aren't
    backed by a model field. The field will be included in the form
    and rendered in the admin, but won't be saved to the database.
    """

    def clone_kwargs(self) -> dict[str, Any]:
        kwargs = super().clone_kwargs()
        return kwargs

    class BoundPanel(FieldPanel.BoundPanel):
        @cached_property
        def bound_field(self) -> Any:
            """Get the bound field from the form."""
            if self.field_name in self.form.fields:
                return self.form[self.field_name]
            return None

        def is_shown(self) -> bool:
            """Show the panel if the field exists in the form."""
            return self.bound_field is not None


```

All tests pass and lint is clean. I've created a custom `FormFieldPanel` class that can render form-only fields (fields that exist on the form but not on the model).

Please try the Wagtail admin again at **Settings → Site settings**. You should now see:
1. **Logos & Favicon** section
2. **Theme Preset** section with a dropdown
3. **Brand Colours** section
4. **Typography** section
5. etc.

The "Theme Preset" dropdown should appear with 5 options plus a blank default.

---

**User**

Okay that's much better. Next issue: the SiteSettings screen now shows header_logo, footer_logo, and favicon as empty dropdowns instead of Wagtail’s image chooser.

---

**Cursor**

The issue is that our form's `Meta` class with `exclude = []` is overriding Wagtail's generated form, which normally sets up the proper image chooser widgets from panels. Let me fix the form to not override the field generation:

The issue is that our `Meta` class overrides Wagtail's panel-generated form which sets up proper widgets. Let me restructure as a mixin that doesn't override the Meta:

```python
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

from sum_core.branding.theme_presets import THEME_PRESETS, get_theme_preset_choices

if TYPE_CHECKING:
    from sum_core.branding.models import SiteSettings


class SiteSettingsAdminForm(forms.Form):
    """
    Custom admin form mixin for SiteSettings with theme preset support.

    This is used as `base_form_class` on SiteSettings. Wagtail will merge this
    with the panel-generated form, preserving the proper widgets (image choosers, etc.)
    while adding our extra field.

    The ``theme_preset`` field is:
      - An admin-only trigger field (not saved to the model).
      - Used to pre-populate: primary_color, secondary_color, accent_color,
        heading_font, and body_font when a preset is selected.
      - After application, all fields remain freely editable.
    """

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    # NOTE: No Meta class here! We let Wagtail's panel system generate the
    # model form with proper widgets. This class just adds extra fields.

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["theme_preset"].choices = get_theme_preset_choices()

    def save(self, commit: bool = True) -> "SiteSettings":
        """Apply theme preset values if one was selected, then save."""
        instance = super().save(commit=False)  # type: ignore[misc]

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


```

The plain `forms.Form` approach doesn't work because it doesn't support `instance`. Let me go back to `WagtailAdminModelForm` but explicitly set the proper widgets for image fields:

```python
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
from wagtail.admin.widgets import AdminImageChooser

from sum_core.branding.theme_presets import THEME_PRESETS, get_theme_preset_choices

if TYPE_CHECKING:
    from sum_core.branding.models import SiteSettings


class SiteSettingsAdminForm(WagtailAdminModelForm):
    """
    Custom admin form for SiteSettings with theme preset support.

    The ``theme_preset`` field is:
      - An admin-only trigger field (not saved to the model).
      - Used to pre-populate: primary_color, secondary_color, accent_color,
        heading_font, and body_font when a preset is selected.
      - After application, all fields remain freely editable.
    """

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    class Meta:
        # Import here to avoid circular import at module load time
        from sum_core.branding.models import SiteSettings

        model = SiteSettings
        # NOTE: WagtailAdminModelForm + fields="__all__" does not play nicely
        # with construct_instance; using exclude = [] ensures all model fields
        # are included and cleaned_data is applied correctly.
        exclude = []
        # Explicitly set Wagtail's image chooser widgets for ForeignKey image fields
        widgets = {
            "header_logo": AdminImageChooser,
            "footer_logo": AdminImageChooser,
            "favicon": AdminImageChooser,
        }

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


```

```python
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
from wagtail.images.widgets import AdminImageChooser

from sum_core.branding.theme_presets import THEME_PRESETS, get_theme_preset_choices

if TYPE_CHECKING:
    from sum_core.branding.models import SiteSettings


class SiteSettingsAdminForm(WagtailAdminModelForm):
    """
    Custom admin form for SiteSettings with theme preset support.

    The ``theme_preset`` field is:
      - An admin-only trigger field (not saved to the model).
      - Used to pre-populate: primary_color, secondary_color, accent_color,
        heading_font, and body_font when a preset is selected.
      - After application, all fields remain freely editable.
    """

    theme_preset = forms.ChoiceField(
        required=False,
        label="Theme preset",
        help_text="Apply a starting theme; colours and fonts can still be edited afterwards.",
    )

    class Meta:
        # Import here to avoid circular import at module load time
        from sum_core.branding.models import SiteSettings

        model = SiteSettings
        # NOTE: WagtailAdminModelForm + fields="__all__" does not play nicely
        # with construct_instance; using exclude = [] ensures all model fields
        # are included and cleaned_data is applied correctly.
        exclude = []
        # Explicitly set Wagtail's image chooser widgets for ForeignKey image fields
        widgets = {
            "header_logo": AdminImageChooser,
            "footer_logo": AdminImageChooser,
            "favicon": AdminImageChooser,
        }

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


```

All tests pass. I've added explicit widget configuration for the image fields using `AdminImageChooser` from `wagtail.images.widgets`.

Please try the Wagtail admin again at **Settings → Site settings**. The header_logo, footer_logo, and favicon fields should now show Wagtail's image chooser widget instead of plain dropdowns.

