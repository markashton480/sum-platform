## Rate Limiting

### Overview

Form submissions use a per-IP, per-site rate limit enforced via Django cache.
The limit is defined by `FormConfiguration.rate_limit_per_ip_per_hour` and is
checked during spam protection in `run_spam_checks()`.

### Behavior

- Scope: per IP address + Wagtail site ID.
- Window: fixed 1-hour TTL (`RATE_LIMIT_WINDOW_SECONDS = 3600`).
- Counting: increment-first. Each request that reaches the rate-limit check
  increments the counter, then is allowed if the new value is within the limit.
- Exceeding: when the counter value is greater than the configured limit, the
  request is rejected with HTTP 429.
- Disable: set `rate_limit_per_ip_per_hour` to `0` to skip rate limiting.

### Backend requirements

Atomic increments are used to avoid race conditions under concurrency:

- Preferred: cache backends that support `cache.incr()` (Redis, Memcached).
- Fallback: if `incr()` is unsupported, a `get` + `set` fallback is used, which
  is not fully atomic under high concurrency but preserves behavior.

### Notes

- The counter is updated as part of the rate-limit check (not post-submit),
  so all attempts count toward the limit, not just successful submissions.
- The TTL is refreshed on increment when supported by the backend.

### Related code and tests

- Implementation: `core/sum_core/forms/services.py`
- Form handler: `core/sum_core/forms/views.py`
- Concurrency test: `tests/forms/test_spam_protection.py`
