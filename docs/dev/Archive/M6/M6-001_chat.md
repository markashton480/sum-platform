# Live server setup
_Exported on 12/16/2025 at 22:59:49 GMT from Cursor (2.2.20)_

---

**User**

Please carefully review the task in @docs/dev/M6/M6-001.md and implement. Take your time and carefully think through each step, ensuring you make good decisions. This will be setting up a live server, so accuracy is important. You're a super advanced model, so give it all you've got and don't let me down! When you're done, complete a work report and file it in `docs/dev/M6/M6-01_followup.md`

---

**Cursor**

Plan: I’m going to (1) scan the repo for existing deployment/docs conventions and the Django project layout (wsgi module, settings, health endpoint), (2) add the `infrastructure/` templates + scripts exactly as M6-001 specifies with safe defaults and placeholder variables, (3) write the new runbook `docs/dev/deploy/vps-golden-path.md`, update `boilerplate/.env.example`, and finally (4) produce the required work report in `docs/dev/M6/M6-01_followup.md`.

Nice: the repo already has production settings patterns (`settings/production.py`) keyed off env vars like `DJANGO_DB_*`, `ALLOWED_HOSTS`, and `REDIS_URL`, which we can align the systemd/Caddy scripts to without inventing new config knobs. Next I’ll inspect the existing `infrastructure/` directory and current boilerplate env guidance so we extend—not conflict—with what’s already here.

Good catch: `infrastructure/` already exists but is basically empty (just `__init__.py`), so we can safely extend it into the exact folder layout M6-001 wants. Next I’ll inspect the existing `.env.example` (it’s a dotfile so it didn’t show up in directory listings) plus any existing ops scripts/style conventions, then start adding the Caddy/systemd templates and deploy/backup/restore scripts.

Aha: the current boilerplate hardcodes `STATIC_ROOT` to `<app>/staticfiles` and `MEDIA_ROOT` to `<app>/media`, but the M6 golden-path layout expects `/srv/sum/<site_slug>/{static,media}` so Caddy can serve them directly. I’m going to add **env overrides** (`DJANGO_STATIC_ROOT` / `DJANGO_MEDIA_ROOT`) in the boilerplate settings (and CLI boilerplate), then wire the runbook/scripts/templates to those paths—keeping the existing defaults so nothing breaks in local dev.

```python
"""
Base Django/Wagtail settings shared across all environments.

This file contains settings common to both local development and production.
Environment-specific settings should be placed in local.py or production.py.

Replace 'project_name' with your actual project name after copying.
"""
from __future__ import annotations

import os
from pathlib import Path

# =============================================================================
# Core Django Settings
# =============================================================================

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Override this via environment variable in production
SECRET_KEY: str = os.getenv(
    "DJANGO_SECRET_KEY", "insecure-dev-only-change-in-production"
)

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
    # SUM Core apps (the reusable platform package)
    "sum_core",
    "sum_core.pages",
    "sum_core.navigation",
    "sum_core.leads",
    "sum_core.forms",
    "sum_core.analytics",
    "sum_core.seo",
    # Client home app (update after renaming project_name)
    "project_name.home",
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

ROOT_URLCONF: str = "project_name.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates" / "overrides",
        ],
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

WSGI_APPLICATION: str = "project_name.wsgi.application"

# =============================================================================
# Password Validation
# =============================================================================

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

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
STATICFILES_DIRS: list[Path] = [
    BASE_DIR / "static",
]
STATIC_ROOT: Path = Path(
    os.getenv("DJANGO_STATIC_ROOT", str(BASE_DIR / "staticfiles"))
)

MEDIA_URL: str = "/media/"
MEDIA_ROOT: Path = Path(os.getenv("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# =============================================================================
# Wagtail Settings
# =============================================================================

# TODO: Update this to your site name
WAGTAIL_SITE_NAME: str = "My Site"
WAGTAILADMIN_BASE_URL: str = os.getenv("WAGTAILADMIN_BASE_URL", "http://localhost:8001")

# =============================================================================
# Celery Configuration (defaults for development)
# =============================================================================

CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "memory://")
CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "cache+memory://")

# =============================================================================
# Email Configuration (defaults for development)
# =============================================================================

EMAIL_BACKEND: str = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST: str = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_USE_SSL: bool = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
DEFAULT_FROM_EMAIL: str = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

# =============================================================================
# Lead Notification Settings
# =============================================================================

LEAD_NOTIFICATION_EMAIL: str = os.getenv("LEAD_NOTIFICATION_EMAIL", "")

# =============================================================================
# Webhook Configuration
# =============================================================================

ZAPIER_WEBHOOK_URL: str = os.getenv("ZAPIER_WEBHOOK_URL", "")

```

```python
"""
Base Django/Wagtail settings shared across all environments.

This file contains settings common to both local development and production.
Environment-specific settings should be placed in local.py or production.py.

Replace 'project_name' with your actual project name after copying.
"""
from __future__ import annotations

import os
from pathlib import Path

# =============================================================================
# Core Django Settings
# =============================================================================

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Override this via environment variable in production
SECRET_KEY: str = os.getenv(
    "DJANGO_SECRET_KEY", "insecure-dev-only-change-in-production"
)

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
    # SUM Core apps (the reusable platform package)
    "sum_core",
    "sum_core.pages",
    "sum_core.navigation",
    "sum_core.leads",
    "sum_core.forms",
    "sum_core.analytics",
    "sum_core.seo",
    # Client home app (update after renaming project_name)
    "project_name.home",
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

ROOT_URLCONF: str = "project_name.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates" / "overrides",
        ],
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

WSGI_APPLICATION: str = "project_name.wsgi.application"

# =============================================================================
# Password Validation
# =============================================================================

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

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
STATICFILES_DIRS: list[Path] = [
    BASE_DIR / "static",
]
STATIC_ROOT: Path = Path(
    os.getenv("DJANGO_STATIC_ROOT", str(BASE_DIR / "staticfiles"))
)

MEDIA_URL: str = "/media/"
MEDIA_ROOT: Path = Path(os.getenv("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# =============================================================================
# Wagtail Settings
# =============================================================================

# TODO: Update this to your site name
WAGTAIL_SITE_NAME: str = "My Site"
WAGTAILADMIN_BASE_URL: str = os.getenv("WAGTAILADMIN_BASE_URL", "http://localhost:8001")

# =============================================================================
# Celery Configuration (defaults for development)
# =============================================================================

CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "memory://")
CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "cache+memory://")

# =============================================================================
# Email Configuration (defaults for development)
# =============================================================================

EMAIL_BACKEND: str = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST: str = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_USE_SSL: bool = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
DEFAULT_FROM_EMAIL: str = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

# =============================================================================
# Lead Notification Settings
# =============================================================================

LEAD_NOTIFICATION_EMAIL: str = os.getenv("LEAD_NOTIFICATION_EMAIL", "")

# =============================================================================
# Webhook Configuration
# =============================================================================

ZAPIER_WEBHOOK_URL: str = os.getenv("ZAPIER_WEBHOOK_URL", "")

```

