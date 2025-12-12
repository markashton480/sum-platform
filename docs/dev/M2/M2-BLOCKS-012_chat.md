# M2-BLOCKS-012 task details
_Exported on 12/12/2025 at 11:48:50 GMT from Cursor (2.1.50)_

---

**User**

Please review the task details in @docs/dev/M2/M2-BLOCKS-012.md and implement.

---

**Cursor**

### Plan
- **Stabilize the flaky homepage rendering tests** by finding where the 404s come from, then making page/site creation + publishing deterministic via a shared helper/fixture.
- **Fix the missing CSS token** by either defining `--duration-default` in `tokens.css` or switching gallery CSS to an existing duration token.
- **Verify** by rerunning the template tests (and ideally once with `-n auto`) to ensure the flake is gone.

Nice—there’s exactly one failing-risk test file (`tests/templates/test_homepage_rendering.py`) and we’ve confirmed the undefined token is used in `components.gallery.css`. Next I’ll read the homepage rendering tests + existing pytest/Wagtail fixtures to fix routing deterministically, then patch `tokens.css` (or refactor the gallery token).

Good catch in the current tests: they create `HomePage` instances but **never publish them**, yet they do HTTP requests (`client.get(home.url)`) which only resolve **live** pages in Wagtail. Next I’ll reproduce the current failure mode, then refactor tests to use a shared “create + publish + attach to default Site” helper so batch order can’t affect routing.

I can’t run the tests yet because this workspace doesn’t currently have `pytest` installed (no active `.venv`). Next I’ll create/activate the repo-root virtualenv, install `sum_core` (+ dev/test deps), then rerun the failing template tests to confirm the exact 404 behavior before patching.

```python
"""
Name: Pytest Django Configuration
Path: tests/conftest.py
Purpose: Configure Django/Wagtail settings and test database for pytest runs.
Family: Shared fixtures for the test suite.
Dependencies: Django test utilities, pytest.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from collections.abc import Generator

import django
import pytest
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)
from wagtail.models import Page, Site

ROOT_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = ROOT_DIR / "core"
TEST_PROJECT_DIR = CORE_DIR / "sum_core" / "test_project"

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sum_core.test_project.test_project.settings")
django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_environment() -> Generator[None, None, None]:
    """Set up Django and the test database for the test session."""

    setup_test_environment()
    db_config = setup_databases(verbosity=0, interactive=False, keepdb=False)
    try:
        yield
    finally:
        teardown_databases(db_config, verbosity=0)
        teardown_test_environment()


@pytest.fixture()
def wagtail_default_site() -> Site:
    """
    Return a deterministic default Wagtail Site for tests that use HTTP routing.

    Why: this repo's test DB is session-scoped (see `django_test_environment`),
    so other tests can mutate `Site` and Wagtail's internal site-root-path cache.
    Rendering tests that call `client.get(page.url)` should not depend on test order.
    """
    # Ensure Wagtail's computed site root paths cache can't go stale across tests.
    Site.clear_site_root_paths_cache()

    root = Page.get_first_root_node()
    site = Site.objects.filter(is_default_site=True).first()

    if site is None:
        site = Site.objects.create(
            hostname="testserver",
            port=80,
            root_page=root,
            is_default_site=True,
        )
    else:
        changed = False
        if site.hostname != "testserver":
            site.hostname = "testserver"
            changed = True
        if site.port != 80:
            site.port = 80
            changed = True
        if site.root_page_id != root.id:
            site.root_page = root
            changed = True
        if not site.is_default_site:
            site.is_default_site = True
            changed = True
        if changed:
            site.save()

    Site.clear_site_root_paths_cache()
    return site

```

