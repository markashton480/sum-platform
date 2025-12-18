# SUM Platform

SUM Platform is a Django/Wagtail foundation for quickly launching lead-focused websites for home improvement trades. The primary deliverable is the installable core package `sum-core` (import path `sum_core`), plus a minimal `test_project/` used for local development and CI-style validation.

This README is the main “how the repo works” entrypoint. The consolidated product/implementation spec lives in `docs/dev/SUM-PLATFORM-SSOT.md`.

## How We Work (Git)

- Default integration branch is `develop`.
- Create branches from `develop` and open PRs back into `develop` (CI check `lint-and-test` must pass).
- Promote releases via PR `develop` → `main`.
- Hotfixes land in `main` first, then get backported to `develop`.

## Where to Start (Documentation)

### For Understanding the Platform

- **Product + Architecture SSOT**: [docs/dev/SUM-PLATFORM-SSOT.md](docs/dev/SUM-PLATFORM-SSOT.md) — Single source of truth for the entire platform
- **Wiring Inventory**: [docs/dev/WIRING-INVENTORY.md](docs/dev/WIRING-INVENTORY.md) — How to consume `sum_core` in client projects
- **Full PRD** (audit trail): [docs/dev/prd-sum-platform-v1.1.md](docs/dev/prd-sum-platform-v1.1.md)

### For Implementing Features

- **Block Catalogue** (authoritative): [docs/dev/blocks-reference.md](docs/dev/blocks-reference.md)
- **Page Types Reference**: [docs/dev/page-types-reference.md](docs/dev/page-types-reference.md)
- **CSS Tokens + Design System**: [docs/dev/design/css-architecture-and-tokens.md](docs/dev/design/css-architecture-and-tokens.md)
- **Navigation System**: [docs/dev/NAV/navigation.md](docs/dev/NAV/navigation.md) — Header, footer, sticky CTA
- **Navigation Template Tags**: [docs/dev/navigation-tags-reference.md](docs/dev/navigation-tags-reference.md)

### For Contributors

- **Repository Hygiene Standards**: [docs/dev/hygiene.md](docs/dev/hygiene.md)
- **Daily Code Review Guidance**: [docs/dev/reviews/daily_code_review.md](docs/dev/reviews/daily_code_review.md)
- **Agent Orientation**: [docs/dev/AGENT-ORIENTATION.md](docs/dev/AGENT-ORIENTATION.md) — Platform vs test harness

### Audit Trail

- **Milestone Documentation**: [docs/dev/M0/](docs/dev/M0/), [docs/dev/M1/](docs/dev/M1/), [docs/dev/M2/](docs/dev/M2/), [docs/dev/M3/](docs/dev/M3/), [docs/dev/M4/](docs/dev/M4/)
- **Release Reviews**: [docs/dev/reports/M4/M4_release_review.md](docs/dev/reports/M4/M4_release_review.md)
- **CORE Audits**: [docs/dev/CM/](docs/dev/CM/)

## Current Status (End of Milestone 5)

Implemented in `sum_core` today:

- **Token-based design system** (`core/sum_core/static/sum_core/css/`) with a single template entrypoint: `sum_core/css/main.css`.
- **Branding + SiteSettings** (Wagtail Settings → "Site settings") providing colours, fonts, logos/favicon, business info, and social links.
- **Page types**:
  - `HomePage` is **client-owned** (canonical example: `clients/sum_client/sum_client/home/models.py`).
    The `core/sum_core/test_project/home/` app contains a harness-only HomePage used for local dev + CI validation of templates/blocks.
  - `StandardPage`, `ServiceIndexPage`, `ServicePage` (in `core/sum_core/pages/`).
  - Shared page metadata via `SeoFieldsMixin`, `OpenGraphMixin`, `BreadcrumbMixin`.
- **Navigation system** (Wagtail Settings → "Header Navigation" / "Footer Navigation"): header menus (3 levels), footer sections, and a mobile sticky CTA; output is cached and invalidated on relevant changes.
- **Forms + lead pipeline**:
  - Frontend blocks: `contact_form`, `quote_request_form`.
  - Submission endpoint: `POST /forms/submit/` (CSRF-protected) with honeypot + timing + rate-limit spam protection.
  - Lead persistence ("no lost leads" invariant), attribution capture, notification tasks (email + webhook), and Wagtail admin UI ("Leads") including CSV export.
- **Technical SEO** (`core/sum_core/seo/`):
  - `/sitemap.xml`: Auto-generated XML sitemap scoped per-site with exclusions for noindex/unpublished pages.
  - `/robots.txt`: Configurable per-site via SiteSettings with sitemap reference.
  - SEO template tags (`{% seo_tags %}`) for meta titles, descriptions, canonical URLs, and Open Graph.
  - JSON-LD structured data (`{% render_schema %}`) for LocalBusiness, Article, FAQ, and Service schemas.
- **Analytics integration** (`core/sum_core/analytics/`):
  - GA4/GTM injection via `{% analytics_head %}` and `{% analytics_body %}` template tags.
  - Lead analytics dashboard in Wagtail admin.
  - `dataLayer` event tracking for forms and CTAs.