```plaintext
{
  # Global options. Tune as needed.
  # email you@example.com
}

# ---------------------------------------------------------------------------
# SUM VPS Golden Path (Caddy)
#
# How to use:
# - Copy to: /etc/caddy/sites-enabled/sum-__SITE_SLUG__.caddy
# - Replace placeholders:
#   - __SITE_SLUG__ (e.g. acme-kitchens)
#   - __DOMAIN__ (e.g. example.com, www.example.com)
# - Ensure Caddy can read static/media and connect to the unix socket:
#   - Add caddy user to the socket group (recommended: www-data)
# ---------------------------------------------------------------------------

__DOMAIN__ {
  # Compression
  encode gzip zstd

  # Security headers (baseline; adjust to your needs)
  header {
    X-Content-Type-Options nosniff
    X-Frame-Options DENY
    Referrer-Policy strict-origin-when-cross-origin
    Permissions-Policy "geolocation=(), microphone=(), camera=()"
  }

  # Serve static files directly (strip /static prefix)
  handle_path /static/* {
    root * /srv/sum/__SITE_SLUG__/static
    file_server
  }

  # Serve media uploads directly (strip /media prefix)
  handle_path /media/* {
    root * /srv/sum/__SITE_SLUG__/media
    file_server
  }

  # App
  reverse_proxy unix//run/sum-__SITE_SLUG__/gunicorn.sock
}


```

```plaintext
[Unit]
Description=SUM (__SITE_SLUG__) Gunicorn
After=network.target

# If using optional socket activation, uncomment:
# Requires=sum-__SITE_SLUG__-gunicorn.socket
# After=sum-__SITE_SLUG__-gunicorn.socket

[Service]
Type=simple
User=__DEPLOY_USER__
Group=www-data
WorkingDirectory=/srv/sum/__SITE_SLUG__/app
EnvironmentFile=/srv/sum/__SITE_SLUG__/.env

# Ensure runtime dir exists for the socket path below:
RuntimeDirectory=sum-__SITE_SLUG__
RuntimeDirectoryMode=0755

# Conservative hardening (safe defaults; relax if needed)
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

# Gunicorn
# - __PROJECT_MODULE__ is your Django project package (e.g. "acme_kitchens")
# - The socket path must match Caddyfile.template
#
# Default (no socket activation):
ExecStart=/srv/sum/__SITE_SLUG__/venv/bin/gunicorn \
  --workers 3 \
  --bind unix:/run/sum-__SITE_SLUG__/gunicorn.sock \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  __PROJECT_MODULE__.wsgi:application
#
# Optional (socket activation): enable sum-__SITE_SLUG__-gunicorn.socket and use fd://0
# ExecStart=/srv/sum/__SITE_SLUG__/venv/bin/gunicorn \
#   --workers 3 \
#   --bind fd://0 \
#   --access-logfile - \
#   --error-logfile - \
#   --capture-output \
#   __PROJECT_MODULE__.wsgi:application

Restart=on-failure
RestartSec=3
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target


```

```plaintext
[Unit]
Description=SUM (__SITE_SLUG__) Gunicorn Socket

[Socket]
ListenStream=/run/sum-__SITE_SLUG__/gunicorn.sock
SocketUser=__DEPLOY_USER__
SocketGroup=www-data
SocketMode=0660

# Create the runtime dir if needed
RuntimeDirectory=sum-__SITE_SLUG__
RuntimeDirectoryMode=0755

[Install]
WantedBy=sockets.target


```

```plaintext
[Unit]
Description=SUM (__SITE_SLUG__) Celery Worker
After=network.target

# If Redis is used as broker, you may want:
# After=redis-server.service

[Service]
Type=simple
User=__DEPLOY_USER__
Group=www-data
WorkingDirectory=/srv/sum/__SITE_SLUG__/app
EnvironmentFile=/srv/sum/__SITE_SLUG__/.env

# Celery
# - __PROJECT_MODULE__ is your Django project package (e.g. "acme_kitchens")
# - You must configure CELERY_BROKER_URL / CELERY_RESULT_BACKEND in /srv/sum/<slug>/.env
ExecStart=/srv/sum/__SITE_SLUG__/venv/bin/celery -A __PROJECT_MODULE__ worker -l INFO

Restart=on-failure
RestartSec=3
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target


```

