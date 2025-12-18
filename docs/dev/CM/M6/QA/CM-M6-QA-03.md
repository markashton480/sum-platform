# CM-M6-QA-03 — Mypy Debt Triage & Controlled Burn-down

**Status**: Open
**Milestone**: M6
**Category**: QA / Type Safety
**Type**: Corrective Mission (Debt Resolution)
**Depends on**: CM-M6-QA-02

---

## Context

Following CM-M6-QA-02, the QA toolchain is now truthful and gating.
As a result, **32 genuine mypy errors across 18 files** are exposed.

These errors pre-existed but were masked by tooling suppression.

Blindly “fixing until green” risks:

- accidental refactors
- API churn
- behavioural changes disguised as typing fixes

This CM exists to **resolve type debt deliberately and audibly**.

---

## Objective

To **systematically reduce mypy debt** while:

- Preserving runtime behaviour
- Avoiding architectural refactors
- Maintaining a clear audit trail of _why_ each change exists

---

## Scope

### In scope

- The 32 reported mypy errors
- Type annotations, narrowings, casts, protocol definitions
- Localised refactors _only where typing requires it_

### Out of scope

- Business logic changes
- Performance optimisations
- Large-scale API redesigns
- “While I’m here” cleanups

---

## Required Investigation Phase (first)

Before fixing anything, the agent must:

1. Run:

   ```bash
   mypy core cli tests --exclude '^clients/'
   ```

2. Categorise each error into one of:

   - **A**: trivial / mechanical (missing return, obvious annotation)
   - **B**: boundary typing (Django, third-party libs, Any leakage)
   - **C**: architectural ambiguity (unclear contracts)

3. Produce a short table:

   - File
   - Error
   - Category
   - Proposed resolution strategy

No fixes yet.

---

## Remediation Strategy

- **Category A**: Fix immediately (mechanical, safe)
- **Category B**: Fix with explicit casts / protocols / ignores _with justification_
- **Category C**: Do **not** fix blindly — propose:

  - deferral
  - scoped ignore
  - follow-up ADR / CM if structural

---

## Deliverables

1. `CM-M6-QA-03_followup.md` containing:

   - Error categorisation table
   - Fixes applied (or deferred)
   - Remaining debt (if any) with rationale

---

## Success Criteria

- `make lint` passes **without** `MYPY_SOFT`
- Any remaining ignores are:

  - minimal
  - documented
  - intentional

---

## Philosophy (explicit)

Type safety is a **long-term platform asset**, not a checkbox.
This CM exists to pay debt without introducing new risk.

---
