# M3-011 Checkpoint Report (Milestone 3)

Date: 2025-12-14

## Scope

Checkpoint review for Milestone 3 Lead flow + Wagtail Leads admin UX, focusing on:

- “No lost leads” invariant (persist first; side-effects never lose data)
- Notification task failure modes (email + webhook + broker/queueing failure)
- Wagtail Leads admin permissions + CSV export stability
- Green quality gates + ≥80% coverage

## Quality Gates

- `source .venv/bin/activate && make lint`: ✅ Pass  
  - Note: `mypy` emits errors but is non-blocking in the `Makefile` (`mypy . || true`).
- `source .venv/bin/activate && make test`: ✅ Pass (`524 passed`)  
  - Coverage: ✅ `89%` total (pytest-cov output).
- `source .venv/bin/activate && python core/sum_core/test_project/manage.py makemigrations --check --dry-run`: ✅ Pass  
  - Output included warning: `templates.W003` about duplicate `navigation_tags` modules, but “No changes detected”.

## Regression Sweep: P0 “No Lost Leads”

### Happy path coverage

- Form submission endpoint persists a `Lead` and returns success (`tests/leads/test_lead_submission_handler.py`).
- Attribution derivation + field persistence covered (`tests/leads/test_attribution.py`, `tests/leads/test_lead_model.py`).

### Failure-mode coverage (Lead persists; statuses updated)

- Broker/queueing failures during submission:
  - Email queueing failure updates `email_status/email_last_error` and preserves Lead
  - Webhook queueing failure updates `webhook_status/webhook_last_error` and preserves Lead  
  (`tests/leads/test_notification_failure_modes.py`)
- Execution-time failures in tasks (no reliance on Celery retry semantics in eager mode):
  - Email send exceptions update attempts and ultimately mark `EmailStatus.FAILED`
  - Webhook 5xx / timeout updates attempts and ultimately marks `WebhookStatus.FAILED`  
  (`tests/leads/test_notification_tasks.py`)

## Wagtail Leads Admin: Stability + Permissions + CSV Export

Key outcomes:

- Admin access + permissions are now model-app-label correct (`sum_core_leads.*`).
- Editor role is treated as view-only (list + inspect); cannot change status; cannot export CSV.
- Export endpoint no longer crashes and now matches list view state:
  - CSV export uses Wagtail’s IndexView queryset pipeline (ordering → filters → search) so filters like `?status=new` apply.  
  - Added regression test: `test_export_respects_status_filter`.

Related tests: `tests/leads/test_lead_admin_wagtail.py`

## Manual Smoke Test

Not executed in this checkpoint (requires interactive run):

1. Create a page with a Contact/Quote form in the test project.
2. Submit a Lead and confirm success response.
3. Confirm Lead appears under Wagtail admin “Leads” with attribution + integration statuses.
4. Confirm CSV export downloads correctly for an admin user.

## Notes / Follow-ups

- `templates.W003` warning: duplicate `navigation_tags` template tag module name under both `sum_core.navigation.templatetags` and `sum_core.templatetags` (non-blocking; consider consolidating naming to avoid ambiguity).
- Ruff warns about deprecated top-level config keys in `pyproject.toml` (non-blocking; housekeeping).

