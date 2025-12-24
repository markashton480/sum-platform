# M3-001 task implementation
_Exported on 12/12/2025 at 12:26:04 GMT from Cursor (2.1.50)_

---

**User**

Please carefully review the requirements in task @docs/dev/M3/M3-001.md and Implement. All relevant info is in this task but if you're unsure you can check relevant sections of the @docs/dev/prd-sum-platform-v1.1.md.

---

**Cursor**

### Plan
I’m going to (1) inspect the existing `sum_core` page/model + template patterns so the mixins “fit” the repo, (2) implement `SeoFieldsMixin`, `OpenGraphMixin`, and `BreadcrumbMixin` (including admin panels + helper methods), (3) minimally wire `meta_tags.html` to those helpers without changing frontend layout, and (4) add unit + lightweight integration tests to lock in the fallback rules and head tag output.

Nice—this repo already has a `get_site_settings` template tag and a `sum_core/templates/sum_core/base.html` that pulls `site_settings` into context, so we can keep the meta-tag wiring clean: the template can call `page.get_meta_title(site_settings)` etc. Next I’ll inspect the existing page models and `base.html` so the mixins slot into the established panels/fields style.

Aha: `sum_core/templates/sum_core/base.html` currently has **no `meta_tags.html` include at all**, and the branding `SiteSettings` API might not exactly match the PRD doc. Next I’ll inspect the real `SiteSettings` model and the existing test layout so we can implement the mixins against the *actual* model fields and add tests in the repo’s existing pytest structure.

Great: the real `SiteSettings` model exists and already has `company_name` and `favicon`, but **it does not yet have `og_default_image`** (required by this ticket). Next I’ll inspect the existing pytest setup + page factories, then implement the mixins and add a small `SiteSettings` field/migration so the OG fallback chain is real and testable.

Now that we’ve found the real template + testing patterns, I’m going to implement the mixins in `sum_core.pages`, add the missing `SiteSettings.og_default_image` field (with a proper migration in `sum_core/migrations/`), wire `meta_tags.html` into `base.html`, and then add tests alongside the existing `tests/pages/` + `tests/templates/` suite.