```python
import pytest
from django.test import Client
from home.models import HomePage

pytestmark = pytest.mark.django_db

def test_homepage_renders_testimonials_block(wagtail_default_site):
    site = wagtail_default_site
    root = site.root_page

    # Create homepage
    home = HomePage(title="Home Test", slug="home-test-testimonials")
    root.add_child(instance=home)

    # Assign testimonials block data
    home.body = [
        ('testimonials', {
            'eyebrow': 'Testimonials',
            'heading': '<p>Client Vibes</p>',
            'testimonials': [
                {
                    'quote': 'Amazing work!',
                    'author_name': 'Alice Smith',
                    'rating': 5
                },
                {
                    'quote': 'Pretty good.',
                    'author_name': 'Bob Jones',
                    'rating': 4
                }
            ]
        })
    ]
    home.save_revision().publish()

    # Function based rendering check via client
    client = Client()
    assert home.url is not None
    response = client.get(home.url)
    assert response.status_code == 200
    content = response.content.decode()

    # Check layout classes
    assert 'class="section section--dark testimonials"' in content
    assert 'testimonials__grid' in content
    assert 'testimonial-card' in content

    # Check content
    assert 'Testimonials' in content
    assert 'Client Vibes' in content
    assert 'Amazing work!' in content
    assert 'Alice Smith' in content

    # Check ratings render
    # There are 2 testimonials, each has 5 star spans. Total 10 star spans.
    assert content.count('aria-hidden="true">★</span>') + content.count('aria-hidden="true">☆</span>') == 10

    # First one is 5 stars (5 filled)
    # Second one is 4 stars (4 filled)
    # Total filled stars = 9
    assert content.count('aria-hidden="true">★</span>') == 9


def test_homepage_renders_gallery_block(wagtail_default_site):
    """Test that HomePage correctly renders a Gallery block with images."""
    from wagtail.images.tests.utils import get_test_image_file
    from wagtail.images.models import Image

    site = wagtail_default_site
    root = site.root_page

    # Create test images
    image1 = Image.objects.create(title="Project Photo 1", file=get_test_image_file())
    image2 = Image.objects.create(title="Project Photo 2", file=get_test_image_file())
    image3 = Image.objects.create(title="Project Photo 3", file=get_test_image_file())

    # Create homepage
    home = HomePage(title="Home Test Gallery", slug="home-test-gallery")
    root.add_child(instance=home)
    home.save()

    # Assign gallery block data
    # Note: StreamField assignments need actual Image objects, not just PKs
    home.body = [
        ('gallery', {
            'eyebrow': 'Selected Works',
            'heading': '<p>Our Recent <em>Projects</em></p>',
            'intro': 'Explore our craftsmanship across London.',
            'images': [
                {
                    'image': image1,
                    'alt_text': 'Custom alt text for image 1',
                    'caption': 'Kensington Townhouse'
                },
                {
                    'image': image2,
                    'alt_text': '',  # Should fallback to image title
                    'caption': 'Surrey Hills Estate'
                },
                {
                    'image': image3,
                    'alt_text': 'Third project alt',
                    'caption': ''  # No caption
                }
            ]
        })
    ]
    home.save_revision().publish()

    # Function based rendering check via client
    client = Client()
    assert home.url is not None
    response = client.get(home.url)
    assert response.status_code == 200
    content = response.content.decode()

    # Check layout classes
    assert 'class="section gallery"' in content
    assert 'gallery__grid' in content
    assert 'gallery__item' in content

    # Check header content
    assert 'Selected Works' in content
    assert 'Our Recent' in content
    assert '<em>Projects</em>' in content  # Italic emphasis in heading
    assert 'Explore our craftsmanship across London.' in content

    # Check correct number of items rendered (3 images)
    assert content.count('gallery__item') == 3

    # Check alt text behaviour
    # Image 1: custom alt text provided
    assert 'alt="Custom alt text for image 1"' in content
    # Image 2: should fallback to image title
    assert 'alt="Project Photo 2"' in content
    # Image 3: custom alt text
    assert 'alt="Third project alt"' in content

    # Check captions render where provided
    assert 'Kensington Townhouse' in content
    assert 'Surrey Hills Estate' in content
    # Image 3 has no caption - verify figcaption doesn't appear for it by count
    # We should have exactly 2 figcaptions (for images 1 and 2)
    assert content.count('gallery__caption') == 2

```

