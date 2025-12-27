# SUM CLI User Guide (v2)

## ⚠️ Important: CLI v2 Availability

**CLI v2 is currently available in monorepo development mode ONLY.**

The features documented in this guide require installing the CLI in editable mode from the repository. The published package (v0.1.0) still ships CLI v1.

**To use CLI v2 now:**
```bash
git clone https://github.com/markashton480/sum-platform.git
cd sum-platform
pip install -e ./cli
```

**Published package users:** See [CLI v1 reference](../cli.md#cli-v1-reference) for the currently shipped features.

---

This guide covers the SUM Platform CLI tool v2, which provides commands for creating and managing SUM client projects.

## Overview

The SUM CLI v2 (`sum`) provides three main commands:

- **`sum init`** - Initialize new client projects with optional full setup
- **`sum run`** - Start the development server
- **`sum check`** - Validate project setup and readiness

## Installation

### Monorepo Development Mode (Required for v2)

From the repository root:

```bash
source .venv/bin/activate
pip install -e ./cli
```

### Standalone Installation

**Note:** The published package currently ships CLI v1 only. CLI v2 features are not yet available.

```bash
pip install sum-cli  # Installs CLI v1 (basic scaffolding only)
```

## Commands

### `sum init` - Initialize a New Project

Create a new client project with flexible setup options.

#### Basic Usage

```bash
sum init <project-name>
```

**Basic mode** (default) scaffolds the project structure and shows next steps:

```bash
sum init acme-kitchens
```

Output:
```
✅ Project scaffolded at /path/to/clients/acme-kitchens
Next steps:
  cd /path/to/clients/acme-kitchens
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python manage.py migrate
```

#### Setup Modes

**Quick Setup** (`--quick`)

Scaffolds project + creates virtualenv + installs dependencies (no database operations):

```bash
sum init acme-kitchens --quick
```

Runs these steps:
1. Scaffold project structure
2. Validate structure
3. Create `.venv`
4. Install dependencies from `requirements.txt`

**Full Setup** (`--full`)

Complete project initialization with database, content, and superuser:

```bash
sum init acme-kitchens --full
```

Runs up to 8 steps:
1. Scaffold project structure
2. Validate structure
3. Create `.venv`
4. Install dependencies
5. Run database migrations
6. Seed initial homepage
7. Create superuser + `.env.local`
8. Start development server (if requested)

#### Options

| Flag | Description |
|------|-------------|
| `--full` | Run complete setup (venv, deps, migrations, seed, superuser) |
| `--quick` | Scaffold + venv + deps only (no database operations) |
| `--no-prompt` | Non-interactive mode, use defaults |
| `--ci` | CI mode (non-interactive, optimized output) |
| `--skip-venv` | Skip virtualenv creation |
| `--skip-migrations` | Skip database migrations |
| `--skip-seed` | Skip homepage seeding |
| `--skip-superuser` | Skip superuser creation |
| `--run` | Start development server after setup |
| `--port <number>` | Development server port (default: 8000) |
| `--preset <name>` | Content preset name (future use) |

**Note:** The `--theme` flag from CLI v1 is not yet available in v2. All projects use the default theme (`theme_a`).

#### Interactive Prompts

When using `--full` without `--no-prompt`, you'll be asked:

```
Setup Python environment? [Y/n]:
Run database migrations? [Y/n]:
Seed initial homepage? [Y/n]:
Create superuser? [Y/n]:
  Username [admin]:
  Email [admin@example.com]:
  Password [admin]:
Start development server? [Y/n]:
```

#### Examples

**Full setup with custom port:**
```bash
sum init acme-kitchens --full --port 8080
```

**Quick setup without prompts:**
```bash
sum init acme-kitchens --quick --no-prompt
```

**Full setup, skip superuser:**
```bash
sum init acme-kitchens --full --skip-superuser
```

**CI/automation mode:**
```bash
sum init acme-kitchens --full --ci
```

#### Output

After successful initialization, you'll see a summary:

```
✅ Project scaffolded at /path/to/clients/acme-kitchens

Summary for acme-kitchens:
  location: /path/to/clients/acme-kitchens
  url: http://127.0.0.1:8000/
  credentials_path: /path/to/clients/acme-kitchens/.env.local
  username: admin
  password: admin
```

The `.env.local` file contains your superuser credentials:

```bash
# Created 2025-12-27 14:30:00
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

**Security Note:** The `.env.local` file is created with restrictive permissions (`0o600`) for security.

---

### `sum run` - Start Development Server

Start the Django development server with automatic virtualenv detection.

#### Basic Usage

```bash
sum run [project-name] [--port 8000]
```

**From project directory:**
```bash
cd clients/acme-kitchens
sum run
```

**From repository root:**
```bash
sum run acme-kitchens
```

#### Features

- **Automatic virtualenv detection** - Uses `.venv/bin/python` if available
- **Port fallback** - If requested port is in use, tries next 10 ports
- **Monorepo mode** - Automatically configures `PYTHONPATH` for core module
- **Graceful shutdown** - Ctrl+C stops server cleanly

#### Options

| Flag | Description |
|------|-------------|
| `--port <number>` | Development server port (default: 8000) |

#### Examples

**Start server on default port:**
```bash
sum run
```

**Start on custom port:**
```bash
sum run --port 8080
```

**Start from repo root:**
```bash
sum run acme-kitchens --port 3000
```

#### Output

```
🚀 Starting acme-kitchens...

Using virtualenv: /path/to/clients/acme-kitchens/.venv
Mode: standalone
Python: /path/to/clients/acme-kitchens/.venv/bin/python

Performing system checks...
Starting development server at http://127.0.0.1:8000/
```

If the port is in use:
```
⚠️  Port 8000 in use, using 8001 instead
🚀 Starting acme-kitchens...
```

---

### `sum check` - Validate Project Setup

Validate that your project is properly set up and ready to run.

#### Basic Usage

```bash
sum check [project-name]
```

**From project directory:**
```bash
cd clients/acme-kitchens
sum check
```

**From repository root:**
```bash
sum check acme-kitchens
```

#### What `sum check` Validates

| Check | Description | Status |
|-------|-------------|--------|
| **Virtualenv** | `.venv` directory exists and contains required packages (django, wagtail) | OK / FAIL / SKIP |
| **Credentials** | `.env.local` file exists (created by superuser setup) | OK / SKIP |
| **Database** | Migrations are up to date (no pending migrations) | OK / FAIL / SKIP |
| **Homepage** | A published HomePage exists in the database | OK / FAIL / SKIP |

#### Output Statuses

- **[OK]** - Check passed successfully
- **[FAIL]** - Check failed, remediation steps shown
- **[SKIP]** - Check skipped (e.g., venv missing, so package check skipped)

#### Example Output

**All checks passing:**
```
[OK] Virtualenv: .venv exists with required packages
[OK] Credentials: .env.local found
[OK] Database: All migrations applied
[OK] Homepage: Published HomePage exists

✅ All checks passed
```

**Failures with remediation:**
```
[FAIL] Virtualenv: .venv not found
      → Run 'sum init --full' or 'python -m venv .venv'
[SKIP] Credentials: No .env.local found (superuser not created)
[SKIP] Database: Virtualenv missing; skipping migration check
[SKIP] Homepage: Virtualenv missing; skipping homepage check

❌ Some checks failed
```

**Partial setup:**
```
[OK] Virtualenv: .venv exists with required packages
[SKIP] Credentials: No .env.local found (superuser not created)
[FAIL] Database: Pending migrations found
      → Run 'python manage.py migrate'
[FAIL] Homepage: No HomePage found
      → Run 'python manage.py seed_homepage'

❌ Some checks failed
```

#### What `sum check` Does NOT Validate

- Full Django startup / `runserver` success
- Template correctness or static file collection
- Runtime configuration (email, Celery, etc.)
- External service connectivity
- Security configuration

---

## Execution Modes

The CLI automatically detects its execution context:

### Monorepo Mode

When running inside the SUM Platform repository (detected by presence of `core/` and `boilerplate/` directories), the CLI:

- Automatically adds `core/` to `PYTHONPATH`
- Allows running without installing `sum_core` globally
- Used during platform development

### Standalone Mode

When running outside the monorepo (e.g., deployed client project):

- Expects `sum_core` to be installed via pip
- Normal Django/Wagtail project behavior
- Used in production environments

---

## Project Naming

Project names are validated and normalized:

- **Allowed:** Lowercase letters, numbers, hyphens
- **Examples:** `acme-kitchens`, `my-site-2024`
- **Not allowed:** Uppercase, underscores, spaces, special characters

**Normalization:**
- Slug: `acme-kitchens` (directory name)
- Python package: `acme_kitchens` (hyphens → underscores)

---

## Seeded Homepage

When using `--full` without `--skip-seed`, the CLI creates a default homepage via the `seed_homepage` management command.

**Default homepage includes:**
- Title: "Welcome"
- Slug: `/home`
- SEO meta fields
- Hero block with placeholder content
- Rich text block with welcome text

**Customize with presets (future):**
```bash
sum init acme-kitchens --full --preset minimal
```

---

## Troubleshooting

### "Virtualenv not found"

**Problem:** Running `sum run` or `sum check` without a `.venv` directory.

**Solution:**
```bash
# Option 1: Use sum init with --quick or --full
sum init --quick

# Option 2: Create manually
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### "Port in use"

**Problem:** Default port 8000 is already in use.

**Solution:**
```bash
# Option 1: Use automatic fallback
sum run  # Will try ports 8001, 8002, etc.

# Option 2: Specify custom port
sum run --port 8080
```

### "No migrations applied"

**Problem:** Database not initialized.

**Solution:**
```bash
source .venv/bin/activate
python manage.py migrate
```

### "No HomePage found"

**Problem:** Homepage not seeded.

**Solution:**
```bash
source .venv/bin/activate
python manage.py seed_homepage
```

### "Package 'django' not installed"

**Problem:** Dependencies not installed in virtualenv.

**Solution:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Migration from CLI v1

If you're upgrading from CLI v1:

### What's New in v2

✅ **`sum init` enhancements:**
- `--full` mode for complete setup
- `--quick` mode for fast scaffolding
- Interactive prompts for configuration
- Automatic virtualenv creation
- Dependency installation
- Database migration
- Homepage seeding
- Superuser creation with `.env.local`

✅ **`sum run` command:**
- New command for starting dev server
- Automatic port fallback
- Virtualenv detection

✅ **`sum check` enhancements:**
- More comprehensive validation
- Status indicators (OK/FAIL/SKIP)
- Remediation guidance

### Breaking Changes

⚠️ **Removed `--theme` flag:** CLI v1's `--theme` option is not yet available in v2. All projects are initialized with the default theme (`theme_a`). This functionality is planned for restoration in a future update.

**Workaround:** Manually swap themes after initialization by copying theme files to the project's active theme directory.

---

## Related Commands

### Django Management Commands

Once your project is initialized, these Django commands are available:

```bash
# Seed homepage (if not done during init)
python manage.py seed_homepage

# Create homepage with force (recreate)
python manage.py seed_homepage --force

# Run migrations
python manage.py migrate

# Create superuser manually
python manage.py createsuperuser

# Start server manually
python manage.py runserver
```

---

## Environment Variables

### During Setup

- `DJANGO_SETTINGS_MODULE` - Set automatically during init
- `PYTHONPATH` - Set automatically in monorepo mode

### After Setup

Your `.env.local` file (created by `--full` setup) contains:

```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

Load these in your environment:

```bash
source .venv/bin/activate
export $(cat .env.local | xargs)
```

---

## Best Practices

### For Quick Testing

```bash
sum init test-project --full --ci
```

Fast, non-interactive full setup for experimentation.

### For Production Projects

```bash
sum init my-client --quick
cd my-client
# Review requirements.txt, configure settings
source .venv/bin/activate
python manage.py migrate
python manage.py createsuperuser  # Use secure password
python manage.py seed_homepage
```

Controlled, step-by-step setup with custom configuration.

### For CI/Automation

```bash
sum init ci-project --full --ci --skip-superuser --skip-seed
```

Fast setup without interactive steps or unnecessary content.

---

## Next Steps

After initializing your project:

1. **Review settings** - Check `project_name/settings/` files
2. **Configure theme** - See [THEME-GUIDE.md](./THEME-GUIDE.md)
3. **Add content** - Use Wagtail admin at `/admin`
4. **Customize blocks** - See [StreamField blocks documentation](./blocks.md)
5. **Deploy** - See [deployment guide](../ops-pack/deployment.md)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/markashton480/sum-platform/issues)
- **Documentation:** `docs/` directory
- **Examples:** `clients/` directory (monorepo mode)
