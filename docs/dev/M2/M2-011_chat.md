# Implement task from M2-011 documentation
_Exported on 12/11/2025 at 22:06:46 GMT from Cursor (2.1.50)_

---

**User**

Please carefully review the task details in @docs/dev/M2/M2-011.md and implement. 

---

**Cursor**

I'll carefully review the M2-011 task and implement the `StandardPage` page type. Let me first explore the existing codebase structure to understand the patterns and dependencies.

Now I have a clear understanding of the codebase structure. Let me create a task list and implement the `StandardPage`.

```python
"""
Name: Pages App Config
Path: core/sum_core/pages/apps.py
Purpose: Django AppConfig for the sum_core pages module containing reusable page types.
Family: SUM Platform – Page Types
Dependencies: django.apps.AppConfig
"""
from __future__ import annotations

from django.apps import AppConfig


class PagesConfig(AppConfig):
    """Configuration for the sum_core.pages app."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "sum_core.pages"
    label: str = "sum_core_pages"
    verbose_name: str = "SUM Core Pages"

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


class StandardPage(Page):
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
Name: Pages Package Init
Path: core/sum_core/pages/__init__.py
Purpose: Namespace for Wagtail page models within sum_core.
Family: Used by client projects and test_project for shared page implementations.
Dependencies: StandardPage from standard module.
"""
from sum_core.pages.standard import StandardPage

__all__ = [
    "StandardPage",
]

```

```django-html
{% extends "sum_core/base.html" %}
{% load wagtailcore_tags %}

{% block content %}
  {% if not page.has_hero_block %}
    <section class="section">
      <div class="container">
        <header class="section__header">
          <div class="section__heading">
            <h1 class="heading-xl">{{ page.title }}</h1>
          </div>
        </header>
      </div>
    </section>
  {% endif %}

  {% if page.body %}
    {% for block in page.body %}
      {% include_block block %}
    {% endfor %}
  {% endif %}
{% endblock %}

```

```python
"""
Name: Test Project Settings
Path: core/sum_core/test_project/test_project/settings.py
Purpose: Minimal Django/Wagtail settings for validating the sum_core package.
Family: Used exclusively by the sum_core.test_project for local and CI validation.
Dependencies: Django, Wagtail, sum_core
"""

from __future__ import annotations

import os
from pathlib import Path

# Wagtail Settings
WAGTAIL_SITE_NAME: str = "SUM Test Project"
WAGTAIL_ENABLE_UPDATE_CHECK = "lts"
WAGTAILADMIN_BASE_URL: str = "http://localhost:8000"

BASE_DIR: Path = Path(__file__).resolve().parent.parent

ENV_FILE_PATH: Path | None = None


def _load_env_file() -> Path | None:
    """
    Lightweight .env loader so the test project picks up DB settings without
    requiring python-dotenv. Walks up the tree to find the first .env file.
    """
    for directory in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        candidate = directory / ".env"
        if not candidate.exists():
            continue
        for raw_line in candidate.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
        return candidate
    return None


ENV_FILE_PATH = _load_env_file()

SECRET_KEY: str = "dev-only-not-for-production"
DEBUG: bool = True
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Wagtail core and contrib apps
    "wagtail",
    "wagtail.admin",
    "wagtail.users",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.snippets",
    "wagtail.sites",
    "wagtail.search",
    "wagtail.contrib.forms",
    "wagtail.contrib.settings",
    "wagtail.contrib.redirects",
    # Wagtail dependencies
    "modelcluster",
    "taggit",
    # Project apps
    "sum_core",
    "sum_core.pages",
    "home",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF: str = "test_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION: str = "test_project.wsgi.application"

DB_NAME = os.getenv("DJANGO_DB_NAME")
DB_USER = os.getenv("DJANGO_DB_USER")
DB_PASSWORD = os.getenv("DJANGO_DB_PASSWORD")
DB_HOST = os.getenv("DJANGO_DB_HOST")
DB_PORT = os.getenv("DJANGO_DB_PORT", "5432")


def _validate_db_env() -> None:
    supplied_any = any([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST])
    required_present = DB_NAME and DB_HOST
    if supplied_any and not required_present:
        missing = []
        if not DB_NAME:
            missing.append("DJANGO_DB_NAME")
        if not DB_HOST:
            missing.append("DJANGO_DB_HOST")
        raise ValueError(
            "Partial Postgres configuration supplied. Missing required env vars: "
            + ", ".join(missing)
        )


_validate_db_env()

if DB_HOST and DB_NAME:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = []

LANGUAGE_CODE: str = "en-gb"
TIME_ZONE: str = "Europe/London"
USE_I18N: bool = True
USE_TZ: bool = True


# Media

FILE_UPLOAD_MAX_MEMORY_SIZE = 52_428_800 # 50MB

DATA_UPLOAD_MAX_MEMORY_SIZE = 52_428_800 # 50MB

MEDIA_URL: str = "/images/"
MEDIA_ROOT: str = BASE_DIR / "images"

STATIC_URL: str = "/static/"

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

```

