# TEST-017: Multi-version test markers and legacy 0.5.x smoke workflow

## Branch

- [ ] Checkout/create branch: chore/TEST-017-multi-version-smoke
- [ ] Verify: git branch --show-current

## Objective

We’ve completed the Phase 5 CLI safety refactor and added Phase 6 CI source-integrity gates. The next step is Phase 7 in the implementation plan: introduce a minimal multi-version testing framework so we can keep the frozen 0.5.x line healthy while 0.6.x+ evolves. This ticket adds version-aware pytest markers (so tests can self-skip appropriately), creates a small smoke suite intended to run against the 0.5.x release line, and adds a scheduled (and manually runnable) CI workflow that executes that smoke suite on the 0.5.x ref.

## Acceptance Criteria

- [ ] Pytest markers exist and are registered (no unknown-marker warnings):

  - requires_themes (tests that only make sense on 0.6.x+)
  - legacy_only (tests intended only for 0.5.x)
  - loopsite (registered now even if loopsite tests land later)

- [ ] Root test runner applies version-aware skipping:

  - If sum_core version is < 0.6, skip tests marked requires_themes
  - If sum_core version is >= 0.6, skip tests marked legacy_only

- [ ] A smoke test suite exists at tests/smoke/ with at least 2–4 stable tests marked legacy_only, designed to run on 0.5.x (keep them small and non-flaky).
- [ ] A GitHub Actions workflow exists at .github/workflows/legacy-smoke.yml that:

  - supports workflow_dispatch (manual run)
  - supports schedule (weekly)
  - checks out the 0.5.x line (release/0.5.x branch if it exists; otherwise the most appropriate 0.5.x ref, documented in the follow-up)
  - installs dependencies needed to run the smoke suite
  - runs only the smoke tests

- [ ] The workflow produces a clear pass/fail signal and prints useful diagnostics on failure.
- [ ] Existing CI (full + slices + source integrity checks) remains unchanged and green.
- [ ] Local verification completes:

  - make test
  - pytest tests/smoke/ -v (in current develop line it may skip due to legacy_only; that is acceptable as long as collection works and markers are registered)

## Steps

1. Branch workflow

   1. git checkout develop
   2. git pull
   3. git checkout -b chore/TEST-017-multi-version-smoke
   4. git branch --show-current

2. Register markers in pytest config

   - Add markers to the repo’s pytest configuration (where markers are currently registered, likely pyproject.toml under pytest ini options).
   - Ensure at minimum: requires_themes, legacy_only, loopsite are present.

3. Implement version-aware skipping in tests/conftest.py

   - Update (or create, if missing) tests/conftest.py so it:

     - determines the running sum_core version robustly (prefer `sum_core.__version__`; if import fails, fall back to `importlib.metadata` for the installed package version; if both fail, do not crash the test run—log a short warning and skip version-based logic).
     - implements pytest_collection_modifyitems to apply the skip rules for requires_themes and legacy_only.

   - Keep this logic scoped to the root tests suite; it must not break running pytest from other subtrees.

4. Add minimal legacy smoke tests

   - Create tests/smoke/ and add a small file such as tests/smoke/test_smoke_0_5_x.py.
   - Keep tests intentionally low-scope and stable. Good examples:

     - sum_core imports and exposes a version string
     - Django settings module for the harness can be imported
     - A trivial Django test client request to /health/ returns 200 or 503 depending on expected semantics in 0.5.x (choose an invariant that is stable in 0.5.x and document it)

   - Mark these tests legacy_only.
   - If a smoke test requires services (Postgres/Redis), make that explicit and keep it as a separate test marked slow (optional). The default smoke suite should not require complex infra unless 0.5.x reality demands it.

5. Add scheduled legacy smoke workflow

   - Create .github/workflows/legacy-smoke.yml with:

     - on: workflow_dispatch
     - on: schedule (weekly)

   - In the workflow:

     - checkout the chosen 0.5.x ref (release/0.5.x if present; otherwise a pinned tag like v0.5.x or equivalent—document the selection)
     - set up python 3.12
     - install dependencies for that ref (use the ref’s own installation path; do not assume develop tooling)
     - run pytest tests/smoke/ -v

   - Add minimal logging so failures are actionable (print version, installed deps, and pytest output).

6. Run verification locally

   - source .venv/bin/activate
   - make test
   - pytest tests/smoke/ -v
   - Confirm no unknown-marker warnings.

## Documentation

- [ ] Create docs/dev/Tasks/TEST/TEST-017_followup.md with:

  - Summary of changes made
  - Files modified/created
  - Which 0.5.x ref the workflow uses and why (branch/tag name)
  - Test results (local + CI evidence if available)
  - Any decisions (e.g., smoke test scope choices)

## Commit & Push

- [ ] Stage changes: git add -A
- [ ] Commit: chore(TEST-017): add version markers and legacy smoke workflow

  - Include BOTH docs/dev/Tasks/TEST/TEST-017.md AND docs/dev/Tasks/TEST/TEST-017_followup.md

- [ ] Push: git push origin chore/TEST-017-multi-version-smoke

## Verification

- [ ] Run git status --porcelain
- [ ] Expected: empty (clean) OR only intentional untracked files (documented in followup)

## Recommended Agent

| Criteria      | Selection                                                                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Model**     | GPT-5.1 Codex Max                                                                                                                           |
| **Thinking**  | Standard                                                                                                                                    |
| **Rationale** | Requires careful compatibility handling across version lines and CI workflow wiring, with moderate risk of subtle collection/import issues. |
