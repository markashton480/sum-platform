# Database Loss Incident Report

**Date:** 2025-12-15  
**Reported by:** Development Team  
**Status:** Resolved (Root Cause Identified)

---

## Executive Summary

Following a system restart for overnight updates, the development PostgreSQL database was found to be in a fresh/empty state. When the Django development server reported unapplied migrations and `manage.py migrate` was executed, it installed all Wagtail migrations from scratch, resulting in a default "Welcome to your new Wagtail site!" homepage instead of the expected development content.

---

## Timeline

| Time (UTC) | Event                                                          |
| ---------- | -------------------------------------------------------------- |
| Overnight  | System restart for updates                                     |
| ~12:44:27  | `make db-up` executed, Docker volume created                   |
| ~12:44:30  | `manage.py migrate` run, fresh database initialized            |
| ~12:51     | Issue reported - "Welcome to your new Wagtail site!" displayed |

---

## Root Cause Analysis

### Finding

The project directory was renamed from `tradesite` to `sum-platform`. Docker Compose uses the **parent directory name** as the default project name, which is used as a prefix for volume names. This created a "parallel universe" scenario where:

- Old volume: `tradesite_sum_db_data` (contains all development data)
- New volume: `sum-platform_sum_db_data` (created fresh when `make db-up` ran)

The application connected to the **new empty volume** instead of the old one with the actual data.

### Evidence

1. **Multiple volumes with different prefixes:**

   ```bash
   $ docker volume ls
   local     tradesite_sum_db_data      # Old volume with data (2025-12-10)
   local     sum-platform_sum_db_data   # New empty volume (2025-12-15)
   ```

2. **Volume creation timestamps:**

   - `tradesite_sum_db_data`: Created 2025-12-10 (original development work)
   - `sum-platform_sum_db_data`: Created 2025-12-15 (fresh volume after directory rename)

3. **Database state in new volume:**
   Only the default Wagtail root page and welcome page exist — no development content.

### Why This Happened

Docker Compose's default behavior:

```
COMPOSE_PROJECT_NAME = basename(current_directory)
Volume name = ${COMPOSE_PROJECT_NAME}_${volume_name_in_compose_file}
```

When the directory changed from `tradesite` → `sum-platform`, the volume namespace changed, creating a new isolated volume.

---

## Current Database Configuration

### Settings Logic

The database configuration in `core/sum_core/test_project/test_project/settings.py` uses environment variables:

```python
DB_NAME = os.getenv("DJANGO_DB_NAME")
DB_USER = os.getenv("DJANGO_DB_USER")
DB_PASSWORD = os.getenv("DJANGO_DB_PASSWORD")
DB_HOST = os.getenv("DJANGO_DB_HOST")
DB_PORT = os.getenv("DJANGO_DB_PORT", "5432")

if (DB_HOST and DB_NAME) and (not RUNNING_TESTS or USE_POSTGRES_FOR_TESTS):
    # Use PostgreSQL
    DATABASES = { ... }
else:
    # Fall back to SQLite
    SQLITE_DB_NAME = ":memory:" if RUNNING_TESTS else str(BASE_DIR / "db.sqlite3")
    DATABASES = { ... }
```

### Current .env Configuration

The `.env` file at repo root is correctly configured:

```
DJANGO_DB_NAME=sum_db
DJANGO_DB_USER=sum_user
DJANGO_DB_PASSWORD=sum_password
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432
```

### Docker Compose Configuration

`docker-compose.yml` defines the PostgreSQL service:

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: sum_db
      POSTGRES_USER: sum_user
      POSTGRES_PASSWORD: sum_password
    volumes:
      - sum_db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  sum_db_data:
```

> [!IMPORTANT]
> The named volume `sum_db_data` persists data between container restarts, but the **volume itself** can be deleted by Docker operations.

---

## Impact Assessment

| Area                 | Impact                                              |
| -------------------- | --------------------------------------------------- |
| **Development Data** | Data still exists in `tradesite_sum_db_data` volume |
| **Test Fixtures**    | No impact — tests use in-memory SQLite by default   |
| **Production**       | No impact — this is development environment only    |
| **Code**             | No impact — all code is in Git                      |

---

## Solution Implemented

### 1. Lock the Compose Project Name

Added `COMPOSE_PROJECT_NAME=sumplatform` to `.env` and `.env.example`:

```bash
# Docker Compose project name (locked to prevent volume namespace changes on dir rename)
COMPOSE_PROJECT_NAME=sumplatform

