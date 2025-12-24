# THEME-011 — THEME-010 hardening: verify canonical theme paths + prove full-suite pass

## THEME-010 review

### What looks good

The follow-up indicates the ticket’s _core objective_ landed:

- `{% branding_css %}` now emits a **complete set of semantic HSL component variables** (primary + secondary + accent + background + text + surface) and font variables (`--font-heading`, `--font-body`).
- Theme A `tailwind.config.js` now maps Theme A tokens (including `sage.*`) onto those semantic branding variables, using HSL (with fallbacks).
- Theme A `input.css` replaced the known hardcoded hex offenders by referencing Tailwind theme tokens (so compiled CSS inherits the variable-based colors).
- Guardrails/tests were added:

  - `tests/branding/test_branding_css_output.py` verifies variable emission
  - `tests/themes/test_theme_a_contract.py` verifies Tailwind config references branding vars + input.css doesn’t contain prohibited hex values

- Tailwind build and `.build_fingerprint` regeneration happened.

This is the “foundation fix” we wanted: **branding contract now exists in a theme-consumable form** without having to rewrite templates first.

### Red flags / drift risks to address

These are small but important.

1. **Possible regression of the “no legacy theme copy in `core/sum_core/themes/theme_a`” rule**
   In the transcript, the agent _lists_ `core/sum_core/themes/theme_a`.
   If that directory exists in the repo/worktree again, it undermines THEME-008’s work and reintroduces ambiguity. Even if it’s untracked locally, it can confuse devs and (depending on wiring) could affect template resolution.

2. **Evidence gap: “make test passes” isn’t demonstrated in the transcript**
   The work report states `make test` passes.
   But the transcript shows only targeted pytest runs (branding/theme tests + guardrails), not the full suite.
   If it did run and just isn’t captured, fine — but we need the audit trail to show it.

Neither of these is a “panic”. They’re exactly the kind of tiny uncertainty that causes future churn.

---

# Next step: corrective full ticket (so the audit trail stays clean)

### Mission

Close the two remaining risks from THEME-010 by producing an audit-proof follow-up:

1. Prove there is **no legacy Theme A directory** under `core/sum_core/themes/` (or remove it if it exists).
2. Run the full test suite and record the exact command/output evidence in the follow-up report.

### Scope

**In scope**

- Canonical theme location enforcement (filesystem + git)
- Full-suite test evidence
- Zero code refactors beyond what’s required to remove a stray legacy directory or fix a failing test caused by it

**Out of scope**

- No template rewrites
- No branding/tag logic changes (unless a failing test forces a minimal fix)

### Steps

#### 1) Canonical theme location check

From repo root run and include output in report:

- `find themes -maxdepth 2 -type d -name "theme_a" -print`
- `find core/sum_core/themes -maxdepth 2 -type d -print` (if the directory exists)

Hard requirement:

- `themes/theme_a/` must exist
- `core/sum_core/themes/theme_a/` must **not** exist

If `core/sum_core/themes/theme_a/` exists:

- delete it (tracked or untracked) and ensure `git status` is clean/expected afterward.

#### 2) Run the full test suite (non-negotiable)

Run:

- `make test`

Include in report:

- the exact command line used
- final pass/fail summary (copy/paste the end of output)

#### 3) Confirm the branding bridge tests still pass

Run explicitly (belt + braces):

- `pytest -q tests/branding/test_branding_css_output.py tests/themes/test_theme_a_contract.py`

Include output summary.

### Acceptance criteria

- No legacy Theme A directory exists outside `themes/theme_a/`
- `make test` passes, with output evidence captured in `THEME-011_followup.md`
- Branding bridge tests pass

### Deliverables

- `docs/dev/THEME/tasks/THEME-011_followup.md`

---
