# TEST-004 — Unblock PR #5 by fixing mypy failure; make CI green

## Context

PR #5 (branch `test/TEST-003-ci-green`) is intended to restore green CI after TEST-002, but the `lint-and-test` check is currently failing at “Run lint checks”. ([GitHub][2])
The diff shows a likely mypy `no-redef` cause in `cli/sum_cli/boilerplate/.../populate_demo_content.py` involving `FakerClass` being defined and then imported into the same name. ([GitHub][3])

## Goal

* Make PR #5 checks pass (at minimum: `lint-and-test` green).
* Ensure the branch ends **clean**: no untracked/unstaged files.

## Plan (short)

1. Patch the Faker optional import pattern so mypy stops erroring.
2. Run the same lint/typecheck commands CI uses.
3. Push a single follow-up commit to the existing branch.
4. Confirm PR checks are green.

## Checklist & Commands

### 1) Precheck

```bash
git checkout test/TEST-003-ci-green
git pull
git status -sb
```

### 2) Fix the mypy `no-redef` pattern

In `cli/sum_cli/boilerplate/project_name/home/management/commands/populate_demo_content.py`, change the approach so we **never import into a name that already exists**.

Use one of these patterns (pick the cleanest given repo conventions):

**Option A (clear + minimal):**

* Import into `_Faker` then assign to `FakerClass` once.

Pseudo-shape:

```python
try:
    from faker import Faker as _Faker
except ImportError:  # pragma: no cover
    _Faker = None

FakerClass: type[Any] | None = _Faker  # (may need a type: ignore[assignment])
```

**Option B (simplest boilerplate, tolerate Any):**

* Avoid the alias + annotation dance entirely; accept a small `type: ignore` in boilerplate if required.

The acceptance criterion is mypy clean, not “perfect typing philosophy”.

### 3) Re-run CI-equivalent locally

Run whatever `make lint` calls (don’t substitute unless you confirm it matches CI):

```bash
make lint
```

Then:

```bash
pytest -q
```

### 4) Commit + push (clean)

```bash
git status -sb
git add -A
git commit -m "test(TEST-04): fix mypy no-redef in CLI boilerplate"
git push
```

## Expected success signals

* PR #5 “Checks” shows `lint-and-test` passing. ([GitHub][2])
* Local `make lint` exits 0.
* Local `pytest -q` exits 0.
* `git status -sb` is clean.

## Stop / rollback triggers

* If making mypy pass requires weakening the overall typecheck scope (e.g., deleting mypy targets or disabling checks globally), stop and split into a separate “CI policy” ticket. This one is a surgical fix.

## Record-keeping

* Only add to `docs/ops-pack/what-broke-last-time.md` if the root cause is **not** already captured in PR #5’s existing entry.

## Notes on task hygiene

* The agent mentioned an untracked `TEST-003.md`. That must not be left behind:

  * All task tickets and any reports associated should be commited with the code. 

**Complexity:** Low → Medium (should be low if it’s only the Faker import fix; medium if mypy surfaces a second issue after that).

When you’ve pushed the follow-up commit, drop the new commit hash + updated Checks link and I’ll greenlight merge + give you the next test-strategy ticket.

[1]: https://github.com/markashton480/sum_platform/pull/5 "Test/test 003 ci green by markashton480 · Pull Request #5 · markashton480/sum_platform · GitHub"
[2]: https://github.com/markashton480/sum_platform/pull/5/checks "Test/test 003 ci green by markashton480 · Pull Request #5 · markashton480/sum_platform · GitHub"
[3]: https://github.com/markashton480/sum_platform/commit/7c7f05dc1d5b9b01e521d42b461345d12fdd57df "test(TEST-03): fix CI lint/typecheck · markashton480/sum_platform@7c7f05d · GitHub"