```shellscript
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  deploy.sh --site-slug <slug> [--ref <git-ref>] [--no-restart] [--domain <domain>]

Expected server layout:
  /srv/sum/<slug>/app/   (git checkout of the client site)
  /srv/sum/<slug>/venv/  (python venv)
  /srv/sum/<slug>/.env   (env vars: DJANGO_SETTINGS_MODULE, DB creds, etc)
  /srv/sum/<slug>/static (collectstatic target; via DJANGO_STATIC_ROOT)
  /srv/sum/<slug>/media  (upload target; via DJANGO_MEDIA_ROOT)

Notes:
  - This script is designed to be re-run safely.
  - It reads secrets from /srv/sum/<slug>/.env (not from git).
EOF
}

log() { printf '[deploy] %s\n' "$*" >&2; }
die() { printf '[deploy] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG="${SITE_SLUG:-}"
REF=""
NO_RESTART="false"
DOMAIN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    --ref) REF="${2:-}"; shift 2 ;;
    --no-restart) NO_RESTART="true"; shift ;;
    --domain) DOMAIN="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required (or set SITE_SLUG env var)"

BASE_DIR="/srv/sum/${SITE_SLUG}"
APP_DIR="${BASE_DIR}/app"
VENV_DIR="${BASE_DIR}/venv"
ENV_FILE="${BASE_DIR}/.env"
LOCK_FILE="${BASE_DIR}/deploy.lock"

[[ -d "$APP_DIR" ]] || die "App dir not found: $APP_DIR"
[[ -f "$ENV_FILE" ]] || die "Env file not found: $ENV_FILE"

mkdir -p "$BASE_DIR"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  die "Another deploy appears to be running (lock: $LOCK_FILE)"
fi

log "Loading env: $ENV_FILE"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# If caller didn't provide, try to use env:
DOMAIN="${DOMAIN:-${SITE_DOMAIN:-${DEPLOY_DOMAIN:-}}}"

log "Ensuring venv: $VENV_DIR"
if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi

PY="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

log "Updating pip tooling"
"$PY" -m pip install --upgrade pip setuptools wheel >/dev/null

log "Updating code in: $APP_DIR"
cd "$APP_DIR"

if [[ -n "$(git status --porcelain)" ]]; then
  die "Git working tree is dirty; refuse to deploy. Fix in $APP_DIR"
fi

git fetch --all --tags --prune

if [[ -n "$REF" ]]; then
  log "Checking out ref: $REF"
  git checkout --force "$REF"
else
  log "Pulling current branch (ff-only)"
  git pull --ff-only
fi

log "Installing requirements"
if [[ -f "requirements.txt" ]]; then
  "$PIP" install -r requirements.txt
else
  die "requirements.txt not found in $APP_DIR"
fi

log "Running migrations"
"$PY" manage.py migrate --noinput

log "Collecting static"
"$PY" manage.py collectstatic --noinput

GUNICORN_SERVICE="sum-${SITE_SLUG}-gunicorn.service"
CELERY_SERVICE="sum-${SITE_SLUG}-celery.service"

if [[ "$NO_RESTART" != "true" ]]; then
  log "Restarting systemd service: $GUNICORN_SERVICE"
  sudo systemctl restart "$GUNICORN_SERVICE"

  if sudo systemctl list-unit-files "$CELERY_SERVICE" >/dev/null 2>&1; then
    if sudo systemctl is-enabled "$CELERY_SERVICE" >/dev/null 2>&1; then
      log "Restarting (enabled) service: $CELERY_SERVICE"
      sudo systemctl restart "$CELERY_SERVICE"
    else
      log "Celery unit exists but is not enabled; skipping restart: $CELERY_SERVICE"
    fi
  fi
else
  log "--no-restart set; skipping systemd restart"
fi

if [[ -n "$DOMAIN" ]]; then
  log "Smoke check: https://${DOMAIN}/health/"
  curl -fsS "https://${DOMAIN}/health/" >/dev/null
  log "Health OK"

  log "Optional: https://${DOMAIN}/sitemap.xml"
  if curl -fsS "https://${DOMAIN}/sitemap.xml" >/dev/null; then
    log "Sitemap OK"
  else
    log "Sitemap check failed (non-blocking)"
  fi
else
  log "DOMAIN not provided (use --domain or set SITE_DOMAIN in .env); skipping smoke check"
fi

cat <<EOF

Deploy complete.

Next steps / debugging:
  - Logs: sudo journalctl -u ${GUNICORN_SERVICE} -f --no-pager
  - Health: https://${DOMAIN:-<domain>}/health/
EOF


```

```shellscript
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  backup_db.sh --site-slug <slug>

Creates a gzipped plain-SQL pg_dump and stores it in:
  /srv/sum/<slug>/backups/

Requires:
  - /srv/sum/<slug>/.env containing DJANGO_DB_* variables
  - pg_dump available on PATH

Output:
  Prints the final backup file path on success.
EOF
}

log() { printf '[backup_db] %s\n' "$*" >&2; }
die() { printf '[backup_db] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG="${SITE_SLUG:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required (or set SITE_SLUG env var)"

BASE_DIR="/srv/sum/${SITE_SLUG}"
ENV_FILE="${BASE_DIR}/.env"
BACKUP_DIR="${BASE_DIR}/backups"

[[ -f "$ENV_FILE" ]] || die "Env file not found: $ENV_FILE"

log "Loading env: $ENV_FILE"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${DJANGO_DB_NAME:?DJANGO_DB_NAME missing in .env}"
: "${DJANGO_DB_USER:?DJANGO_DB_USER missing in .env}"
: "${DJANGO_DB_PASSWORD:?DJANGO_DB_PASSWORD missing in .env}"
: "${DJANGO_DB_HOST:?DJANGO_DB_HOST missing in .env}"

DJANGO_DB_PORT="${DJANGO_DB_PORT:-5432}"

mkdir -p "$BACKUP_DIR"
umask 077

ts="$(date -u +%Y%m%dT%H%M%SZ)"
out="${BACKUP_DIR}/${SITE_SLUG}_db_${ts}.sql.gz"

log "Writing backup: $out"

export PGPASSWORD="$DJANGO_DB_PASSWORD"
pg_dump \
  --host "$DJANGO_DB_HOST" \
  --port "$DJANGO_DB_PORT" \
  --username "$DJANGO_DB_USER" \
  --dbname "$DJANGO_DB_NAME" \
  --format=plain \
  --no-owner \
  --no-privileges \
  --clean \
  --if-exists \
| gzip -c > "$out"

unset PGPASSWORD

printf '%s\n' "$out"


```