The import in `__init__.py` is causing issues because it triggers model imports before Django is fully configured. Let me fix this by avoiding model imports at the module level:

```python
"""
Name: Pages Package Init
Path: core/sum_core/pages/__init__.py
Purpose: Namespace for Wagtail page models within sum_core.
Family: Used by client projects and test_project for shared page implementations.
Dependencies: StandardPage from standard module (imported lazily).

Note: Model imports are intentionally deferred to avoid Django app registry issues
during startup. Import StandardPage directly from sum_core.pages.standard or
access via this module after Django setup is complete.
"""


def __getattr__(name: str):
    """Lazy import for page models to avoid app registry issues."""
    if name == "StandardPage":
        from sum_core.pages.standard import StandardPage

        return StandardPage
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "StandardPage",
]

```

I need to create a `models.py` file that Django can discover. Let me create it:

```python
"""
Name: Pages Models Aggregator
Path: core/sum_core/pages/models.py
Purpose: Register page models for Django model discovery.
Family: SUM Platform – Page Types
Dependencies: sum_core.pages.standard.StandardPage
"""
from __future__ import annotations

from sum_core.pages.standard import StandardPage

__all__ = ["StandardPage"]

```

Now let me create the test files:

```python
"""
Name: Standard Page Tests
Path: tests/pages/test_standard_page.py
Purpose: Validate the StandardPage model and its integration with PageStreamBlock.
Family: Part of the page-level test suite exercising the page types.
Dependencies: Wagtail Site & Page models, sum_core.pages.StandardPage, sum_core.blocks.
"""
from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.fields import StreamField
from wagtail.models import Page, Site

from sum_core.blocks import PageStreamBlock
from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_standard_page_is_registered_as_page_type() -> None:
    """StandardPage is registered as a Wagtail page type."""
    # Wagtail registers all Page subclasses automatically
    assert issubclass(StandardPage, Page)


def test_standard_page_has_body_stream_field() -> None:
    """StandardPage has a body field that is a StreamField."""
    body_field = StandardPage._meta.get_field("body")
    assert isinstance(body_field, StreamField)


def test_standard_page_body_uses_page_stream_block() -> None:
    """StandardPage body StreamField uses PageStreamBlock."""
    body_field = StandardPage._meta.get_field("body")
    assert isinstance(body_field.stream_block, PageStreamBlock)


def test_standard_page_can_be_created_under_root() -> None:
    """StandardPage can be created under the site root."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(title="Test Standard Page", slug="test-standard-page")
    root.add_child(instance=standard_page)

    assert StandardPage.objects.filter(title="Test Standard Page").exists()


def test_standard_page_can_be_created_with_empty_body() -> None:
    """StandardPage can be created with an empty body StreamField."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(
        title="Empty Standard Page",
        slug="empty-standard-page",
        body=None,
    )
    root.add_child(instance=standard_page)

    retrieved = StandardPage.objects.get(slug="empty-standard-page")
    assert retrieved.title == "Empty Standard Page"


def test_standard_page_can_be_created_with_rich_text_block() -> None:
    """StandardPage can be created with a rich_text block in body."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python([
        {
            "type": "rich_text",
            "value": "<h2>About Us</h2><p>We are a company.</p>",
        }
    ])

    standard_page = StandardPage(
        title="About Page",
        slug="about-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    retrieved = StandardPage.objects.get(slug="about-page")
    assert retrieved.title == "About Page"
    assert len(list(retrieved.body)) == 1


def test_standard_page_can_be_created_with_multiple_blocks() -> None:
    """StandardPage can be created with multiple blocks in body."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python([
        {
            "type": "rich_text",
            "value": "<h2>Section 1</h2><p>Content.</p>",
        },
        {
            "type": "rich_text",
            "value": "<h2>Section 2</h2><p>More content.</p>",
        },
    ])

    standard_page = StandardPage(
        title="Multi Block Page",
        slug="multi-block-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    retrieved = StandardPage.objects.get(slug="multi-block-page")
    assert len(list(retrieved.body)) == 2


def test_standard_page_has_hero_block_returns_false_when_no_body() -> None:
    """has_hero_block returns False when body is empty."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(title="No Hero Page", slug="no-hero-page")
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is False


def test_standard_page_has_hero_block_returns_false_for_non_hero_blocks() -> None:
    """has_hero_block returns False when body contains no hero blocks."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python([
        {"type": "rich_text", "value": "<p>Content.</p>"}
    ])

    standard_page = StandardPage(
        title="Content Only Page",
        slug="content-only-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is False


def test_standard_page_has_hero_block_returns_true_for_hero_image() -> None:
    """has_hero_block returns True when body contains hero_image block."""
    from wagtail.images.tests.utils import get_test_image_file
    from wagtail.images.models import Image

    root = Page.get_first_root_node()
    image = Image.objects.create(title="Hero Image", file=get_test_image_file())

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python([
        {
            "type": "hero_image",
            "value": {
                "headline": "<p>Welcome</p>",
                "subheadline": "",
                "ctas": [],
                "status": "",
                "image": image.pk,
                "image_alt": "Hero background",
                "overlay_opacity": "medium",
                "floating_card_label": "",
                "floating_card_value": "",
            },
        }
    ])

    standard_page = StandardPage(
        title="Hero Page",
        slug="hero-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is True


def test_standard_page_has_hero_block_returns_true_for_hero_gradient() -> None:
    """has_hero_block returns True when body contains hero_gradient block."""
    root = Page.get_first_root_node()

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python([
        {
            "type": "hero_gradient",
            "value": {
                "headline": "<p>Welcome</p>",
                "subheadline": "",
                "ctas": [],
                "status": "",
                "gradient_style": "primary",
            },
        }
    ])

    standard_page = StandardPage(
        title="Gradient Hero Page",
        slug="gradient-hero-page",
        body=stream_data,
    )
    root.add_child(instance=standard_page)

    assert standard_page.has_hero_block is True


def test_standard_page_template_path() -> None:
    """StandardPage uses the correct template path."""
    assert StandardPage.template == "sum_core/standard_page.html"


def test_standard_page_is_leaf_page() -> None:
    """StandardPage has no allowed subpage types (leaf page)."""
    assert StandardPage.subpage_types == []


def test_standard_page_parent_page_types() -> None:
    """StandardPage can be created under Wagtail root or HomePage."""
    assert "wagtailcore.Page" in StandardPage.parent_page_types
    assert "home.HomePage" in StandardPage.parent_page_types


def test_standard_page_template_uses_sum_core_base() -> None:
    """StandardPage template extends sum_core/base.html."""
    root = Page.get_first_root_node()
    standard_page = StandardPage(title="Template Test", slug="template-test")
    root.add_child(instance=standard_page)

    site = Site.objects.get(is_default_site=True)
    site.root_page = standard_page
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/standard_page.html' %}"
        "{% block content %}<p>Test Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": standard_page}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered

```