- **Observability baseline** (`core/sum_core/ops/`):
  - `/health/` endpoint returning JSON status (DB, cache, Celery checks).
  - Sentry integration (optional, enabled via `SENTRY_DSN`).
  - Structured JSON logging with request correlation IDs.
- **Email delivery**:
  - HTML + plain-text multipart emails for lead notifications.
  - Per-site From/Reply-To/subject prefix configuration in SiteSettings.
  - Env-driven SMTP configuration for production providers.
- **Zapier integration**: Per-site webhook delivery with retries and status tracking.

Present but currently stubs/placeholders:

- `infrastructure/` (deployment scaffolding; not part of the core package).

## Prerequisites

- Python **3.12+**
- Optional (recommended): Docker + Docker Compose (local Postgres)

## Quick Start (Local Development)

Create and activate the repo-root virtualenv:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install `sum-core` in editable mode + dev tooling:

```bash
make install-dev
```

Run the test project:

```bash
make run
```

Then visit:

- Wagtail admin: `http://localhost:8000/admin/`
- Django admin: `http://localhost:8000/django-admin/` (used for some non-Wagtail models)

## Quick Start (Canonical Consumer: `sum_client`)

`clients/sum_client/` is the recommended “real client consumer” reference project. It consumes `sum_core` the way an external client would (settings split, URL wiring, overrides), without relying on `test_project`.

```bash
cd clients/sum_client
pip install -r requirements.txt
python manage.py migrate
DJANGO_SETTINGS_MODULE=sum_client.settings.local python manage.py runserver 8001
```

Then visit:

- Wagtail admin: `http://localhost:8001/admin/`
- Health check: `http://localhost:8001/health/`

## Database (Postgres fallback to Sqlite)

`core/sum_core/test_project/test_project/settings.py` uses SQLite unless a complete Postgres config is supplied via environment variables (it also auto-loads the first `.env` it finds while walking up the tree).

### Start Postgres via Docker Compose:

```bash
make db-up
```

And set a repo-root `.env` (example):

```bash
DJANGO_DB_NAME=sum_db
DJANGO_DB_USER=sum_user
DJANGO_DB_PASSWORD=sum_password
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432
```

Stop Postgres:

```bash
make db-down
```

## Core Package: `sum-core` (`sum_core`)

Source lives in `core/sum_core/`.

### Design system & tokens

- CSS entrypoint referenced by templates: `core/sum_core/static/sum_core/css/main.css`
- Token source of truth: `core/sum_core/static/sum_core/css/tokens.css`
- Rules and architecture: `docs/dev/design/css-architecture-and-tokens.md`

Branding is injected at runtime via template tags:

- `{% branding_fonts %}` inserts Google Fonts links for configured fonts.
- `{% branding_css %}` inserts a `<style>` block with CSS variables derived from Wagtail SiteSettings.

### Navigation system

Navigation is managed per-site in Wagtail Settings:

- **Header Navigation**: menu structure, header CTA, phone toggle, mobile sticky CTA config.
- **Footer Navigation**: footer sections, optional tagline/social overrides.

Technical deep-dive: `docs/dev/NAV/navigation.md`.

### Forms & leads

Forms are implemented as StreamField blocks and submit to `POST /forms/submit/`:

- Spam protection: honeypot, timing token, and per-IP rate limiting.
- Attribution capture: UTM parameters, referrer, landing page URL (via `form_attribution_script`).
- Persistence: every valid submission creates a `Lead` record; async side-effects are queued after persistence.

Admin surfaces:

- Wagtail: “Leads” (list/detail, filters/search, status updates, CSV export).
- Django admin: `FormConfiguration` (per-site spam/rate-limit/notification settings).

Runtime configuration (environment variables used by the test project):

- `LEAD_NOTIFICATION_EMAIL`: destination for lead email notifications.
- `ZAPIER_WEBHOOK_URL`: webhook URL for lead POSTs (optional).
- `DEFAULT_FROM_EMAIL`: sender address for notifications.
- `SENTRY_DSN`: Sentry error tracking (optional; if unset, Sentry is disabled).
- `LOG_LEVEL`: logging verbosity (default: `INFO`).

See [.env.example](.env.example) for all available environment variables including email SMTP settings, Celery broker configuration, and observability options.

## Repository Layout (What's Real vs Planned)

- `core/`: Installable `sum-core` package (the product) + `test_project/` (harness-only dev/CI project)
- `tests/`: Pytest suite for `sum_core`
- `docs/dev/`: PRD, SSOT, design docs, and milestone audit trail
- `clients/sum_client/`: Canonical consumer project (recommended “real site” reference)
- `clients/_smoke_consumer/`: Proof-of-concept consumer project validating core package consumability
- Placeholders today: `cli/`, `boilerplate/`, `scripts/`, `infrastructure/`

## Commands

From repo root (with `.venv` active):

- `make help`: list targets
- `make lint`: ruff + mypy + black + isort (check-only)
- `make format`: black + isort (write)
- `make test`: pytest
- `make run`: migrate + runserver for the test project
- `make db-up` / `make db-down` / `make db-logs`: local Postgres via Docker Compose

## License

TBD