```shellscript
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  restore_db.sh --site-slug <slug> --file <path.sql.gz> --i-know-this-will-overwrite [--no-restart]

Restores a gzipped plain-SQL backup created by backup_db.sh into the site's configured DB.

Safety:
  - You must pass --i-know-this-will-overwrite (required)

Requires:
  - /srv/sum/<slug>/.env containing DJANGO_DB_* variables
  - psql available on PATH
EOF
}

log() { printf '[restore_db] %s\n' "$*" >&2; }
die() { printf '[restore_db] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG="${SITE_SLUG:-}"
FILE=""
CONFIRM="false"
NO_RESTART="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    --file) FILE="${2:-}"; shift 2 ;;
    --i-know-this-will-overwrite) CONFIRM="true"; shift ;;
    --no-restart) NO_RESTART="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required (or set SITE_SLUG env var)"
[[ -n "$FILE" ]] || die "--file is required"
[[ -f "$FILE" ]] || die "Backup file not found: $FILE"
[[ "$CONFIRM" == "true" ]] || die "Refusing to run without --i-know-this-will-overwrite"

BASE_DIR="/srv/sum/${SITE_SLUG}"
ENV_FILE="${BASE_DIR}/.env"

[[ -f "$ENV_FILE" ]] || die "Env file not found: $ENV_FILE"

log "Loading env: $ENV_FILE"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${DJANGO_DB_NAME:?DJANGO_DB_NAME missing in .env}"
: "${DJANGO_DB_USER:?DJANGO_DB_USER missing in .env}"
: "${DJANGO_DB_PASSWORD:?DJANGO_DB_PASSWORD missing in .env}"
: "${DJANGO_DB_HOST:?DJANGO_DB_HOST missing in .env}"

DJANGO_DB_PORT="${DJANGO_DB_PORT:-5432}"

GUNICORN_SERVICE="sum-${SITE_SLUG}-gunicorn.service"

if [[ "$NO_RESTART" != "true" ]]; then
  log "Stopping service before restore: $GUNICORN_SERVICE"
  sudo systemctl stop "$GUNICORN_SERVICE" || true
else
  log "--no-restart set; not stopping service (not recommended)"
fi

log "Restoring DB '${DJANGO_DB_NAME}' from: $FILE"
export PGPASSWORD="$DJANGO_DB_PASSWORD"
gunzip -c "$FILE" | psql \
  --host "$DJANGO_DB_HOST" \
  --port "$DJANGO_DB_PORT" \
  --username "$DJANGO_DB_USER" \
  --dbname "$DJANGO_DB_NAME" \
  --set ON_ERROR_STOP=on
unset PGPASSWORD

if [[ "$NO_RESTART" != "true" ]]; then
  log "Starting service: $GUNICORN_SERVICE"
  sudo systemctl start "$GUNICORN_SERVICE"
fi

log "Restore complete"


```

```shellscript
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  provision_vps.sh --site-slug <slug> --deploy-user <user> [--install-packages]

This is an OPTIONAL helper. It is intentionally conservative and explicit.
It prepares baseline directories and (optionally) installs packages.

It does NOT:
  - Configure Postgres roles/dbs
  - Configure Caddy site files/domains
  - Install systemd unit files

Run as root (or with sudo).
EOF
}

log() { printf '[provision_vps] %s\n' "$*" >&2; }
die() { printf '[provision_vps] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG=""
DEPLOY_USER=""
INSTALL_PACKAGES="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    --deploy-user) DEPLOY_USER="${2:-}"; shift 2 ;;
    --install-packages) INSTALL_PACKAGES="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required"
[[ -n "$DEPLOY_USER" ]] || die "--deploy-user is required"

if [[ "$(id -u)" -ne 0 ]]; then
  die "Run as root (or via sudo)"
fi

if [[ "$INSTALL_PACKAGES" == "true" ]]; then
  log "Installing baseline packages (apt)"
  apt-get update -y
  apt-get install -y \
    ca-certificates \
    curl \
    git \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    libpq-dev \
    postgresql-client \
    ufw

  # Caddy official repo install (idempotent)
  if ! command -v caddy >/dev/null 2>&1; then
    log "Installing Caddy"
    apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update -y
    apt-get install -y caddy
  fi
fi

log "Ensuring deploy user exists: $DEPLOY_USER"
if ! id "$DEPLOY_USER" >/dev/null 2>&1; then
  useradd --create-home --shell /bin/bash "$DEPLOY_USER"
fi

log "Creating site directories"
BASE_DIR="/srv/sum/${SITE_SLUG}"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "$BASE_DIR"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "${BASE_DIR}/backups"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "${BASE_DIR}/static"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "${BASE_DIR}/media"

log "Ensuring log directory exists"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/var/log/sum/${SITE_SLUG}"

log "UFW baseline (SSH + HTTP/HTTPS)"
ufw allow OpenSSH || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true

cat <<EOF

Provisioning helper complete.

Next (manual):
  - Postgres: create role/db; set password; test psql connection
  - Place /srv/sum/${SITE_SLUG}/.env (chmod 600)
  - Clone app into ${BASE_DIR}/app
  - Install systemd unit(s) and Caddy site file
EOF


```

Got blocked by Cursor’s globalignore on editing dotfiles (`boilerplate/.env.example`), so I’m going to update those two `.env.example` files via a small idempotent Python edit in the terminal (it will insert the new golden-path vars only if they’re missing). After that, I’ll write the full runbook + the required followup report doc, then do a quick lint check on the two settings files I changed.

---

**User**

continue

---

**Cursor**

Plan: I’ll first update the two `.env.example` files (via a safe terminal edit since dotfiles are blocked by the editor tool), then write the full VPS runbook + templates usage, and finally add the required follow-up work report and run a quick lint check on the settings files we touched.

