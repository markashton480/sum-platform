---
trigger: always_on
---

# SUM Platform – Cursor Global Rules

## Project Context

- This repo is **SUM Platform**:
  - `core/sum_core/` – reusable Django/Wagtail core package.
  - `boilerplate/` – starter client project.
  - `cli/` – `sum` CLI for scaffolding client sites.
  - `docs/` – architecture, dev guides, ADRs.
- Goal: provide a fast-launch core for multiple Wagtail sites (home improvement trades).

## Design Tokens

- This project has a design token system as outlined in `docs/dev/THEME-GUIDE.md`
- Always check and follow the existing design tokens
- Never hard code values
- Only create new design tokens when absolutely necessary.
- The objective is uniformity.

## Environment & Tooling

- Use **Python 3.12** in a **virtualenv at repo root**:
  - Create: `python -m venv .venv`
  - Activate (WSL / Linux): `source .venv/bin/activate`
- After activation, install core + dev deps as needed:
  - `pip install -e ./core`
  - If a dev requirements file exists, install it too (e.g. `pip install -r requirements-dev.txt`).
- Use **pytest / pytest-django** for tests (no `manage.py test`).
- Linting / formatting / tests are driven via **Makefile**:
  - `make lint` – lint/checks (Ruff, etc.).
  - `make test` – run the test suite.
  - Use these as the default commands when “run tests” or “run lint” is requested.

## Git & Branching Conventions

- Default branch is **`develop`** (must remain stable).
- For each task/ticket, create a branch from `develop`:
  - Example: `git checkout -b feat/m0-001-monorepo-tooling`
- Prefer **small, focused commits** using these prefixes:
  - `feature:<scope>-<description>` – new user-facing behaviour or styling.
  - `fix:<scope>-<description>` – bug fixes (including CSS bugs).
  - `chore:<description>` – tooling, infra, refactors that don’t change behaviour.
  - `docs:<description>` – documentation-only changes.
  - `refactor:<scope>-<description>` – internal code reshaping.
- Never commit directly to `main` or `develop` ; always go via a feature/fix branch.

## Code & Testing Guidelines

- Treat `core/sum_core` as the **primary product**:
  - Keep it installable (`pip install -e ./core`).
  - Prefer small, modular Django apps and well-scoped changes.
- When adding functionality:
  - Put reusable logic into `sum_core` where possible.
  - Add / update **pytest tests** near the code you touch.
  - Ensure `make lint` and `make test` pass **after activating `.venv`**:
    - `source .venv/bin/activate && make lint`
    - `source .venv/bin/activate && make test`
- Prefer updating existing patterns (blocks, pages, leads, branding, etc.) over inventing new structures, unless explicitly asked.

## Scope for Agents

- Assume working directory is the **repo root**.
- Don’t introduce new top-level directories unless clearly justified.
- Avoid heavy CI/infra changes unless the task explicitly targets them.
- Keep changes aligned with the technical spec and implementation plan; update docs/ADRs if you make architectural changes.