# Database settings for local Postgres (Docker)
DJANGO_DB_NAME=sum_db
DJANGO_DB_USER=sum_user
DJANGO_DB_PASSWORD=sum_password
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432
```

**Benefit:** Directory renames will no longer create new volume namespaces.

### 2. Add `make db-info` Target

Created a diagnostic command to show current configuration:

```bash
$ make db-info
=== Docker Compose Configuration ===
Project Name:    sumplatform
Active Volume:   sumplatform_sum_db_data

=== All sum_db_data Volumes ===
  sum-platform_sum_db_data (created: 2025-12-15)
  sumplatform_sum_db_data (created: 2025-12-15) ← ACTIVE
  tradesite_sum_db_data (created: 2025-12-10)

=== Database Connection Details ===
DB Host:         localhost
DB Port:         5432
DB Name:         sum_db
DB User:         sum_user

=== Container Status ===
sumplatform-db-1   postgres:17   Up 8 seconds   0.0.0.0:5432->5432/tcp
```

**Benefit:** Immediately see which volume is active and spot "parallel universe" scenarios.

### 3. Add `make db-migrate-volume` Target

Created a helper to migrate data from old volumes:

```makefile
db-migrate-volume: ## Migrate data from old volume to current volume
	# Copies data from tradesite_sum_db_data to sumplatform_sum_db_data
	# Includes safety prompt before overwriting
```

**Usage:**

```bash
$ make db-migrate-volume
This will copy data from tradesite_sum_db_data to the current active volume.
WARNING: This will OVERWRITE any data in the current volume!
Continue? [y/N] y
```

---

## Recovery Steps

1. ✅ Identified the root cause (directory rename → volume namespace change)
2. ✅ Added `COMPOSE_PROJECT_NAME=sumplatform` to `.env`
3. ✅ Restarted database with `docker-compose down && docker-compose up -d db`
4. ✅ Verified new volume created: `sumplatform_sum_db_data`
5. ⏳ **Next:** Run `make db-migrate-volume` to copy data from `tradesite_sum_db_data`

---

## Additional Preventive Measures (Recommended)

### Database Backup/Restore Targets

Consider adding to `Makefile`:

```makefile
db-dump: ## Export database to backup file
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U sum_user sum_db > backups/sum_db_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Restore database from most recent backup
	@LATEST=$$(ls -t backups/*.sql 2>/dev/null | head -1); \
	docker-compose exec -T db psql -U sum_user -d sum_db < "$$LATEST"
```

### Development Fixture

After setting up development content, export it:

```bash
python core/sum_core/test_project/manage.py dumpdata \
    --natural-foreign \
    --exclude=contenttypes \
    --exclude=auth.permission \
    --indent=2 \
    > fixtures/dev_content.json
```

---

## Lessons Learned

1. **Docker Compose project names matter** — They're not just cosmetic; they affect volume namespaces
2. **Directory renames have hidden consequences** — Always set `COMPOSE_PROJECT_NAME` explicitly
3. **Diagnostic tools prevent confusion** — `make db-info` would have immediately revealed the issue
4. **Volume inspection is crucial** — Check `docker volume ls` when database state seems wrong

---

## Action Items

| Priority  | Action                                    | Status      |
| --------- | ----------------------------------------- | ----------- |
| ✅ High   | Lock `COMPOSE_PROJECT_NAME` in `.env`     | **DONE**    |
| ✅ High   | Add `make db-info` diagnostic command     | **DONE**    |
| ✅ High   | Add `make db-migrate-volume` helper       | **DONE**    |
| ⏳ High   | Migrate data from `tradesite_sum_db_data` | **Pending** |
| 🔲 Medium | Add `db-dump` / `db-restore` targets      | Pending     |
| 🔲 Low    | Document Docker volume risks in README    | Pending     |