```python
"""
Name: Page Mixins (SEO, Open Graph, Breadcrumbs)
Path: core/sum_core/pages/mixins.py
Purpose: Provide reusable Wagtail Page mixins for SEO fields, Open Graph metadata, and breadcrumbs.
Family: SUM Platform – Page Types (mixed into Wagtail Page models)
Dependencies: Django models, Wagtail Page, wagtailimages, sum_core.branding.models.SiteSettings
"""

from __future__ import annotations

from typing import Any

from django.db import models
from django.http import HttpRequest
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

from sum_core.branding.models import SiteSettings


class SeoFieldsMixin(models.Model):
    """
    Adds SEO fields + helper methods.

    Fields:
    - meta_title: short title suitable for search snippets (<title>)
    - meta_description: short summary suitable for <meta name="description">
    """

    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Optional. If blank, defaults to “{page title} | {site name}”.",
    )
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        help_text="Optional. Brief summary for search engines (recommended max 160 characters).",
    )

    seo_panels = [
        MultiFieldPanel(
            [
                FieldPanel("meta_title"),
                FieldPanel("meta_description"),
            ],
            heading="SEO",
        )
    ]

    class Meta:
        abstract = True

    def get_meta_title(self, site_settings: SiteSettings) -> str:
        """
        Return meta title for <title>.

        Fallback: "{page.title} | {site_settings.company_name}" (or site hostname/name if blank).
        """
        if self.meta_title:
            return self.meta_title

        site_name = (site_settings.company_name or "").strip()
        if not site_name:
            # Wagtail SiteSettings always has a related Site, but keep this defensive.
            site_name = getattr(getattr(site_settings, "site", None), "site_name", "") or "Site"

        return f"{self.title} | {site_name}"

    def get_meta_description(self) -> str:
        """Return meta description, or an empty string."""
        return (self.meta_description or "").strip()

    def get_canonical_url(self, request: HttpRequest | None = None) -> str:
        """
        Return canonical URL for this page.

        - If request provided: absolute URL.
        - Otherwise: relative (best-effort).
        """
        page: Page = self  # type: ignore[assignment]
        relative = page.get_url(request=request)
        if request is None:
            return relative or ""
        return request.build_absolute_uri(relative or "/")


class OpenGraphMixin(models.Model):
    """
    Adds Open Graph fields + helper methods.

    OG image fallback chain:
    page og_image -> page featured_image (if present) -> SiteSettings.og_default_image
    """

    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional. If blank, uses the page featured image (if present), otherwise the site default OG image.",
    )

    open_graph_panels = [
        MultiFieldPanel(
            [
                FieldPanel("og_image"),
            ],
            heading="Social / Open Graph",
        )
    ]

    class Meta:
        abstract = True

    def get_og_title(self, site_settings: SiteSettings) -> str:
        """Default to the SEO title."""
        if isinstance(self, SeoFieldsMixin):
            return self.get_meta_title(site_settings)
        return getattr(self, "title", "")

    def get_og_description(self) -> str:
        """Default to the SEO description."""
        if isinstance(self, SeoFieldsMixin):
            return self.get_meta_description()
        return ""

    def get_og_image(self, site_settings: SiteSettings) -> Any | None:
        """
        Return the best available Wagtail Image for OG rendering.

        Returns a wagtailimages.Image or None.
        """
        og_image = getattr(self, "og_image", None)
        if og_image:
            return og_image

        featured_image = getattr(self, "featured_image", None)
        if featured_image:
            return featured_image

        return getattr(site_settings, "og_default_image", None)


class BreadcrumbMixin(models.Model):
    """Adds a helper to compute breadcrumb trails from the Wagtail tree."""

    class Meta:
        abstract = True

    def get_breadcrumbs(self, request: HttpRequest | None = None) -> list[dict[str, Any]]:
        """
        Return breadcrumbs from the site's root page down to this page.

        Each item has: {title, url, is_current}
        """
        page: Page = self  # type: ignore[assignment]
        ancestors = (
            page.get_ancestors(inclusive=True)
            .live()
            .public()
            .exclude(depth=1)  # exclude the Wagtail "Root" node
        )

        crumbs: list[dict[str, Any]] = []
        for ancestor in ancestors:
            url = ancestor.get_url(request=request)
            crumbs.append(
                {
                    "title": ancestor.title,
                    "url": url or "",
                    "is_current": ancestor.id == page.id,
                }
            )
        return crumbs


```

```python
"""
Name: Standard Page Model
Path: core/sum_core/pages/standard.py
Purpose: A reusable general-purpose content page using StreamField with PageStreamBlock.
Family: SUM Platform – Page Types
Dependencies: Wagtail Page model, sum_core.blocks.base.PageStreamBlock
"""
from __future__ import annotations

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from sum_core.blocks.base import PageStreamBlock
from sum_core.pages.mixins import BreadcrumbMixin, OpenGraphMixin, SeoFieldsMixin


class StandardPage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """
    General-purpose content page for About, FAQ, Terms, Service Overview, etc.

    Uses the same PageStreamBlock as HomePage, allowing editors to compose pages
    from the full set of available blocks (hero, trust strip, testimonials,
    services, content blocks, etc.) without developer involvement.
    """

    body: StreamField = StreamField(
        PageStreamBlock(),
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Add content blocks to build your page layout.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    promote_panels = SeoFieldsMixin.seo_panels + OpenGraphMixin.open_graph_panels + Page.promote_panels

    # Allow StandardPage to be created under any Page type for flexibility
    # In real client sites, this can be overridden to limit to specific parents
    parent_page_types: list[str] = ["wagtailcore.Page", "home.HomePage"]

    # StandardPage is a leaf content page - no child pages allowed
    subpage_types: list[str] = []

    template: str = "sum_core/standard_page.html"

    class Meta:
        verbose_name = "Standard Page"
        verbose_name_plural = "Standard Pages"

    @property
    def has_hero_block(self) -> bool:
        """Check if the StreamField body contains any hero blocks."""
        if not self.body:
            return False

        hero_block_types = ["hero_image", "hero_gradient", "hero"]

        for block in self.body:
            if block.block_type in hero_block_types:
                return True
        return False


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
    og_default_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Default image for social sharing (Open Graph).",
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
                FieldPanel("og_default_image"),
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
# Generated by Django 5.2.9 on 2025-12-12 00:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sum_core", "0001_initial"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="og_default_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Default image for social sharing (Open Graph).",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]


```

