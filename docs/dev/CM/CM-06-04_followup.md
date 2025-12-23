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
  - `9c55ad3 fix(navigation): [CM-06-04] footer effective settings + time-safe caching`
  - `cc7a5ca docs: new AGENTS.md added`
  - `a529b99 docs: removed AGENTS.md so I can refresh it automatically`
  - `162fabd Merge pull request #54 from markashton480/fix/M6-XXX-nav-active-nplus1`
  - `db260d3 Merge pull request #53 from markashton480/fix/issue-30-atomic-rate-limit`

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
