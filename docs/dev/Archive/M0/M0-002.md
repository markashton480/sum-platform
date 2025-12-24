## **[M0-002] `sum_core` Package Skeleton & `sum_core.test_project`**

---

### Context (from PRD)

From **US-F02: Core Package Structure**:

> As a developer, I want a well-organised core package (`sum_core`) so that shared functionality can be maintained centrally and imported by client projects.

Key acceptance criteria from the PRD:

* `sum_core` installable via `pip install -e ./core`
* App structure: `blocks/`, `pages/`, `leads/`, `branding/`, `analytics/`, `seo/`, `integrations/`, `utils/`
* Version defined in `__init__.py`: `__version__ = "X.Y.Z"`
* `pyproject.toml` with package metadata, dependencies, and optional dev dependencies
* Test project `sum_core.test_project` for CI
* Templates under `sum_core/templates/sum_core/`
* Static files under `sum_core/static/sum_core/`

Implementation Plan Milestone 0 also requires:

* `sum_core` package skeleton installable via `pip install -e ./core`
* Test project (`sum_core.test_project`) for CI validation

---

### Technical Requirements

**1. Package layout**

Create the core package inside `core/`:

```text
core/
  pyproject.toml          # NEW: packaging for sum_core
  sum_core/
    __init__.py
    apps.py
    blocks/
      __init__.py
    pages/
      __init__.py
    leads/
      __init__.py
    branding/
      __init__.py
    analytics/
      __init__.py
    seo/
      __init__.py
    integrations/
      __init__.py
    utils/
      __init__.py
    templates/
      sum_core/
        base.html         # placeholder
    static/
      sum_core/
        css/              # empty for now
        js/               # empty for now
```

**2. Packaging config (core/pyproject.toml)**

Add a **separate** `core/pyproject.toml` describing the package (root `pyproject.toml` remains for tooling).

* `project.name = "sum-core"`
* `project.version = "0.1.0"` (must match `__version__` in `sum_core/__init__.py`)
* `project.dependencies` should at least include `Django` and `Wagtail` with sensible version ranges (we can refine later).
* Optionally define:

  ```toml
  [project.optional-dependencies]
  dev = ["pytest", "pytest-cov", "mypy", "ruff", "black", "isort"]
  ```

This will let us later do: `pip install -e ./core[dev]`.

**3. App config**

In `core/sum_core/apps.py`, define a standard Django app config `SumCoreConfig` with:

* `name = "sum_core"`
* `default_auto_field = "django.db.models.BigAutoField"`

**4. Namespacing**

* Templates must live under `sum_core/templates/sum_core/`.
* Static assets must live under `sum_core/static/sum_core/`.

Even for placeholders, respect this structure so we don’t have to move files later.

**5. Test project: `sum_core.test_project`**

Inside `core/sum_core/`, create a minimal Django/Wagtail project:

```text
core/
  sum_core/
    test_project/
      manage.py
      test_project/
        __init__.py
        settings.py
        urls.py
        wsgi.py
```

Key requirements:

* `INSTALLED_APPS` includes:

  * Standard Django apps: `django.contrib.admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`
  * Wagtail + dependencies
  * `"sum_core"` (using the app config)
* DB: simple SQLite for now (`db.sqlite3` in the project directory).
* `ROOT_URLCONF = "test_project.urls"`
* `STATIC_URL = "/static/"` (fine for dev).
* Should be able to run:

  ```bash
  cd core/sum_core/test_project
  python manage.py check
  ```

without errors once dependencies are installed.

---

### Design Specifications (from design / PRD)

Even though we’re not styling yet, align structure with the design system:

* Templates:

  * `sum_core/templates/sum_core/base.html`
    → can be a minimal HTML5 skeleton with a `{% block content %}`.
* We will later drop in:

  * Token-based CSS (design system)
  * Component partials (hero, trust strip, etc.)

So for now just ensure we have the **correct paths**, not pretty HTML.

---

### Implementation Guidelines

#### 1. Header comments

For each Python module you create, include the required header comment:

```python
"""
Name: [Module Name]
Path: [File path]
Purpose: [Brief description]
Family: [What depends on this]
Dependencies: [What this depends on]
"""
```

Use this consistently (`__init__.py`, `apps.py`, `settings.py`, `urls.py`, etc.).

#### 2. `sum_core/__init__.py`

Example:

