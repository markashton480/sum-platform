# TEST-011.md — Split CI into real gates (lint / full / cli / themes)

### Objective

Refactor GitHub Actions CI into separate, meaningful gates so failures are localised and readable:

- `lint`
- `test-full` (full suite)
- `test-cli` (slice)
- `test-themes` (slice)

This implements the strategy step: “Re-baseline CI into separate, meaningful gates… (unit/integration/theme/CLI), each with hard safety checks.”

### Non-goals

- No new tests.
- No Tailwind/node build work in this ticket.
- No changes to `Makefile` targets (they already exist).
- No refactors outside `.github/workflows/ci.yml` and the task docs.

### Branch + PR rules

- Base: `origin/develop`
- Branch: `test/TEST-011-ci-split-gates`
- PR target: `develop`
- One branch == one PR. If PR already exists, **do not create another PR**.

### Required Git hygiene (agent)

1. Start clean:

```bash
git status --porcelain
```

Must be empty.

2. Branch from `origin/develop`:

```bash
git fetch origin
git checkout -b test/TEST-011-ci-split-gates origin/develop
```

3. Commit the ticket first, then push immediately:

```bash
git add docs/dev/Tasks/TEST/TEST-011.md
git commit -m "docs(TEST-011): add task ticket"
git push -u origin HEAD
```

4. PR creation:

- If `gh` is available + authenticated, create PR.
- If not, paste the PR-create URL in the followup and continue implementation without waiting.

### Implementation requirements

Edit `.github/workflows/ci.yml` to:

#### A) Create a `lint` job

- Runs `make lint`
- Uses the same install/caching approach as existing CI.
- Other test jobs should use `needs: lint` (so we don’t waste compute when lint fails).

#### B) Create `test-full` job

- Runs `make test` (or `pytest -q` if that’s what `make test` does—keep consistent with repo conventions).
- Must include the **existing protected assets guard** after tests.
- Must include the existing “themes/theme_a exists” check.

#### C) Create `test-cli` job

- Runs `make test-cli`
- Must include the same protected assets guard + theme existence check after tests.
- Must perform the same “clean stale artifacts” step _before_ tests (the same as current CI).

#### D) Create `test-themes` job

- Runs `make test-themes`
- Must include the same protected assets guard + theme existence check after tests.
- Must perform the same “clean stale artifacts” step _before_ tests.

#### E) Keep CI behaviour sensible

- All jobs should use the same Python version and dependency install approach currently used.
- Keep timeouts reasonable (existing 15 mins is fine unless you have a concrete reason to change).
- Prefer duplication over clever YAML abstraction for now (readability + audit > DRY).

### Acceptance criteria

- CI workflow now shows separate jobs: `lint`, `test-full`, `test-cli`, `test-themes`.
- All jobs run on PRs to `develop` and pushes to `develop/main` (same triggers as existing CI).
- Each test job runs the protected assets guard and fails if protected dirs contain tracked/untracked changes.
- Local verification (agent must run and include outputs in followup):

```bash
source .venv/bin/activate
make lint
pytest -q
make test-cli
make test-themes
```

### Deliverables

- Commit 1: `docs(TEST-011): add task ticket`
- Commit 2: `ci(TEST-011): split CI into lint/full/cli/themes gates`
- Commit 3: `docs(TEST-011): record CI gate split + results`

  - Add `docs/dev/Tasks/TEST/TEST-011_followup.md` including:

    - what changed in CI
    - job names
    - commands run + results
    - PR link (or PR-create link if PR wasn’t created)

### Stop / rollback triggers

Stop and report immediately if:

- Any job starts failing due to protected-assets guard false positives that indicate we’ve been relying on artifacts in protected dirs.
- Splitting jobs requires introducing new tooling (e.g. node) to pass.

---
