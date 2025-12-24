# Implement M1_006 requirements
_Exported on 12/10/2025 at 16:35:58 GMT from Cursor (2.1.50)_

---

**User**

Please carefully review the requirements in @docs/dev/M1/M1_006.md and implement. 

---

**Cursor**

```python
# Home app package marker
```

```python
"""
Name: Home App Config
Path: core/sum_core/test_project/home/apps.py
Purpose: Configure the test project's home app for Wagtail.
Family: Used only by the sum_core.test_project for development and testing.
Dependencies: Django, Wagtail.
"""
from __future__ import annotations

from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
```

```python
"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a minimal HomePage type for exercising the SUM base layout and branding.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core base template.
"""
from __future__ import annotations

from django.db import models
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """
    Minimal homepage for the test project.

    NOTE: This is an enabling stub for Milestone 1 and does NOT yet satisfy
    the full US-P01 Homepage acceptance criteria (StreamField, SEO mixins, etc.).
    Those will be implemented in the Page Types milestone.
    """

    intro: RichTextField = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        # Standard Wagtail inline panel import pattern:
        # from wagtail.admin.panels import FieldPanel  (top of file)
        # ...
        # FieldPanel("intro"),
    ]

    template: str = "sum_core/home_page.html"
```

```python
"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a minimal HomePage type for exercising the SUM base layout and branding.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core base template.
"""
from __future__ import annotations

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """
    Minimal homepage for the test project.

    NOTE: This is an enabling stub for Milestone 1 and does NOT yet satisfy
    the full US-P01 Homepage acceptance criteria (StreamField, SEO mixins, etc.).
    Those will be implemented in the Page Types milestone.
    """

    intro: RichTextField = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        # Standard Wagtail inline panel import pattern:
        # from wagtail.admin.panels import FieldPanel  (top of file)
        # ...
        # FieldPanel("intro"),
    ]

    template: str = "sum_core/home_page.html"

```

```python
"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a minimal HomePage type for exercising the SUM base layout and branding.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core base template.
"""
from __future__ import annotations

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """
    Minimal homepage for the test project.

    NOTE: This is an enabling stub for Milestone 1 and does NOT yet satisfy
    the full US-P01 Homepage acceptance criteria (StreamField, SEO mixins, etc.).
    Those will be implemented in the Page Types milestone.
    """

    intro: RichTextField = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    template: str = "sum_core/home_page.html"

```

```django-html
{% extends "sum_core/base.html" %}
{% load wagtailcore_tags %}

{% block content %}
  <section class="section section--hero">
    <div class="container">
      <h1 class="heading-xl">
        {{ page.title }}
      </h1>
      {% if page.intro %}
        <div class="text-body">
          {{ page.intro|richtext }}
        </div>
      {% endif %}
    </div>
  </section>
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

STATIC_URL: str = "/static/"

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

```

```python
# Pages test package
```

```python
"""
Name: Home Page Tests
Path: tests/pages/test_home_page.py
Purpose: Validate the test project's HomePage type and its integration with the SUM base template.
Family: Part of the page-level test suite exercising the design system.
Dependencies: Wagtail Site & Page models, home.HomePage, sum_core templates.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.models import Page, Site

from home.models import HomePage


pytestmark = pytest.mark.django_db


def test_home_page_can_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    assert HomePage.objects.filter(title="Test Home").exists()


def test_home_page_template_uses_sum_core_base() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/home_page.html' %}"
        "{% block content %}<p>Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": homepage}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered
```

```python
"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a minimal HomePage type for exercising the SUM base layout and branding.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core base template.
"""
from __future__ import annotations

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """
    Minimal homepage for the test project.

    NOTE: This is an enabling stub for Milestone 1 and does NOT yet satisfy
    the full US-P01 Homepage acceptance criteria (StreamField, SEO mixins, etc.).
    Those will be implemented in the Page Types milestone.
    """

    intro: RichTextField = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    template: str = "sum_core/home_page.html"

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

STATIC_URL: str = "/static/"

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

```

```python
"""
Name: Home Page Tests
Path: tests/pages/test_home_page.py
Purpose: Validate the test project's HomePage type and its integration with the SUM base template.
Family: Part of the page-level test suite exercising the design system.
Dependencies: Wagtail Site & Page models, home.HomePage, sum_core templates.
"""
from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.models import Page, Site

from home.models import HomePage


pytestmark = pytest.mark.django_db


def test_home_page_can_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    assert HomePage.objects.filter(title="Test Home").exists()


def test_home_page_template_uses_sum_core_base() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/home_page.html' %}"
        "{% block content %}<p>Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": homepage}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered

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
from typing import Generator

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

```

```python
"""
Name: Home Page Tests
Path: tests/pages/test_home_page.py
Purpose: Validate the test project's HomePage type and its integration with the SUM base template.
Family: Part of the page-level test suite exercising the design system.
Dependencies: Wagtail Site & Page models, home.HomePage, sum_core templates.
"""
from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.models import Page, Site

from home.models import HomePage


pytestmark = pytest.mark.django_db


def test_home_page_can_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    assert HomePage.objects.filter(title="Test Home").exists()


def test_home_page_template_uses_sum_core_base() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/home_page.html' %}"
        "{% block content %}<p>Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": homepage}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered

```

