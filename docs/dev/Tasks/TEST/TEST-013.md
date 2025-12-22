# TASK TICKET: TEST-013 — Phase 3 test infrastructure (shared fixtures + isolation helpers)

### Goal

Implement Phase 3 (“Test Infrastructure”) from `test-strategy-implementation-plan.md`: create shared fixtures/helpers that enforce hermetic test behavior (tmp-only writes), standardise repo-root/protected-path handling, and reduce per-slice bespoke setup.

### Context

We’ve already established:

- Protected-assets guardrails + CI enforcement
- Runnable slices (`test-cli`, `test-themes`, `test-templates`)
  Now we need the _infrastructure layer_ so new tests don’t reintroduce unsafe patterns.

### Scope (IN)

1. **Create shared test utilities**

- Add (or extend if already present):

  - `tests/utils/__init__.py`
  - `tests/utils/fixtures.py`

- Include utilities/fixtures for:

  - `repo_root` resolution
  - `protected_paths` canonical list (single source of truth for tests)
  - helper assertion: “protected paths unchanged” (optional but ideal)

2. **Add root test conftest**

- Add `tests/conftest.py` that exposes standard fixtures used across suites:

  - `repo_root`
  - `protected_paths`
  - any common temp-dir helpers used by templates/themes/cli tests

3. **Make template determinism tests more future-proof (tighten TEST-012 contract)**

- Update `tests/templates/test_template_loading_order.py` so the “core fallback” test does **not depend on theme_a staying absent** of a specific template forever.

  - Preferred pattern: create a temporary “theme candidate” dir in `tmp_path` that intentionally lacks the template, ensure loader checks it first, then assert fallback resolves to core.
  - Keep the existing “theme overrides core” test intact.

4. **Verification + documentation**

- If the repo uses a central pytest config (pyproject/pytest.ini), update it only if needed for markers/collection consistency (don’t add new plugins).
- Add/update a short note in the ticket follow-up report about the final fixture layout and how to use it.

### Scope (OUT)

- No new theme feature tests (that’s Phase 4)
- No CLI safety refactor work (that’s Phase 5)
- No new CI jobs unless required to keep gates equivalent (Phase 6)

### Acceptance Criteria

- `make lint` passes
- `make test` passes
- `make test-cli` passes
- `make test-themes` passes
- `make test-templates` passes
- Template fallback test is **not coupled** to whether `themes/theme_a` happens to include a template in the future

### Commands (agent must run and paste results in follow-up)

```bash
make lint
make test
make test-cli
make test-themes
make test-templates
git status --porcelain
```

---

## Agent Git hygiene (must follow)

1. Start clean and up-to-date:

```bash
git checkout develop
git pull --ff-only origin develop
git status
```

2. Create ONE branch from develop:

```bash
git checkout -b test/TEST-013-test-infra origin/develop
```

3. Commit the ticket first:

```bash
git add docs/dev/Tasks/TEST/TEST-013.md
git commit -m "docs(TEST-013): add task ticket"
git push -u origin test/TEST-013-test-infra
```

4. Implement in small commits (examples):

- `test(TEST-013): add shared fixtures utilities`
- `test(TEST-013): add tests/conftest shared fixtures`
- `test(TEST-013): make template fallback test hermetic`

5. Push, open PR → `develop`, and attach:

- PR link
- `docs/dev/Tasks/TEST/TEST-013_followup.md` with verification output

### Stop / rollback triggers

- Any change that causes tests to write into repo-root or mutate protected dirs
- Any flakiness introduced (non-deterministic failures)
- Any CI gate removal or weakening

---
