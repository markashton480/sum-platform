# RED FLAGS REPORT - SUM Platform

This report identifies potential bugs, security risks, structural issues, and "gotchas" discovered during a codebase scan. These should be addressed to ensure platform stability, data integrity, and security.

## 1. High Risk & Critical Issues

### 1.1 Duplicate External Side Effects on Retry

**Location:** `core/sum_core/leads/tasks.py` (`send_lead_notification`, `send_lead_webhook`, `send_zapier_webhook`)  
**Risk:** **Duplicate emails/webhooks sent to clients.**  
**Description:** External side effects (sending email, POSTing to webhooks) are performed _inside_ a `transaction.atomic()` block. If the subsequent `lead.save()` fails or the transaction fails to commit (e.g., database timeout, deadlock), the entire transaction rolls back. However, the email/webhook has already been sent. Celery will retry the task, see the status as still "Pending" (due to rollback), and send the external notification **again**.  
**Fix:** Move external requests outside the main transaction or use a "Locked" status update before the request and commit it.

### 1.2 Race Condition in Task Queueing

**Location:** `core/sum_core/forms/views.py` (`_queue_notification_tasks`)  
**Risk:** **Tasks failing because "Lead not found".**  
**Description:** `send_lead_notification.delay(...)` is called immediately after `create_lead_from_submission`. If the view is wrapped in a transaction (standard in many Django setups), the Celery worker might pick up the task and try to fetch the Lead _before_ the database transaction in the view has committed.  
**Fix:** Use `transaction.on_commit(lambda: task.delay(...))` to ensure the record is visible to the worker.

### 1.3 Non-Streaming CSV Export (Memory Risk)

**Location:** `core/sum_core/leads/services.py` (`build_lead_csv`)  
**Risk:** **Server OOM (Out of Memory) crash.**  
**Description:** The CSV export builds a gigantic string in memory using `StringIO`. For a client with 50,000 leads, this could consume hundreds of megabytes of RAM during the request, potentially crashing the worker process.  
**Fix:** Refactor to use a generator and Django's `StreamingHttpResponse`.

## 2. PII & Privacy Risks

### 2.1 Sentry PII Leakage via Tags

**Location:** `core/sum_core/ops/sentry.py` (`_strip_pii`) and usage in `tasks.py`  
**Risk:** **Sensitive data leaking into Sentry logs.**  
**Description:** The custom `_strip_pii` hook only scrubs the `extra` dictionary. However, `set_sentry_context` sets data as **tags**. Tags are not scrubbed by the current logic. Additionally, if PII is included in the exception message or breadcrumbs not explicitly in `extra`, it may leak.  
**Fix:** Update `_strip_pii` to also scrub `tags` and verify breadcrumb scrubbing.

### 2.2 Losing Visitor IP for Leads

**Location:** `core/sum_core/leads/models.py`  
**Risk:** **Inability to audit fraud or block malicious actors.**  
**Description:** `get_client_ip` is implemented in two places but the IP address is never saved to the `Lead` model. This data is critical for identifying bot patterns and providing audit trails for lead submissions.  
**Fix:** Add `ip_address` to the `Lead` model and populate it during submission.

## 3. Structural & Tooling Issues

### 3.1 Brittle Makefile Volume Operations

**Location:** `Makefile` (`db-migrate-volume`)  
**Risk:** **Data loss or "command not found" errors during project setup.**  
**Description:** This target uses hardcoded volume names like `tradesite_sum_db_data`. If the project is renamed or the `COMPOSE_PROJECT_NAME` changes, this command will either fail silently or copy data to/from the wrong place.  
**Fix:** Derive volume names from environment variables or provide them as arguments to the `make` command.

### 3.2 Explicit `update_fields` Risk

**Location:** `core/sum_core/leads/tasks.py`  
**Risk:** **Silent data loss during development.**  
**Description:** Almost all `save()` calls in the task file use explicit `update_fields`. If a developer adds a new field to the `Lead` model (e.g., `assigned_to`) and updates it in a task, it will **not** be saved unless they also remember to update the `update_fields` list in every `save()` call.  
**Fix:** Use a more robust pattern (like a state machine) or remove `update_fields` unless strict performance/concurrency control is required.

### 3.3 Silent Spam Bypass

**Location:** `core/sum_core/forms/services.py` (`check_timing`)  
**Risk:** **Undetected spam bypass.**  
**Description:** The code allows submissions with missing `time_token` to pass as "not spam" to avoid breaking users with JS disabled. A comment says "log in production", but no actual logging is implemented. This means bots can bypass timing checks completely and silently.  
**Fix:** Add `logger.warning` when `time_token` is missing.

## 4. Minor Issues

### 4.1 Missing Field Validation

**Location:** `core/sum_core/branding/models.py` (`SiteSettings.established_year`)  
**Risk:** **Invalid data in frontend.**  
**Description:** No range validation on `established_year`. Users can enter `0`, `-500`, or `9999`, which might break frontend logic or look unprofessional.  
**Fix:** Add `MinValueValidator(1800)` and `MaxValueValidator(2100)`.

---

_Report generated on: 2025-12-22_
