# TASK ID: THEME-005
## Mission: 

Align theme source-of-truth to `THEME-ARCHITECTURE-SPECv1.md` (create `/themes`, migrate Theme A, update docs, keep test_project working)

## Goal

Bring the repo into **strict compliance** with Theme Architecture Spec v1 by:

1. Establishing **repo-level `themes/`** as the canonical theme source. 
2. Moving Theme A’s templates/static/etc into `themes/theme_a/…` (as per canonical layout). 
3. Ensuring `core/sum_core/test_project/` continues to render Theme A correctly using repo-level `themes/…` (fast iteration stays intact).
4. Updating docs (`CODEBASE-STRUCTURE.md`, `WIRING-INVENTORY.md`, and any other “pointer docs”) so future work stops drifting.

## Background / Why

We currently have a mismatch between:

* The spec-defined canonical layout (`./themes/…`) 
* Existing implementation/assumptions implying theme templates live under `core/sum_core/themes/…` and are “canonical sources used by tooling” (seen in THEME-004 work).
* Docs that still describe “templates/overrides” as the primary client mechanism (legacy). 

This causes exactly the chaos you described: people edit the wrong file tree and get “random rendering.”

## Scope

### In scope

* Create and populate repo root `themes/theme_a/` matching spec structure.
* Stop treating `core/sum_core/themes/…` as canonical (either remove it, or clearly demote it to non-authoritative).
* Ensure harness points to repo-level themes for templates + statics and is still functional.
* Update core docs so the theme system is clearly described and aligns with the spec.

### Out of scope

* Tailwind build pipeline changes (unless needed to keep theme assets discoverable).
* Reworking Theme A markup/styling (this ticket is structure + wiring + documentation).

## Implementation steps

### 1) Add canonical `themes/` directory at repo root

Create this structure (as per spec): 

```
themes/
  theme_a/
    theme.json
    templates/
    static/
    tailwind/
    README.md
```

### 2) Migrate Theme A into `themes/theme_a/`

Identify current Theme A source (likely `core/sum_core/themes/theme_a/...` from recent work) and migrate it into the canonical location:

* Move/copy:

  * `templates/…` → `themes/theme_a/templates/…`
  * `static/…` → `themes/theme_a/static/…`
  * Any `tailwind/` config → `themes/theme_a/tailwind/…`
  * Ensure `theme.json` exists at `themes/theme_a/theme.json` and its slug matches directory name (spec expects validity).

**Important:** do not use symlinks (cross-platform + tooling pain). Do a real move/copy.

### 3) Demote or remove `core/sum_core/themes/*` as a “canonical” theme source

Spec says canonical is repo-level themes, and bundling is “CLI optional later.” 

So:

* Remove (or clearly mark deprecated) any module/docs claiming themes are “shipped with sum_core” and used by tooling. 
* Replace any internal theme discovery logic that scans `core/sum_core/themes/*` with logic that targets repo-level `./themes/…` **for platform repo development**.

If something in CLI currently needs packaged themes, that’s a separate explicit packaging step and should live under the CLI package per spec (“bundled themes inside CLI package”). 

### 4) Ensure `test_project` uses canonical repo-level themes

`test_project` settings already contain candidates that look for:

* `REPO_ROOT / "themes" / "theme_a" / "templates"`
* `REPO_ROOT / "themes" / "theme_a" / "static"`

After Theme A is moved to `./themes/theme_a`, verify:

* Running `runserver` picks up templates from `themes/theme_a/templates/…`
* Static files are served from `themes/theme_a/static/…` (or collectstatic resolves correctly depending on harness approach)

Also ensure comments in settings reflect the spec’s intended loader order (theme first, then overrides, then core templates).

### 5) Documentation updates (required)

#### A) `CODEBASE-STRUCTURE.md`

* Add `themes/` to the directory tree as a first-class repo directory.
* Update “Client Projects” section:

  * Replace “Override templates in `templates/overrides/`” with the spec-defined mechanism:

    * `clients/<client>/theme/active/templates` first
    * then `templates/overrides`
    * then core templates last

#### B) `WIRING-INVENTORY.md`

Add a new section: **Theme Wiring (v0.6+)** describing:

* What lives in `themes/` vs client `theme/active`
* Template resolution order
* Static resolution expectations
* `DJANGO_DB_*` reminder + that SQLite fallback exists, but Postgres is expected for real dev parity (already mentioned but currently too vague).

#### C) Cleanup: `POST-MVP_BIG-PLAN.md`

There’s an example theme structure that references `sum_core/themes/theme_a/…` which conflicts with the spec and will mislead future work. Update it to point at `themes/theme_a/…` or annotate as legacy.

### 6) Grep + replace any hardcoded old theme paths

Search for references to:

* `core/sum_core/themes/`
* `sum_core.themes`
* “themes shipped with sum_core”

and update them to align with the canonical `themes/` model (and/or CLI bundling model if needed).

7) When finished, please complete a full, comprehensive work report in `THEME-005_followup.md` - include all work completed, as well as any observations, red flags, potential issues and confusions you noticed along the way.

## Test plan

### Harness check (manual)

* `make db-up`
* Run `core/sum_core/test_project`:

  * confirm `connection.vendor == postgresql` (we don’t want SQLite surprises again)
* `python core/sum_core/test_project/manage.py runserver`
* Edit a file under `themes/theme_a/templates/…` and confirm the change is reflected on refresh.

### Automated

* `pytest`
* Add/adjust a small guardrail test if needed:

  * Assert that `themes/theme_a/theme.json` exists in repo context
  * Assert harness theme template dir resolution prefers repo-level `themes/theme_a/templates` when present

## Acceptance criteria

* Repo has canonical `themes/theme_a/…` matching the spec’s directory contract. 
* No code/docs claim `core/sum_core/themes/…` is canonical.
* `test_project` renders using templates from `themes/theme_a/templates/…` when present.
* `CODEBASE-STRUCTURE.md` and `WIRING-INVENTORY.md` reflect the spec’s theme wiring and no longer present `templates/overrides/` as the primary mechanism.

---