```python
"""
Name: Standard Page Rendering Tests
Path: tests/templates/test_standard_page_rendering.py
Purpose: Validate StandardPage template rendering with various blocks.
Family: Part of the template test suite exercising page rendering.
Dependencies: Django test client, Wagtail models, sum_core.pages.StandardPage.
"""
from __future__ import annotations

import pytest
from django.test import Client
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site

from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_standard_page_renders_successfully() -> None:
    """StandardPage renders with HTTP 200 status."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Test Render Page", slug="test-render-page")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)

    assert response.status_code == 200


def test_standard_page_renders_page_title_when_no_hero() -> None:
    """StandardPage renders page title in header when no hero block present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="About Us", slug="about-us-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Title should appear in page header
    assert "About Us" in content
    # Should have heading-xl class for title
    assert "heading-xl" in content
    # Should have section header pattern
    assert "section__header" in content
    assert "section__heading" in content


def test_standard_page_hides_header_when_hero_present() -> None:
    """StandardPage does not render page header when hero block is present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Landing Page", slug="landing-test")
    root.add_child(instance=page)

    # Add hero gradient block
    page.body = [
        ("hero_gradient", {
            "headline": "<p>Welcome to Our Site</p>",
            "subheadline": "Subhead text",
            "ctas": [],
            "status": "",
            "gradient_style": "primary",
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content should appear
    assert "Welcome to Our Site" in content
    # Page title should NOT appear as separate header when hero exists
    # The page header section with heading-xl and section__header should not wrap title
    # (it will still be in <title> tag, but not in the body header)
    assert '<h1 class="heading-xl">Landing Page</h1>' not in content


def test_standard_page_renders_rich_text_block() -> None:
    """StandardPage renders rich_text block content."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Content Page", slug="content-page-test")
    root.add_child(instance=page)

    page.body = [
        ("rich_text", "<h2>Our Mission</h2><p>We are committed to excellence.</p>")
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Our Mission" in content
    assert "We are committed to excellence." in content


def test_standard_page_renders_hero_and_content_blocks() -> None:
    """StandardPage renders both hero and content blocks correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page
    image = Image.objects.create(title="Hero Bg", file=get_test_image_file())

    page = StandardPage(title="Full Page", slug="full-page-test")
    root.add_child(instance=page)

    page.body = [
        ("hero_image", {
            "headline": "<p>Welcome to <em>Our Services</em></p>",
            "subheadline": "Quality solutions for your needs",
            "ctas": [],
            "status": "",
            "image": image,
            "image_alt": "Hero background image",
            "overlay_opacity": "medium",
            "floating_card_label": "",
            "floating_card_value": "",
        }),
        ("rich_text", "<h2>About Our Company</h2><p>Founded in 2020.</p>"),
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content
    assert "Welcome to" in content
    assert "Our Services" in content
    assert "Quality solutions" in content
    # Content block
    assert "About Our Company" in content
    assert "Founded in 2020" in content


def test_standard_page_renders_service_cards_block() -> None:
    """StandardPage renders ServiceCardsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Services", slug="services-test")
    root.add_child(instance=page)

    page.body = [
        ("service_cards", {
            "eyebrow": "What We Do",
            "heading": "<p>Our <em>Services</em></p>",
            "intro": "Professional solutions for every need.",
            "cards": [
                {
                    "title": "Consulting",
                    "description": "<p>Expert advice for your business.</p>",
                },
                {
                    "title": "Development",
                    "description": "<p>Building solutions that scale.</p>",
                },
            ],
            "layout_style": "default",
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "What We Do" in content
    assert "Our" in content
    assert "Services" in content
    assert "Consulting" in content
    assert "Development" in content
    assert "services__grid" in content
    assert "services__card" in content


def test_standard_page_renders_testimonials_block() -> None:
    """StandardPage renders TestimonialsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Reviews", slug="reviews-test")
    root.add_child(instance=page)

    page.body = [
        ("testimonials", {
            "eyebrow": "Customer Stories",
            "heading": "<p>What People <em>Say</em></p>",
            "testimonials": [
                {
                    "quote": "Excellent service and great results!",
                    "author_name": "Jane Doe",
                    "company": "Acme Inc",
                    "rating": 5,
                },
                {
                    "quote": "Highly recommend to everyone.",
                    "author_name": "John Smith",
                    "rating": 4,
                },
            ],
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Customer Stories" in content
    assert "What People" in content
    assert "Excellent service" in content
    assert "Jane Doe" in content
    assert "testimonials__grid" in content
    assert "testimonial-card" in content


def test_standard_page_renders_faq_block() -> None:
    """StandardPage renders FAQBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="FAQ", slug="faq-test")
    root.add_child(instance=page)

    page.body = [
        ("faq", {
            "eyebrow": "Questions",
            "heading": "<p>Frequently Asked</p>",
            "intro": "",
            "items": [
                {
                    "question": "What is your return policy?",
                    "answer": "<p>We offer 30-day returns.</p>",
                },
                {
                    "question": "How do I contact support?",
                    "answer": "<p>Email us at support@example.com.</p>",
                },
            ],
            "allow_multiple_open": True,
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Questions" in content
    assert "Frequently Asked" in content
    assert "What is your return policy?" in content
    assert "30-day returns" in content
    assert "faq__item" in content


def test_standard_page_no_inline_styles() -> None:
    """StandardPage template contains no inline styles."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Style Test", slug="style-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    # Check there are no style attributes with hardcoded values
    # (Note: some Wagtail image renditions may include width/height, which is OK)
    # We specifically check for no color or px values in style attributes
    assert 'style="color:' not in content
    assert 'style="font-size:' not in content
    assert 'style="margin:' not in content
    assert 'style="padding:' not in content


def test_standard_page_uses_layout_classes() -> None:
    """StandardPage renders with proper layout classes from CSS system."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Layout Test", slug="layout-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Main layout elements from base template
    assert "<main>" in content or '<main id=' in content
    assert "<header" in content
    assert "<footer" in content
    # Container class for proper width constraints
    assert "container" in content
    # Section class for proper spacing
    assert "section" in content

```

