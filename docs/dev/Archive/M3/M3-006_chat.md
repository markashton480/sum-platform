**[M3-006] Implementation Notes (Codex Chat Log Summary)**

This document records what was implemented for M3-006 (“Lead model + form submission persistence (no lost leads)”) and how it was verified.

---

## Scope Implemented

### Lead persistence model (canonical)

Implemented a new `Lead` model within `sum_core` with the minimum required fields for M3-006:

- Core contact fields: `name`, `email`, `phone` (optional), `message`
- Form metadata: `form_type`, `form_data` (JSON)
- Page association: `source_page` FK to Wagtail `Page` (nullable, `SET_NULL`)
- Timestamps: `submitted_at` (auto timestamp)
- Workflow: `status` (default `"new"` with explicit choices)
- Soft delete: `is_archived` (default `False`)

Deliberately deferred (per task spec): attribution fields (UTM/referrer/etc.), source derivation rules, integrations/celery status fields.

---

## Files Added / Updated

### New app package (leads)

- `core/sum_core/leads/apps.py`
  - Adds `LeadsConfig` (`label="sum_core_leads"`) following the pattern used by other `sum_core.*` sub-apps.
- `core/sum_core/leads/models.py`
  - Implements `Lead` model and `Lead.Status` (`TextChoices`) for explicit workflow status values.
- `core/sum_core/leads/services.py`
  - Adds a small service function to create and persist a Lead before any downstream side-effects.
- `core/sum_core/leads/admin.py`
  - Registers `Lead` in Django admin for minimum viable visibility (list + detail, with pretty JSON display).
- `core/sum_core/leads/migrations/__init__.py`
- `core/sum_core/leads/migrations/0001_initial.py`
  - Creates the `Lead` model table.
- `core/sum_core/leads/__init__.py`
  - Sets `default_app_config` for compatibility with existing project patterns.

### Test project registration

- `core/sum_core/test_project/test_project/settings.py`
  - Adds `"sum_core.leads"` to `INSTALLED_APPS` so migrations/tests load consistently.

### Tests

- `tests/leads/__init__.py`
- `tests/leads/test_lead_model.py`
  - Verifies defaults (`status="new"`, `is_archived=False`, `submitted_at` set) and JSON persistence for `form_data`.
- `tests/leads/test_lead_submission_handler.py`
  - Verifies “submission → Lead created” and the “no lost leads” invariant using a simulated downstream exception.

### Additional migration created to satisfy “no pending migrations”

While validating `makemigrations --check --dry-run`, Django detected pending changes in the existing navigation models.

- `core/sum_core/navigation/migrations/0002_alter_footernavigation_social_facebook_and_more.py`
  - Captures updates to help_text / StreamField block schema for `sum_core.navigation` that were previously not migrated in the repo state.
  - This is not directly part of M3-006 feature logic, but it is required to meet the explicit acceptance criterion: “makemigrations --check --dry-run shows no pending changes”.

---

## Lead Model Details

### Model: `sum_core.leads.models.Lead`

- `status` choices:
  - `new`, `contacted`, `quoted`, `won`, `lost`
- Default ordering:
  - `["-submitted_at"]` (newest first)
- `source_page`:
  - `ForeignKey(Page, null=True, blank=True, on_delete=SET_NULL, related_name="leads")`

Migration file: `core/sum_core/leads/migrations/0001_initial.py`

---

## “No Lost Leads” Submission Service

### Service: `sum_core.leads.services.create_lead_from_submission`

Key behaviour aligned to SSOT step “Create Lead record (ALWAYS succeeds)”:

1. Validates required inputs (`name`, `email`, `message`, `form_type`) are non-empty after trimming.
2. Persists a `Lead` record immediately via `Lead.objects.create(...)`.
3. Executes an optional `post_create_hook(lead)` only after the Lead is committed.
4. If `post_create_hook` raises an exception, the exception is propagated, but the Lead record remains persisted (no rollback because the hook is not inside an atomic transaction that would include the create).

The current implementation is intentionally service-level (not wired to an HTTP endpoint yet). This keeps M3-006 focused on persistence and provides an integration point for form blocks in later milestones.

---

## Admin Visibility (Minimum Viable)

### Django admin registration: `sum_core.leads.admin.LeadAdmin`

- `list_display` includes:
  - `submitted_at`, `name`, `email`, `form_type`, `source_page`, `status`, `is_archived`
- `readonly_fields` prevents accidental edits of immutable / raw submission data:
  - At minimum: `submitted_at` plus submitted contact + form fields
- JSON is rendered as a readable `<pre>` block:
  - `formatted_form_data` renders pretty-printed `form_data`

Note: The SSOT mentions Wagtail ModelAdmin; for M3-006 a Django admin view was added to satisfy “minimum viable admin visibility” quickly. If the project standardizes on Wagtail’s admin UI for non-Page models, this can be migrated to a Wagtail viewset / modeladmin in a follow-up task.

---

## Validation Performed

### Tests

Ran:

- `venv/bin/python -m pytest tests/leads`
- `venv/bin/python -m pytest` (full suite)

Notes:

- The repository’s `venv/bin/pytest` script had an invalid shebang (pointing to a different workspace path), so `python -m pytest` was used to ensure the correct interpreter.
- Django warnings observed during test runs were unrelated to this task’s logic (e.g., URLField scheme warning in Django 5.2 / upcoming Django 6.0 default changes).

### Migrations

Confirmed clean state:

- `PYTHONPATH=core ... venv/bin/python core/sum_core/test_project/manage.py makemigrations --check --dry-run`
  - Required blanking out any partial Postgres env vars in this environment (otherwise Django attempts to configure Postgres without `psycopg` installed).

Recommended command (works in environments where `DJANGO_DB_*` variables may be set):

```bash
PYTHONPATH=core \
DJANGO_DB_HOST= DJANGO_DB_NAME= DJANGO_DB_USER= DJANGO_DB_PASSWORD= DJANGO_DB_PORT= \
venv/bin/python core/sum_core/test_project/manage.py makemigrations --check --dry-run
```

---

## Known Follow-ups / Next Integrations

- Wire `ContactFormBlock` / `QuoteRequestFormBlock` submissions to `create_lead_from_submission(...)` in the actual form-handling flow (views/endpoints) once the form backend is introduced.
- If Wagtail-native admin is preferred for Leads, implement Wagtail viewset/modeladmin for the `Lead` model (keeping the same list/detail requirements).
- Consider adding spam/rate-limit layers from SSOT (honeypot + rate-limit) when a real submission endpoint is created; M3-006 intentionally focuses on persistence.