```postcss
/* ==========================================================================
   Name: Design Tokens
   Path: core/sum_core/static/sum_core/css/tokens.css
   Purpose: CSS Custom Properties for the SUM Platform Design System.
            Contains all design tokens: colours, typography scale, spacing,
            shadows, radii, and animation easings. This is the single source
            of truth for design values.
   Family: SUM Platform Design System – Tokens
   Dependencies: None (this is the foundational layer)
   ========================================================================== */

:root {
  /*
     Base HSL Values are injected by Wagtail via branding_tags.py:
     --brand-h, --brand-s, --brand-l

     If not present, fallback values are defined here.
  */
  --brand-h: 30; /* Brown/Gold Default */
  --brand-s: 40%;
  --brand-l: 35%;

  /* Derived Palette */
  --primary: var(--brand-h), var(--brand-s), var(--brand-l);
  --primary-deep: var(--brand-h), var(--brand-s), calc(var(--brand-l) - 15%);

  /* Surface & Text - Derived for harmony */
  --surface-tint: var(--brand-h), 10%, 97%;
  --surface-pure: 0, 0%, 100%;

  --text-main: var(--brand-h), 15%, 15%;
  --text-muted: var(--brand-h), 5%, 45%;

  /* Accent - Analogous calculation or custom injection */
  --accent-pop: calc(var(--brand-h) + 30), 60%, 55%;

  /* Semantic Colors - PRD 6.3.1 */
  --color-success: 142, 71%, 45%;      /* Green - confirmation, positive */
  --color-warning: 38, 92%, 50%;        /* Amber - caution, attention */
  --color-error: 0, 72%, 51%;           /* Red - error, destructive */
  --color-info: 199, 89%, 48%;          /* Blue - informational */

  /* Typography - PRD Design Token System */
  /* Font Families - Populated from SiteSettings per client */
  --font-heading: "Fraunces", serif;
  --font-body: "Manrope", sans-serif;
  /* Distinct Display Font - defaults to Heading font unless overridden by theme injection */
  --font-display: var(--font-heading);

  /* Font Weights - PRD C.1.2 */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights - PRD C.1.2 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Font Size Scale - PRD C.1.2 */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */
  --text-5xl: 3rem;        /* 48px */
  --text-6xl: 3.75rem;     /* 60px */
  --text-display: clamp(3rem, 8vw, 5.5rem); /* Huge Editorial Headings */

  /* Spacing - PRD C.1.3 */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */

  /* Layout Spacing */
  --container-padding: clamp(var(--space-6), 5vw, var(--space-16));
  --section-gap: clamp(var(--space-16), 10vw, var(--space-24));

  /* Animation Easings */
  --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);

  /* Animation Durations */
  --duration-default: 240ms;

  /* Borders & Radius - PRD C.1.5 (extended) */
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-3xl: 1.5rem;   /* 24px */
  --radius-full: 9999px;  /* Pill shape */

  /* Shadows - PRD C.1.4 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-xl: 0 10px 25px rgba(0, 0, 0, 0.15);
}

/* Technical Theme Override */
[data-theme="technical"] {
  --brand-h: 210; /* Deep Blue */
  --brand-s: 80%;
  --brand-l: 25%;

  --surface-tint: 210, 20%, 98%;

  --accent-pop: 200, 90%, 40%;
  --font-heading: "Manrope", sans-serif; /* Cleaner look for technical */
}

```

```python
"""
Name: Pytest Django Configuration
Path: tests/conftest.py
Purpose: Configure Django/Wagtail settings and test database for pytest runs.
Family: Shared fixtures for the test suite.
Dependencies: Django test utilities, pytest.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from collections.abc import Generator

import django
import pytest
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = ROOT_DIR / "core"
TEST_PROJECT_DIR = CORE_DIR / "sum_core" / "test_project"

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sum_core.test_project.test_project.settings")
django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_environment() -> Generator[None, None, None]:
    """Set up Django and the test database for the test session."""

    setup_test_environment()
    db_config = setup_databases(verbosity=0, interactive=False, keepdb=False)
    try:
        yield
    finally:
        teardown_databases(db_config, verbosity=0)
        teardown_test_environment()


@pytest.fixture()
def wagtail_default_site():
    """
    Return a deterministic default Wagtail Site for tests that use HTTP routing.

    Why: this repo's test DB is session-scoped (see `django_test_environment`),
    so other tests can mutate `Site` and Wagtail's internal site-root-path cache.
    Rendering tests that call `client.get(page.url)` should not depend on test order.
    """
    from wagtail.models import Page, Site

    # Ensure Wagtail's computed site root paths cache can't go stale across tests.
    Site.clear_site_root_paths_cache()

    root = Page.get_first_root_node()
    site = Site.objects.filter(is_default_site=True).first()

    if site is None:
        site = Site.objects.create(
            hostname="testserver",
            port=80,
            root_page=root,
            is_default_site=True,
        )
    else:
        changed = False
        if site.hostname != "testserver":
            site.hostname = "testserver"
            changed = True
        if site.port != 80:
            site.port = 80
            changed = True
        if site.root_page_id != root.id:
            site.root_page = root
            changed = True
        if not site.is_default_site:
            site.is_default_site = True
            changed = True
        if changed:
            site.save()

    Site.clear_site_root_paths_cache()
    return site

```