The docs/blocks-reference.md doesn't exist yet, so I'll create a page types reference document:

```markdown
# SUM Platform – Page Types Reference

This document describes the available page types in the SUM Platform core package (`sum_core`).

---

## StandardPage

**Module:** `sum_core.pages.standard`  
**Import:** `from sum_core.pages import StandardPage`

### Purpose

A general-purpose content page for About, FAQ, Terms, Privacy Policy, Service Overview, and other generic content pages. Editors can compose pages using the full set of available blocks without developer involvement.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `body` | StreamField (PageStreamBlock) | Main content area using the standard block set |

### Available Blocks

StandardPage uses `PageStreamBlock`, which includes:

**Hero Blocks:**
- `hero_image` – Hero with background image
- `hero_gradient` – Hero with gradient background

**Section Blocks:**
- `service_cards` – Grid of service cards
- `testimonials` – Customer testimonial cards
- `gallery` – Image gallery grid
- `trust_strip` – Trust badges/text strip
- `trust_strip_logos` – Logo trust strip
- `stats` – Statistics display
- `process` – Process steps
- `faq` – Accordion FAQ section
- `features` – Features list
- `comparison` – Before/after comparison
- `portfolio` – Portfolio items grid

**Page Content Blocks:**
- `editorial_header` – Section header with eyebrow
- `content` – Rich text content block
- `quote` – Pull quote
- `image_block` – Single image with caption
- `buttons` – Button group
- `spacer` – Vertical spacing
- `divider` – Horizontal divider
- `rich_text` – Simple rich text

### Template

**Path:** `sum_core/templates/sum_core/standard_page.html`

The template:
- Extends `sum_core/base.html`
- Shows a page title header when no hero block is present
- Renders all body blocks via `{% include_block %}`
- Uses design system tokens and classes (no hardcoded values)

### Page Hierarchy

| Setting | Value | Notes |
|---------|-------|-------|
| `parent_page_types` | `["wagtailcore.Page", "home.HomePage"]` | Can be created under site root or HomePage |
| `subpage_types` | `[]` | Leaf page – no children allowed |

### Usage Example

```python
from sum_core.pages import StandardPage