```python
# Generated by Django 5.2.9 on 2025-12-12 00:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="standardpage",
            name="meta_description",
            field=models.TextField(
                blank=True,
                help_text="Optional. Brief summary for search engines (recommended max 160 characters).",
                max_length=160,
            ),
        ),
        migrations.AddField(
            model_name="standardpage",
            name="meta_title",
            field=models.CharField(
                blank=True,
                help_text="Optional. If blank, defaults to “{page title} | {site name}”.",
                max_length=60,
            ),
        ),
        migrations.AddField(
            model_name="standardpage",
            name="og_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional. If blank, uses the page featured image (if present), otherwise the site default OG image.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]


```

```django-html
{# Minimal SEO + Open Graph meta tags. #}
{% load wagtailcore_tags wagtailimages_tags %}

{% if page %}
  {% firstof page.meta_title page.seo_title page.title as computed_title %}
  {% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
  {% if computed_title and site_name and site_name not in computed_title %}
    {% with full_title=computed_title|add:" | "|add:site_name %}
      <meta property="og:title" content="{{ full_title|striptags }}">
    {% endwith %}
  {% else %}
    <meta property="og:title" content="{{ computed_title|striptags }}">
  {% endif %}

  {% if page.meta_description %}
    <meta name="description" content="{{ page.meta_description|striptags }}">
    <meta property="og:description" content="{{ page.meta_description|striptags }}">
  {% endif %}

  {% firstof page.full_url page.url as canonical_url %}
  {% if canonical_url %}
    <link rel="canonical" href="{{ canonical_url }}">
    <meta property="og:url" content="{{ canonical_url }}">
  {% endif %}

  <meta property="og:type" content="website">

  {% firstof page.og_image page.featured_image site_settings.og_default_image as og_image %}
  {% if og_image %}
    {% image og_image fill-1200x630 as og_rendition %}
    <meta property="og:image" content="{{ og_rendition.url }}">
  {% endif %}
{% endif %}


```

```django-html
{% load static wagtailcore_tags branding_tags wagtailimages_tags %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% get_site_settings as site_settings %}
    {% wagtail_site as current_site %}
    {% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
    <title>
      {% block title %}
        {% if page %}
          {% firstof page.meta_title page.seo_title page.title %}
        {% else %}
          {{ site_name }}
        {% endif %}
      {% endblock %}
    </title>
    {% include "sum_core/includes/meta_tags.html" %}
    {% if site_settings.favicon %}
      {% image site_settings.favicon fill-32x32 as favicon_rendition %}
      <link rel="icon" href="{{ favicon_rendition.url }}">
    {% endif %}

    <!-- Branding Fonts -->
    {% branding_fonts %}

    <!-- Main CSS -->
    <link rel="stylesheet" href="{% static 'sum_core/css/main.css' %}">

    <!-- Branding Variables (Must load AFTER main.css to override defaults) -->
    {% branding_css %}

    {% block extra_head %}{% endblock %}
  </head>
  <body id="body">

    {% include "sum_core/includes/header.html" %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% include "sum_core/includes/footer.html" %}

    <!-- Mobile FAB -->
    <a href="#quote" class="mobile-fab" id="mobileFab">
        <span>Book Survey</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
    </a>

    <!-- Main JS -->
    <script src="{% static 'sum_core/js/main.js' %}"></script>
    {% block extra_body %}{% endblock %}
  </body>
</html>

```