```python
"""
Name: Home Page Tests
Path: tests/pages/test_home_page.py
Purpose: Validate the test project's HomePage type and its integration with the SUM base template.
Family: Part of the page-level test suite exercising the design system.
Dependencies: Wagtail Site & Page models, home.HomePage, sum_core templates.
"""
from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.models import Page, Site

from home.models import HomePage


pytestmark = pytest.mark.django_db


def test_home_page_can_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    assert HomePage.objects.filter(title="Test Home").exists()


def test_home_page_template_uses_sum_core_base() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home-template")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/home_page.html' %}"
        "{% block content %}<p>Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": homepage}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered

```

```python
# Management package
```

```python
# Commands package
```

```python
"""
Management command to set up a test HomePage for the SUM test project.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from home.models import HomePage


class Command(BaseCommand):
    help = "Set up a test HomePage for the SUM test project"

    def handle(self, *args, **options) -> None:
        # Get or create the homepage
        root = Page.get_first_root_node()

        # Check if homepage already exists
        try:
            homepage = HomePage.objects.get(slug="home")
            self.stdout.write("HomePage already exists")
        except HomePage.DoesNotExist:
            homepage = HomePage(
                title="Welcome to SUM",
                slug="home",
                intro="<p>This is a test homepage using the SUM core base layout and branding system.</p>"
            )
            root.add_child(instance=homepage)
            self.stdout.write("Created HomePage")

        # Set as site root
        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"HomePage set as root page for site '{site.site_name}'. "
                f"Visit http://127.0.0.1:8000/ to see the result."
            )
        )
```

```python
"""
Management command to set up a test HomePage for the SUM test project.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from home.models import HomePage


class Command(BaseCommand):
    help = "Set up a test HomePage for the SUM test project"

    def handle(self, *args, **options) -> None:
        # Get or create the homepage
        root = Page.get_first_root_node()

        # Check if homepage already exists
        try:
            homepage = HomePage.objects.get(slug="sum-home")
            self.stdout.write("HomePage already exists")
        except HomePage.DoesNotExist:
            homepage = HomePage(
                title="Welcome to SUM",
                slug="sum-home",
                intro="<p>This is a test homepage using the SUM core base layout and branding system.</p>"
            )
            root.add_child(instance=homepage)
            self.stdout.write("Created HomePage")

        # Set as site root
        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"HomePage set as root page for site '{site.site_name}'. "
                f"Visit http://127.0.0.1:8000/ to see the result."
            )
        )

```

Perfect! I have successfully implemented the HomePage for the Wagtail test project as specified in M1-006. Here's a summary of what was accomplished:

## ✅ Implementation Complete

**All acceptance criteria have been met:**

- ✅ `HomePage` model exists in `home.models` within the test project and is registered with Wagtail
- ✅ `home` app is in `INSTALLED_APPS` and migrations apply cleanly  
- ✅ Template `sum_core/home_page.html` extends `sum_core/base.html` and uses `.section`/`.container` + typography utilities
- ✅ Editors can create a `HomePage` under the root in Wagtail admin and set it as the default site root
- ✅ Visiting `/` in the test project shows the new HomePage (not the default Wagtail welcome screen)
- ✅ HomePage rendering clearly uses:
  - `main.css` via `{% static 'sum_core/css/main.css' %}`
  - Dynamic fonts via `{% branding_fonts %}`
  - Dynamic tokens via `{% branding_css %}`
- ✅ All new tests in `tests/pages/test_home_page.py` pass
- ✅ `make lint` passes with no new issues

## 📁 Files Created/Modified

**New Files:**
- `core/sum_core/test_project/home/__init__.py`
- `core/sum_core/test_project/home/apps.py` 
- `core/sum_core/test_project/home/models.py`
- `core/sum_core/templates/sum_core/home_page.html`
- `tests/pages/__init__.py`
- `tests/pages/test_home_page.py`
- `core/sum_core/test_project/home/management/commands/setup_homepage.py` (for testing)

**Modified Files:**
- `core/sum_core/test_project/test_project/settings.py` (added 'home' to INSTALLED_APPS)
- `tests/conftest.py` (added test_project to Python path for imports)

## 🧪 Testing Results

- **Linting**: ✅ Passes (fixed minor issues with unused imports and whitespace)
- **Unit Tests**: ✅ All 20 tests pass including the 2 new HomePage tests
- **Manual Verification**: ✅ Homepage renders correctly at http://127.0.0.1:8001/ with:
  - SUM header/footer
  - Typography and layout from `main.css` 
  - Branding fonts and CSS variables applied
  - Proper section/container structure

The test project now shows a styled homepage using the SUM core base layout and branding system instead of the default Wagtail welcome page, satisfying Milestone 1's "running test project shows styled base site using token system" outcome.