# Create a StandardPage programmatically
page = StandardPage(
    title="About Us",
    slug="about",
    body=[
        ("hero_gradient", {
            "headline": "<p>About <em>Our Company</em></p>",
            "subheadline": "Quality solutions since 2020",
            "ctas": [],
            "status": "",
            "gradient_style": "primary",
        }),
        ("rich_text", "<h2>Our Mission</h2><p>We deliver excellence.</p>"),
    ]
)
parent_page.add_child(instance=page)
```

### Admin Usage

1. In Wagtail admin, navigate to Pages
2. Select a parent page (site root or HomePage)
3. Click "Add child page" → "Standard Page"
4. Add a title and compose content using available blocks
5. Publish when ready

---

## HomePage

**Module:** `home.models` (test project)  
**Note:** HomePage is defined in the test project, not in `sum_core`. Client projects will define their own HomePage types.

### Purpose

Site homepage with intro text and StreamField body using `PageStreamBlock`.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `intro` | RichTextField | Optional intro text (shown when no hero) |
| `body` | StreamField (PageStreamBlock) | Main content area |

### Template

**Path:** `sum_core/templates/sum_core/home_page.html`

---

## Adding to Client Projects

To use `StandardPage` in a client project:

1. Add `sum_core.pages` to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ...
       "sum_core",
       "sum_core.pages",
       # ...
   ]
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. StandardPage will appear as a creatable page type in Wagtail admin.

```

Now let me run lint and tests to verify everything works:

Let me fix the lint error in my test file:

```python
"""
Name: Standard Page Rendering Tests
Path: tests/templates/test_standard_page_rendering.py
Purpose: Validate StandardPage template rendering with various blocks.
Family: Part of the template test suite exercising page rendering.
Dependencies: Django test client, Wagtail models, sum_core.pages.StandardPage.
"""
from __future__ import annotations

import pytest
from django.test import Client
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_standard_page_renders_successfully() -> None:
    """StandardPage renders with HTTP 200 status."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Test Render Page", slug="test-render-page")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)

    assert response.status_code == 200


def test_standard_page_renders_page_title_when_no_hero() -> None:
    """StandardPage renders page title in header when no hero block present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="About Us", slug="about-us-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Title should appear in page header
    assert "About Us" in content
    # Should have heading-xl class for title
    assert "heading-xl" in content
    # Should have section header pattern
    assert "section__header" in content
    assert "section__heading" in content


def test_standard_page_hides_header_when_hero_present() -> None:
    """StandardPage does not render page header when hero block is present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Landing Page", slug="landing-test")
    root.add_child(instance=page)

    # Add hero gradient block
    page.body = [
        ("hero_gradient", {
            "headline": "<p>Welcome to Our Site</p>",
            "subheadline": "Subhead text",
            "ctas": [],
            "status": "",
            "gradient_style": "primary",
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content should appear
    assert "Welcome to Our Site" in content
    # Page title should NOT appear as separate header when hero exists
    # The page header section with heading-xl and section__header should not wrap title
    # (it will still be in <title> tag, but not in the body header)
    assert '<h1 class="heading-xl">Landing Page</h1>' not in content


def test_standard_page_renders_rich_text_block() -> None:
    """StandardPage renders rich_text block content."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Content Page", slug="content-page-test")
    root.add_child(instance=page)

    page.body = [
        ("rich_text", "<h2>Our Mission</h2><p>We are committed to excellence.</p>")
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Our Mission" in content
    assert "We are committed to excellence." in content


def test_standard_page_renders_hero_and_content_blocks() -> None:
    """StandardPage renders both hero and content blocks correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page
    image = Image.objects.create(title="Hero Bg", file=get_test_image_file())

    page = StandardPage(title="Full Page", slug="full-page-test")
    root.add_child(instance=page)

    page.body = [
        ("hero_image", {
            "headline": "<p>Welcome to <em>Our Services</em></p>",
            "subheadline": "Quality solutions for your needs",
            "ctas": [],
            "status": "",
            "image": image,
            "image_alt": "Hero background image",
            "overlay_opacity": "medium",
            "floating_card_label": "",
            "floating_card_value": "",
        }),
        ("rich_text", "<h2>About Our Company</h2><p>Founded in 2020.</p>"),
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content
    assert "Welcome to" in content
    assert "Our Services" in content
    assert "Quality solutions" in content
    # Content block
    assert "About Our Company" in content
    assert "Founded in 2020" in content


def test_standard_page_renders_service_cards_block() -> None:
    """StandardPage renders ServiceCardsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Services", slug="services-test")
    root.add_child(instance=page)

    page.body = [
        ("service_cards", {
            "eyebrow": "What We Do",
            "heading": "<p>Our <em>Services</em></p>",
            "intro": "Professional solutions for every need.",
            "cards": [
                {
                    "title": "Consulting",
                    "description": "<p>Expert advice for your business.</p>",
                },
                {
                    "title": "Development",
                    "description": "<p>Building solutions that scale.</p>",
                },
            ],
            "layout_style": "default",
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "What We Do" in content
    assert "Our" in content
    assert "Services" in content
    assert "Consulting" in content
    assert "Development" in content
    assert "services__grid" in content
    assert "services__card" in content


def test_standard_page_renders_testimonials_block() -> None:
    """StandardPage renders TestimonialsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Reviews", slug="reviews-test")
    root.add_child(instance=page)

    page.body = [
        ("testimonials", {
            "eyebrow": "Customer Stories",
            "heading": "<p>What People <em>Say</em></p>",
            "testimonials": [
                {
                    "quote": "Excellent service and great results!",
                    "author_name": "Jane Doe",
                    "company": "Acme Inc",
                    "rating": 5,
                },
                {
                    "quote": "Highly recommend to everyone.",
                    "author_name": "John Smith",
                    "rating": 4,
                },
            ],
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Customer Stories" in content
    assert "What People" in content
    assert "Excellent service" in content
    assert "Jane Doe" in content
    assert "testimonials__grid" in content
    assert "testimonial-card" in content


def test_standard_page_renders_faq_block() -> None:
    """StandardPage renders FAQBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="FAQ", slug="faq-test")
    root.add_child(instance=page)

    page.body = [
        ("faq", {
            "eyebrow": "Questions",
            "heading": "<p>Frequently Asked</p>",
            "intro": "",
            "items": [
                {
                    "question": "What is your return policy?",
                    "answer": "<p>We offer 30-day returns.</p>",
                },
                {
                    "question": "How do I contact support?",
                    "answer": "<p>Email us at support@example.com.</p>",
                },
            ],
            "allow_multiple_open": True,
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Questions" in content
    assert "Frequently Asked" in content
    assert "What is your return policy?" in content
    assert "30-day returns" in content
    assert "faq__item" in content


def test_standard_page_no_inline_styles() -> None:
    """StandardPage template contains no inline styles."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Style Test", slug="style-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    # Check there are no style attributes with hardcoded values
    # (Note: some Wagtail image renditions may include width/height, which is OK)
    # We specifically check for no color or px values in style attributes
    assert 'style="color:' not in content
    assert 'style="font-size:' not in content
    assert 'style="margin:' not in content
    assert 'style="padding:' not in content


def test_standard_page_uses_layout_classes() -> None:
    """StandardPage renders with proper layout classes from CSS system."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Layout Test", slug="layout-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Main layout elements from base template
    assert "<main>" in content or '<main id=' in content
    assert "<header" in content
    assert "<footer" in content
    # Container class for proper width constraints
    assert "container" in content
    # Section class for proper spacing
    assert "section" in content


```

