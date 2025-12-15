"""
Name: Smoke Consumer Settings
Path: clients/_smoke_consumer/smoke_consumer/settings.py
Purpose: Minimal Django/Wagtail settings demonstrating sum_core consumption
         WITHOUT any dependency on test_project.
Family: Validation/proof project for sum_core consumability.
Dependencies: Django, Wagtail, sum_core

This file proves that sum_core is consumable as an installable package.
It contains ONLY the minimum configuration needed to run core features.
"""

from __future__ import annotations

import os
from pathlib import Path

# Import sum_core utilities for logging and Sentry
from sum_core.ops.logging import get_logging_config
from sum_core.ops.sentry import init_sentry

# =============================================================================
# Core Django Settings
# =============================================================================

BASE_DIR: Path = Path(__file__).resolve().parent.parent

SECRET_KEY: str = "smoke-consumer-dev-only-not-for-production"
DEBUG: bool = True
ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "[::1]", "testserver"]

# =============================================================================
# Application Definition
# =============================================================================

INSTALLED_APPS: list[str] = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Wagtail core
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
    # SUM Core apps (the package we're proving is consumable)
    "sum_core",
    "sum_core.pages",
    "sum_core.navigation",
    "sum_core.leads",
    "sum_core.forms",
    "sum_core.analytics",
    "sum_core.seo",
    # Smoke consumer's own home app
    "smoke_consumer.home",
]

MIDDLEWARE: list[str] = [
    "sum_core.ops.middleware.CorrelationIdMiddleware",  # Request correlation
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF: str = "smoke_consumer.urls"

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

WSGI_APPLICATION: str = "smoke_consumer.wsgi.application"

# =============================================================================
# Database - SQLite for simplicity (smoke test only)
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =============================================================================
# Cache - Required for health checks and rate limiting
# =============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "smoke-consumer-cache",
    }
}

# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE: str = "en-gb"
TIME_ZONE: str = "Europe/London"
USE_I18N: bool = True
USE_TZ: bool = True

# =============================================================================
# Static & Media Files
# =============================================================================

STATIC_URL: str = "/static/"
MEDIA_URL: str = "/media/"
MEDIA_ROOT: Path = BASE_DIR / "media"

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# =============================================================================
# Wagtail Settings
# =============================================================================

WAGTAIL_SITE_NAME: str = "Smoke Consumer"
WAGTAILADMIN_BASE_URL: str = "http://localhost:8001"

# =============================================================================
# Celery (sync mode for smoke testing)
# =============================================================================

CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "memory://")
CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "cache+memory://")
CELERY_TASK_ALWAYS_EAGER: bool = True
CELERY_TASK_EAGER_PROPAGATES: bool = True

# =============================================================================
# Email (console backend for smoke testing)
# =============================================================================

EMAIL_BACKEND: str = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL: str = "smoke@example.com"
LEAD_NOTIFICATION_EMAIL: str = ""

# =============================================================================
# Observability (sum_core.ops)
# =============================================================================

LOGGING = get_logging_config(debug=DEBUG)

# Initialize Sentry if SENTRY_DSN is set (no-ops otherwise)
init_sentry()
