# CM-M6-QA-07 Follow-up Report

**Task:** CI Gate Proof + Evidence Completion + Cleanup  
**Status:** ⏳ In progress (requires GitHub UI actions)  
**Date:** 2025-12-18

---

## Objective

1. Prove branch protection genuinely blocks merges when the required `lint-and-test` check is failing/missing.
2. Capture evidence URLs (PR + CI run) for both the failing and passing states.
3. Backfill missing evidence in CM-M6-QA-06 follow-up.

---

## Local Changes Prepared in This Branch

- Adds this report file.
- Adds the task ticket file: `docs/dev/CM/M6/QA/CM-M6-QA-07.md`.
- Updates CM-M6-QA-06 follow-up to include missing evidence placeholders.
- Introduces an intentional, reversible CI failure in `.github/workflows/ci.yml` (workflow remains valid; the job deterministically fails).

---

## Evidence (Fill In After PR Is Open)

| Item | URL |
| --- | --- |
| PR URL | _[paste PR URL]_ |
| Failing CI run URL (lint-and-test) | _[paste failing run URL]_ |
| Passing CI run URL (lint-and-test) | _[paste passing run URL]_ |
| Screenshot: merge blocked (optional) | _[paste link]_ |
| Screenshot: merge enabled (optional) | _[paste link]_ |

---

## Gate Proof Narrative (Fill In)

### A) Failing state

- What was intentionally broken:
  - _[e.g. “lint-and-test job forced to fail”]_ 
- Observed outcome:
  - _[merge button blocked / required check failed or missing]_ 

### B) Recovery state

- What was restored:
  - _[e.g. “CI failure removed; workflow restored”]_ 
- Observed outcome:
  - _[lint-and-test green; merge becomes available only after checks + up-to-date + conversations resolved]_ 

---

## Checklist

- [ ] Push branch `cm/CM-M6-QA-07-ci-gate-proof`
- [ ] Open PR targeting `main`
- [ ] Verify merge is blocked while CI fails
- [ ] Capture failing PR + CI run evidence
- [ ] Restore workflow (remove intentional failure), push fix
- [ ] Verify merge becomes allowed only after green + up-to-date + conversations resolved
- [ ] Capture passing CI run evidence
- [ ] Backfill CM-M6-QA-06 evidence URLs
- [ ] Merge PR
- [ ] Delete branch in GitHub