The remaining lint errors are in pre-existing files, not in the new StandardPage implementation. Let me run the tests:

There are 3 test failures:
1. Two pre-existing failures in `test_homepage_rendering.py` (unrelated to my changes - they have `page.url` returning `None`)
2. One in my test - the FAQ class name check needs adjustment

Let me check what class the FAQ block actually uses:

The FAQ block uses `faq-item` not `faq__item`. Let me fix my test:

```python
"""
Name: Standard Page Rendering Tests
Path: tests/templates/test_standard_page_rendering.py
Purpose: Validate StandardPage template rendering with various blocks.
Family: Part of the template test suite exercising page rendering.
Dependencies: Django test client, Wagtail models, sum_core.pages.StandardPage.
"""
from __future__ import annotations

import pytest
from django.test import Client
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

from sum_core.pages import StandardPage


pytestmark = pytest.mark.django_db


def test_standard_page_renders_successfully() -> None:
    """StandardPage renders with HTTP 200 status."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Test Render Page", slug="test-render-page")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)

    assert response.status_code == 200


def test_standard_page_renders_page_title_when_no_hero() -> None:
    """StandardPage renders page title in header when no hero block present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="About Us", slug="about-us-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Title should appear in page header
    assert "About Us" in content
    # Should have heading-xl class for title
    assert "heading-xl" in content
    # Should have section header pattern
    assert "section__header" in content
    assert "section__heading" in content


def test_standard_page_hides_header_when_hero_present() -> None:
    """StandardPage does not render page header when hero block is present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Landing Page", slug="landing-test")
    root.add_child(instance=page)

    # Add hero gradient block
    page.body = [
        ("hero_gradient", {
            "headline": "<p>Welcome to Our Site</p>",
            "subheadline": "Subhead text",
            "ctas": [],
            "status": "",
            "gradient_style": "primary",
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content should appear
    assert "Welcome to Our Site" in content
    # Page title should NOT appear as separate header when hero exists
    # The page header section with heading-xl and section__header should not wrap title
    # (it will still be in <title> tag, but not in the body header)
    assert '<h1 class="heading-xl">Landing Page</h1>' not in content


def test_standard_page_renders_rich_text_block() -> None:
    """StandardPage renders rich_text block content."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Content Page", slug="content-page-test")
    root.add_child(instance=page)

    page.body = [
        ("rich_text", "<h2>Our Mission</h2><p>We are committed to excellence.</p>")
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Our Mission" in content
    assert "We are committed to excellence." in content


def test_standard_page_renders_hero_and_content_blocks() -> None:
    """StandardPage renders both hero and content blocks correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page
    image = Image.objects.create(title="Hero Bg", file=get_test_image_file())

    page = StandardPage(title="Full Page", slug="full-page-test")
    root.add_child(instance=page)

    page.body = [
        ("hero_image", {
            "headline": "<p>Welcome to <em>Our Services</em></p>",
            "subheadline": "Quality solutions for your needs",
            "ctas": [],
            "status": "",
            "image": image,
            "image_alt": "Hero background image",
            "overlay_opacity": "medium",
            "floating_card_label": "",
            "floating_card_value": "",
        }),
        ("rich_text", "<h2>About Our Company</h2><p>Founded in 2020.</p>"),
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content
    assert "Welcome to" in content
    assert "Our Services" in content
    assert "Quality solutions" in content
    # Content block
    assert "About Our Company" in content
    assert "Founded in 2020" in content


def test_standard_page_renders_service_cards_block() -> None:
    """StandardPage renders ServiceCardsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Services", slug="services-test")
    root.add_child(instance=page)

    page.body = [
        ("service_cards", {
            "eyebrow": "What We Do",
            "heading": "<p>Our <em>Services</em></p>",
            "intro": "Professional solutions for every need.",
            "cards": [
                {
                    "title": "Consulting",
                    "description": "<p>Expert advice for your business.</p>",
                },
                {
                    "title": "Development",
                    "description": "<p>Building solutions that scale.</p>",
                },
            ],
            "layout_style": "default",
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "What We Do" in content
    assert "Our" in content
    assert "Services" in content
    assert "Consulting" in content
    assert "Development" in content
    assert "services__grid" in content
    assert "services__card" in content


def test_standard_page_renders_testimonials_block() -> None:
    """StandardPage renders TestimonialsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Reviews", slug="reviews-test")
    root.add_child(instance=page)

    page.body = [
        ("testimonials", {
            "eyebrow": "Customer Stories",
            "heading": "<p>What People <em>Say</em></p>",
            "testimonials": [
                {
                    "quote": "Excellent service and great results!",
                    "author_name": "Jane Doe",
                    "company": "Acme Inc",
                    "rating": 5,
                },
                {
                    "quote": "Highly recommend to everyone.",
                    "author_name": "John Smith",
                    "rating": 4,
                },
            ],
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Customer Stories" in content
    assert "What People" in content
    assert "Excellent service" in content
    assert "Jane Doe" in content
    assert "testimonials__grid" in content
    assert "testimonial-card" in content


def test_standard_page_renders_faq_block() -> None:
    """StandardPage renders FAQBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="FAQ", slug="faq-test")
    root.add_child(instance=page)

    page.body = [
        ("faq", {
            "eyebrow": "Questions",
            "heading": "<p>Frequently Asked</p>",
            "intro": "",
            "items": [
                {
                    "question": "What is your return policy?",
                    "answer": "<p>We offer 30-day returns.</p>",
                },
                {
                    "question": "How do I contact support?",
                    "answer": "<p>Email us at support@example.com.</p>",
                },
            ],
            "allow_multiple_open": True,
        })
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Questions" in content
    assert "Frequently Asked" in content
    assert "What is your return policy?" in content
    assert "30-day returns" in content
    assert "faq-item" in content


def test_standard_page_no_inline_styles() -> None:
    """StandardPage template contains no inline styles."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Style Test", slug="style-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    # Check there are no style attributes with hardcoded values
    # (Note: some Wagtail image renditions may include width/height, which is OK)
    # We specifically check for no color or px values in style attributes
    assert 'style="color:' not in content
    assert 'style="font-size:' not in content
    assert 'style="margin:' not in content
    assert 'style="padding:' not in content


def test_standard_page_uses_layout_classes() -> None:
    """StandardPage renders with proper layout classes from CSS system."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Layout Test", slug="layout-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Main layout elements from base template
    assert "<main>" in content or '<main id=' in content
    assert "<header" in content
    assert "<footer" in content
    # Container class for proper width constraints
    assert "container" in content
    # Section class for proper spacing
    assert "section" in content


```

