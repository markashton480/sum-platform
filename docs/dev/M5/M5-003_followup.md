## **[M5-003]: Implement CLI v1 (`sum init`, `sum check`) using boilerplate — Follow-up Report**

### Summary

Implemented the v1 SUM CLI with exactly two commands:

- **`sum init <project-name>`**: deterministic client scaffolding by copying the canonical boilerplate into `clients/<project-name>/` and applying safe, boring renames.
- **`sum check`**: structural validation for a client project with clear pass/fail output and exit codes (no stack traces on expected failures).

This work keeps the CLI strictly **filesystem + validation** as required: no venv creation, no dependency installation, no git init, no DB touches.

---

### Key decisions (explicitly allowed by spec)

#### 1) Project name rules + normalization

- **Accepted input**: lowercase letters, digits, hyphens; must start with a letter.
  - Regex: `^[a-z][a-z0-9-]*$`
- **Python package name**: hyphens are converted to underscores for importability.
  - Example: `acme-kitchens` → `acme_kitchens`

This aligns the CLI with the platform’s documented “project slug” expectations while still producing a valid Django project package.

#### 2) Boilerplate resolution (canonical-first, works outside monorepo)

`sum init` selects boilerplate source in this order:

1. `SUM_BOILERPLATE_PATH` (explicit override)
2. `./boilerplate/` when run from a repo root containing a valid boilerplate (canonical source)
3. packaged boilerplate bundled inside the CLI distribution (so the CLI works outside the monorepo)

#### 3) Making `sum init` projects pass `sum check`

To satisfy the milestone acceptance criteria (“`sum init foo` … passes `sum check`”) while still keeping `sum init` deterministic, `sum init` **copies `.env.example` to `.env`** (no secret generation, no “magic”).

---

### Implementation details

#### CLI structure

- Implemented as a dedicated installable package under `cli/`:
  - `cli/pyproject.toml` defines the `sum` console script and bundles boilerplate as package data.
  - Commands are implemented with Python’s built-in `argparse` (no extra runtime dependencies).

#### `sum init`

Behaviour:

- Copies boilerplate → `clients/<project-slug>/`
- Renames the internal Django project package:
  - `project_name/` → `<python_package>/`
- Replaces all `project_name` placeholders in file contents (including dotfiles)
- Creates `.env` from `.env.example` (deterministic copy)
- Refuses to overwrite existing target directory
- Fails loudly on invalid project names or malformed boilerplate

#### `sum check`

Checks implemented (minimum set from the milestone spec):

- **Required env vars present**: reads required keys from `.env.example` assignments and verifies they are provided by `.env` and/or the process environment.
- **Settings module importable**: inferred from `.env` or `manage.py` and imported safely.
- **`/health/` wiring**: verifies URLConf includes `sum_core.ops.urls`.
- **`sum_core` importable**
- **No `test_project` references**: scans common project text files for `test_project`.

Output:

- Human-readable checklist: `[OK]` / `[FAIL]` lines with short details
- Exit code `0` if all pass, `1` otherwise

---

### Documentation added

Created `docs/dev/cli.md` documenting:

- installation for monorepo development (`pip install -e ./cli`)
- command usage for `sum init` and `sum check`
- boilerplate source resolution rules

---

### Tests

Added pytest coverage under `cli/tests/` (kept separate from the Django-heavy `tests/` tree):

- Unit test: project name validation + normalization
- Integration-style test:
  - create temp workspace
  - run `sum init acme-kitchens`
  - run `sum check` in the created project
- Negative test: `sum check` fails on missing required env vars

Repo wiring update:

- Root `pyproject.toml` updated to include `cli/tests` in pytest discovery and add `cli` to `pythonpath`.

Test run performed (in repo `.venv`):

- `python -m pytest cli/tests -q`

---

### Files changed / added

- **CLI package**
  - `cli/pyproject.toml`
  - `cli/sum_cli/__main__.py`
  - `cli/sum_cli/cli.py`
  - `cli/sum_cli/util.py`
  - `cli/sum_cli/commands/init.py`
  - `cli/sum_cli/commands/check.py`
  - `cli/sum_cli/boilerplate/**` (bundled boilerplate copy for non-monorepo usage)

- **Tests**
  - `cli/tests/test_cli_init_and_check.py`

- **Repo test config**
  - `pyproject.toml` (added `cli/tests` + `cli` pythonpath)

- **Docs**
  - `docs/dev/cli.md`

---

### Notes / follow-ups (not implemented here)

- **Future optional path argument**: SSOT mentions `sum check <project-path>`, but M5-003 locked scope is `sum check` with no args. Implementation is structured so an optional `--path` / positional can be added later without redesign.
- **Boilerplate sync**: the CLI bundles a boilerplate copy to work outside the monorepo. In practice, release automation should ensure this packaged boilerplate stays in sync with the canonical `/boilerplate/`.


