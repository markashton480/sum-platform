# M5-001 Follow-up Report: Canonical `sum_client` Consumer Project

**Task**: M5-001  
**Status**: ✅ Complete  
**Date**: 2025-12-16  
**Branch**: (commit pending)

---

## Summary

Created a real, runnable Django/Wagtail project named `sum_client` at `clients/sum_client/` that consumes `sum_core` without any dependency on `test_project`. The project demonstrates proper settings split, URL wiring, and template/static override structure.

---

## Files Created

### Project Root

| File                                  | Purpose                               |
| ------------------------------------- | ------------------------------------- |
| `clients/sum_client/manage.py`        | Django management entry point         |
| `clients/sum_client/requirements.txt` | Dependencies pinning sum_core         |
| `clients/sum_client/pytest.ini`       | Pytest configuration for client tests |

### Settings Module

| File                                                   | Purpose                                             |
| ------------------------------------------------------ | --------------------------------------------------- |
| `clients/sum_client/sum_client/settings/__init__.py`   | Package init                                        |
| `clients/sum_client/sum_client/settings/base.py`       | Shared settings (INSTALLED_APPS, MIDDLEWARE, etc.)  |
| `clients/sum_client/sum_client/settings/local.py`      | Dev settings (SQLite, DEBUG=True, eager Celery)     |
| `clients/sum_client/sum_client/settings/production.py` | Prod settings (PostgreSQL, Redis, security headers) |

### Application Wiring

| File                                        | Purpose                                      |
| ------------------------------------------- | -------------------------------------------- |
| `clients/sum_client/sum_client/__init__.py` | Package init                                 |
| `clients/sum_client/sum_client/wsgi.py`     | WSGI entry point                             |
| `clients/sum_client/sum_client/urls.py`     | URL routing including all sum_core endpoints |

### Home App

| File                                                        | Purpose                              |
| ----------------------------------------------------------- | ------------------------------------ |
| `clients/sum_client/sum_client/home/__init__.py`            | Package init                         |
| `clients/sum_client/sum_client/home/apps.py`                | Django AppConfig                     |
| `clients/sum_client/sum_client/home/models.py`              | HomePage model using sum_core mixins |
| `clients/sum_client/sum_client/home/migrations/__init__.py` | Migrations package init              |

### Template/Static Overrides

| File                                              | Purpose                             |
| ------------------------------------------------- | ----------------------------------- |
| `clients/sum_client/templates/overrides/.gitkeep` | Placeholder for template overrides  |
| `clients/sum_client/static/client/.gitkeep`       | Placeholder for client static files |

### Tests

| File                                      | Purpose                                 |
| ----------------------------------------- | --------------------------------------- |
| `clients/sum_client/tests/__init__.py`    | Package init                            |
| `clients/sum_client/tests/test_health.py` | Integration tests for /health/ endpoint |

---

## Technical Details

### Settings Split

The settings module follows Django best practices with environment-specific configuration:

- **base.py**: Contains all shared settings including:

  - `INSTALLED_APPS` with all sum_core apps
  - `MIDDLEWARE` with sum_core correlation ID middleware
  - Template configuration with `templates/overrides/` directory
  - Static files configuration with `static/` directory
  - Celery and email defaults

- **local.py**: Development-specific settings:

  - `DEBUG = True`
  - SQLite database
  - LocMem cache
  - Celery eager mode (synchronous tasks)
  - Includes observability setup from sum_core

- **production.py**: Production-specific settings:
  - `DEBUG = False`
  - PostgreSQL database (from environment variables)
  - Redis cache
  - Security headers (HSTS, secure cookies, XSS protection)
  - Celery broker from environment

### URL Configuration

Routes configured in `urls.py`:

```python
urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("forms/", include("sum_core.forms.urls")),
    path("", include("sum_core.ops.urls")),      # /health/
    path("", include("sum_core.seo.urls")),      # sitemap, robots
    path("", include(wagtail_urls)),              # pages (catch-all)
]
```

### HomePage Model

The `HomePage` model demonstrates proper sum_core consumption:

- Inherits from `SeoFieldsMixin`, `OpenGraphMixin`, `BreadcrumbMixin`, `Page`
- Uses `PageStreamBlock` for StreamField body content
- Enforces one-per-site via `clean()` method
- Uses sum_core's `home_page.html` template
- Defines allowed parent/subpage types for proper page hierarchy

---

## Verification Results

### Acceptance Criteria

| Criterion                                    | Status | Evidence                               |
| -------------------------------------------- | ------ | -------------------------------------- |
| `clients/sum_client/` is runnable            | ✅     | Server starts, migrations run          |
| Settings split exists                        | ✅     | `base.py`, `local.py`, `production.py` |
| `/health/` returns JSON with status + checks | ✅     | Verified via curl                      |
| URL wiring supports pages, forms, admin      | ✅     | All endpoints accessible               |
| No `test_project` references                 | ✅     | `grep -r "test_project"` returns empty |

### Test Results

**sum_client Tests:**

```
tests/test_health.py::test_health_endpoint_returns_200 PASSED
tests/test_health.py::test_health_endpoint_returns_json_with_status_and_checks PASSED
tests/test_health.py::test_health_endpoint_returns_503_when_degraded PASSED
======================== 3 passed ========================
```

**Main Test Suite:**

```
================= 647 passed, 45 warnings in 188.97s =================
```

**Linting:**

```
ruff check . - All checks passed!
black --check . - No issues
isort --check-only . - No issues
```

### Manual Verification

```bash
# Health endpoint
$ curl -s http://localhost:8001/health/ | python -m json.tool
{
    "status": "degraded",
    "checks": {
        "db": {"status": "ok", "latency_ms": 2.28},
        "cache": {"status": "ok", "latency_ms": 0.56},
        "celery": {"status": "fail", "detail": "Connection refused"}
    },
    ...
}

# Wagtail admin
$ curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/admin/login/
200
```

---

## How to Use

### Local Development

```bash
# From repo root with .venv activated
cd clients/sum_client
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

### Running Tests

```bash
cd clients/sum_client
python -m pytest tests/ -v
```

### Production Deployment

Set required environment variables:

```bash
DJANGO_SECRET_KEY=<your-secret-key>
DJANGO_DB_NAME=<database-name>
DJANGO_DB_USER=<database-user>
DJANGO_DB_PASSWORD=<database-password>
DJANGO_DB_HOST=<database-host>
ALLOWED_HOSTS=example.com,www.example.com
REDIS_URL=redis://localhost:6379/0
```

Then run with production settings:

```bash
DJANGO_SETTINGS_MODULE=sum_client.settings.production python manage.py migrate
```

---

## Notes

1. **Celery check shows "fail"** in local dev because no broker is running - this is expected behavior and demonstrates the health check is working correctly.

2. **Template/static override directories** are present but empty - this matches the boilerplate expectation of providing structure for client customization.

3. **HomePage uses sum_core template** (`sum_core/home_page.html`) - clients can override this by placing a custom template in `templates/overrides/`.

4. **Production settings require Redis** - the `production.py` settings assume Redis is available for caching and Celery broker.

---

## Related Files

- Task specification: `docs/dev/M5/M5-001.md`
- Implementation plan: `.gemini/antigravity/brain/*/implementation_plan.md`
- Existing smoke consumer: `clients/_smoke_consumer/`
