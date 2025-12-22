# TEST-012 — Fix template resolution determinism (THEME-15-A) + add template loading gate

## Goal

Eliminate settings/template-loading divergence between “isolated runs” and “full suite runs” by removing RUNNING_TESTS-dependent template path logic and replacing it with a deterministic theme template resolution strategy. Add a focused test that proves ordering (theme override > core fallback) and wire it into CI as an early gate.

This implements Phase 2 of `test-strategy-implementation-plan.md` (Root Cause Fixes).

## Scope (IN)

1. Audit `core/sum_core/test_project/test_project/settings.py` for `RUNNING_TESTS` conditionals that affect template loading.
2. Replace conditional template-dir logic with:
   - A deterministic `THEME_TEMPLATES_CANDIDATES` list
   - “First existing path wins” resolution
   - Identical `TEMPLATES[...]` configuration in test and production code paths
   - Clear inline comments documenting resolution order
3. Add `tests/templates/test_template_loading_order.py` that verifies:
   - A known overridden template resolves from the theme directory (theme precedence)
   - A known non-overridden template resolves from core (core fallback)
   - Repeated resolution is stable (no flip/flop between dirs across calls)
4. Add the template-order test as a **distinct CI gate** (fast fail) after lint.

## Scope (OUT)

- Refactoring unrelated theme/CLI tests
- Adding new theme tests (Phase 4)
- Fixture/conftest framework work (Phase 3)

## Acceptance Criteria

- [ ] No `RUNNING_TESTS` conditional changes template loading behavior (specifically THEME template dir resolution).
- [ ] Template resolution order is deterministic and documented in settings comments.
- [ ] `pytest tests/templates/test_template_loading_order.py -v` passes.
- [ ] Full suite still passes (`make test`).
- [ ] CI runs the new gate (e.g. `test-templates`) and it fails independently if ordering breaks.

## Files to modify / add

- MODIFY: `core/sum_core/test_project/test_project/settings.py`
- ADD: `tests/templates/test_template_loading_order.py`
- MODIFY: `.github/workflows/ci.yml` (add `test-templates` job, `needs: lint`)
- (Optional but nice) MODIFY: `Makefile` (add `make test-templates` target used by CI)
- ADD: `docs/dev/Tasks/TEST/TEST-012.md` (ticket + notes)

## Implementation Notes

- Pick 2 concrete templates for the test:
  1. One that is definitely overridden by `themes/theme_a/templates/...`
  2. One that exists only in core templates (no theme override)
- In the test, assert template origin path (e.g. `template.origin.name`) contains either `themes/theme_a` or `sum_core/templates` as appropriate.
- Ensure the test does not write anywhere outside `tmp_path`.

## CI Gate Design

Preferred:

- Add a `test-templates` job:
  - `needs: lint`
  - installs deps (same as other test jobs)
  - runs `make test-templates` (or `pytest tests/templates/test_template_loading_order.py -q`)
  - (If your CI policy is “every job enforces invariants”): include the same protected-assets guard step pattern used elsewhere.

## Verification Commands (must run locally)

- `make lint`
- `pytest tests/templates/test_template_loading_order.py -v`
- `make test`
- `make test-cli`
- `make test-themes`

## Git / PR Hygiene (non-negotiable)

1. Start from up-to-date develop:
   - `git fetch origin`
   - `git checkout develop`
   - `git pull --ff-only origin develop`
2. Create a single task branch from develop:
   - `git checkout -b test/TEST-012-template-resolution origin/develop`
3. Commit the ticket first:
   - add `docs/dev/Tasks/TEST/TEST-012.md`
   - `git commit -m "docs(TEST-012): add task ticket"`
4. Then implement code + tests in small commits:
   - e.g. `test(TEST-012): deterministic theme template resolution`
   - e.g. `test(TEST-012): add template loading order gate`
5. Push branch and open PR to `develop`.

## Stop / Rollback Triggers

- If template resolution changes break `make test-themes` or cause widespread Django template failures:
  - revert settings changes in the branch and re-approach with a smaller change
- If CI becomes materially slower due to the new gate:
  - keep the test, but run it inside `test-full` instead of as a separate job (only if needed)

## Deliverables

- PR against `develop`
- Work report summarizing:
  - what RUNNING_TESTS conditionals were removed/changed
  - chosen templates for precedence/fallback tests
  - local verification output (commands + results)
  - Called `TEST-12_followup.md` in same directory
  - Commit this ticket with the same commit message