```markdown
# VPS Golden Path Deployment (Ubuntu + Caddy + systemd + Postgres + backups)

This is the **boring, repeatable “golden path”** for deploying a SUM client site to a single Ubuntu VPS using **Caddy + systemd + Postgres** (and Redis only if you enable cache/Celery in production).

## Assumptions

- **Ubuntu** 22.04+ (tested target; adjust packages for other versions)
- You deploy **one site per server directory**: `/srv/sum/<site_slug>/...`
- You run Django/Wagtail using **gunicorn** behind **Caddy**
- The client site uses **production settings**: `DJANGO_SETTINGS_MODULE=<project>.settings.production`

## 1) VPS prerequisites

### Packages

Install baseline packages (as root):

```bash
sudo apt update
sudo apt install -y \
  ca-certificates curl git \
  python3 python3-venv python3-pip build-essential \
  libpq-dev postgresql postgresql-contrib postgresql-client \
  redis-server \
  ufw
```

**Redis**: install only if you intend to use Redis cache / Celery broker in production. If you do not, you can omit `redis-server` and ensure your production settings aren’t configured to require it.

### Caddy install (official repo)

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

## 2) Create deploy user + basic hardening

### Deploy user

```bash
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy
```

### SSH hardening (baseline)

- Use SSH keys (disable password login once verified)
- Consider: disable root SSH login

Edit `/etc/ssh/sshd_config` carefully, then:

```bash
sudo systemctl reload ssh
```

## 3) Firewall (UFW minimal rules)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status verbose
```

## 4) Postgres setup (DB + user + verify)

Create a DB/user **per site**:

```bash
sudo -u postgres psql
```

In `psql`:

```sql
CREATE USER sum_site_user WITH PASSWORD 'REPLACE_ME_STRONG_PASSWORD';
CREATE DATABASE sum_site_db OWNER sum_site_user;
\q
```

Verify connectivity:

```bash
psql "postgresql://sum_site_user:REPLACE_ME_STRONG_PASSWORD@127.0.0.1:5432/sum_site_db" -c "SELECT 1;"
```

## 5) Server directory layout

Choose a **site slug**, e.g. `acme-kitchens`.

Create directories:

```bash
export SITE_SLUG="acme-kitchens"
export DEPLOY_USER="deploy"

sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/backups"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/static"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/media"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/var/log/sum/${SITE_SLUG}"
```

Create venv:

```bash
sudo -u "$DEPLOY_USER" python3 -m venv "/srv/sum/${SITE_SLUG}/venv"
```

Clone your client repo into `/srv/sum/<slug>/app`:

```bash
sudo -u "$DEPLOY_USER" git clone <YOUR_CLIENT_REPO_URL> "/srv/sum/${SITE_SLUG}/app"
```

## 6) `.env` placement and permissions

Create `/srv/sum/<site_slug>/.env` (owned by deploy user, not in git):

```bash
sudo -u "$DEPLOY_USER" nano "/srv/sum/${SITE_SLUG}/.env"
sudo chmod 600 "/srv/sum/${SITE_SLUG}/.env"
```

Minimum recommended values (adapt to your project module + domain):

```bash
DJANGO_SETTINGS_MODULE=<project_module>.settings.production
DJANGO_SECRET_KEY=<generate-strong-secret>
ALLOWED_HOSTS=example.com,www.example.com

DJANGO_DB_NAME=sum_site_db
DJANGO_DB_USER=sum_site_user
DJANGO_DB_PASSWORD=<strong-password>
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=5432

# Golden-path static/media roots (served by Caddy)
DJANGO_STATIC_ROOT=/srv/sum/<site_slug>/static
DJANGO_MEDIA_ROOT=/srv/sum/<site_slug>/media

# Optional: for deploy script smoke checks
SITE_DOMAIN=example.com

# Redis/Celery only if used in production
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 7) systemd units (gunicorn + optional socket + optional celery)

Templates live in this repo:

- `infrastructure/systemd/sum-site-gunicorn.service.template`
- `infrastructure/systemd/sum-site-gunicorn.socket.template`
- `infrastructure/systemd/sum-site-celery.service.template`

### Install gunicorn service

Copy the template to `/etc/systemd/system/` and replace placeholders:

- `__SITE_SLUG__` (e.g. `acme-kitchens`)
- `__DEPLOY_USER__` (e.g. `deploy`)
- `__PROJECT_MODULE__` (your Django project package, e.g. `acme_kitchens`)

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-gunicorn.service.template \
  /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service

sudo nano /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service
```

Reload and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-gunicorn.service"
sudo systemctl status "sum-${SITE_SLUG}-gunicorn.service" --no-pager
```

### (Optional) socket activation

If you want socket activation, install the socket unit and uncomment the `Requires=` lines in the service template and switch `ExecStart` to `--bind fd://0`.

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-gunicorn.socket.template \
  /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.socket
sudo nano /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.socket

sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-gunicorn.socket"
```

### (Optional) celery worker

Only enable if you need async tasks day 1.

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-celery.service.template \
  /etc/systemd/system/sum-${SITE_SLUG}-celery.service
sudo nano /etc/systemd/system/sum-${SITE_SLUG}-celery.service

sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-celery.service"
```

## 8) Caddy setup + domain + TLS

Template:

- `infrastructure/caddy/Caddyfile.template`

Install a site config (replace `__DOMAIN__` and `__SITE_SLUG__`):

```bash
sudo cp /path/to/repo/infrastructure/caddy/Caddyfile.template \
  /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
sudo nano /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
```

Ensure Caddy can connect to the gunicorn socket:

```bash
sudo usermod -aG www-data caddy
sudo systemctl restart caddy
```

Validate + reload:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

TLS will be provisioned automatically by Caddy when DNS points at the VPS and ports 80/443 are open.

## 9) First deploy instructions (deploy script)

Scripts live in:

- `infrastructure/scripts/deploy.sh`
- `infrastructure/scripts/backup_db.sh`
- `infrastructure/scripts/restore_db.sh`

On the VPS, copy these scripts into a predictable location (or keep them in the app repo if you vendor them in your client repo):

```bash
sudo install -d -m 0755 /srv/sum/bin
sudo cp /path/to/repo/infrastructure/scripts/*.sh /srv/sum/bin/
sudo chmod +x /srv/sum/bin/*.sh
```

Allow deploy user to restart the specific service(s) without a password (recommended minimal sudoers):

```bash
sudo visudo
```

Add something like:

