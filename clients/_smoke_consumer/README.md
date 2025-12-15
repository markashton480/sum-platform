# Smoke Consumer Project

> **Purpose**: This is a validation project that proves `sum_core` is consumable as an installable package, independent of the `test_project` harness.

## What This Proves

1. **No test_project dependencies**: Settings, URLs, and models import only from `sum_core`, not from the test harness.

2. **Standard Django patterns**: Installation follows documented patterns from `WIRING-INVENTORY.md`.

3. **Core endpoints work**: `/health/`, `/sitemap.xml`, `/robots.txt` all respond correctly.

## Quick Start

From the repo root (with `.venv` activated):

```bash
# Ensure sum_core is installed
pip install -e ./core

# Change to smoke consumer directory
cd clients/_smoke_consumer

# Run Django checks
python manage.py check

# Apply migrations
python manage.py migrate

# Start dev server (on port 8001 to avoid conflict with test_project)
python manage.py runserver 8001
```

Then verify:

- http://localhost:8001/health/ → Should return JSON `{"status": "healthy", ...}`
- http://localhost:8001/admin/ → Wagtail admin

## Project Structure

```
_smoke_consumer/
├── manage.py
└── smoke_consumer/
    ├── __init__.py
    ├── settings.py      # Minimal settings, NO test_project imports
    ├── urls.py          # Standard include() patterns
    ├── wsgi.py
    └── home/
        ├── __init__.py
        ├── apps.py
        └── models.py    # HomePage extending sum_core.pages.BasePage
```

## Key Differences from test_project

| Aspect   | test_project                  | \_smoke_consumer           |
| -------- | ----------------------------- | -------------------------- |
| Location | `core/sum_core/test_project/` | `clients/_smoke_consumer/` |
| Purpose  | Development + CI testing      | Consumability proof        |
| Database | Postgres or SQLite            | SQLite only                |
| Features | Full feature coverage         | Minimal viable             |

## This Is Not For Production

This project exists purely to validate that the documented wiring works. It:

- Uses development-only settings
- Has no production security
- Is intentionally minimal

For actual client projects, follow the full `WIRING-INVENTORY.md` documentation.
