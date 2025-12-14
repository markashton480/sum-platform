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
    for directory in [
        Path(__file__).resolve().parent,
        *Path(__file__).resolve().parents,
    ]:
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
    "sum_core.navigation",
    "sum_core.leads",
    "sum_core.forms",
    "home",
]

# Cache configuration (used for rate limiting)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sum-core-cache",
    }
}

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

FILE_UPLOAD_MAX_MEMORY_SIZE = 52_428_800  # 50MB

DATA_UPLOAD_MAX_MEMORY_SIZE = 52_428_800  # 50MB

MEDIA_URL: str = "/images/"
MEDIA_ROOT: str = BASE_DIR / "images"

STATIC_URL: str = "/static/"

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
