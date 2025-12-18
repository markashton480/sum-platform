# CM-M6-QA-01 — QA Tooling Contract Investigation (Lint / Format / Typecheck)

**Status**: Open
**Milestone**: M6
**Category**: QA / Tooling
**Type**: Investigation (No Fixes)
**Related ADRs**: ADR-002 (Rendering Contract Reset)
**Related Tasks**: M6-002, M6-003, CM-M6-04, CM-M6-05, M6-A-001 → M6-A-003 (maybe more we don't know when the lint/test exclusions took place)

---

## Context

During post–Milestone 6-A QA validation, the following inconsistencies were observed:

1. `make lint` reports **mypy errors**, but does **not fail**
2. `black --check` reports **“No Python files are present”** when run against valid Python source directories (`core`, `cli`, `tests`)
3. `isort` appears to skip large portions of the codebase
4. These conditions exist **despite a large, actively-tested Python codebase**
5. The issues passed unnoticed through Milestone 6-A, indicating a **tooling signal failure**, not a code failure

Given SUM’s emphasis on **traceability, reproducibility, and release safety**, this warrants a **formal investigation before remediation**.

---

## Objective

To **establish a factual, auditable understanding** of the current QA tooling state by answering:

- What exactly is happening?
- Why is it happening?
- When / how did this configuration emerge?
- What contract do the tools _actually_ enforce today?
- Where does behaviour diverge from intent?

⚠️ **This task must not modify repo state**
⚠️ **No fixes, config changes, or refactors permitted**

---

## Scope (Strict)

### In scope

- Black
- Isort
- Ruff
- Mypy
- `make lint` and related Makefile targets
- `pyproject.toml` tool configuration
- Repo directory structure interaction (`core/`, `cli/`, `tests/`, `clients/`)
- Git history relevant to QA/tooling configuration
- CI vs local behaviour (if applicable)

### Out of scope

- Theme rendering
- Test coverage improvements
- Type annotation refactors
- Formatting changes
- Dependency upgrades

---

## Investigation Tasks

### 1. Black behaviour audit

Determine why:

```bash
black --check core cli tests
```

reports:

> “No Python files are present to be formatted”

Required outputs:

- Exact Black config resolution (include/exclude patterns)
- How Black is interpreting file discovery
- Whether `.py` files are being excluded intentionally or accidentally
- When this behaviour was introduced (git history)

---

### 2. Isort behaviour audit

Determine:

- Why isort skips files
- Whether skip behaviour is config-driven or path-driven
- Whether isort’s behaviour matches Black’s file discovery (or diverges)

---

### 3. Mypy contract audit

Determine:

- Why mypy errors do not fail `make lint`
- Whether this is intentional policy or accidental
- Impact of `clients/` directories on module resolution
- Whether current behaviour matches intended QA guarantees

---

### 4. Makefile contract audit

Determine:

- What `make lint` **actually guarantees today**
- Whether it is informational-only or intended as a gate
- Whether naming matches behaviour (potentially misleading)

---

### 5. Historical trace

Identify:

- Commits where QA/tooling config changed
- Whether changes were intentional, incidental, or emergent
- Whether tooling assumptions changed during M6-A work

---

## Deliverables

The investigation **must produce**:

1. `CM-M6-QA-01_followup.md`

   - Clear findings, structured as:

     - **Observed behaviour**
     - **Root causes**
     - **Intent vs reality**
     - **Risk assessment**

   - No proposed fixes yet

2. Optional appendices:

   - Relevant commit SHAs
   - Extracts of `pyproject.toml` with commentary
   - Tool documentation references (if needed)

---

## Success Criteria

This task is **complete** when:

- We can clearly explain **why** Black, Isort, and Mypy behave as observed
- We know whether this state is:

  - intentional
  - accidental
  - legacy drift

- We can decide _with confidence_ what to fix next (in a follow-up CM)

---

## Explicit Non-Goals

- “Make it green”
- “Clean up typing”
- “Fix Black”
- “Just exclude clients and move on”

Those come **after** understanding.

---

### Closing note

This CM exists because **SUM treats QA tooling as part of the platform contract**, not developer convenience. A linter that lies is worse than no linter at all.