```python
"""
Name: Branding Template Tags
Path: core/sum_core/branding/templatetags/branding_tags.py
Purpose: Exposes branding-related template tags, including access to SiteSettings and branding-driven CSS/font helpers.
Family: Used by Django templates to retrieve branding configuration and inject runtime styles.
Dependencies: Django template system, Wagtail Site and SiteSettings, Django cache.
"""

from __future__ import annotations

import colorsys
from typing import Any
from collections.abc import Callable
from urllib.parse import quote_plus

from django import template
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from django.utils.html import SafeString, format_html
from django.utils.safestring import mark_safe
from wagtail.models import Site

from sum_core.branding.models import SiteSettings

register = template.Library()

FONT_FALLBACK_STACK = (
    'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
)


@register.simple_tag(takes_context=True)
def get_site_settings(context: dict[str, Any]) -> SiteSettings:
    """
    Return the SiteSettings for the current request/site.

    Caches per-request to avoid repeated DB hits.
    """

    request = context.get("request")
    if request is None or not isinstance(request, HttpRequest):
        raise ValueError("get_site_settings requires 'request' in the template context.")

    cached_settings = getattr(request, "_site_settings_cache", None)
    if cached_settings is not None:
        return cached_settings

    site = Site.find_for_request(request)
    if site is None:
        site = Site.objects.get(is_default_site=True)

    site_settings = SiteSettings.for_site(site)
    request._site_settings_cache = site_settings
    return site_settings


def _format_font_value(font_name: str) -> str:
    family = font_name.strip()
    if not family:
        return ""
    return f'"{family}", {FONT_FALLBACK_STACK}'


def _hex_to_hsl(hex_value: str) -> tuple[int, int, int] | None:
    """
    Convert hex color to CSS HSL values (h=0-360, s=0-100, l=0-100).
    """
    hex_value = hex_value.lstrip("#")
    if len(hex_value) not in (3, 6):
        return None

    if len(hex_value) == 3:
        hex_value = "".join(c * 2 for c in hex_value)

    try:
        r, g, b = (int(hex_value[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
        return round(hue * 360), round(saturation * 100), round(lightness * 100)
    except (ValueError, IndexError):
        return None


def _build_css_variables(site_settings: SiteSettings) -> list[str]:
    variables: list[str] = []

    # Inject HSL variables from Primary Color
    if site_settings.primary_color:
        hsl = _hex_to_hsl(site_settings.primary_color)
        if hsl:
            hue, saturation, lightness = hsl
            variables.extend([
                f"    --brand-h: {hue};",
                f"    --brand-s: {saturation}%;",
                f"    --brand-l: {lightness}%;",
            ])
        else:
            # Fallback if invalid hex, let CSS defaults handle it
            pass

    # If no primary color set, we do NOT inject defaults here.
    # We rely on main.css :root variables to provide the default "Gold" theme.


    # Also inject other specific colors if needed, but the system relies on HSL
    # We can inject them as overrides if we want, or just stick to the design system logic.
    # For now, let's inject the provided secondary/accent as simple hex variables
    # in case we want to use them directly, but the main theme will drive off brand-h/s/l.

    if site_settings.secondary_color:
        variables.append(f"    --color-secondary-custom: {site_settings.secondary_color};")

    if site_settings.accent_color:
        variables.append(f"    --color-accent-custom: {site_settings.accent_color};")
        # Also try to generate accent HSL if needed
        accent_hsl = _hex_to_hsl(site_settings.accent_color)
        if accent_hsl:
             variables.append(f"    --accent-h: {accent_hsl[0]};")
             variables.append(f"    --accent-s: {accent_hsl[1]}%;")
             variables.append(f"    --accent-l: {accent_hsl[2]}%;")


    heading_font = _format_font_value(site_settings.heading_font)
    if heading_font:
        variables.append(f"    --font-heading: {heading_font};")

    body_font = _format_font_value(site_settings.body_font)
    if body_font:
        variables.append(f"    --font-body: {body_font};")

    return variables


def _cacheable_response(cache_key: str, build: Callable[[], SafeString]) -> SafeString:
    if settings.DEBUG:
        return build()

    cached = cache.get(cache_key)
    if cached:
        return cached

    rendered = build()
    cache.set(cache_key, rendered, timeout=None)
    return rendered


@register.simple_tag(takes_context=True)
def branding_css(context: dict[str, Any]) -> SafeString:
    """
    Emit a <style> block with CSS variables sourced from SiteSettings.

    In development, the output is regenerated on every call.
    In production, the output is cached per site and invalidated on settings changes.
    """

    site_settings = get_site_settings(context)
    cache_key = f"branding_css:{site_settings.site_id}"

    def build() -> SafeString:
        variables = _build_css_variables(site_settings)
        css_lines = [":root {", *variables, "}"]
        css = mark_safe("\n".join(css_lines))
        return format_html('<style id="branding-css">\n{}\n</style>', css)

    return _cacheable_response(cache_key, build)


def _unique_fonts(site_settings: SiteSettings) -> list[str]:
    fonts = []
    for font in (site_settings.heading_font, site_settings.body_font):
        cleaned = font.strip() if font else ""
        if cleaned and cleaned not in fonts:
            fonts.append(cleaned)

    # If no fonts configured, fallback to the design system defaults
    if not fonts:
        return ["Fraunces", "Manrope"]

    return fonts


@register.simple_tag(takes_context=True)
def branding_fonts(context: dict[str, Any]) -> SafeString:
    """
    Emit Google Fonts <link> tags for configured heading/body fonts.

    In development, the output is regenerated on every call.
    In production, the output is cached per site and invalidated on settings changes.
    """

    site_settings = get_site_settings(context)
    cache_key = f"branding_fonts:{site_settings.site_id}"

    def build() -> SafeString:
        fonts = _unique_fonts(site_settings)
        if not fonts:
            return ""

        families = "&".join(
            f"family={quote_plus(font)}:wght@300;400;500;600;700" for font in fonts
        )
        href = f"https://fonts.googleapis.com/css2?{families}&display=swap"

        links = [
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            f'<link rel="stylesheet" href="{href}">',
        ]

        return mark_safe("\n".join(links))

    return _cacheable_response(cache_key, build)

```

### Implemented (BLOCKS-012)

- **Stabilised homepage rendering tests (eliminated batch-run 404/`/None`)**
  - Added a deterministic `wagtail_default_site` fixture that:
    - Forces the default `Site` to `hostname="testserver"`, `port=80`, `root_page=Page.get_first_root_node()`
    - Clears Wagtail’s site-root-path cache before/after (prevents cross-test cache staleness in this session-scoped DB setup)
  - Updated `tests/templates/test_homepage_rendering.py` to use the fixture and **publish** the created `HomePage` revision before routing.
  - Files:
    - `tests/conftest.py`
    - `tests/templates/test_homepage_rendering.py`

- **Patched missing token**
  - Added `--duration-default` to `tokens.css` (used by gallery hover transition).
  - File:
    - `core/sum_core/static/sum_core/css/tokens.css`

- **Optional cleanup included (was blocking `make lint`)**
  - Renamed ambiguous variable `l` → `lightness` (and related names) to satisfy Ruff `E741`.
  - File:
    - `core/sum_core/branding/templatetags/branding_tags.py`

### Verification
- **`make lint`**: passes (Ruff clean; mypy still reports existing issues but is non-blocking due to `|| true` in Makefile).
- **`make test`**: passes (`111 passed`).
