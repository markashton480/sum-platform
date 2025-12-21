# TEST-010 — Enforce test slices in CI (no more “full suite green, slices broken”)

**ID:** TEST-010
**Goal:** CI must explicitly run `make test-cli` and `make test-themes` so slice regressions cannot sneak through.
**Branch:** `test/TEST-010-ci-enforce-slices`
**Base:** `origin/develop` (must include merged TEST-009)
**PR target:** `develop`

## Plan (short)

1. Create a new branch from updated `origin/develop`.
2. Add the TEST-010 task ticket, commit, push, and open PR immediately.
3. Update `.github/workflows/ci.yml` to run `make test-cli` and `make test-themes` as explicit CI steps.
4. Run local verification commands.
5. Add follow-up doc + commit.
6. Push and ensure PR checks run green.

## Checklist & Commands

### 0) Preflight: ensure base is correct

```bash
git switch develop
git fetch origin
git pull --ff-only
git status -sb
```

Success signal: `develop` is up to date and clean.

### 1) Create branch from `origin/develop`

```bash
git checkout -b test/TEST-010-ci-enforce-slices origin/develop
git status -sb
```

### 2) Add task ticket early + push + open PR immediately

Create:

- `docs/dev/Tasks/TEST/TEST-010.md` (task ticket)
  Then:

```bash
git add docs/dev/Tasks/TEST/TEST-010.md
git commit -m "docs(TEST-010): add task ticket"
git push -u origin HEAD
```

**IMPORTANT:** After this push, **open the PR immediately** targeting `develop` (even before implementation).
This prevents the “branch exists locally but not on GitHub / where’s the PR?” confusion.

### 3) Implement CI slice enforcement

Edit:

- `.github/workflows/ci.yml`

Add **two explicit steps** (prefer after the existing `make test` step):

- `make test-cli`
- `make test-themes`

Keep existing guardrails intact (protected assets / git status checks).

### 4) Local verification (must run)

```bash
source .venv/bin/activate
make lint
pytest -q
make test-cli
make test-themes
git status -sb
```

Success signals:

- all commands succeed
- working tree is clean

### 5) Commit implementation + push

```bash
git add .github/workflows/ci.yml
git commit -m "ci(TEST-010): enforce cli + themes test slices"
git push
```

### 6) Follow-up documentation + push

Create:

- `docs/dev/Tasks/TEST/TEST-010_followup.md`

Include:

- commands run + outputs (or summary + key lines)
- what was changed in CI and why
- PR link + commit SHAs

Then:

```bash
git add docs/dev/Tasks/TEST/TEST-010_followup.md
git commit -m "docs(TEST-010): record CI slice enforcement"
git push
git status -sb
```

## Expected success signals

- CI now runs:

  - lint
  - full test suite
  - `make test-cli`
  - `make test-themes`
  - protected-dir guard

- CI fails if either slice fails (even if `pytest -q` would pass).
- PR checks green.

## Stop / rollback triggers

- If CI timeouts increase significantly: stop and report timings (don’t start “optimising” without evidence).
- If slice steps fail in CI but pass locally: stop and capture logs + environment differences.

## Record-keeping updates

- `docs/dev/Tasks/TEST/TEST-010.md` (ticket)
- `docs/dev/Tasks/TEST/TEST-010_followup.md` (execution log)
- If anything surprising happens, append to:

  - `docs/ops-pack/what-broke-last-time.md`

## Git hygiene rules (non-negotiable)

- Ticket commit **first**
- Push immediately and open PR immediately
- Keep commits clean and scoped
- End with `git status -sb` clean

**Complexity:** Low → Medium

---

### Who does what (explicit)

- **You (Mark):** merge PR #8 into `develop` first.
- **Agent:** does _everything_ in TEST-010 including:

  - committing the task ticket
  - pushing the branch
  - opening the PR early
  - implementing CI changes
  - follow-up doc + commits + pushes
