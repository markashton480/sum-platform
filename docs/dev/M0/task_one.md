### **[M0-001] Monorepo Structure & Python Tooling**

---

#### Context (from PRD)

* We need a **properly configured monorepo with Docker-based local development** so the platform can be developed consistently: directory structure, pre-commit hooks, Makefile, Docker Compose. 
* The **core package (`sum_core`)** is the central dependency all client projects will install, so its structure and packaging need to be clean and standardised from day one. 
* Test Strategy expects ≥80–85% coverage for `sum_core` and boilerplate and a CI gate for lint/tests, so we need test and lint tooling baked into the repo foundation. 

---

#### Technical Requirements

From Implementation Plan / PRD:

* Monorepo root must include: `core/`, `boilerplate/`, `clients/`, `cli/`, `docs/`, `scripts/`, `infrastructure/`.
* Configure `pyproject.toml` to define:

  * Black, isort, ruff/flake8 config.
  * pytest configuration (test paths, Django settings module placeholder).
  * mypy (or pyright) config for type checking (even if we relax it initially).
* Pre-commit hooks with at least:

  * Black
  * isort
  * ruff or flake8
* `Makefile` with targets:

  * `make lint` → run ruff/flake8 + maybe mypy.
  * `make test` → run pytest (unit+integration later).
  * `make format` → run Black + isort.
  * `make run` → placeholder for local dev (will be wired to Docker in a later ticket).
* `.editorconfig` to keep whitespace/encoding consistent (optional but recommended).

No Docker or Wagtail wiring here yet — this ticket is strictly “repo skeleton + Python tooling”.

---

#### Design Specifications (repo-level “design”)

* Directory names must match PRD/Implementation Plan exactly so later tasks can reference them without ambiguity.
* Keep the repo root clean: avoid dropping random tooling files in subdirectories (centralise config in root where possible).
* Prepare for test coverage gates described in Test Strategy (CI will eventually fail if coverage <80%). 

---

#### Implementation Guidelines

**Files / folders to create or modify**

* `/core/`
* `/boilerplate/`
* `/clients/`
* `/cli/`
* `/docs/`
* `/scripts/`
* `/infrastructure/`

Plus:

* `/pyproject.toml`
* `/.pre-commit-config.yaml`
* `/Makefile`
* `/.editorconfig` (recommended)
* `/README.md` (stub; extended in a later ticket)

**Header comment convention**

For any Python module you add in this ticket (even if minimal), include:

```python
"""
Name: [Module Name]
Path: [File path]
Purpose: [Brief description]
Family: [What depends on this]
Dependencies: [What this depends on]
"""
```

* Use type hints for any real functions; for now you may just have `__init__.py` with `__version__` and constants, but keep the pattern in mind for the next tickets.

**Suggested steps**

1. **Create folder structure** in the repo root.
2. Add `pyproject.toml`:

   * `[tool.black]`, `[tool.isort]`, `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.mypy]` sections.
   * Configure Python version `3.12` per PRD. 
3. Add `Makefile` with basic shell recipes that call `python -m pytest`, `ruff`, `black`, `isort`, etc.
4. Add `.pre-commit-config.yaml` with hooks for formatting/linting.
5. Run `pre-commit install` locally and ensure `pre-commit run --all-files` succeeds.
6. Add a tiny `tests/` package (e.g. `tests/test_smoke.py` with a single passing test) so `make test` does something real.
7. Update `README.md` with a minimal “Getting started (tooling)” section describing:

   * How to install dev requirements.
   * How to run `make lint`, `make test`, `make format`.

---

#### Acceptance Criteria

* [ ] Monorepo root contains `core/`, `boilerplate/`, `clients/`, `cli/`, `docs/`, `scripts/`, `infrastructure/`.
* [ ] `pyproject.toml` exists and configures Black, isort, ruff/flake8, pytest (including default test paths and Python version).
* [ ] `Makefile` provides working `lint`, `test`, `format` (they run without error on the empty project).
* [ ] `.pre-commit-config.yaml` exists, and `pre-commit run --all-files` succeeds on a clean checkout.
* [ ] A basic smoke test suite runs via `make test` and exits with status 0.
* [ ] README has a short section explaining how to run linting and tests locally.

---

#### Dependencies & Prerequisites

* No upstream task dependencies (this is the first step).
* Requires Python 3.12 and a working virtualenv on your machine. 

This should be completed **before**:

* [M0-002] Core package skeleton & test project.
* [M0-003] Docker Compose dev environment.

---

#### Testing Requirements

* **Unit tests**

  * At least one simple “smoke” test in `tests/` (e.g. assert `True` or import a standard library module) to validate pytest wiring.
* **Integration tests**

  * Not applicable yet (no Django/Wagtail wiring).
* **Manual checks**

  * Run `make lint`, `make test`, `make format` and confirm all succeed.
  * Run `pre-commit run --all-files` and confirm no failing hooks.