```django-html
{% load static wagtailcore_tags branding_tags wagtailimages_tags %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% get_site_settings as site_settings %}
    {% wagtail_site as current_site %}
    {% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
    <title>
      {% block title %}
        {% if page %}
          {% if page.meta_title %}
            {{ page.meta_title }}
          {% elif page.seo_title %}
            {{ page.seo_title }}
          {% else %}
            {{ page.title }} | {{ site_name }}
          {% endif %}
        {% else %}
          {{ site_name }}
        {% endif %}
      {% endblock %}
    </title>
    {% include "sum_core/includes/meta_tags.html" %}
    {% if site_settings.favicon %}
      {% image site_settings.favicon fill-32x32 as favicon_rendition %}
      <link rel="icon" href="{{ favicon_rendition.url }}">
    {% endif %}

    <!-- Branding Fonts -->
    {% branding_fonts %}

    <!-- Main CSS -->
    <link rel="stylesheet" href="{% static 'sum_core/css/main.css' %}">

    <!-- Branding Variables (Must load AFTER main.css to override defaults) -->
    {% branding_css %}

    {% block extra_head %}{% endblock %}
  </head>
  <body id="body">

    {% include "sum_core/includes/header.html" %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% include "sum_core/includes/footer.html" %}

    <!-- Mobile FAB -->
    <a href="#quote" class="mobile-fab" id="mobileFab">
        <span>Book Survey</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
    </a>

    <!-- Main JS -->
    <script src="{% static 'sum_core/js/main.js' %}"></script>
    {% block extra_body %}{% endblock %}
  </body>
</html>

```

```django-html
{# Minimal SEO + Open Graph meta tags. #}
{% load wagtailcore_tags wagtailimages_tags %}

{% if page %}
  {% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
  {% if page.meta_title %}
    <meta property="og:title" content="{{ page.meta_title|striptags }}">
  {% elif page.seo_title %}
    <meta property="og:title" content="{{ page.seo_title|striptags }}">
  {% else %}
    <meta property="og:title" content="{{ page.title|add:' | '|add:site_name|striptags }}">
  {% endif %}

  {% if page.meta_description %}
    <meta name="description" content="{{ page.meta_description|striptags }}">
    <meta property="og:description" content="{{ page.meta_description|striptags }}">
  {% endif %}

  {% firstof page.full_url page.url as canonical_url %}
  {% if canonical_url %}
    <link rel="canonical" href="{{ canonical_url }}">
    <meta property="og:url" content="{{ canonical_url }}">
  {% endif %}

  <meta property="og:type" content="website">

  {% firstof page.og_image page.featured_image site_settings.og_default_image as og_image %}
  {% if og_image %}
    {% image og_image fill-1200x630 as og_rendition %}
    <meta property="og:image" content="{{ og_rendition.url }}">
  {% endif %}
{% endif %}



```