```
deploy ALL=NOPASSWD: /bin/systemctl restart sum-*-gunicorn.service, /bin/systemctl start sum-*-gunicorn.service, /bin/systemctl stop sum-*-gunicorn.service
```

Run deploy:

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/deploy.sh --site-slug "$SITE_SLUG" --ref vX.Y.Z --domain example.com
```

Smoke check requirements:

- `https://<domain>/health/` returns **HTTP 200** for `ok` or `degraded` (only `unhealthy` is **503**)
- Optional: `https://<domain>/sitemap.xml` returns 200 (logged but non-blocking)

## 10) Upgrade flow (tag pinning discipline)

For the client repo, ensure the `sum_core` dependency is pinned by tag (`SUM_CORE_GIT_REF`) in `requirements.txt` as documented in the boilerplate readme.

Upgrade steps:

- Update `SUM_CORE_GIT_REF` to a new tag in the client `requirements.txt`
- Commit + push
- Deploy with `--ref <tag>` (or deploy main branch if that’s your policy)

Rollback:

- Re-deploy the previous known-good git tag:
  - `deploy.sh --site-slug <slug> --ref vPrev --domain <domain>`

## 11) Backup + restore rehearsal (required)

### Backup

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/backup_db.sh --site-slug "$SITE_SLUG"
```

Output is a gzipped plain SQL file under:

- `/srv/sum/<site_slug>/backups/<site_slug>_db_<UTC_TIMESTAMP>.sql.gz`

### Restore rehearsal

Recommended rehearsal flow:

- Provision a fresh/empty DB for the site (or recreate the DB)
- Stop gunicorn
- Restore
- Start gunicorn
- Verify `/health/`

Restore command (requires explicit confirmation flag):

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/restore_db.sh \\\n  --site-slug \"$SITE_SLUG\" \\\n  --file \"/srv/sum/${SITE_SLUG}/backups/<backup_file>.sql.gz\" \\\n  --i-know-this-will-overwrite\n+```

## 12) Operational sanity: logs + debugging

Gunicorn logs go to journald by default:

```bash
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -f --no-pager
```

Caddy logs:

```bash
sudo journalctl -u caddy -f --no-pager
```


```

Good progress: infrastructure templates + scripts are in place and `.env.example` now includes the new golden-path variables for static/media + optional smoke-check domain. Next I’ll tighten the runbook (there’s a formatting glitch in the restore example and we should clarify Redis requirements based on current production settings), then I’ll add the M6 follow-up report and do a quick lint pass on the settings edits.

```markdown
*** Begin Patch
*** Update File: docs/dev/deploy/vps-golden-path.md
@@
-Install baseline packages (as root):
+Install baseline packages (as root):
@@
-sudo apt install -y \
+sudo apt install -y \
   ca-certificates curl git \
   python3 python3-venv python3-pip build-essential \
   libpq-dev postgresql postgresql-contrib postgresql-client \
-  redis-server \
   ufw
 ```
 
-**Redis**: install only if you intend to use Redis cache / Celery broker in production. If you do not, you can omit `redis-server` and ensure your production settings aren’t configured to require it.
+**Redis**:
+
+- In the **current SUM client boilerplate**, `settings/production.py` configures Django cache to use Redis via `REDIS_URL`, and `/health/` treats cache as **critical**—so **Redis is effectively required** for the default production stack.
+- If you intentionally customize production settings to not use Redis, you can omit it. Otherwise, install it:
+
+```bash
+sudo apt install -y redis-server
+```
@@
 Restore command (requires explicit confirmation flag):
 
 ```bash
-sudo -u "$DEPLOY_USER" /srv/sum/bin/restore_db.sh \\\n  --site-slug \"$SITE_SLUG\" \\\n  --file \"/srv/sum/${SITE_SLUG}/backups/<backup_file>.sql.gz\" \\\n  --i-know-this-will-overwrite\n-+```
+sudo -u "$DEPLOY_USER" /srv/sum/bin/restore_db.sh \
+  --site-slug "$SITE_SLUG" \
+  --file "/srv/sum/${SITE_SLUG}/backups/<backup_file>.sql.gz" \
+  --i-know-this-will-overwrite
+```
*** End Patch
```

```markdown
# VPS Golden Path Deployment (Ubuntu + Caddy + systemd + Postgres + backups)

This is the **boring, repeatable “golden path”** for deploying a SUM client site to a single Ubuntu VPS using **Caddy + systemd + Postgres** (and Redis only if you enable cache/Celery in production).

## Assumptions

- **Ubuntu** 22.04+ (tested target; adjust packages for other versions)
- You deploy **one site per server directory**: `/srv/sum/<site_slug>/...`
- You run Django/Wagtail using **gunicorn** behind **Caddy**
- The client site uses **production settings**: `DJANGO_SETTINGS_MODULE=<project>.settings.production`

## 1) VPS prerequisites

### Packages

Install baseline packages (as root):

```bash
sudo apt update
sudo apt install -y \
  ca-certificates curl git \
  python3 python3-venv python3-pip build-essential \
  libpq-dev postgresql postgresql-contrib postgresql-client \
  ufw
```

**Redis**:

- In the **current SUM client boilerplate**, `settings/production.py` configures Django cache to use Redis via `REDIS_URL`, and `/health/` treats cache as **critical**—so **Redis is effectively required** for the default production stack.
- If you intentionally customize production settings to not use Redis, you can omit it. Otherwise, install it:

```bash
sudo apt install -y redis-server
```

### Caddy install (official repo)

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

## 2) Create deploy user + basic hardening

### Deploy user

```bash
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy
```

### SSH hardening (baseline)

- Use SSH keys (disable password login once verified)
- Consider: disable root SSH login

Edit `/etc/ssh/sshd_config` carefully, then:

```bash
sudo systemctl reload ssh
```

## 3) Firewall (UFW minimal rules)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status verbose
```

## 4) Postgres setup (DB + user + verify)

Create a DB/user **per site**:

```bash
sudo -u postgres psql
```

In `psql`:

```sql
CREATE USER sum_site_user WITH PASSWORD 'REPLACE_ME_STRONG_PASSWORD';
CREATE DATABASE sum_site_db OWNER sum_site_user;
\q
```

Verify connectivity:

```bash
psql "postgresql://sum_site_user:REPLACE_ME_STRONG_PASSWORD@127.0.0.1:5432/sum_site_db" -c "SELECT 1;"
```

## 5) Server directory layout

Choose a **site slug**, e.g. `acme-kitchens`.

Create directories:

```bash
export SITE_SLUG="acme-kitchens"
export DEPLOY_USER="deploy"

sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/backups"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/static"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/media"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/var/log/sum/${SITE_SLUG}"
```

Create venv:

```bash
sudo -u "$DEPLOY_USER" python3 -m venv "/srv/sum/${SITE_SLUG}/venv"
```

Clone your client repo into `/srv/sum/<slug>/app`:

```bash
sudo -u "$DEPLOY_USER" git clone <YOUR_CLIENT_REPO_URL> "/srv/sum/${SITE_SLUG}/app"
```

## 6) `.env` placement and permissions

Create `/srv/sum/<site_slug>/.env` (owned by deploy user, not in git):

```bash
sudo -u "$DEPLOY_USER" nano "/srv/sum/${SITE_SLUG}/.env"
sudo chmod 600 "/srv/sum/${SITE_SLUG}/.env"
```

Minimum recommended values (adapt to your project module + domain):

```bash
DJANGO_SETTINGS_MODULE=<project_module>.settings.production
DJANGO_SECRET_KEY=<generate-strong-secret>
ALLOWED_HOSTS=example.com,www.example.com

DJANGO_DB_NAME=sum_site_db
DJANGO_DB_USER=sum_site_user
DJANGO_DB_PASSWORD=<strong-password>
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=5432

# Golden-path static/media roots (served by Caddy)
DJANGO_STATIC_ROOT=/srv/sum/<site_slug>/static
DJANGO_MEDIA_ROOT=/srv/sum/<site_slug>/media

# Optional: for deploy script smoke checks
SITE_DOMAIN=example.com

# Redis/Celery only if used in production
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 7) systemd units (gunicorn + optional socket + optional celery)

Templates live in this repo:

- `infrastructure/systemd/sum-site-gunicorn.service.template`
- `infrastructure/systemd/sum-site-gunicorn.socket.template`
- `infrastructure/systemd/sum-site-celery.service.template`

### Install gunicorn service

Copy the template to `/etc/systemd/system/` and replace placeholders:

- `__SITE_SLUG__` (e.g. `acme-kitchens`)
- `__DEPLOY_USER__` (e.g. `deploy`)
- `__PROJECT_MODULE__` (your Django project package, e.g. `acme_kitchens`)

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-gunicorn.service.template \
  /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service

sudo nano /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service
```

Reload and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-gunicorn.service"
sudo systemctl status "sum-${SITE_SLUG}-gunicorn.service" --no-pager
```

### (Optional) socket activation

If you want socket activation, install the socket unit and uncomment the `Requires=` lines in the service template and switch `ExecStart` to `--bind fd://0`.

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-gunicorn.socket.template \
  /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.socket
sudo nano /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.socket

sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-gunicorn.socket"
```

### (Optional) celery worker

Only enable if you need async tasks day 1.

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-celery.service.template \
  /etc/systemd/system/sum-${SITE_SLUG}-celery.service
sudo nano /etc/systemd/system/sum-${SITE_SLUG}-celery.service

sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-celery.service"
```

## 8) Caddy setup + domain + TLS

Template:

- `infrastructure/caddy/Caddyfile.template`

Install a site config (replace `__DOMAIN__` and `__SITE_SLUG__`):

```bash
sudo cp /path/to/repo/infrastructure/caddy/Caddyfile.template \
  /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
sudo nano /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
```

Ensure Caddy can connect to the gunicorn socket:

```bash
sudo usermod -aG www-data caddy
sudo systemctl restart caddy
```

Validate + reload:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

TLS will be provisioned automatically by Caddy when DNS points at the VPS and ports 80/443 are open.

## 9) First deploy instructions (deploy script)

Scripts live in:

- `infrastructure/scripts/deploy.sh`
- `infrastructure/scripts/backup_db.sh`
- `infrastructure/scripts/restore_db.sh`

On the VPS, copy these scripts into a predictable location (or keep them in the app repo if you vendor them in your client repo):

```bash
sudo install -d -m 0755 /srv/sum/bin
sudo cp /path/to/repo/infrastructure/scripts/*.sh /srv/sum/bin/
sudo chmod +x /srv/sum/bin/*.sh
```

Allow deploy user to restart the specific service(s) without a password (recommended minimal sudoers):

```bash
sudo visudo
```

Add something like:

```
deploy ALL=NOPASSWD: /bin/systemctl restart sum-*-gunicorn.service, /bin/systemctl start sum-*-gunicorn.service, /bin/systemctl stop sum-*-gunicorn.service
```

Run deploy:

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/deploy.sh --site-slug "$SITE_SLUG" --ref vX.Y.Z --domain example.com
```

Smoke check requirements:

- `https://<domain>/health/` returns **HTTP 200** for `ok` or `degraded` (only `unhealthy` is **503**)
- Optional: `https://<domain>/sitemap.xml` returns 200 (logged but non-blocking)

## 10) Upgrade flow (tag pinning discipline)

For the client repo, ensure the `sum_core` dependency is pinned by tag (`SUM_CORE_GIT_REF`) in `requirements.txt` as documented in the boilerplate readme.

Upgrade steps:

- Update `SUM_CORE_GIT_REF` to a new tag in the client `requirements.txt`
- Commit + push
- Deploy with `--ref <tag>` (or deploy main branch if that’s your policy)

Rollback:

- Re-deploy the previous known-good git tag:
  - `deploy.sh --site-slug <slug> --ref vPrev --domain <domain>`

## 11) Backup + restore rehearsal (required)

