# SUM Platform Codebase Structure

This document provides a comprehensive overview of the SUM Platform codebase directory structure and organization.

## Directory Tree

```
sum-platform/
├── core/                          # Core installable package (sum-core)
│   └── sum_core/                  # Main Django/Wagtail package
│       ├── analytics/              # Analytics integration (GA4/GTM)
│       ├── blocks/                 # StreamField blocks (hero, forms, content, etc.)
│       ├── branding/               # Branding system (colors, fonts, logos)
│       ├── forms/                  # Form handling and submission
│       ├── integrations/           # External integrations (Zapier, etc.)
│       ├── leads/                  # Lead management and persistence
│       ├── navigation/             # Navigation system (header, footer, menus)
│       ├── ops/                    # Operations (health checks, logging, Sentry)
│       ├── pages/                  # Page types (StandardPage, ServicePage, etc.)
│       ├── seo/                    # SEO features (sitemap, robots.txt, meta tags)
│       ├── static/                 # Static assets (CSS, JS)
│       ├── templates/              # Django/Wagtail templates
│       ├── templatetags/           # Custom template tags
│       ├── test_project/           # Test harness project (dev/CI only)
│       └── utils/                  # Utility functions
│
├── clients/                        # Client consumer projects
│   ├── sum_client/                 # Canonical reference client project
│   ├── _smoke_consumer/            # Proof-of-concept consumer
│   ├── showroom/                   # Demo/testing client project
│   └── client-name/                # Placeholder client scaffold
│
├── themes/                         # Canonical theme source-of-truth (Theme Architecture Spec v1)
│   └── theme_a/                    # Reference theme (Sage & Stone)
│
├── cli/                            # Command-line interface package
│   └── sum_cli/                    # CLI implementation
│       ├── boilerplate/            # Project boilerplate templates
│       └── commands/               # CLI commands (init, check)
│
├── tests/                          # Pytest test suite
│   ├── analytics/                  # Analytics tests
│   ├── blocks/                     # Block tests
│   ├── branding/                   # Branding tests
│   ├── forms/                      # Form tests
│   ├── leads/                      # Lead tests
│   ├── navigation/                 # Navigation tests
│   ├── ops/                        # Operations tests
│   ├── pages/                      # Page tests
│   ├── seo/                        # SEO tests
│   └── templates/                  # Template tests
│
├── docs/                           # Documentation
│   ├── ops-pack/                   # Operational runbooks
│   ├── release/                    # Release prompts + declarations
│   ├── user/                       # User-facing guides
│   └── dev/                        # Development documentation
│       ├── Archive/                # Historical docs (CM, milestones, NAV, DOC)
│       ├── deploy/                 # Deployment documentation
│       ├── design/                 # Design references + wireframes
│       ├── master-docs/            # Master documentation (SSOT, PRD, etc.)
│       ├── reports/                # Status reports and reviews
│       ├── agents/reviews/         # Code review guidelines
│       ├── side_quests/            # Side quest documentation
│       └── planning/               # Planning templates and work orders
│
├── infrastructure/                 # Deployment infrastructure
│   ├── caddy/                      # Caddy web server configuration
│   ├── systemd/                    # Systemd service templates
│   └── scripts/                    # Deployment scripts
│
├── boilerplate/                    # Standalone boilerplate project
│   ├── project_name/               # Project template
│   ├── templates/                  # Template files
│   └── static/                     # Static files
│
├── scripts/                        # Repository utility scripts
│   └── set_boilerplate_core_ref.py # Script to update boilerplate references
│
├── pyproject.toml                  # Root project configuration
├── Makefile                        # Build and development commands
├── docker-compose.yml              # Docker Compose configuration
├── README.md                       # Main project README
└── AGENTS.md                       # Agent-specific documentation
```

## Major Directory Overviews

### `/core/` - Core Package

The **installable `sum-core` package** (import path: `sum_core`). This is the main product deliverable.

**Key Subdirectories:**

- **`sum_core/analytics/`**: Google Analytics 4 and Google Tag Manager integration, lead analytics dashboard, dataLayer event tracking
- **`sum_core/blocks/`**: StreamField blocks for Wagtail (hero, content, forms, gallery, testimonials, services, trust indicators, etc.)
- **`sum_core/branding/`**: Site branding system with Wagtail SiteSettings integration (colors, fonts, logos, favicon, business info)
- **`sum_core/forms/`**: Form submission handling (`POST /forms/submit/`), spam protection (honeypot, timing, rate limiting), CSRF protection
- **`sum_core/integrations/`**: External service integrations (Zapier webhooks with retries and status tracking)
- **`sum_core/leads/`**: Lead persistence ("no lost leads" invariant), attribution capture (UTM, referrer, landing page), Wagtail admin UI, CSV export
- **`sum_core/navigation/`**: Navigation system (header menus 3-level deep, footer sections, mobile sticky CTA), cached output with invalidation
- **`sum_core/ops/`**: Operations and observability (`/health/` endpoint, Sentry integration, structured JSON logging with correlation IDs). **Health endpoint semantics:** cache backend is baseline-critical; failure results in `unhealthy` (503) status.
- **`sum_core/pages/`**: Page type models (`StandardPage`, `ServiceIndexPage`, `ServicePage`), SEO mixins (`SeoFieldsMixin`, `OpenGraphMixin`, `BreadcrumbMixin`)
- **`sum_core/seo/`**: Technical SEO (`/sitemap.xml`, `/robots.txt`, SEO template tags, JSON-LD structured data)
- **`sum_core/static/sum_core/css/`**: Design system CSS (tokens, main.css entrypoint)
- **`sum_core/templates/sum_core/`**: Django/Wagtail templates (blocks, pages, emails, includes, admin overrides)
- **`sum_core/test_project/`**: Test harness project used for local development and CI validation (NOT for client consumption)

