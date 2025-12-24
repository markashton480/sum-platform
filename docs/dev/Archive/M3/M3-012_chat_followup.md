# M3-012 Investigation Report (follow-up)

Context: Manual testing still reported (a) missing **“Leads”** in Wagtail admin sidebar, and (b) frontend form submissions failing. Prior agent work is preserved in `docs/dev/M3/M3-012_chat.md`.

## Findings (root causes)

### 1) “Leads” missing from Wagtail admin sidebar

`LeadViewSet` was registered, but Wagtail’s `ModelViewSet` defaults to **not** appearing in the sidebar unless `add_to_admin_menu = True`.

- Wagtail 7 `ModelViewSet.add_to_admin_menu` default is `False`.
- Our `LeadViewSet` did not set `add_to_admin_menu`, so `/admin/leads/` existed, but the sidebar item did not render.

Fix: `core/sum_core/leads/wagtail_admin.py` now sets `LeadViewSet.add_to_admin_menu = True`.

### 2) Frontend form submission failures

The submit endpoint (`/forms/submit/`) is used via `fetch(...)` in:

- `core/sum_core/templates/sum_core/blocks/contact_form.html`
- `core/sum_core/templates/sum_core/blocks/quote_request_form.html`

There were two significant issues:

1) The endpoint was decorated with `csrf_exempt`, which is not aligned with the task spec (and makes cross-site spam significantly easier).  
2) When spam protection rejects a request (especially the timing check), the backend returned a generic `"Invalid submission"` message, which makes manual diagnosis hard and looks like “the form is broken”.

Fixes:

- Enabled CSRF protection on `FormSubmissionView` by switching to `@csrf_protect`.
- Updated both form block JS implementations to explicitly send cookies and pass the CSRF token header (`credentials: 'same-origin'`, `X-CSRFToken`).
- Improved the spam rejection message for XHR requests for the two most common human-visible cases:
  - “Submitted too quickly …” → “Please wait a moment and try again.”
  - “Time token expired” → “Please refresh the page and try again.”

### 3) Site resolution edge case

Wagtail’s `Site.find_for_request()` can return `None` if:

- no `Site` is marked as default, and
- the request host doesn’t match any `Site.hostname`.

This can happen in dev after manual edits in Settings → Sites. If that occurs, the submission endpoint previously returned `400 {"Site not found"}`.

Fix: `FormSubmissionView._get_site()` now falls back to `Site.objects.first()` if `find_for_request()` returns `None`.

## Code changes made

- `core/sum_core/leads/wagtail_admin.py`: set `LeadViewSet.add_to_admin_menu = True` so “Leads” appears in the sidebar.
- `core/sum_core/forms/views.py`: enable CSRF protection, make spam errors more user-friendly for XHR, and add a Site fallback.
- `core/sum_core/templates/sum_core/blocks/contact_form.html`: include CSRF header + credentials in `fetch`.
- `core/sum_core/templates/sum_core/blocks/quote_request_form.html`: include CSRF header + credentials in `fetch`.
- `tests/forms/test_form_submission.py`: add regression coverage for CSRF enforcement and for the “no default site” fallback path.

## Verification

Ran:

- `pytest tests/forms/test_form_submission.py tests/leads/test_lead_admin_wagtail.py` (with Postgres env vars blanked to force sqlite) → **pass**

## Remaining notes / what to check manually

- If submissions still fail, inspect the network response from `/forms/submit/`:
  - `403` indicates CSRF problems (cookies not being sent, or CSRF token missing/mismatched).
  - `400 {"Invalid submission"}` indicates spam checks (honeypot / timing / token expiry).
  - `429` indicates rate limiting.
- Timing check defaults to `min_seconds_to_submit=3`. Very fast submissions (e.g., aggressive autofill + immediate submit) can still be rejected, but the XHR error message is now explicit for that case.

