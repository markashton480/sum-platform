# Ready-to-paste issues

> Note: `filecite…` links point to the exact lines I cited during the review.

### Critical issues

#### 1) Critical: Rate-limiting race condition and bypassable IP-based enforcement

**Labels**: `security`, `critical`, `bug`, `forms`
**Body**:

```
Summary
-------
Rate-limiting for form submissions is implemented using cache get/set operations and an IP extraction method that trusts X-Forwarded-For unconditionally. This combination allows trivial bypass and race conditions under concurrency.

Location
--------
- core/sum_core/forms/services.py: get_client_ip(), check_rate_limit(), increment_rate_limit_counter()
  (see get_client_ip: :contentReference[oaicite:0]{index=0}, check_rate_limit/increment: :contentReference[oaicite:1]{index=1})

Problem
-------
- `get_client_ip()` takes the first IP from `X-Forwarded-For` without validating trusted proxies, enabling client IP spoofing.
- Rate-limit counter logic uses `cache.get()` and `cache.set()` (non-atomic). Concurrent requests can both observe the same counter value and both proceed, allowing the hourly limit to be exceeded.

Impact
------
- Attackers can bypass per-IP rate-limits and spam leads.
- Under load the limit is unreliable; legitimate protections fail.
- Possible DoS vector for notification systems and storage.

Recommended Fix
-------------
1. **Trust model for X-Forwarded-For**: Only accept `X-Forwarded-For` when request passes through a trusted proxy. Use Django/infra config (ProxyFix or equivalent) or a central utility that checks an explicit list of trusted proxy IPs.
2. **Centralize client IP logic**: Move IP extraction to a single utility function used system-wide (and document the trusted proxy requirement).
3. **Atomic counters**: Use atomic increment operations (Redis `INCR` or `cache.incr`) or the `cache.add` then `cache.incr` pattern:
   - `if cache.add(key, 1, timeout=3600): count = 1 else: count = cache.incr(key)`
   - Or increment first and reject if result > limit (with proper handling).
4. Add concurrency tests (simulate parallel submissions) and monitoring for rate-limit violations.

Notes / Citations
-----------------
- get_client_ip: :contentReference[oaicite:2]{index=2}
- check_rate_limit / increment_rate_limit_counter: :contentReference[oaicite:3]{index=3}
```

---

#### 2) Critical: Duplicate `get_client_ip` implementations and untrusted proxy header usage

**Labels**: `security`, `bug`, `tech-debt`
**Body**:

```
Summary
-------
There are duplicate implementations of client IP extraction in two places, both of which trust `X-Forwarded-For` without validating trusted proxies:

- core/sum_core/forms/services.py::get_client_ip
- core/sum_core/leads/services.py::get_client_ip

Locations & citations
--------------------
- forms/services.get_client_ip: :contentReference[oaicite:4]{index=4}
- leads/services.get_client_ip: :contentReference[oaicite:5]{index=5}

Problem
-------
- Duplication increases the chance of inconsistent behavior.
- Both implementations accept `X-Forwarded-For` blindly; if a reverse proxy is absent or misconfigured, clients can spoof IPs for rate-limit evasion and other protections.

Impact
------
- IP-based protections (rate limiting, logging, attribution) can be circumvented or behave inconsistently across modules.
- Troubleshooting is harder because multiple copies must be updated for any change.

Recommended Fix
-------------
1. Implement a single, shared util function (e.g. `sum_core.ops.request_utils.get_client_ip`) that:
   - Uses Django / infrastructure trusted proxy config.
   - Falls back to `REMOTE_ADDR` appropriately.
   - Is thoroughly tested behind proxy scenarios.
2. Replace the duplicated functions with the new util.
3. Document expectations for trusted proxies in deployment docs.

Notes
-----
See also the race/atomicity issues for rate limiting (this ties into the trust model).
```

---

#### 3) Critical: Non-atomic rate-limit counter implementation (race window)

**Labels**: `bug`, `high`, `forms`
**Body**:

```
Summary
-------
Rate-limit enforcement uses `cache.get(key)` to read a counter and `cache.set(key, current + 1, timeout=3600)` to increment. These operations are not atomic, allowing race conditions and limit bypass.

Location
--------
- core/sum_core/forms/services.py: check_rate_limit / increment_rate_limit_counter
  (see: :contentReference[oaicite:6]{index=6})

Problem
-------
- Two concurrent requests may both read the same `current_count` and set the same incremented value, making the limit unreliable.

Impact
------
- Rate limits can be exceeded under concurrent submission bursts.
- An attacker could use concurrent workers to bypass the per-hour restriction.

Recommended Fix
-------------
- Use atomic cache operations (e.g., `cache.incr`) or Redis `INCR` semantics.
- If backend doesn't support `incr`, use `cache.add` to seed the key then `cache.incr`.
- Consider increment-first-then-check approach: increment atomically; if value > limit then reject.
- Add concurrency unit/integration tests to demonstrate the fix.

Notes
-----
Implementing this also requires ensuring TTL semantics are what we intend (sliding vs fixed window).
```