### `/clients/` - Client Consumer Projects

Reference implementations showing how to consume `sum_core` in real projects.

- **`sum_client/`**: **Canonical reference client** - Recommended "real site" example with proper settings split, URL wiring, and template overrides
- **`_smoke_consumer/`**: Proof-of-concept consumer validating core package consumability
- **`acme-kitchens/`**: Example client project

### `/cli/` - Command-Line Interface

CLI package (`sum_cli`) for project scaffolding and management.

- **`sum_cli/commands/`**: CLI commands (`init`, `check`)
- **`sum_cli/boilerplate/`**: Project boilerplate templates synced from `/boilerplate/`

### `/tests/` - Test Suite

Pytest test suite organized by feature area, mirroring the `sum_core` package structure.

### `/docs/dev/` - Development Documentation

Comprehensive development documentation organized by:

- **`Archive/`**: Historical docs (CM, milestones, NAV, DOC)
- **`master-docs/`**: Single source of truth documents:
  - `SUM-PLATFORM-SSOT.md` - Main architecture/product spec
  - `prd-sum-platform-v1.1.md` - Product Requirements Document
  - `POST-MVP_BIG-PLAN.md` - Post-MVP expansion plans
  - `THEME-ARCHITECTURE-SPECv1.md` - Theme architecture specification
- **`deploy/`**: Deployment runbooks (`vps-golden-path.md`)
- **`design/`**: Design references and wireframes
- **`reports/`**: Status reports, release reviews, daily reports
- **`agents/reviews/`**: Code review guidelines
- **Reference docs**: `blocks-reference.md`, `page-types-reference.md`, `navigation-tags-reference.md`, `WIRING-INVENTORY.md`

### `/infrastructure/` - Deployment Infrastructure

Deployment scaffolding (not part of the core package):

- **`caddy/`**: Caddy web server configuration templates
- **`systemd/`**: Systemd service templates (gunicorn, celery)
- **`scripts/`**: Deployment automation scripts

### `/boilerplate/` - Standalone Boilerplate

Standalone Django/Wagtail project template that can be used to bootstrap new client projects. Synced to CLI package boilerplate.

### `/scripts/` - Utility Scripts

Repository-level utility scripts:

- **`set_boilerplate_core_ref.py`**: Updates boilerplate to pin to a specific `sum-core` version tag

## Key Files

### Root Level

- **`pyproject.toml`**: Root project configuration (build system, dev dependencies, tool configs)
- **`Makefile`**: Development commands (`make run`, `make test`, `make lint`, `make db-up`, etc.)
- **`docker-compose.yml`**: Local Postgres database setup
- **`README.md`**: Main project entrypoint with quick start guide
- **`AGENTS.md`**: Agent-specific documentation

### Configuration Files

- **`core/pyproject.toml`**: Core package build configuration
- **`cli/pyproject.toml`**: CLI package build configuration
- **`core/sum_core/test_project/test_project/settings.py`**: Test project Django settings (SQLite fallback to Postgres)

### Documentation Entry Points

- **`docs/dev/master-docs/SUM-PLATFORM-SSOT.md`**: Single source of truth for platform architecture
- **`docs/dev/WIRING-INVENTORY.md`**: How to consume `sum_core` in client projects
- **`docs/dev/AGENT-ORIENTATION.md`**: Platform vs test harness explanation
- **`docs/dev/hygiene.md`**: Repository hygiene standards
- **`docs/dev/blocks-reference.md`**: Authoritative block catalogue
- **`docs/dev/page-types-reference.md`**: Page types reference
- **`docs/dev/navigation-tags-reference.md`**: Navigation template tags reference

## Package Structure Notes

### Core Package (`sum_core`)

- Installable via `pip install -e ./core[dev]`
- Import path: `sum_core`
- Contains Django apps: `analytics`, `blocks`, `branding`, `forms`, `integrations`, `leads`, `navigation`, `ops`, `pages`, `seo`
- Test project (`test_project/`) is harness-only, not for client consumption

### Client Projects

Client projects consume `sum_core` as an installed package and:

- Define their own `HomePage` model (client-owned)
- Use a fixed, init-time selected theme (copied into `clients/<client>/theme/active/`)
- Override templates in this order (highest priority first):
  - `clients/<client>/theme/active/templates/` (theme templates)
  - `clients/<client>/templates/overrides/` (client overrides)
  - `sum_core/templates/` (core fallbacks)
- Configure settings in their own `settings/` module
- Define URL routing in their own `urls.py`

### Testing

- Tests live in `/tests/` at repo root
- Tests mirror `sum_core` package structure
- Uses pytest with Django test client
- Test project settings: `sum_core.test_project.test_project.settings`

## Development Workflow

1. **Local Development**: Use `core/sum_core/test_project/` (run via `make run`)
2. **Client Reference**: Use `clients/sum_client/` to see canonical consumption patterns
3. **Testing**: Run `make test` from repo root
4. **Linting**: Run `make lint` (ruff, mypy, black, isort)
5. **Documentation**: See `docs/dev/` for all development docs

## See Also

- **Main README**: `/README.md` - Quick start and overview
- **SSOT**: `docs/dev/master-docs/SUM-PLATFORM-SSOT.md` - Complete platform specification
- **Wiring Guide**: `docs/dev/WIRING-INVENTORY.md` - How to wire `sum_core` into projects
- **Agent Guide**: `docs/dev/AGENT-ORIENTATION.md` - Platform vs test harness distinction
