# THEME-008 — Purge legacy theme paths + enforce canonical Theme A location

## Mission

Remove any remaining non-canonical Theme A directories (and references to them) so the repo conforms strictly to Theme Architecture Spec v1:

- Canonical theme source lives at: `themes/<theme_slug>/...`
- `sum_core` must NOT contain a second editable theme copy

Then add a guardrail test so this never regresses.

## Source of truth

- `docs/dev/master-docs/THEME-ARCHITECTURE-SPECv1.md` (canonical theme layout + intent)
- `docs/dev/WIRING-INVENTORY.md` (“Theme Wiring (v0.6+)” section)

## Context / Why this exists

THEME-007 transcript indicates the agent interacted with theme files under:

- `sum_core/themes/theme_a/...` (unexpected)
- `core/sum_core/themes/theme_a/...` (should not exist post THEME-005)

This ambiguity will keep causing drift (people edit the wrong copy).

## Scope (strict)

IN SCOPE:

1. Delete any non-canonical Theme A directories/files (outside `themes/theme_a/`) that still exist in the repo.
2. Remove/update any references to old theme paths in code/docs/tests (only “final pointer docs” or live code — do NOT edit historical task artifacts).
3. Add an automated guardrail test that fails if `core/sum_core/themes/theme_a/` (or any `core/sum_core/themes/theme_*`) exists.
4. Ensure Theme A compiled CSS + fingerprint are consistent with current templates (rebuild CSS + regenerate fingerprint if needed).
5. Ensure `test_project/` remains functional and still prefers repo-root `themes/theme_a` in its candidate wiring.

OUT OF SCOPE:

- No new blocks
- No redesign / template restyling (except incidental edits strictly required by path cleanup)
- No CLI feature additions (theme switching etc.)

## Implementation steps

### 0) Preflight: identify all theme_a locations

From repo root, run:

- `find . -maxdepth 6 -type d -name "theme_a" | sort`
- `find . -maxdepth 6 -type f -path "*theme_a*" | sort`

Record findings in the follow-up report.

### 1) Remove legacy Theme A directories (if present)

Hard requirement: after this task, the only Theme A directory in the platform repo is:

- `themes/theme_a/`

Delete (if they exist):

- `core/sum_core/themes/theme_a/`
- `sum_core/themes/theme_a/` (if this path exists in the repo at all)
- Any other duplicate theme copies

If `core/sum_core/themes/` must exist for API/back-compat, it must contain ONLY the deprecation stub (`__init__.py` and/or README) — no theme folders.

### 2) Remove references to old theme paths

Search and update any live references:

- `rg -n "core/sum_core/themes|sum_core/themes|sum_core\\.themes" .`

Rules:

- Update live code/docs/tests to reference repo-root `themes/theme_a` as canonical.
- Do NOT edit or rewrite historical artifacts under:
  - `docs/dev/THEME/tasks/**`
  - any `*_chat.md` transcripts
  - any historical followups for completed tasks

### 3) Add a guardrail test to prevent regressions

Add a pytest that fails loudly if any theme directory exists under `core/sum_core/themes/` other than allowed stubs.

Preferred location:

- extend `tests/themes/test_theme_a_guardrails.py` OR add `tests/themes/test_theme_canonical_locations.py`

Acceptance-level behavior:

- If `core/sum_core/themes/theme_a` exists -> FAIL with a message:
  “Themes must live under repo-root `themes/` only. Remove legacy copy.”

### 4) Ensure Theme A CSS + fingerprint are in sync

Because templates are part of Tailwind inputs, ensure:

- `themes/theme_a/static/theme_a/css/main.css` represents current templates
- `themes/theme_a/static/theme_a/css/.build_fingerprint` matches current inputs

Run:

- `cd themes/theme_a/tailwind && npm install` (or `npm ci` if lockfile workflow is established)
- `npm run build`
- `python ../build_fingerprint.py`

Then:

- `git add themes/theme_a/static/theme_a/css/main.css themes/theme_a/static/theme_a/css/.build_fingerprint`

### 5) Verify

Automated:

- `make test`

Harness sanity (quick):

- run `python core/sum_core/test_project/manage.py runserver`
- confirm edits under `themes/theme_a/templates/...` would be picked up by the harness wiring (no duplicate directories confusing the dev workflow)

## Deliverables

- No Theme A copies exist outside `themes/theme_a/`
- Old-path references removed from live code/docs/tests
- New/updated pytest guardrail prevents reintroduction
- `main.css` + `.build_fingerprint` updated consistently (if rebuild was necessary)
- Follow-up report committed

## Acceptance criteria

- [ ] `find` shows only `themes/theme_a/` as Theme A location in the platform repo
- [ ] `rg` finds **zero** references to `core/sum_core/themes/theme_a` in live code/docs/tests
- [ ] Guardrail test fails if a legacy theme path is reintroduced
- [ ] `make test` passes
- [ ] Follow-up report contains:
  - the `find` output
  - the `rg` output (or summary with count=0)
  - commands run
  - any deletions performed

## Work report

Create: `docs/dev/THEME/tasks/THEME-008_followup.md`
Include: what you found, what you deleted, what you changed, exact commands, and any risks noticed.