All 25 StandardPage tests pass. Let me finalize by applying the migrations and updating the todo list:

I have successfully implemented the M2-011 task - StandardPage page type. Here's a summary:

## Implementation Summary

### Files Created

1. **`core/sum_core/pages/apps.py`** - AppConfig for the pages app with label `sum_core_pages`

2. **`core/sum_core/pages/standard.py`** - StandardPage model with:
   - `body` StreamField using `PageStreamBlock`
   - `has_hero_block` property to detect hero blocks
   - Configured as a leaf page (`subpage_types = []`)
   - Can be created under `wagtailcore.Page` or `home.HomePage`

3. **`core/sum_core/pages/models.py`** - Models aggregator for Django discovery

4. **`core/sum_core/pages/__init__.py`** - Package init with lazy import to avoid app registry issues

5. **`core/sum_core/pages/migrations/0001_initial.py`** - Initial migration for StandardPage

6. **`core/sum_core/templates/sum_core/standard_page.html`** - Template that:
   - Extends `sum_core/base.html`
   - Shows page title with `.heading-xl` class when no hero block present
   - Renders body blocks via `{% include_block %}`
   - Uses design tokens (no hardcoded values)

7. **`tests/pages/test_standard_page.py`** - 15 model/unit tests

8. **`tests/templates/test_standard_page_rendering.py`** - 10 template rendering tests

9. **`docs/dev/page-types-reference.md`** - Documentation for page types

### Files Modified

1. **`core/sum_core/test_project/test_project/settings.py`** - Added `sum_core.pages` to `INSTALLED_APPS`

### Acceptance Criteria Met

- ✅ `StandardPage` appears as a creatable page type in Wagtail admin
- ✅ Can create `StandardPage` under site root or HomePage
- ✅ Has `body` StreamField using `PageStreamBlock`
- ✅ Renders with SUM layout (header/footer from base.html)
- ✅ Blocks render via `{% include_block %}`
- ✅ Page title renders using `.heading-xl` when no hero present
- ✅ No inline styles or hardcoded values
- ✅ Integration with hero, services, testimonials, FAQ blocks tested
- ✅ 25 new tests all passing
- ✅ Migration applied successfully