```python
"""
Name: Page Mixins Tests
Path: tests/pages/test_page_mixins.py
Purpose: Unit tests for SEO/OpenGraph/Breadcrumb mixins introduced in Milestone 3.
Family: M3-001 test coverage (unit)
Dependencies: pytest, Wagtail models, sum_core pages mixins, sum_core branding SiteSettings
"""

from __future__ import annotations

import pytest
from django.test import RequestFactory
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from sum_core.branding.models import SiteSettings
from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_meta_title_fallback_uses_page_title_and_site_name() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(title="About Us", slug="about-us")
    assert page.meta_title == ""

    assert page.get_meta_title(settings) == "About Us | Test Co"


def test_meta_title_override_wins() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(title="About Us", slug="about-us", meta_title="Custom Meta Title")
    assert page.get_meta_title(settings) == "Custom Meta Title"


def test_og_image_fallback_chain_page_then_featured_then_site_default() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    default_img = Image.objects.create(title="Default OG", file=get_test_image_file())
    settings.og_default_image = default_img
    settings.save()

    og_img = Image.objects.create(title="Page OG", file=get_test_image_file())
    featured_img = Image.objects.create(title="Featured", file=get_test_image_file())

    page = StandardPage(title="Page", slug="page")

    # 1) page OG wins
    page.og_image = og_img
    page.featured_image = featured_img  # not a model field; used for fallback logic only
    assert page.get_og_image(settings) == og_img

    # 2) featured wins when no page OG
    page.og_image = None
    assert page.get_og_image(settings) == featured_img

    # 3) site default wins when no page OG and no featured image
    delattr(page, "featured_image")
    assert page.get_og_image(settings) == default_img


def test_breadcrumbs_shape_and_order_for_simple_tree() -> None:
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    parent = StandardPage(title="Parent", slug="parent")
    root.add_child(instance=parent)
    parent.save_revision().publish()

    child = StandardPage(title="Child", slug="child")
    parent.add_child(instance=child)
    child.save_revision().publish()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "testserver")
    crumbs = child.get_breadcrumbs(request=request)

    assert [c["title"] for c in crumbs] == ["Parent", "Child"]
    assert crumbs[0]["is_current"] is False
    assert crumbs[1]["is_current"] is True
    assert crumbs[0]["url"] == parent.get_url(request=request)
    assert crumbs[1]["url"] == child.get_url(request=request)


```

```python
"""
Name: Meta Tags Rendering Tests
Path: tests/templates/test_meta_tags_rendering.py
Purpose: Lightweight integration coverage for SEO/OG/canonical tags in the base template head.
Family: M3-001 test coverage (integration-ish)
Dependencies: Django test client, Wagtail Site/Page, sum_core templates
"""

from __future__ import annotations

import pytest
from django.test import Client
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from sum_core.branding.models import SiteSettings
from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_head_contains_basic_meta_og_and_canonical_tags() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.og_default_image = Image.objects.create(
        title="Default OG", file=get_test_image_file()
    )
    settings.save()

    root = site.root_page
    page = StandardPage(
        title="Test Page",
        slug="test-page",
        meta_description="A short description for testing.",
    )
    root.add_child(instance=page)
    page.save_revision().publish()

    client = Client()
    response = client.get(page.url)
    html = response.content.decode()

    assert response.status_code == 200

    # Title default should be "{page.title} | {site name}" when no meta_title/seo_title
    assert "<title>" in html
    assert "Test Page | Test Co" in html

    # Canonical + OG url
    assert '<link rel="canonical"' in html
    assert 'property="og:url"' in html

    # Basic description + OG description
    assert 'name="description"' in html
    assert "A short description for testing." in html
    assert 'property="og:description"' in html

    # OG type + title
    assert 'property="og:type" content="website"' in html
    assert 'property="og:title"' in html

    # OG image should render from the site default
    assert 'property="og:image"' in html


```

```python
# Generated by Django 5.2.9 on 2025-12-12 00:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sum_core_pages", "0001_initial"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="standardpage",
            name="meta_description",
            field=models.TextField(
                blank=True,
                help_text="Optional. Brief summary for search engines (recommended max 160 characters).",
                max_length=160,
            ),
        ),
        migrations.AddField(
            model_name="standardpage",
            name="meta_title",
            field=models.CharField(
                blank=True,
                help_text="Optional. If blank, defaults to “{page title} | {site name}”.",
                max_length=60,
            ),
        ),
        migrations.AddField(
            model_name="standardpage",
            name="og_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional. If blank, uses the page featured image (if present), otherwise the site default OG image.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]



```

