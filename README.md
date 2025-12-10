# SUM Platform

Monorepo for trade website platform built on Django and Wagtail.

## Overview

This repository contains the **SUM Platform** core package (`sum_core`), a reusable Django/Wagtail foundation for building trade website platforms. The platform provides:

- **Token-based CSS design system** with dynamic branding
- **SiteSettings** for per-site customization (colours, fonts, logos, business info)
- **Base templates** and component library
- **Theme presets** for quick brand setup
- **Test project** for development and CI validation

## Prerequisites

* **Python 3.12+**
* **Docker** and **Docker Compose** (for PostgreSQL database)
* A working virtual environment

## Getting Started

### 1. Create and Activate Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
make install-dev
```

This installs:
- Core package (`sum_core`) in editable mode
- Development tools (Black, isort, ruff, pytest, mypy, pre-commit)
- Sets up pre-commit hooks

### 3. Database Setup

The project uses **PostgreSQL** via Docker for development. The test project will fall back to SQLite if database environment variables are not set.

**Start PostgreSQL:**

```bash
make db-up
```

This starts a PostgreSQL 17 container with:
- Database: `sum_db`
- User: `sum_user`
- Password: `sum_password`
- Port: `5432`

**Stop PostgreSQL:**

```bash
make db-down
```

**View database logs:**

```bash
make db-logs
```

### 4. Configure Environment Variables (Optional)

For PostgreSQL, create a `.env` file in the repo root:

```bash
# Database settings for local Postgres (Docker)
DJANGO_DB_NAME=sum_db
DJANGO_DB_USER=sum_user
DJANGO_DB_PASSWORD=sum_password
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432
```

The test project will automatically load `.env` files. If these variables are not set, it will use SQLite as a fallback.

### 5. Run Migrations

With the database running and environment configured:

```bash
cd core/sum_core/test_project
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
```

### 6. Run the Test Project

```bash
make run
```

Or manually:

```bash
cd core/sum_core/test_project
python manage.py runserver
```

Visit `http://localhost:8000/admin/` to access the Wagtail admin interface.

## Development Commands

All commands should be run from the repository root with the virtual environment activated.

### Available Make Targets

Run `make help` to see all available commands:

```bash
make help
```

#### Installation

- `make install` - Install project dependencies
- `make install-dev` - Install development dependencies and set up pre-commit hooks

#### Code Quality

- `make lint` - Run linting checks (ruff + mypy)
- `make format` - Format code with Black and isort
- `make test` - Run test suite with pytest

#### Database

- `make db-up` - Start PostgreSQL via Docker Compose
- `make db-down` - Stop PostgreSQL container
- `make db-logs` - Tail PostgreSQL logs

#### Development Server

- `make run` - Run Django development server (test project)

#### Cleanup

- `make clean` - Clean up generated files (pyc, cache, etc.)

### Pre-commit Hooks

Pre-commit hooks are automatically installed when you run `make install-dev`. They run automatically on git commit. You can also run them manually:

```bash
pre-commit run --all-files
```

## Project Structure

```
.
├── core/                    # Core package (sum_core)
│   └── sum_core/           # Reusable Django/Wagtail core
│       ├── branding/       # SiteSettings, theme presets, branding tags
│       ├── blocks/         # Wagtail blocks
│       ├── pages/          # Page models
│       ├── leads/          # Lead capture
│       ├── analytics/       # Analytics integration
│       ├── seo/            # SEO utilities
│       ├── integrations/   # Third-party integrations
│       ├── utils/          # Utility functions
│       ├── templates/      # Base templates
│       ├── static/         # CSS, JS, images
│       └── test_project/   # Test Django project for CI/development
├── boilerplate/            # Boilerplate templates
├── clients/                # Client projects
├── cli/                    # CLI tools
├── docs/                   # Documentation
│   └── dev/                # Development documentation
│       ├── M0/             # Milestone 0 tasks
│       └── M1/             # Milestone 1 tasks
├── scripts/                # Utility scripts
├── infrastructure/         # Infrastructure as code
├── tests/                  # Test suite
├── docker-compose.yml      # Docker Compose config (PostgreSQL)
├── Makefile               # Development commands
└── pyproject.toml         # Root tooling configuration
```