---

### High Priority Warnings

#### 4) High: Time-token HMAC truncated to 16 hex characters (weak MAC)

**Labels**: `security`, `high`
**Body**:

```
Summary
-------
The HMAC used to sign time tokens is truncated to 16 hex characters (`hexdigest()[:16]`), producing a ~64-bit tag which reduces cryptographic strength.

Location
--------
- core/sum_core/forms/services.py: _sign_timestamp(), generate_time_token()
  (see: :contentReference[oaicite:7]{index=7})

Problem
-------
- Truncating the MAC reduces brute-force resistance. An attacker could attempt forgery more easily than with the full HMAC output.

Impact
------
- Timing checks can be bypassed more easily, weakening spam protection.

Recommended Fix
-------------
- Use the full HMAC output, or truncate to at least 32 hex chars (128 bits). Prefer returning entire HMAC or base64 encode it.
- Consider dedicated signing key for form tokens (see next item for rotation).

```

---

#### 5) High: Missing logging for missing or malformed time tokens

**Labels**: `ops`, `high`
**Body**:

```
Summary
-------
check_timing() currently treats missing tokens permissively and has a comment “Fall through without blocking, but log in production” — but no logging is implemented.

Location
--------
- core/sum_core/forms/services.py::check_timing
  (see: :contentReference[oaicite:8]{index=8})

Problem
-------
- No logging/metrics for missing/malformed tokens means we lose visibility into token bypass or frequent missing tokens.

Impact
------
- Operators cannot detect or track when timing protection is being bypassed or misconfigured.

Recommended Fix
-------------
- Add structured logging for missing/malformed tokens (without logging secret material).
- Add a metric/tag to monitor frequency and alert on unusual rates.
```

---

#### 6) High: Time-token signing key tied to SECRET_KEY with no rotation plan

**Labels**: `security`, `medium`
**Body**:

```
Summary
-------
Time tokens are signed with Django `SECRET_KEY`. Rotating SECRET_KEY will invalidate prior tokens and cause UX breakage. There's no dedicated key or rotation plan.

Location
--------
- core/sum_core/forms/services.py::_sign_timestamp
  (see: :contentReference[oaicite:9]{index=9})

Problem
-------
- Using the global SECRET_KEY ties token validity to uncoordinated rotations.

Impact
------
- Token invalidation after key rotations causes client errors until pages are refreshed. Hard to rotate keys safely.

Recommended Fix
-------------
- Use a dedicated signing key (config var `FORM_TIME_TOKEN_KEY`) and support an optional list of old keys for graceful rotation.
- Document rotation process and tests.
```

---

#### 7) High: Possible wrong permission string used for lead export

**Labels**: `bug`, `medium`, `leads`
**Body**:

```
Summary
-------
Permission check uses `user.has_perm("sum_core_leads.export_lead")`, which likely does not match the actual app_label/permission format in Django.

Location
--------
- core/sum_core/leads/services.py::can_user_export_leads
  (see: :contentReference[oaicite:10]{index=10})

Problem
-------
- Django permission strings are `<app_label>.<perm_codename>`. The code uses `sum_core_leads.export_lead`, which is probably incorrect.

Impact
------
- Authorized users may not be able to export leads, or the check always returns false.

Recommended Fix
-------------
- Use `Lead._meta.app_label` or confirm the app label and use `f"{app_label}.export_lead"`.
- Add a unit test for `can_user_export_leads`.
```

---

#### 8) High: `Site` fallback selection may pick an arbitrary site (multi-site risk)

**Labels**: `bug`, `medium`
**Body**:

```
Summary
-------
When `Site.find_for_request(request)` returns `None`, code falls back to `Site.objects.filter(is_default_site=True).first() or Site.objects.first()`.

Location
--------
- core/sum_core/forms/views.py::_get_site
  (see: :contentReference[oaicite:11]{index=11})

Problem
-------
- In multi-site deployments this fallback can select the wrong site, causing incorrect site-scoped configuration (honeypot name, rate limits, notification emails).

Impact
------
- Leads could be attributed to the wrong site, notifications misrouted, or privacy leaks.

Recommended Fix
-------------
- Prefer stricter behavior: reject requests that cannot be mapped to a site, or require a validated Host header.
- Log occurrences and add a monitoring alert for fallback usage.
```

---

#### 9) High: Time-token replayable / token design allows reuse across users/pages

