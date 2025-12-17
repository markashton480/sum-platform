# Smoke Tests

**Purpose:** Quick post-deploy/upgrade sanity checks (10–15 minutes).  
**When to use:** After every deploy, upgrade, or rollback.

---

## Overview

Smoke tests verify **critical baseline functionality** is working.

**Not comprehensive** — for that, see [`full-verification.md`](full-verification.md).

**Goal:** Catch showstopper issues immediately.

---

## Prerequisites

- [ ] Site deployed or upgraded
- [ ] Services running (gunicorn, celery if applicable)
- [ ] Domain resolving to VPS

---

## Test Checklist

### 1. Health Endpoint

**Purpose:** Verify runtime baseline (Redis, database, cache).

**Test:**

```bash
export DOMAIN="example.com"
curl -i "https://${DOMAIN}/health/"
```

**Expected:**

**Healthy (ideal):**

```
HTTP/2 200
Content-Type: application/json

{"status": "ok", "checks": {...}}
```

**Degraded (acceptable):**

```
HTTP/2 200
Content-Type: application/json

{"status": "degraded", "checks": {...}}
```

**Unhealthy (failure):**

```
HTTP/2 503
Content-Type: application/json

{"status": "unhealthy", "checks": {...}}
```

**✅ Pass if:** 200 status (ok or degraded)  
**❌ STOP if:** 503 status (unhealthy) — **Redis or database failure**

---

### 2. Redis Connectivity

**Purpose:** Verify Redis is running and reachable.

**Test:**

```bash
# On VPS
ssh deploy@<vps-hostname>
redis-cli ping
```

**Expected:** `PONG`

**✅ Pass if:** `PONG` returned  
**❌ STOP if:** `Could not connect` or `Connection refused`

**If failed:**

```bash
# Check Redis service
sudo systemctl status redis-server

# Start if stopped
sudo systemctl start redis-server
```

---

### 3. Homepage Render

**Purpose:** Verify Django/Wagtail serving pages without errors.

**Test:**

```bash
curl -I "https://${DOMAIN}/"
```

**Expected:**

```
HTTP/2 200
Content-Type: text/html
```

**✅ Pass if:** 200 status  
**❌ STOP if:** 500, 502, 503, or timeout

**Investigate:**

```bash
# Check gunicorn logs
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -n 50 --no-pager

# Check Caddy logs
sudo journalctl -u caddy -n 50 --no-pager
```

---

### 4. Static Files Serving

**Purpose:** Verify Caddy serving static files correctly.

**Test:**

```bash
# Check a known static file (e.g., CSS)
curl -I "https://${DOMAIN}/static/sum_core/css/main.css"
```

**Expected:**

```
HTTP/2 200
Content-Type: text/css
```

**✅ Pass if:** 200 status  
**❌ STOP if:** 404 (static files not collected or Caddy misconfigured)

**If failed:**

```bash
# Re-collect static files
cd /srv/sum/${SITE_SLUG}/app
source /srv/sum/${SITE_SLUG}/venv/bin/activate
python manage.py collectstatic --noinput --settings=<module>.settings.production

# Restart Caddy
sudo systemctl reload caddy
```

---

### 5. Admin Login (if accessible)

**Purpose:** Verify Wagtail admin is functional.

**⚠️ Skip if admin is not publicly accessible** (e.g., IP-restricted or preview sites with basic auth).

**Test:**

```bash
curl -I "https://${DOMAIN}/admin/login/"
```

**Expected:**

```
HTTP/2 200
Content-Type: text/html
```

**Manual check:**

- Open `https://<domain>/admin/` in browser
- Log in with superuser credentials
- Verify dashboard loads

**✅ Pass if:** Login page loads, dashboard accessible  
**❌ STOP if:** 500 error, unable to log in, or missing CSS

---

### 6. Form Submission (if applicable)

**Purpose:** Verify lead capture pipeline is working.

**⚠️ Skip if site has no forms deployed yet.**

**Test:**

**Manual:**

1. Navigate to a page with a form (e.g., homepage CTA)
2. Fill in form fields (use test email)
3. Submit form

**Expected:**

- Success message displayed
- No 500 errors
- Lead saved (check Wagtail admin → Leads)

**✅ Pass if:** Form submits successfully and lead appears in admin  
**❌ STOP if:** Form submission errors, lead not saved

**Investigate:**

```bash
# Check application logs
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -f --no-pager

# Check celery logs (if using async tasks)
sudo journalctl -u "sum-${SITE_SLUG}-celery.service" -n 50 --no-pager
```

---

## Pass/Fail Criteria

**All tests MUST pass** before declaring deploy/upgrade successful.

**If ANY test fails:**

1. ❌ **DO NOT** declare site production-ready
2. Investigate failure immediately
3. Check logs (`journalctl` for gunicorn/celery/caddy)
4. If can't resolve in < 15 minutes, **trigger rollback** (see [`rollback-runbook.md`](rollback-runbook.md))

---

## Record Results

### Update loop sites matrix

Open [`loop-sites-matrix.md`](loop-sites-matrix.md) and update:

- Smoke tests: Pass / Fail
- Date tested
- Notes (if any issues)

---

### Log issues

If any test failed but was resolved:

Open [`what-broke-last-time.md`](what-broke-last-time.md) and append:

- **Test failed:** `<which test>`
- **Symptom:** `<description>`
- **Fix:** `<what you did>`
- **Follow-up:** `<prevention idea>`

---

## Next Steps

**If all smoke tests pass:**

- ✅ Site is **minimally functional**
- For production sites: run [`full-verification.md`](full-verification.md)
- For staging/dev: monitor for 24 hours

**If any smoke test fails:**

- ❌ Investigate and resolve
- OR trigger rollback if can't fix quickly

---

## Optional: Automated Smoke Test Script

**Future enhancement:** Create `smoke_test.sh` script to automate these checks.

**Example structure:**

```bash
#!/bin/bash
# smoke_test.sh
DOMAIN=$1
SITE_SLUG=$2

# Health check
curl -f -s "https://${DOMAIN}/health/" || exit 1

# Homepage
curl -f -I "https://${DOMAIN}/" || exit 1

# Static files
curl -f -I "https://${DOMAIN}/static/sum_core/css/main.css" || exit 1

echo "Smoke tests passed."
```

**Usage:**

```bash
./smoke_test.sh example.com acme-kitchens
```

---

**END OF CHECKLIST**
