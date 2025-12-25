# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

SUM Platform is a **reusable core platform** for launching lead-focused websites for home improvement trades. It is NOT a single Django site or demo project.

**Primary product:** `core/sum_core/` - an installable Django/Wagtail package that powers multiple client sites.

Everything else exists to test, scaffold, or demonstrate it:
- `test_project/` - pytest harness (not production config)
- `boilerplate/` - starter template for new clients
- `cli/` - scaffolding tool for client sites
- `themes/` - visual rendering packages

**Rule of thumb:** If your change only works inside test_project, it's incomplete. Ask: "Where would a real client configure this?"

## Commands

**Activate the virtualenv first:**
```bash
source .venv/bin/activate
```

```bash
# Setup
make install-dev          # Install core + dev deps in editable mode
make db-up                # Start PostgreSQL via docker-compose

# Development
make run                  # Migrate and start test server
make lint                 # Ruff, mypy, Black, isort checks (strict)
make format               # Auto-format code

# Testing
make test                 # Full pytest suite with coverage
make test-fast            # CLI + themes test slices (quick gate)
make test-cli             # CLI tests only
make test-themes          # Theme tests only
make test-templates       # Template loading order tests

# Release
make release-check        # Pre-release: lint + test + CLI sync verification
make check-cli-boilerplate # Verify CLI boilerplate matches canonical
make sync-cli-boilerplate  # Sync canonical boilerplate to CLI package
```

**Run a single test:**
```bash
python -m pytest tests/path/to/test_file.py::TestClass::test_method -v
```

## Architecture

### Core-Client Pattern
- `sum_core` is installed via pip from git tags: `sum-core @ git+...@vX.Y.Z#subdirectory=core`
- Client projects are thin shells that consume core
- Each client has its own PostgreSQL database

### Theme System
- Themes are fixed per-site, selected at initialization (`sum init <client> --theme <slug>`)
- Block **definitions** (data structures) live in `core/sum_core/blocks/`
- Block **templates** (visual rendering) live in `themes/<theme>/templates/`
- Template priority: client theme > client overrides > core defaults
- Tailwind-first styling with CSS variables for runtime branding

### Lead Pipeline ("No Lost Leads")
1. Form POST to `/forms/submit/`
2. Lead saved to Postgres immediately (atomic)
3. Celery queues async side effects (email, webhooks)

Persistence happens before any external integrations.

### Key Modules
- `sum_core.pages` - Abstract and concrete page models (StandardPage, ServicePage, etc.)
- `sum_core.blocks` - StreamField block definitions
- `sum_core.leads` - Lead persistence, attribution, pipeline
- `sum_core.forms` - Contact/quote forms with spam protection
- `sum_core.navigation` - Header/footer/sticky CTA logic
- `sum_core.branding` - SiteSettings and template tags
- `sum_core.seo` - Sitemaps, robots.txt, JSON-LD
- `sum_core.analytics` - GA4/GTM integration
- `sum_core.ops` - Health checks, middleware

## Development Guidelines

### Where Things Belong
- **Persistent behavior** → `core/sum_core/*` (installable apps, reusable settings)
- **Test-only behavior** → `test_project/`, pytest fixtures, mocks

Red flags:
- Registering apps only in test INSTALLED_APPS
- URLs wired only in test URLConf
- Settings that exist only to make tests pass

### Design Tokens
- Follow existing design tokens in `docs/dev/THEME-GUIDE.md`
- Never hard-code values
- Only create new tokens when absolutely necessary

### Git Conventions
- Default branch: `develop` (must remain stable)
- Create feature branches from develop: `git checkout -b feat/issue-description`
- Commit prefixes: `feature:`, `fix:`, `chore:`, `docs:`, `refactor:`
- Never commit directly to `main` or `develop`

## Tech Stack
- Python 3.12+
- Django 5.2 LTS
- Wagtail 7.0 LTS
- PostgreSQL 17
- Redis (cache/broker)
- Celery (async tasks)
- Tailwind CSS v3.4

## Key Documentation
- `docs/HANDBOOK.md` - Complete platform guide
- `docs/dev/AGENT-ORIENTATION.md` - Platform vs test harness philosophy
- `docs/dev/WIRING-INVENTORY.md` - Integrating sum_core into client projects
- `docs/dev/blocks-reference.md` - Available StreamField blocks
- `docs/dev/THEME-GUIDE.md` - CSS architecture and token system