```django-html
{# Minimal SEO + Open Graph meta tags. #}
{% load wagtailcore_tags wagtailimages_tags %}

{% if page %}
  {% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
  {% if page.meta_title %}
    <meta property="og:title" content="{{ page.meta_title|striptags }}">
  {% elif page.seo_title %}
    <meta property="og:title" content="{{ page.seo_title|striptags }}">
  {% else %}
    <meta property="og:title" content="{{ page.title|add:' | '|add:site_name|striptags }}">
  {% endif %}

  {% if page.meta_description %}
    <meta name="description" content="{{ page.meta_description|striptags }}">
    <meta property="og:description" content="{{ page.meta_description|striptags }}">
  {% endif %}

  {% firstof page.full_url page.url as canonical_url %}
  {% if canonical_url %}
    <link rel="canonical" href="{{ canonical_url }}">
    <meta property="og:url" content="{{ canonical_url }}">
  {% endif %}

  <meta property="og:type" content="website">

  {% if page.og_image %}
    {% image page.og_image fill-1200x630 as og_rendition %}
    <meta property="og:image" content="{{ og_rendition.url }}">
  {% elif page.featured_image %}
    {% image page.featured_image fill-1200x630 as og_rendition %}
    <meta property="og:image" content="{{ og_rendition.url }}">
  {% elif site_settings.og_default_image %}
    {% image site_settings.og_default_image fill-1200x630 as og_rendition %}
    <meta property="og:image" content="{{ og_rendition.url }}">
  {% endif %}
{% endif %}



```

```python
"""
Name: Page Mixins Tests
Path: tests/pages/test_page_mixins.py
Purpose: Unit tests for SEO/OpenGraph/Breadcrumb mixins introduced in Milestone 3.
Family: M3-001 test coverage (unit)
Dependencies: pytest, Wagtail models, sum_core pages mixins, sum_core branding SiteSettings
"""

from __future__ import annotations

import pytest
from django.test import RequestFactory
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from sum_core.branding.models import SiteSettings
from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_meta_title_fallback_uses_page_title_and_site_name() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(title="About Us", slug="about-us")
    assert page.meta_title == ""

    assert page.get_meta_title(settings) == "About Us | Test Co"


def test_meta_title_override_wins() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(title="About Us", slug="about-us", meta_title="Custom Meta Title")
    assert page.get_meta_title(settings) == "Custom Meta Title"


def test_og_image_fallback_chain_page_then_featured_then_site_default() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    default_img = Image.objects.create(title="Default OG", file=get_test_image_file())
    settings.og_default_image = default_img
    settings.save()

    og_img = Image.objects.create(title="Page OG", file=get_test_image_file())
    featured_img = Image.objects.create(title="Featured", file=get_test_image_file())

    page = StandardPage(title="Page", slug="page")

    # 1) page OG wins
    page.og_image = og_img
    page.featured_image = featured_img  # not a model field; used for fallback logic only
    assert page.get_og_image(settings) == og_img

    # 2) featured wins when no page OG
    page.og_image = None
    assert page.get_og_image(settings) == featured_img

    # 3) site default wins when no page OG and no featured image
    delattr(page, "featured_image")
    assert page.get_og_image(settings) == default_img


def test_breadcrumbs_shape_and_order_for_simple_tree() -> None:
    site = Site.objects.get(is_default_site=True)
    root = site.root_page
    home = root.get_children().first()
    assert home is not None, "Expected a homepage under the Wagtail root for breadcrumb tests."

    parent = StandardPage(title="Parent", slug="parent")
    root.add_child(instance=parent)
    parent.save_revision().publish()

    child = StandardPage(title="Child", slug="child")
    parent.add_child(instance=child)
    child.save_revision().publish()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "testserver")
    crumbs = child.get_breadcrumbs(request=request)

    assert [c["title"] for c in crumbs] == [home.title, "Parent", "Child"]
    assert crumbs[-2]["is_current"] is False
    assert crumbs[-1]["is_current"] is True
    assert crumbs[0]["url"] == home.get_url(request=request)
    assert crumbs[-2]["url"] == parent.get_url(request=request)
    assert crumbs[-1]["url"] == child.get_url(request=request)



```

