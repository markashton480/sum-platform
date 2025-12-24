# THEME-016-A: Fix CI lint failure on PR #25 (ruff errors in CLI boilerplate)

## Branch

- [ ] Checkout/create: `feat/theme-016-service-cards`
- [ ] Verify: `git branch --show-current`

## Context

PR #25 (THEME-016) is blocked in GitHub Actions because the **lint** job fails with exit code 2. ([GitHub][1])
This repo’s CI lint step runs `ruff check .`, which scans **all Python files**, including CLI boilerplate templates. The PR includes edits in boilerplate files under `cli/sum_cli/boilerplate/...` and at least one of those edits appears to have introduced invalid or ruff-unfriendly code (notably the optional `Faker` import block). ([GitHub][2])

## Objective

Unblock PR #25 by fixing ruff lint errors introduced in THEME-016 changes **without changing** the intended ServiceCardsBlock output/behaviour.

## Key Files

- `cli/sum_cli/boilerplate/project_name/home/management/commands/populate_demo_content.py` – optional `Faker` import section appears broken and is a prime candidate for ruff exit-code-2 failures. ([GitHub][2])
- `cli/sum_cli/boilerplate/project_name/home/management/commands/seed_showroom.py` – recent option-sanitising removals may have introduced lint/type issues; keep it clean and explicit. ([GitHub][2])
- `cli/sum_cli/boilerplate/project_name/settings/base.py` – `_get_project_theme_slug()` changed to return `config.get("theme")` directly; reinstate safe narrowing to `str | None` (and keep code lint-friendly). ([GitHub][2])
- `.github/workflows/ci.yml` and `pyproject.toml` (or wherever ruff config lives) – to understand which ruff rules are enabled and reproduce CI locally.

## Acceptance Criteria

- [ ] `ruff check .` passes locally (no violations).
- [ ] CI “lint” job passes on PR #25 after pushing the fix commit. ([GitHub][1])
- [ ] No behavioural regressions to THEME-016’s ServiceCardsBlock rendering/tests.
- [ ] Tests pass per `test-strategy-post-mvp-v1.md`.

## Steps

1. **Branch verification**

   - Checkout `feat/theme-016-service-cards`
   - Confirm branch name matches ticket.

2. **Reproduce CI locally**

   - Run: `ruff check .`
   - Note exact failing files/rules (capture in followup).

3. **Fix `populate_demo_content.py` optional Faker pattern**

   - Make the optional import block unambiguous, syntactically valid, and ruff-friendly.
   - Recommended pattern (avoid shadowing + keep types readable):

     - `try: from faker import Faker as FakerImpl`
     - `except ImportError: FakerClass = None`
     - `else: FakerClass = FakerImpl`
     - then instantiate via `FakerClass()` when not None.

   - Remove any duplicated/contradictory `except ImportError` branches if present. ([GitHub][2])

4. **Reinstate safe narrowing in `_get_project_theme_slug()`**

   - Restore the `isinstance(..., str)` guard so the function truly returns `str | None`, not arbitrary JSON values. ([GitHub][2])

5. **Review `seed_showroom.py` option handling**

   - If ruff flags anything (or if the current code passes “Any” where strings/ints are expected), restore explicit coercion:

     - `hostname` should be `str | None`
     - `port` should be `int | None`
     - `homepage_model` should be `str | None`

   - Keep changes minimal and consistent with existing project patterns. ([GitHub][2])

6. **Re-run validation**

   - `ruff check .`
   - `mypy core/sum_core/ --ignore-missing-imports` (match CI)
   - `make test`

7. **Push fix to update PR #25**

   - This is a corrective ticket; keep PR branch, just add a commit.

## Testing Requirements

- [ ] Run: `ruff check .`
- [ ] Run: `mypy core/sum_core/ --ignore-missing-imports`
- [ ] Run: `make test`
- [ ] Expected: all green locally; PR #25 lint check green in GH Actions.

## Documentation Updates

Update if changes affect:

- [ ] `WIRING-INVENTORY.md` (not expected)
- [ ] `blocks-reference.md` (not expected)
- [ ] `page-types-reference.md` (not expected)

## Deliverables

- [ ] Create `THEME-016-A_followup.md` (same directory as this ticket) containing:

  - Summary of what ruff complained about (exact errors)
  - Files modified
  - Test results (commands + outcomes)
  - Any decisions/tradeoffs

## Commit & Push

- [ ] Stage: `git add -A`
- [ ] Commit: `fix(THEME-016-A): repair ruff issues in CLI boilerplate`

  - **Must include both** `THEME-016-A.md` AND `THEME-016-A_followup.md`

- [ ] Push: `git push origin feat/theme-016-service-cards`

## Verification

- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent

### Criteria Selection

- **Model:** GPT-5.2 Codex
- **Thinking:** Standard
- **Rationale:** CI-lint failures can be deceptively fiddly (ruff config + syntax edge cases in boilerplate). This needs careful tracing with minimal behavioural change.

[1]: https://github.com/markashton480/sum_platform/pull/25/checks "feat(THEME-016): implement theme_a ServiceCardsBlock template by markashton480 · Pull Request #25 · markashton480/sum_platform · GitHub"
[2]: https://github.com/markashton480/sum_platform/pull/25/files "feat(THEME-016): implement theme_a ServiceCardsBlock template by markashton480 · Pull Request #25 · markashton480/sum_platform · GitHub"
