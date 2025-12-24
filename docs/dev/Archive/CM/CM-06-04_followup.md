# CM-06-04 Follow-up Report

**Task**: Fix footer effective settings + time-safe copyright caching  
**Branch**: fix/CM-06-04-footer-copyright-effective-settings  
**Date**: 2025-12-23  
**Status**: ✅ Complete

## Summary

Delivered the footer effective settings update and made footer caching time-safe. The effective settings resolver now surfaces `copyright_text`, the footer tag caches only stable data, and `{year}` rendering is computed per request without cache staleness. Added tests to cover the new resolver field, safe placeholder handling, and year updates across cache hits. Documentation now clarifies cached vs rendered footer fields and placeholder behavior.

## Changes

- Added `copyright_text` to `EffectiveFooterSettings` and wired it from `FooterNavigation`.
- Refactored `footer_nav` to cache base context only and render time-dependent copyright after cache retrieval.
- Added safe placeholder handling tests (including unknown placeholders) and cache-hit year rollover coverage.
- Updated navigation tags reference to clarify cached vs rendered behavior.

## Tests

```bash
./.venv/bin/python -m pytest tests/navigation/test_services.py tests/navigation/test_templatetags.py tests/navigation/test_cache.py -q
```

Result: **109 passed** (with existing Django URLField warning about default scheme).

## Risks / Notes

- Low risk: changes are scoped to footer resolver data and tag rendering logic.
- Cached payload now excludes rendered copyright; rendering happens per invocation.

## Evidence (Git)

- `git log -n 5 --oneline`
  - `a526a35 docs: add CM-06-04 follow-up report`
  - `9c55ad3 fix(navigation): [CM-06-04] footer effective settings + time-safe caching`
  - `cc7a5ca docs: new AGENTS.md added`
  - `a529b99 docs: removed AGENTS.md so I can refresh it automatically`
  - `162fabd Merge pull request #54 from markashton480/fix/M6-XXX-nav-active-nplus1`

- Files changed in implementation commit:
  - `core/sum_core/navigation/services.py`
  - `core/sum_core/navigation/templatetags/navigation_tags.py`
  - `docs/dev/navigation-tags-reference.md`
  - `tests/navigation/test_cache.py`
  - `tests/navigation/test_services.py`
  - `tests/navigation/test_templatetags.py`

## Work Report Evidence Checklist

- [x] `git status`
- [x] `git log -n 5 --oneline`
- [x] High-level list of files changed
- [x] Notes on risks/surprises
- [x] Tests run with results
- [x] Follow-up report filed at `docs/dev/CM/CM-06-04_followup.md`

---

# CM-06-04 Follow-up Report (Lead Tasks)

**Task**: Fix lead notification retry bookkeeping + move side-effects out of transactions  
**Branch**: fix/cm-06-04-leads-task-tx-retry  
**Date**: 2025-12-23  
**Status**: ✅ Complete

## Summary

Refactored lead notification tasks to persist attempt/error tracking across retries and moved email/webhook/Zapier side effects outside transactional locks. Added in-progress statuses for email/webhook/Zapier, enforced durable retry bookkeeping, and added tests that assert non-atomic side effects plus retry persistence for email/webhook/Zapier.

## Changes

- Added IN_PROGRESS status for email, webhook, and Zapier integrations.
- Split lead notification tasks into short DB transactions with side effects outside atomic blocks.
- Persisted attempt counters and last_error/status_code updates before retrying.
- Added retry persistence + atomic boundary tests and hardened Zapier site fixture setup.

## Tests

```bash
./.venv/bin/python -m pytest tests/leads/test_notification_tasks.py tests/leads/test_zapier.py
```

Result: **28 passed** (with existing warnings about URLField default scheme and sentry scope deprecation).

## Risks / Notes

- Moderate risk: behavior changes to integration status flow; mitigated by explicit IN_PROGRESS gate and targeted tests.
- No schema migrations needed; choices updated in code only.

## Evidence (Git)

- `git log -n 5 --oneline`
  - `6147c6c fix(leads): [CM-06-04] persist attempts across retries; move side-effects out of transactions`
  - `e2318e9 docs: THEME-028`
  - `b1ea58e docs: THEME-028`
  - `1467a75 Merge pull request #58 from markashton480/chore/THEME-026-codex-preflight`
  - `553ca19 chore(THEME-026): add Codex preflight script + prompt template`

- Files changed:
  - `core/sum_core/leads/models.py`
  - `core/sum_core/leads/tasks.py`
  - `tests/leads/test_notification_tasks.py`
  - `tests/leads/test_zapier.py`
  - `docs/dev/CM/CM-06-04_followup.md`

## Work Report Evidence Checklist

- [x] `git status`
- [x] `git log -n 5 --oneline`
- [x] High-level list of files changed
- [x] Notes on risks/surprises
- [x] Tests run with results
- [x] Follow-up report filed at `docs/dev/CM/CM-06-04_followup.md`