```python
"""
Name: sum_core Package Init
Path: core/sum_core/__init__.py
Purpose: Expose package metadata and establish package-level configuration.
Family: Imported by client projects and test_project; used for diagnostics and version checks.
Dependencies: None (standard library only).
"""

__all__ = ["__version__"]

__version__: str = "0.1.0"
```

#### 3. `sum_core/apps.py`

Example:

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
```

#### 4. `core/pyproject.toml` (example skeleton)

You can adapt this to match versions you want:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sum-core"
version = "0.1.0"
description = "Shared core package for SUM client websites"
requires-python = ">=3.12"
dependencies = [
  "Django>=4.2,<5.0",
  "wagtail>=6.0,<7.0",
]

[project.optional-dependencies]
dev = [
  "pytest",
  "pytest-cov",
  "mypy",
  "ruff",
  "black",
  "isort",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["sum_core*"]
```

This makes `pip install -e ./core` work as expected.

#### 5. Test project files (concrete skeletons)

**`core/sum_core/test_project/manage.py`**

```python
"""
Name: Test Project Manage Script
Path: core/sum_core/test_project/manage.py
Purpose: Entry point for Django management commands in the sum_core test project.
Family: Used by developers and CI to run checks, migrations, and tests against sum_core.
Dependencies: django.core.management
"""

from __future__ import annotations

import os
import sys
from typing import NoReturn


def main() -> NoReturn:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

**`core/sum_core/test_project/test_project/settings.py`** (minimal)

```python
"""
Name: Test Project Settings
Path: core/sum_core/test_project/test_project/settings.py
Purpose: Minimal Django/Wagtail settings for validating the sum_core package.
Family: Used exclusively by the sum_core.test_project for local and CI validation.
Dependencies: Django, Wagtail, sum_core
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent

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
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    # Project apps
    "sum_core",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
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

**`core/sum_core/test_project/test_project/urls.py`**

```python
"""
Name: Test Project URL Configuration
Path: core/sum_core/test_project/test_project/urls.py
Purpose: Minimal URL configuration to expose Wagtail admin and root page.
Family: Used by test_project when running the development server or checks.
Dependencies: Django, Wagtail
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include("wagtail.admin.urls")),
    path("documents/", include("wagtail.documents.urls")),
]
```

**`core/sum_core/test_project/test_project/wsgi.py`** can be the standard Django boilerplate.

---

### Acceptance Criteria

* [ ] `core/sum_core/` exists and is a valid Python package.
* [ ] Subpackages created: `blocks/`, `pages/`, `leads/`, `branding/`, `analytics/`, `seo/`, `integrations/`, `utils/`.
* [ ] `core/sum_core/__init__.py` defines `__version__ = "0.1.0"` (or similar) and is importable.
* [ ] `core/pyproject.toml` exists and `pip install -e ./core` installs `sum_core` successfully.
* [ ] Templates root exists at `core/sum_core/templates/sum_core/`.
* [ ] Static root exists at `core/sum_core/static/sum_core/`.
* [ ] Test project `core/sum_core/test_project` exists and:

  * `python manage.py check` runs without errors (once deps installed).
* [ ] From repo root, **after** installing deps:

  * `python -c "import sum_core; print(sum_core.__version__)"` works.
  * `make test` still passes (new tests included).

---

### Dependencies & Prerequisites

* M0-001 completed:

  * Root `pyproject.toml` with tooling config.
  * `Makefile` with `lint`, `test`, `format`.
  * Pre-commit set up.
* Python 3.12 virtualenv with dev tools installed.
* Wagtail + Django versions chosen and installed (via `pip install -e ./core` once this ticket is implemented).

---

### Testing Requirements

**Unit tests**

Add at least:

* `tests/test_sum_core_import.py`:

  ```python
  """
  Name: sum_core Import Tests
  Path: tests/test_sum_core_import.py
  Purpose: Basic sanity checks that sum_core is importable and exposes __version__.
  Family: Part of the root test suite validating core package wiring.
  Dependencies: sum_core
  """

  from sum_core import __version__


  def test_sum_core_has_version() -> None:
      assert isinstance(__version__, str)
      assert __version__
  ```

**Integration / sanity checks**

From `core/sum_core/test_project`:

* `python manage.py check`
* (Optional, later) `python manage.py migrate`
* (Later milestone) runserver via Docker.

**Manual checks**

* `pip install -e ./core` from repo root.
* Start a Python shell and `import sum_core`.