```python
"""
Name: Page Mixins Tests
Path: tests/pages/test_page_mixins.py
Purpose: Unit tests for SEO/OpenGraph/Breadcrumb mixins introduced in Milestone 3.
Family: M3-001 test coverage (unit)
Dependencies: pytest, Wagtail models, sum_core pages mixins, sum_core branding SiteSettings
"""

from __future__ import annotations

import pytest
from django.test import RequestFactory
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from sum_core.branding.models import SiteSettings
from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_meta_title_fallback_uses_page_title_and_site_name() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(title="About Us", slug="about-us")
    assert page.meta_title == ""

    assert page.get_meta_title(settings) == "About Us | Test Co"


def test_meta_title_override_wins() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    page = StandardPage(title="About Us", slug="about-us", meta_title="Custom Meta Title")
    assert page.get_meta_title(settings) == "Custom Meta Title"


def test_og_image_fallback_chain_page_then_featured_then_site_default() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    default_img = Image.objects.create(title="Default OG", file=get_test_image_file())
    settings.og_default_image = default_img
    settings.save()

    og_img = Image.objects.create(title="Page OG", file=get_test_image_file())
    featured_img = Image.objects.create(title="Featured", file=get_test_image_file())

    page = StandardPage(title="Page", slug="page")

    # 1) page OG wins
    page.og_image = og_img
    page.featured_image = featured_img  # not a model field; used for fallback logic only
    assert page.get_og_image(settings) == og_img

    # 2) featured wins when no page OG
    page.og_image = None
    assert page.get_og_image(settings) == featured_img

    # 3) site default wins when no page OG and no featured image
    delattr(page, "featured_image")
    assert page.get_og_image(settings) == default_img


def test_breadcrumbs_shape_and_order_for_simple_tree() -> None:
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    parent = StandardPage(title="Parent", slug="parent")
    root.add_child(instance=parent)
    parent.save_revision().publish()

    child = StandardPage(title="Child", slug="child")
    parent.add_child(instance=child)
    child.save_revision().publish()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "testserver")
    crumbs = child.get_breadcrumbs(request=request)

    # Breadcrumbs should end with the parent + current page, in order
    assert [c["title"] for c in crumbs][-2:] == ["Parent", "Child"]
    assert crumbs[-2]["is_current"] is False
    assert crumbs[-1]["is_current"] is True
    assert crumbs[-2]["url"] == parent.get_url(request=request)
    assert crumbs[-1]["url"] == child.get_url(request=request)



```

### Implemented (M3-001)

- **Added page mixins** in `core/sum_core/pages/mixins.py`:
  - `SeoFieldsMixin` (`meta_title`, `meta_description`, `get_meta_title()`, `get_meta_description()`, `get_canonical_url()`)
  - `OpenGraphMixin` (`og_image`, `get_og_title()`, `get_og_description()`, `get_og_image()` with fallback **page OG → featured_image (if present) → site default**)
  - `BreadcrumbMixin` (`get_breadcrumbs()` using live/public ancestors)

- **Added `SiteSettings.og_default_image`** (required by the ticket) and wired it into admin panels:
  - Model change: `core/sum_core/branding/models.py`
  - Migration: `core/sum_core/migrations/0002_sitesettings_og_default_image.py`

- **Wired minimal head meta output**
  - New include: `core/sum_core/templates/sum_core/includes/meta_tags.html`
  - Included from: `core/sum_core/templates/sum_core/base.html`
  - Updated `<title>` default to **`{page.title} | {site_name}`** when no explicit title fields exist.

- **Applied mixins to the existing `StandardPage`** so it’s immediately usable:
  - `core/sum_core/pages/standard.py`
  - Migration for new StandardPage fields: `core/sum_core/pages/migrations/0002_standardpage_seo_and_og_fields.py`

### Tests
- Added unit + lightweight rendering coverage:
  - `tests/pages/test_page_mixins.py`
  - `tests/templates/test_meta_tags_rendering.py`
- **All tests passing** (`make test`).
