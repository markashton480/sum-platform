# CM-004 Follow-up: Task Correlation ID Propagation Fix

**Date:** 2025-12-15
**Task:** CM-004 - Fix Task Correlation ID Propagation Failures
**Status:** ✅ Completed
**Engineer:** Claude Sonnet 4.5

---

## Executive Summary

Successfully resolved all 3 failing correlation-id tests in `tests/leads/test_task_correlation.py` by fixing a test configuration issue. The underlying implementation was **already correct** — `request_id` was being properly propagated into tasks and included in structured logs. The tests were failing due to a logging propagation misconfiguration that prevented pytest's `caplog` fixture from capturing log records.

**Key Insight:** This was a test infrastructure issue, not an implementation bug. The production correlation ID propagation was working correctly all along.

---

## Problem Analysis

### Failing Tests
Three tests were failing:
1. `test_send_lead_notification_logs_request_id`
2. `test_send_lead_webhook_includes_request_id`
3. `test_send_zapier_webhook_includes_request_id`

### Root Cause

The tests were checking for `request_id` attributes on captured log records:
```python
assert any(
    str(getattr(r, "request_id", "")) == "test-correlation-123"
    for r in caplog.records
)
```

However, `caplog.records` was **empty** despite logs being emitted. The issue was in the logging configuration hierarchy:

