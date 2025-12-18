# CM-M6-QA-02 — Restore QA Tooling Contract (Black/Ruff/Mypy) + Makefile Truthfulness

**Status**: Open
**Milestone**: M6
**Category**: QA / Tooling
**Type**: Corrective Mission (Remediation)
**Depends on**: CM-M6-QA-01
**Goal**: Make `make lint` a **truthful gate** again (no false greens)

---

## Assumptions / Inputs needed (only if missing)

- Repo is currently in the state investigated in CM-M6-QA-01 (same `pyproject.toml`, `Makefile`, `core/pyproject.toml`, `cli/pyproject.toml`).
- We accept that fixing Black include will likely surface real formatting drift and require committing mechanical formatting changes.

---

## Plan

1. **Fix Black include regex** so it actually discovers `.py/.pyi` files.
2. **Force Ruff to use the root config** consistently (monorepo config-discovery currently fragments due to sub `pyproject.toml` files).
3. **Make `make lint` truthful**: remove silent pass-throughs and/or gate via an explicit switch (no more “green even when broken”).
4. Keep changes **minimal and auditable**: config + Makefile first, then only the **mechanical** formatting changes required to satisfy the restored contract.

---

## Checklist & Commands

### A) Black: restore file discovery (root cause fix)

**Change**

- In root `pyproject.toml`, fix Black’s `include` value (currently a literal string that matches nothing).

**Recommended setting**

- Use a normal TOML string so the regex becomes `\.pyi?$` (backslash-dot), e.g.

  - `include = "\\.pyi?$"` _(preferred)_

**Commands**

```bash
black --check core cli tests
# if failing (expected), then:
black core cli tests
black --check core cli tests
```

---

### B) Ruff: eliminate monorepo config fragmentation

**Fix options (choose the least invasive that works):**

1. **Makefile enforces root config** (fastest, least repo-structural risk):

- In `Makefile`, change Ruff invocation to:

  - `ruff check . --config pyproject.toml`
  - (and same for any `ruff format` if used)

2. **OR** unify Ruff discovery by updating subproject pyprojects:

- Add Ruff config “extend” in `core/pyproject.toml` and `cli/pyproject.toml` so they inherit root rules, preventing fallback-to-default behaviour. (The investigation indicates sub pyprojects are currently breaking discovery.)

**Commands**

```bash
ruff check . --statistics
ruff check . --verbose 2>&1 | grep "Checking" | head
ruff check core cli tests
```

---

### C) Mypy: remove the “false green” behaviour

**Root cause**

- `Makefile` currently uses `mypy ... || true`, masking ~32 errors and making `make lint` non-gating.

**Required change**

- `make lint` must not silently pass if mypy fails.

**Implementation approach (explicit + controllable)**

- Replace `|| true` with an explicit, documented escape hatch:

  - Default: **fail on mypy errors**
  - Optional: allow temporary non-gating mode only via env var, e.g. `MYPY_SOFT=1 make lint`

**Commands**

```bash
mypy core cli tests --exclude '^clients/'
make lint
# Optional soft mode (if implemented):
MYPY_SOFT=1 make lint
```

---

### D) Makefile contract: make the signal honest

**Update**

- Ensure `make lint` is a reliable gate:

  - Black actually checks files (A)
  - Ruff uses intended rules consistently (B)
  - Mypy failures are not silently ignored (C)

**Commands**

```bash
make lint
make test
```

---

## Expected success signals

- `black --check core cli tests` no longer says “No Python files are present…” and instead checks real files.
- `ruff check .` applies the **same rules** across `core/` + `cli/` (no silent defaulting due to subproject pyprojects).
- `make lint`:

  - **fails** when mypy has errors (or only soft-passes with an explicit `MYPY_SOFT=1` mode if you adopt that model).

- A “green” `make lint` now genuinely means “format + lint + typecheck contract satisfied”.

---

## Stop / rollback triggers

- If fixing Black causes an unexpectedly massive diff that touches non-mechanical code, stop and split into:

  1. “contract restore (config only)”
  2. “mechanical formatting only”

- If Ruff config changes affect behaviour beyond linting (e.g., exclude/include shifts that alter what CI checks), stop and document the discrepancy before proceeding.
- If enforcing mypy blocks progress due to a large backlog, do **not** revert to `|| true`; instead implement the explicit soft-mode switch and open a follow-up CM to burn down mypy debt.

---

## Record-keeping

After completion, update:

- `docs/ops-pack/what-broke-last-time.md`

  - Add: “Black include regex in TOML was literal-broken → formatter was a no-op; Makefile masked mypy; Ruff config discovery fragmented by sub pyprojects.”

- `docs/ops-pack/release-checklist.md`

  - Ensure release gating references a **truthful** `make lint` (and document any intentional soft-mode switch if adopted).

- `docs/ops-pack/smoke-tests.md`

  - Add a quick “QA tooling sanity” check: `black --check ...` must report checking files; `make lint` must fail on mypy unless explicitly soft.

- File a comprehensive work report in `docs/dev/CM/M6/QA/CM-M6-QA-02_followup.md`
