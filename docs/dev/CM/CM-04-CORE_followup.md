# CM-04-CORE: Core vs Test Project Alignment Audit Report

**Audit Date**: 2025-12-15  
**Auditor**: AI Assistant  
**Scope**: Milestone 4 implementation alignment

---

## Executive Summary

The Milestone 4 implementation is **well-aligned** with SUM Core principles. All M4 functionality resides in `sum_core` modules and is consumable by client projects via standard Django patterns. No code changes were required; only documentation updates were made.

---

## What Was Checked

### 1. Settings & Configuration ✅

| Area          | Finding                                                  |
| ------------- | -------------------------------------------------------- |
| Email backend | Env-driven in test_project; no core assumptions          |
| Sentry        | `init_sentry()` checks env var, no-ops when absent       |
| Logging       | `get_logging_config()` provides reusable config function |
| Zapier        | Per-site SiteSettings field, not global env var          |
| SEO           | Per-site robots.txt in SiteSettings                      |
| Cache         | Client-configured, health check uses whatever's set      |

### 2. App Registration ✅

| App                  | Status                                          |
| -------------------- | ----------------------------------------------- |
| `sum_core.seo`       | Correctly documented in apps.py                 |
| `sum_core.analytics` | Has AnalyticsConfig app                         |
| `sum_core.ops`       | Intentionally not a Django app (utility module) |

### 3. URL Routing ✅

All M4 endpoints use standard `include()` patterns:

- `/health/` → `include("sum_core.ops.urls")`
- `/sitemap.xml` → `include("sum_core.seo.urls")`
- `/robots.txt` → `include("sum_core.seo.urls")`

### 4. Environment Variables ⚠️

All env vars have safe defaults. Documentation was missing.

### 5. Documentation ⚠️

README was at M3 status; .env.example lacked M4 vars.

---

## What Was Changed

### Documentation Updates

1. **`.env.example`**: Added M4 environment variables:

   - Email SMTP settings
   - Celery broker configuration
   - Sentry/observability settings
   - Logging configuration
   - Build/version info vars

2. **`README.md`**: Updated to reflect M4 completion:
   - Changed status heading from M3 to M4
   - Added Technical SEO features
   - Added Analytics integration
   - Added Observability baseline
   - Added Email delivery features
   - Added Zapier integration
   - Extended runtime configuration section

### Code Changes

**None.** The audit confirmed all M4 code is correctly placed in core.

---

## What Was Intentionally Left As-Is

1. **`sum_core.ops` not a Django app**: Correct design—contains utility functions, not models/admin. No need for AppConfig.

2. **Email settings in test_project**: Correct—clients must configure SMTP. Core provides no default backend.

3. **No default SiteSettings values**: Correct—per-site configuration is defined by site admins in Wagtail.

---

## Follow-ups Deferred to Later Milestones

| Item                       | Reason               |
| -------------------------- | -------------------- |
| Boilerplate generator      | Future CLI milestone |
| Client project template    | Future milestone     |
| Production deployment docs | Beyond CM scope      |

---

## Conclusion

> _"If the test project disappeared, would Milestone 4 still exist?"_

**Yes.** All M4 functionality is:

- Defined in `sum_core` modules
- Configured via env vars or SiteSettings
- Included via standard Django `include()` patterns
- Documented for client consumption

The audit passes with documentation updates only.