1. **Logging Config** ([logging.py:160-164](../core/sum_core/ops/logging.py#L160-L164)):
   ```python
   "sum_core": {
       "handlers": ["console"],
       "level": log_level,
       "propagate": False,  # ← Prevented propagation to root
   }
   ```

2. **Test Setup** ([test_task_correlation.py:34-36](../tests/leads/test_task_correlation.py#L34-L36)):
   ```python
   logger = logging.getLogger("sum_core.leads.tasks")
   old_propagate = logger.propagate
   logger.propagate = True  # Only set on child logger
   ```

3. **Propagation Chain:**
   - `sum_core.leads.tasks` (propagate=True) → `sum_core` (propagate=False) → ❌ root logger
   - Logs were handled by `sum_core` logger's console handler but never reached root
   - `caplog` relies on propagation to root logger to capture records

### Verification

Created debug script that confirmed:
- Log records **were** being created with correct `request_id` attribute
- Console handler **was** formatting logs correctly (visible in output)
- `caplog` **was not** capturing records due to propagation barrier

---

## Solution Implemented

### Change Summary

Modified three test methods to enable propagation on **both** the child logger and parent `sum_core` logger:

**File:** `tests/leads/test_task_correlation.py`

**Before:**
```python
logger = logging.getLogger("sum_core.leads.tasks")
old_propagate = logger.propagate
logger.propagate = True

try:
    # test code
finally:
    logger.propagate = old_propagate
```

**After:**
```python
logger = logging.getLogger("sum_core.leads.tasks")
old_propagate = logger.propagate
logger.propagate = True

# Also enable propagation on parent logger so caplog can capture
parent_logger = logging.getLogger("sum_core")
old_parent_propagate = parent_logger.propagate
parent_logger.propagate = True

try:
    # test code
finally:
    logger.propagate = old_propagate
    parent_logger.propagate = old_parent_propagate
```

### Files Modified

1. **tests/leads/test_task_correlation.py**
   - `test_send_lead_notification_logs_request_id` (lines 38-45, 54-55)
   - `test_send_lead_webhook_includes_request_id` (lines 102-109, 114-115)
   - `test_send_zapier_webhook_includes_request_id` (lines 143-150, 158-159)

### Files Reviewed (No Changes Required)

The following files were examined and confirmed to be working correctly:

1. **core/sum_core/leads/tasks.py**
   - ✅ All three tasks accept `request_id: str | None = None` parameter
   - ✅ All tasks call `set_sentry_context(request_id=request_id, ...)`
   - ✅ All log statements include `request_id` in `extra` dict
   - ✅ Pattern: `extra={"...", "request_id": request_id or "-"}`

2. **core/sum_core/ops/logging.py**
   - ✅ `RequestIdFilter` correctly adds `request_id` to LogRecords
   - ✅ Filter preserves existing `request_id` from `extra` dict
   - ✅ JSON and verbose formatters both handle `request_id`

3. **core/sum_core/ops/sentry.py**
   - ✅ `set_sentry_context()` properly scopes request_id for error tracking

---

## Implementation Details

### Request ID Flow (Already Correct)

```
HTTP Request
    ↓
[CorrelationIdMiddleware generates request_id]
    ↓
[Request context: get_request_id() returns UUID]
    ↓
[View/Form handler triggers task]
    ↓
task.delay(lead_id=X, request_id=request_id)  ← Explicit kwarg
    ↓
[Task execution]
    ↓
├─ set_sentry_context(request_id=request_id)  ← Error tracking
├─ logger.info("...", extra={"request_id": request_id})  ← Structured logs
└─ requests.post(..., headers={"X-Request-ID": request_id})  ← Webhooks
```

### Logging Flow (Now Fixed in Tests)

```
Task executes
    ↓
logger.info("message", extra={"request_id": "abc-123"})
    ↓
[LogRecord created with request_id attribute]
    ↓
[RequestIdFilter.filter() preserves existing request_id]
    ↓
[Handler formats and emits log]
    ↓
[Log propagates: sum_core.leads.tasks → sum_core → root]  ← Fixed
    ↓
[caplog captures record]  ← Now works
```

---

## Testing

### Test Execution Results

**Before Fix:**
```bash
$ make test
FAILED tests/leads/test_task_correlation.py::...::test_send_lead_notification_logs_request_id
FAILED tests/leads/test_task_correlation.py::...::test_send_lead_webhook_includes_request_id
FAILED tests/leads/test_task_correlation.py::...::test_send_zapier_webhook_includes_request_id
```

**After Fix:**
```bash
$ make test
tests/leads/test_task_correlation.py::TestTaskCorrelation::test_send_lead_notification_logs_request_id PASSED
tests/leads/test_task_correlation.py::TestTaskCorrelation::test_send_lead_webhook_includes_request_id PASSED
tests/leads/test_task_correlation.py::TestTaskCorrelation::test_send_zapier_webhook_includes_request_id PASSED

======================= 647 passed, 11 warnings in 38.91s =======================
```

### Acceptance Criteria

- [✅] `tests/leads/test_task_correlation.py` passes fully (all 5 tests)
- [✅] `make test` passes (647/647 tests passing)
- [✅] `make lint` passes (ruff, black, isort all clean)
- [✅] `request_id` propagated correctly in:
  - [✅] Email task logs
  - [✅] Lead webhook logs
  - [✅] Zapier webhook logs
- [✅] No degradation in reliability/idempotency behavior
- [✅] Comprehensive work report provided

---

## Production Impact Assessment

### ✅ No Production Changes Required

**Critical Finding:** The production code was already correct. This fix only modified test infrastructure.

### Existing Behavior (Confirmed Working)

1. **Request Correlation**
   - `CorrelationIdMiddleware` generates unique `request_id` per HTTP request
   - `request_id` is stored in context via `contextvars`
   - Available throughout request lifecycle

2. **Task Propagation**
   - All three async tasks accept `request_id` parameter
   - Tasks are called with explicit `request_id` from request context
   - Example: `send_lead_notification.delay(lead.id, request_id=request_id)`

3. **Observability**
   - **Logs:** `request_id` included in all task log entries via `extra` dict
   - **Sentry:** `request_id` scoped to error events via `set_sentry_context()`
   - **Webhooks:** `request_id` can be included in headers (implementation dependent)

4. **Default Handling**
   - When `request_id=None` (e.g., admin-triggered task), logs use `"-"`
   - Tasks execute normally without request context

---

## Technical Notes

### Why the Original Tests Were Written This Way

The test comment "Force propagation to capture logs since strict config disables it" indicates the test author was aware of the propagation issue but only addressed it partially by enabling propagation on the child logger.

### Why This Wasn't Caught Earlier

1. **Silent Failure:** Tests expected records but got empty list — no exception
2. **Logging to Console:** Logs were visible in test output, suggesting tests worked
3. **Propagation Complexity:** Nested logger hierarchy requires understanding parent/child relationships

### Lessons for Future Tests

When testing logging with `caplog` in projects using custom logging configurations:

```python
# ❌ Insufficient
logger = logging.getLogger("some.child.logger")
logger.propagate = True

# ✅ Correct
child_logger = logging.getLogger("some.child.logger")
parent_logger = logging.getLogger("some")  # Get parent explicitly
child_logger.propagate = True
parent_logger.propagate = True
```

Or better yet, use `caplog.set_level()` with the full logger name:
```python
caplog.set_level(logging.INFO, logger="sum_core")
```

---

## Guardrails Verification

### ✅ All Guardrails Respected

- ✅ Did not delete, skip, xfail, or loosen tests
- ✅ Did not log PII (no changes to logging content)
- ✅ Reused existing structured logging patterns (no changes needed)
- ✅ Maintained idempotency locking pattern (no changes needed)
- ✅ No changes to production code paths
- ✅ No changes to task signatures or behavior

---

## Code References

### Key Files

1. **Tests Fixed:**
   - [tests/leads/test_task_correlation.py](../tests/leads/test_task_correlation.py)

2. **Production Code (Verified Correct):**
   - [core/sum_core/leads/tasks.py](../core/sum_core/leads/tasks.py) - Task implementations
   - [core/sum_core/ops/logging.py](../core/sum_core/ops/logging.py) - Logging configuration
   - [core/sum_core/ops/middleware.py](../core/sum_core/ops/middleware.py) - Request ID generation
   - [core/sum_core/ops/sentry.py](../core/sum_core/ops/sentry.py) - Error tracking context

### Specific Line References

**Task Signatures:**
- Email task: [tasks.py:103-104](../core/sum_core/leads/tasks.py#L103-L104)
- Webhook task: [tasks.py:299](../core/sum_core/leads/tasks.py#L299)
- Zapier task: [tasks.py:494-495](../core/sum_core/leads/tasks.py#L494-L495)

**Sentry Context:**
- Email: [tasks.py:123-128](../core/sum_core/leads/tasks.py#L123-L128)
- Webhook: [tasks.py:316](../core/sum_core/leads/tasks.py#L316)
- Zapier: [tasks.py:516-522](../core/sum_core/leads/tasks.py#L516-L522)

**Example Log Calls:**
- Email: [tasks.py:160-163](../core/sum_core/leads/tasks.py#L160-L163)
- Webhook: [tasks.py:343-345](../core/sum_core/leads/tasks.py#L343-L345)
- Zapier: [tasks.py:585-595](../core/sum_core/leads/tasks.py#L585-L595)

---

## Recommendations

### 1. Consider Updating Test Utilities

Create a test helper function to handle logging propagation setup:

```python
# tests/conftest.py
@contextmanager
def enable_logging_propagation(*logger_names):
    """Enable propagation on logger hierarchy for caplog compatibility."""
    loggers = [logging.getLogger(name) for name in logger_names]
    old_propagate = [logger.propagate for logger in loggers]

    for logger in loggers:
        logger.propagate = True

    try:
        yield
    finally:
        for logger, old_value in zip(loggers, old_propagate):
            logger.propagate = old_value
```

Usage:
```python
with enable_logging_propagation("sum_core.leads.tasks", "sum_core"):
    # test code
```

### 2. Document Logging Testing Patterns

Add to developer documentation or TESTING.md:
- Explain the `propagate=False` configuration and why it exists
- Provide pattern for testing with `caplog`
- Link to this follow-up report as reference

### 3. No Production Changes Needed

The correlation ID propagation is working as designed. No further implementation work required.

---

## Conclusion

This task successfully **validated** that SUM Core's observability baseline is genuinely consumable and working correctly. The failing tests were due to test infrastructure configuration, not implementation bugs.

The fix was minimal (3 test methods, ~10 lines total) and surgical. All acceptance criteria met with zero production impact and zero risk.

**Milestone 4 Observability Status:** ✅ **COMPLETE**
- Request correlation IDs flow correctly from requests → tasks
- Structured logging includes correlation context
- Sentry error tracking includes correlation context
- All tests passing
- No pre-existing red tests remaining

---

## Appendix: Debugging Process

For future reference, the debugging approach that identified the root cause:

1. **Initial Hypothesis:** `request_id` not being added to LogRecords
   - ✅ Disproved by examining code — all tasks use `extra={"request_id": ...}`

2. **Second Hypothesis:** `RequestIdFilter` overwriting task-provided `request_id`
   - ✅ Disproved by code inspection — filter checks `if not hasattr(record, "request_id")`

3. **Third Hypothesis:** `caplog` not capturing logs
   - ✅ **Confirmed** by creating debug test that:
     - Added custom handler directly to logger
     - Captured logs successfully
     - Demonstrated `caplog.records` was empty
     - Identified propagation barrier

4. **Solution Validation:**
   - Enabled parent logger propagation
   - Debug test passed
   - Applied fix to failing tests
   - All tests passed

**Key Takeaway:** When `caplog` is empty but logs are visible in console output, check logging propagation hierarchy.

---

**Report Generated:** 2025-12-15
**Task Status:** ✅ Closed
**All Acceptance Criteria:** ✅ Met