## Core Package (`sum_core`)

The `sum_core` package is the central dependency for all client projects. It provides:

### Design System

- **CSS Token System** (`main.css`) - Token-based design system with colour, typography, spacing, radius, and shadow tokens
- **Dynamic Branding** - CSS variables generated from `SiteSettings` via `{% branding_css %}` template tag
- **Google Fonts Integration** - Dynamic font loading via `{% branding_fonts %}` template tag
- **Component Library** - Buttons, cards, forms, navigation styles using tokens exclusively

### SiteSettings

- Brand colours (primary, secondary, accent, background, text)
- Logo uploads (header, footer, favicon)
- Typography (heading and body fonts)
- Business information (company name, tagline, contact details)
- Social media links
- **Theme Presets** - 5 pre-configured themes (Premium Trade, Professional Blue, Modern Green, Warm Earth, Clean Slate)

### Templates

- `base.html` - Core layout template with header, main, footer
- `home_page.html` - Homepage template
- Includes: `header.html`, `footer.html`

### Template Tags

- `{% get_site_settings %}` - Access SiteSettings in templates
- `{% branding_css %}` - Generate CSS variables from SiteSettings
- `{% branding_fonts %}` - Generate Google Fonts links

## Test Project

The test project (`core/sum_core/test_project`) serves multiple purposes:

- **CI Validation** - Ensures `sum_core` works correctly
- **Development** - Local testing and development environment
- **Documentation** - Example implementation

### Running the Test Project

1. Ensure database is running: `make db-up`
2. Run migrations: `cd core/sum_core/test_project && python manage.py migrate`
3. Start server: `make run` or `python manage.py runserver`
4. Access admin: `http://localhost:8000/admin/`

### Test Project Structure

```
core/sum_core/test_project/
├── manage.py
├── test_project/
│   ├── settings.py      # Django settings (env-aware DB config)
│   ├── urls.py         # URL configuration
│   └── wsgi.py         # WSGI application
└── home/               # Home app (HomePage model)
    ├── models.py
    └── apps.py
```

## Database Configuration

The test project supports both **PostgreSQL** (via Docker) and **SQLite** (fallback).

### PostgreSQL (Recommended)

1. Start database: `make db-up`
2. Set environment variables (via `.env` or export):
   ```bash
   export DJANGO_DB_NAME=sum_db
   export DJANGO_DB_USER=sum_user
   export DJANGO_DB_PASSWORD=sum_password
   export DJANGO_DB_HOST=localhost
   export DJANGO_DB_PORT=5432
   ```
3. Run migrations: `python core/sum_core/test_project/manage.py migrate`

### SQLite (Fallback)

If database environment variables are not set, the project automatically uses SQLite. No additional setup required.

## Development Workflow

1. **Activate virtual environment**: `source .venv/bin/activate`
2. **Start database**: `make db-up`
3. **Run tests**: `make test`
4. **Run linting**: `make lint`
5. **Format code**: `make format`
6. **Start dev server**: `make run`

## Testing

Run the full test suite:

```bash
make test
```

Tests use **pytest** and **pytest-django**. The test suite includes:

- Unit tests for `sum_core` components
- Template tag tests
- Model tests
- Integration tests for the test project

## Code Style

The project uses:

- **Black** - Code formatting
- **isort** - Import sorting
- **ruff** - Linting
- **mypy** - Type checking

Format code before committing:

```bash
make format
```

## Git Workflow

- Default branch: `main` (must remain stable)
- Create feature branches: `git checkout -b feat/m0-001-description`
- Commit prefixes:
  - `feature:` - New user-facing behaviour
  - `fix:` - Bug fixes
  - `chore:` - Tooling, infrastructure, refactors
  - `docs:` - Documentation changes
  - `refactor:` - Internal code restructuring

## License

TBD
