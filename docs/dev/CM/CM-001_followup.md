# CM-001 Followup Report: Production Hardening Sweep

**Date:** 2025-12-15
**Status:** Complete
**Task Reference:** [CM-001.md](CM-001.md)

---

## Summary

All BLOCKER and HIGH priority issues from the 2025-12-14 code review have been addressed. This corrective mission eliminated XSS/CSP security risks, strengthened server-side validation, made async tasks concurrency-safe, reduced navigation cache staleness, and documented SEO app registration requirements.

---

## Changes Made

### A) Forms: Removed Inline JS Template Interpolation (BLOCKER)

**Files modified:**
- `core/sum_core/templates/sum_core/blocks/contact_form.html`
- `core/sum_core/templates/sum_core/blocks/quote_request_form.html`

**Problem:** Template variables were embedded directly inside JavaScript string literals (`innerHTML = '{{ template_var }}'`), creating XSS vectors and potential CSP conflicts.

**Solution:**
- Added `data-success-message` and `data-error-message` attributes to form elements containing escaped template content
- Rewrote JavaScript to use `document.createElement()` and `textContent` instead of `innerHTML` with string concatenation
- Success/error messages now safely read from `form.dataset.successMessage`

**Security benefit:** Eliminates XSS injection vectors and ensures CSP compatibility.

---

### B) Forms: Added Server-Side Email Validation (BLOCKER)

**File modified:** `core/sum_core/forms/views.py`

**Problem:** Only presence check was performed on email field; invalid formats (e.g., "not-an-email") would be accepted.

**Solution:**
- Added Django's `validate_email` validator to `_validate_submission()`
- Invalid email formats now return 400 with "Please enter a valid email address"
- Validation occurs after presence check, so empty emails get "Email is required"

**Tests added:**
- `test_invalid_email_format_rejected`
- `test_invalid_email_missing_domain_rejected`

---

### C) Forms: Added Server-Side Phone Validation (HIGH)

**File modified:** `core/sum_core/forms/views.py`

**Problem:** Phone field was optional but accepted any input without validation.

**Solution:**
- Added UK phone number regex validation supporting:
  - UK mobile: `07xxx xxx xxx`, `+447xxx xxx xxx`
  - UK landline: `01234 567890`, `020 7946 0958`, `+44 1234 567890`
- Phone remains optional (empty is valid)
- Invalid formats return 400 with "Please enter a valid UK phone number"

**Tests added:**
- `test_malformed_phone_rejected`
- `test_valid_uk_mobile_phone_accepted`
- `test_valid_uk_landline_accepted`
- `test_international_format_uk_phone_accepted`
- `test_empty_phone_is_optional`

---

### D) Lead Notification Tasks: Concurrency-Safe Idempotency (HIGH)

**File modified:** `core/sum_core/leads/tasks.py`

**Problem:** Idempotency check (`if lead.email_status == EmailStatus.SENT`) was not atomic. Two concurrent task instances could both see `PENDING` and both attempt to send.

**Solution:**
- Wrapped both `send_lead_notification()` and `send_lead_webhook()` in `transaction.atomic()`
- Added `select_for_update(nowait=False)` to acquire a row-level lock before checking status
- Status transitions now happen within the same transaction as the lock
- Concurrent tasks will block until the first completes, then see `SENT` and skip

**Tests added:**
- `test_duplicate_email_tasks_only_send_once` (simulates double-run scenario)
- `test_duplicate_webhook_tasks_only_send_once`

---

### E) Navigation Caching: Reduced Default TTL (HIGH)

**File modified:** `core/sum_core/navigation/templatetags/navigation_tags.py`

**Problem:** Navigation cache TTL was hardcoded to 3600 seconds (1 hour), causing a poor UX when editors made changes that wouldn't appear for up to an hour.

**Solution:**
- Changed `CACHE_TTL_DEFAULT` from `3600` to `300` (5 minutes)
- Settings override via `NAV_CACHE_TTL` still works for sites that want different values

---

### F) sum_core.seo App Registration Audit

**File modified:** `core/sum_core/apps.py`

**Status:** Already registered in test project settings (confirmed at line 84).

**Solution:**
- Added comprehensive docstring to `apps.py` documenting all required `INSTALLED_APPS` entries
- Explicitly notes that `sum_core.seo` MUST be included for SEO template tags to work
- References `test_project/test_project/settings.py` as the canonical configuration example

This ensures client projects following the documented setup will include all necessary apps.

---

## Test Results

```
$ make test
565 passed, 11 warnings in 135.99s (0:02:15)
```

All existing tests continue to pass. New tests specifically cover:
- Email format validation rejection
- Phone format validation rejection
- Concurrent task idempotency (email + webhook)

---

## Lint Results

```
$ make lint
ruff check . -> All checks passed!
black --check . -> Nothing to do
isort --check-only --diff . -> Skipped 36 files (no changes needed)
mypy . -> Pre-existing type annotation warnings (allowed to fail via `|| true`)
```

---

## Acceptance Criteria Status

| Criterion | Status |
|-----------|--------|
| No template variables embedded inside JS string literals in form templates | DONE |
| Success/error messaging via data attributes or hidden DOM templates | DONE |
| Invalid email formats rejected server-side, no Lead created | DONE |
| Invalid phone formats (if provided) rejected server-side | DONE |
| Email + webhook tasks cannot double-send under concurrent execution | DONE |
| Tests cover concurrency/idempotency scenario | DONE |
| Default nav cache TTL is 300 seconds | DONE |
| `sum_core.seo` documented as required in INSTALLED_APPS | DONE |
| `make test` passes | DONE |
| `make lint` passes | DONE |

---

## Files Changed Summary

| File | Change Type |
|------|-------------|
| `core/sum_core/templates/sum_core/blocks/contact_form.html` | Modified (XSS fix) |
| `core/sum_core/templates/sum_core/blocks/quote_request_form.html` | Modified (XSS fix) |
| `core/sum_core/forms/views.py` | Modified (email + phone validation) |
| `core/sum_core/leads/tasks.py` | Modified (concurrency safety) |
| `core/sum_core/navigation/templatetags/navigation_tags.py` | Modified (TTL reduction) |
| `core/sum_core/apps.py` | Modified (documentation) |
| `tests/forms/test_form_submission.py` | Modified (added validation tests) |
| `tests/leads/test_notification_tasks.py` | Modified (added concurrency tests) |
