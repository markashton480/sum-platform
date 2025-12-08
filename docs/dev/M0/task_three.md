**[M0-003] Docker Dev Environment**

Now that the Python side is stable, the next milestone-0 job is:

> Have a **Docker-based dev environment** so you can run the test project (and later client projects) the same way everywhere.

Here’s the ticket in the same style as before.

---

### **[M0-003] Docker Dev Environment for `sum_core.test_project`**

#### Context (from PRD / Implementation intent)

* Local development should run via **Docker Compose**, not ad-hoc `python manage.py runserver`.
* Stack for dev:

  * Python 3.12
  * Django 5.2.x / Wagtail 7.0.x (already sorted)
  * Postgres 17 (preferred) and Redis (for future caching / tasks).
* Milestone 0 “done” includes:

  * `docker-compose up` → Wagtail admin available at `http://localhost:8000/admin/`.
  * `make run` acting as a convenience wrapper for Docker.

We’ll run the **test project** (`core/sum_core/test_project`) as the app inside the container for now.

---

#### Technical Requirements

Create a Docker-based setup that:

1. **Defines services via `docker-compose.yml`** at the repo root:

   * `web`: Django/Wagtail app
   * `db`: Postgres 17
   * `redis`: Redis 7 (even if unused yet)
2. **Builds the web image** from a `Dockerfile` at the repo root:

   * Python 3.12 base image (slim is fine).
   * Copies project code.
   * Installs `sum_core` + dependencies via `pip install -e ./core[dev]`.
3. **Runs the test project** inside the `web` container with:

   * Working directory set so `python core/sum_core/test_project/manage.py runserver 0.0.0.0:8000` works.
4. **Keeps local dev happy**:

   * Volume-mounts the repo so code changes are reflected without rebuilding the image every time.
   * Uses Postgres for DB in the test project (we can switch settings from SQLite to Postgres for Docker, or make it conditional on env vars).
5. **Integrates with Makefile**:

   * `make run` → `docker-compose up`
   * `make down` (add this) → `docker-compose down`
   * Optionally `make web-shell` → `docker-compose exec web bash`.

---

#### Design / “Dev UX” Specifications

We want the dev experience to feel like:

```bash
make run      # bring everything up
make down     # tear it down
```

And inside the container:

* Admin at: `http://localhost:8000/admin/`
* DB persisted in a named volume (e.g. `sum_db_data`), not inside the container filesystem.

Config-wise:

* Use environment variables for DB connection details (host/user/password/db).
* Provide a `.env.example` at the repo root that devs can copy to `.env`.

---

#### Implementation Guidelines

**1. Root `Dockerfile`**

Create `Dockerfile` at the repo root, e.g.:

```dockerfile
# Name: Web Application Dockerfile
# Path: Dockerfile
# Purpose: Build the web container for the sum_core.test_project Wagtail app.
# Family: Used by docker-compose `web` service.
# Dependencies: core/pyproject.toml, sum_core package, Python 3.12 base image.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (build tools, Postgres client libs, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install pip & tooling
RUN python -m pip install --upgrade pip

# Copy pyproject for core and install dependencies before copying full source (better caching)
COPY core/pyproject.toml core/pyproject.toml

RUN pip install -e ./core[dev]

# Now copy the rest of the repo
COPY . .

# Default command (can be overridden in docker-compose)
CMD ["python", "core/sum_core/test_project/manage.py", "runserver", "0.0.0.0:8000"]
```

> Note: we might refine this for build performance later, but this is fine for milestone 0.

**2. `docker-compose.yml`**

At repo root:

```yaml
version: "3.9"

services:
  web:
    build: .
    command: python core/sum_core/test_project/manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DJANGO_SETTINGS_MODULE: test_project.settings
      DATABASE_URL: postgres://sum_user:sum_password@db:5432/sum_db
    depends_on:
      - db
      - redis
    volumes:
      - .:/app

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

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  sum_db_data:
```

**3. `.env.example`**

At repo root:

```env
# Name: Example Environment Configuration
# Path: .env.example
# Purpose: Example environment variables for local Docker development.
# Family: Used as a template for .env; consumed by docker-compose and Django settings.
# Dependencies: docker-compose.yml, test_project.settings

DJANGO_DEBUG=1
DJANGO_SECRET_KEY=dev-only-not-for-production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_DB_NAME=sum_db
DJANGO_DB_USER=sum_user
DJANGO_DB_PASSWORD=sum_password
DJANGO_DB_HOST=db
DJANGO_DB_PORT=5432
WAGTAILADMIN_BASE_URL=http://localhost:8000
```

You’ll copy this to `.env` locally:

```bash
cp .env.example .env
```

**4. Update `test_project/settings.py` for Postgres (but still easy for local)**

Right now it uses SQLite. Let’s make it env-driven so it works both in Docker and directly:

At the top of `settings.py`:

```python
import os
```

Change `DATABASES` to something like:

```python
DB_NAME = os.getenv("DJANGO_DB_NAME", BASE_DIR / "db.sqlite3")
DB_USER = os.getenv("DJANGO_DB_USER", "")
DB_PASSWORD = os.getenv("DJANGO_DB_PASSWORD", "")
DB_HOST = os.getenv("DJANGO_DB_HOST", "")
DB_PORT = os.getenv("DJANGO_DB_PORT", "")

if DB_HOST:
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
            "NAME": DB_NAME,
        }
    }
```

And set:

```python
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", "http://localhost:8000")
```

This keeps:

* Local "bare" runs using SQLite.
* Docker runs using Postgres.

**5. Makefile integration**

Extend the root `Makefile`:

```make
run:
	docker-compose up

down:
	docker-compose down

web-shell:
	docker-compose exec web bash
```

Now dev loop is dead simple.

---

#### Acceptance Criteria

* [ ] `Dockerfile` and `docker-compose.yml` exist at repo root.
* [ ] `.env.example` exists and can be copied to `.env` for local Docker dev.
* [ ] `core/sum_core/test_project/test_project/settings.py` reads DB config from env vars and uses:

  * Postgres if `DJANGO_DB_HOST` is set.
  * SQLite otherwise.
* [ ] From a clean checkout:

  1. `cp .env.example .env`
  2. `make run`
  3. Go to `http://localhost:8000/admin/` → Wagtail admin loads (even if unstyled/basic).
* [ ] `make down` stops and removes containers.
* [ ] Local Python-based workflow (without Docker) still works:

  * `python core/sum_core/test_project/manage.py check`
  * `make lint`
  * `make test`

---

#### Dependencies & Prerequisites

* M0-001 & M0-002 must be done (which they are).
* Docker + docker-compose installed locally.
* Your `.env` based on `.env.example`.

---

#### Testing Requirements

* **Manual**

  * `make run` → Wagtail admin accessible at `http://localhost:8000/admin/`.
  * `make down` shuts everything down cleanly.
* **Sanity**

  * `python manage.py migrate` runs successfully inside the web container.
* **Tooling**

  * `make lint` and `make test` still pass on the host.

