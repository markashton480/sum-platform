## SUM CLI (v1): `sum init`, `sum check`

This repo ships a minimal **filesystem scaffolding + validation CLI**.
It intentionally does **not** create virtualenvs, install dependencies, initialise git, or touch databases.

### Install (monorepo dev)

From repo root (using the repo virtualenv):

```bash
source .venv/bin/activate
pip install -e ./cli
```

### `sum init <project-name>`

Creates a new client project at `clients/<project-name>/` by copying the boilerplate and applying deterministic renames:

- client directory name uses the provided slug (e.g. `acme-kitchens`)
- Django project package name is normalized for Python imports (hyphens → underscores, e.g. `acme_kitchens`)
- all `project_name` placeholders are replaced
- `.env` is created by copying `.env.example` (no secret generation)

Run from the repo root:

```bash
sum init acme-kitchens
```

### `sum check`

Validates the **current working directory** is a structurally-correct client project:

- `.env.example` exists
- required env var keys (from `.env.example`) are provided via `.env` and/or process environment
- settings module is importable (inferred from `.env` or `manage.py`)
- URLConf includes sum_core ops wiring (health endpoint)
- `sum_core` is importable
- no references to `test_project` exist in the project tree

Run from a client project directory:

```bash
cd clients/acme-kitchens
sum check
```

### Boilerplate source resolution

`sum init` uses the canonical repo `/boilerplate/` if present (and valid). If not, it falls back to a boilerplate copy bundled with the CLI package.

You can override the boilerplate path for development:

```bash
SUM_BOILERPLATE_PATH=/path/to/boilerplate sum init acme-kitchens
```