**Labels**: `security`, `medium`
**Body**:

```
Summary
-------
Time tokens only contain the timestamp signed by a secret. Tokens can be replayed within their 1-hour lifetime and are not bound to the page or user.

Location
--------
- core/sum_core/forms/services.py::generate_time_token / check_timing
  (see: :contentReference[oaicite:12]{index=12} :contentReference[oaicite:13]{index=13})

Problem
-------
- A valid token can be reused across pages/users until it expires => timing protection weakened.

Impact
------
- Attackers could capture valid tokens and reuse them to circumvent timing checks.

Recommended Fix
-------------
- Include additional context when signing the token (site ID, path, per-render nonce).
- If using a nonce, store it server-side or compute deterministically.
- Reduce token lifetime for production if per-render binding isn't feasible.
```

---

#### 10) High: Unbounded `form_data` persisted to DB (no size checks)

**Labels**: `bug`, `medium`
**Body**:

```
Summary
-------
Additional form fields (`form_data`) are saved directly into `Lead.form_data` JSONField without size/type limits.

Location
--------
- core/sum_core/leads/services.py::create_lead_from_submission
  (see: :contentReference[oaicite:14]{index=14})

Problem
-------
- Attackers could submit very large JSON blobs or unexpected types, causing storage blow-up, slow exports, or UI problems.

Impact
------
- DB growth, performance degradation, possible DoS on database or admin UI export.

Recommended Fix
-------------
- Enforce limits (max bytes and allowed types) for `form_data` before persisting.
- Truncate or reject oversized values and log truncations.
- Add tests ensuring oversized submissions are rejected or sanitized.
```

---

### Code Quality Improvements

#### 11) CQ: Centralize client-IP extraction (duplicate detected)

**Labels**: `refactor`, `tech-debt`
**Body**:

```
Summary
-------
Duplicate `get_client_ip` implementations exist (forms/services & leads/services). Centralize this logic and document proxy assumptions.

Location
--------
- core/sum_core/forms/services.py & core/sum_core/leads/services.py
  (see: :contentReference[oaicite:15]{index=15} :contentReference[oaicite:16]{index=16})

Recommended Fix
-------------
- Create `sum_core.ops.request_utils.get_client_ip` and use everywhere.
- Add tests and document trusted proxies expected in production.
```

---

#### 12) CQ: Broad exception catches when validating JSON and email

**Labels**: `bug`, `low`
**Body**:

```
Summary
-------
Some blocks catch broad `Exception`, masking unexpected failures (e.g. email validation).

Location
--------
- core/sum_core/forms/views.py::_parse_request_data, _validate_submission
  (see: JSON decode handling: :contentReference[oaicite:17]{index=17}, email validation catch: :contentReference[oaicite:18]{index=18})

Recommended Fix
-------------
- Catch specific exceptions (e.g., `json.JSONDecodeError`, `django.core.exceptions.ValidationError`).
- Log unexpected exceptions to sentry/structured logs.
```

---

#### 13) CQ: Honeypot default name `company` is ambiguous

**Labels**: `improvement`, `low`
**Body**:

```
Summary
-------
The default honeypot field name is `company`, which may clash with legitimate forms and is easy for bots to detect.

Location
--------
- core/sum_core/forms/models.py::FormConfiguration.honeypot_field_name
  (see: :contentReference[oaicite:19]{index=19})

Recommended Fix
-------------
- Use a less-obvious default (e.g., `__company__`) or per-site random name.
- Document how to choose/override the honeypot field for clients.
```

#### 14) CQ: Rate-limit counter TTL semantics reset on each increment (sliding vs fixed window)

**Labels**: `improvement`, `low`
**Body**:

```
Summary
-------
increment_rate_limit_counter uses cache.set(..., timeout=3600) on every increment, which results in a sliding expirations window rather than fixed per-hour bucket.

Location
--------
- core/sum_core/forms/services.py::increment_rate_limit_counter
  (see: :contentReference[oaicite:20]{index=20})

Recommended Fix
-------------
- Decide fixed-window vs sliding-window policy.
- If fixed-window is desired, use bucket keys (e.g., keyed by hour) or a value+expiry tuple.
- Document choice and add tests.
```

---

#### 15) CQ: Add tests & docs for key areas

**Labels**: `test`, `docs`
**Body**:

```
Summary
-------
We should add automated tests and docs for:
- Rate-limit concurrency and behavior.
- Trusted proxy / get_client_ip semantics.
- Time-token forgery/resilience tests.
- form_data size limits and export handling.

Recommended Fix
-------------
- Add concurrency tests that hammer rate limit counter and verify atomicity after fixes.
- Add a short doc describing deployment expectations (trusted proxies, required env var for token signing).
```

---