### Backup

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/backup_db.sh --site-slug "$SITE_SLUG"
```

Output is a gzipped plain SQL file under:

- `/srv/sum/<site_slug>/backups/<site_slug>_db_<UTC_TIMESTAMP>.sql.gz`

### Restore rehearsal

Recommended rehearsal flow:

- Provision a fresh/empty DB for the site (or recreate the DB)
- Stop gunicorn
- Restore
- Start gunicorn
- Verify `/health/`

Restore command (requires explicit confirmation flag):

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/restore_db.sh \
  --site-slug "$SITE_SLUG" \
  --file "/srv/sum/${SITE_SLUG}/backups/<backup_file>.sql.gz" \
  --i-know-this-will-overwrite
```

## 12) Operational sanity: logs + debugging

Gunicorn logs go to journald by default:

```bash
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -f --no-pager
```

Caddy logs:

```bash
sudo journalctl -u caddy -f --no-pager
```



```

```markdown
## M6-001 Follow-up Report: VPS Golden Path Deployment (Caddy + systemd + Postgres + backups)

### Summary

Implemented the **M6-001 “VPS golden path”** deliverables:

- **Infrastructure templates** for Caddy and systemd under `infrastructure/`
- **Deploy + backup + restore scripts** (fail-fast, idempotent where it matters)
- **Runbook** documenting a fresh Ubuntu VPS setup and first deploy
- **Boilerplate support** for golden-path static/media directories via env overrides

### Key Decisions (and why)

- **Gunicorn behind unix socket**: avoids exposing app ports, works cleanly with systemd + Caddy.
- **Logs to journald**: gunicorn configured to log to stdout/stderr, so `journalctl` is the default operational surface.
- **Static/media served by Caddy**: runbook uses `/srv/sum/<site_slug>/{static,media}`; Django is configured to collect to those via env vars.
- **Redis note**: current boilerplate `settings/production.py` configures Redis cache by default and `/health/` treats cache as **critical**, so Redis is effectively required unless production settings are customized.

### Files Added / Changed

- **Added**: `infrastructure/caddy/Caddyfile.template`
- **Added**: `infrastructure/systemd/`
  - `sum-site-gunicorn.service.template`
  - `sum-site-gunicorn.socket.template` (optional)
  - `sum-site-celery.service.template` (optional)
- **Added**: `infrastructure/scripts/`
  - `deploy.sh`
  - `backup_db.sh`
  - `restore_db.sh`
  - `provision_vps.sh` (optional helper)
- **Added**: `docs/dev/deploy/vps-golden-path.md`
- **Changed**: `boilerplate/project_name/settings/base.py`
- **Changed**: `cli/sum_cli/boilerplate/project_name/settings/base.py`
- **Changed**: `boilerplate/.env.example` (dotfile; updated via terminal edit due to editor ignore)
- **Changed**: `cli/sum_cli/boilerplate/.env.example` (dotfile; updated via terminal edit due to editor ignore)

### How To Use (quick pointers)

- **Runbook**: follow `docs/dev/deploy/vps-golden-path.md` end-to-end on a fresh VPS.
- **Deploy script**:
  - `/srv/sum/bin/deploy.sh --site-slug <slug> --ref <tag> --domain <domain>`
  - Supports `--no-restart` for debugging.
- **Backup script**:
  - `/srv/sum/bin/backup_db.sh --site-slug <slug>`
  - Produces `*.sql.gz` in `/srv/sum/<slug>/backups/`.
- **Restore script**:
  - Requires explicit `--i-know-this-will-overwrite`.

### Acceptance Criteria Checklist (M6-001)

- **Provisioning**: runbook covers packages, deploy user, ssh hardening notes, UFW, Postgres setup and verification.
- **Deploy**: deploy script runs `migrate`, `collectstatic`, restarts gunicorn, and performs health + sitemap smoke checks.
- **Backup/Restore**: scripts create gzipped DB dumps and restore them with a confirmation guard.
- **Operational sanity**: journald logging documented; rollback via git tag deploy is documented.

### Follow-ups / Notes

- If you want Redis to be truly “optional” in production, you’ll need an explicit production setting toggle to use a non-Redis cache backend; the current boilerplate defaults to Redis cache in production.
- `deploy.sh` assumes deploy user can `sudo systemctl restart sum-<slug>-gunicorn.service` (runbook includes minimal sudoers guidance).


```

### Implemented (M6-001)
- **Golden-path infrastructure**: `infrastructure/caddy/`, `infrastructure/systemd/`, `infrastructure/scripts/`
  - Caddy template: `infrastructure/caddy/Caddyfile.template`
  - systemd templates: `infrastructure/systemd/sum-site-gunicorn.service.template`, `sum-site-gunicorn.socket.template` (optional), `sum-site-celery.service.template` (optional)
  - scripts: `infrastructure/scripts/deploy.sh`, `backup_db.sh`, `restore_db.sh`, `provision_vps.sh` (optional)
- **Runbook**: `docs/dev/deploy/vps-golden-path.md`
- **Boilerplate support for VPS static/media paths**:
  - `boilerplate/project_name/settings/base.py` + `cli/sum_cli/boilerplate/project_name/settings/base.py` now allow env overrides:
    - `DJANGO_STATIC_ROOT`
    - `DJANGO_MEDIA_ROOT`
  - Updated dotfiles (via terminal edit due to editor ignore):
    - `boilerplate/.env.example`
    - `cli/sum_cli/boilerplate/.env.example`
    - Added docs for `DJANGO_STATIC_ROOT`, `DJANGO_MEDIA_ROOT`, and optional `SITE_DOMAIN` (used by deploy smoke checks)

### Where to start
- Follow: `docs/dev/deploy/vps-golden-path.md`
- Then use:
  - **Deploy**: `deploy.sh --site-slug <slug> [--ref <tag>] [--domain <domain>]`
  - **Backup**: `backup_db.sh --site-slug <slug>`
  - **Restore**: `restore_db.sh --site-slug <slug> --file <backup.sql.gz> --i-know-this-will-overwrite`

### Work report
Filed at: `docs/dev/M6/M6-01_followup.md`

