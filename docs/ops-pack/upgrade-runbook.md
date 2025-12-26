# Upgrade Runbook

**Purpose:** Upgrade an existing SUM client site to a new `sum_core` version.  
**Reference:** [`docs/dev/master-docs/POST-MVP_BIG-PLAN.md`](../dev/master-docs/POST-MVP_BIG-PLAN.md) (Practice Loop)

---

## Prerequisites

Before starting:

- [ ] New `sum_core` version released and tagged
- [ ] Client repository updated with new version pin in `requirements.txt`
- [ ] Release notes reviewed for breaking changes
- [ ] Maintenance window scheduled (if required)
- [ ] Backup rehearsal completed (know how to restore)

---

## Pre-Upgrade Checks

### 1. Verify current state

```bash
# SSH to VPS
ssh deploy@<vps-hostname>

# Set site slug
export SITE_SLUG="acme-kitchens"
export DOMAIN="example.com"

# Check current service status
sudo systemctl status "sum-${SITE_SLUG}-gunicorn.service" --no-pager

# Check current health endpoint
curl -i "https://${DOMAIN}/health/"
```

**Expected:** Service running, health returns 200 or 503 (degraded ok).

**Stop if:** Service not running or health returns unexpected status.

---

### 2. Check disk space

```bash
df -h /srv/sum/${SITE_SLUG}
df -h /srv/sum/${SITE_SLUG}/backups
```

**Ensure:** At least 2GB free for backups.

**Stop if:** Insufficient disk space.

---

### 3. Review release notes

**Check:**

- Breaking changes
- Migration requirements
- New environment variables required
- Deprecated features

**Location:** Release notes in the `sum-core` repository (or attach a summary in the release PR).

**Stop if:** Breaking changes require code changes in client project (fix client code first).

---

## Backup

### 4. Create pre-upgrade backup

```bash
sudo -u deploy /srv/sum/bin/backup_db.sh --site-slug "$SITE_SLUG"
```

**Verify backup created:**

```bash
ls -lht /srv/sum/${SITE_SLUG}/backups/ | head -3
```

**Record backup filename:**  
`BACKUP_FILE=<filename>.sql.gz`

**Stop if:** Backup fails or file not created.

---

### 5. (Optional) Backup media files

**If media files are critical:**

```bash
sudo tar -czf /srv/sum/${SITE_SLUG}/backups/media_$(date -u +%Y%m%d_%H%M%S).tar.gz \
  -C /srv/sum/${SITE_SLUG}/media .
```

---

## Upgrade Steps

### 6. Pull latest client code

```bash
cd /srv/sum/${SITE_SLUG}/app
sudo -u deploy git fetch origin
sudo -u deploy git checkout <tag-or-branch>
sudo -u deploy git pull origin <tag-or-branch>
```

**Replace `<tag-or-branch>`** with target version (e.g., `main` or `v1.2.0`).

**Verify `requirements.txt` updated:**

```bash
grep "sum-core" /srv/sum/${SITE_SLUG}/app/requirements.txt
```

**Expected:** New `sum_core` version pinned.

**Stop if:** `requirements.txt` not updated or incorrect version.

---

### 7. Activate virtualenv and upgrade dependencies

```bash
cd /srv/sum/${SITE_SLUG}
source venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
```

**Stop if:** Dependency installation fails.

---

### 8. Run migrations

```bash
cd /srv/sum/${SITE_SLUG}/app
python manage.py migrate --settings=<project_module>.settings.production
```

**Expected:** Migrations apply cleanly.

**Stop if:** Migration fails. **DO NOT PROCEED.** Investigate error, may need rollback.

---

### 9. Collect static files

```bash
python manage.py collectstatic --noinput --settings=<project_module>.settings.production
```

**Expected:** Static files collected to `/srv/sum/${SITE_SLUG}/static/`

---

### 10. Restart services

```bash
sudo systemctl restart "sum-${SITE_SLUG}-gunicorn.service"

# If using Celery:
sudo systemctl restart "sum-${SITE_SLUG}-celery.service"
```

**Verify services started:**

```bash
sudo systemctl status "sum-${SITE_SLUG}-gunicorn.service" --no-pager
```

**Stop if:** Service fails to start. Check logs:

```bash
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -n 50 --no-pager
```

---

## Verification

### 11. Run smoke tests

Follow [`smoke-tests.md`](smoke-tests.md):

- [ ] `/health/` returns 200 (ok) or 503 (degraded)
- [ ] Homepage renders without errors
- [ ] Admin login works
- [ ] Form submission works (if applicable)
- [ ] Redis connectivity verified

**Stop if:** Critical smoke tests fail. **Trigger rollback.**

---

### 12. Check for errors

**Application logs:**

```bash
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -f --no-pager
```

**Watch for:**

- ❌ 500 errors
- ❌ Missing static files (404s)
- ❌ Database errors
- ❌ Template errors

**Stop if:** Errors detected. **Trigger rollback.**

---

### 13. Spot-check site functionality

**Manual checks:**

- [ ] Navigate to key pages (homepage, services, blog if applicable)
- [ ] Check navigation menus render correctly
- [ ] Submit a test form (use test email)
- [ ] Check admin interface (if accessible)

**Stop if:** Major functionality broken. **Trigger rollback.**

---

## Rollback Trigger Conditions

**Trigger rollback immediately if:**

- ❌ Migrations fail
- ❌ Service won't start after restart
- ❌ `/health/` returns `unhealthy` (503)
- ❌ Critical pages returning 500 errors
- ❌ Data loss or corruption detected

**See:** [`rollback-runbook.md`](rollback-runbook.md)

---

## Post-Upgrade

### 14. Run full verification (if time permits)

Follow [`full-verification.md`](full-verification.md) for comprehensive checks.

**Recommended for:**

- Major version upgrades (e.g., `0.6.x` → `0.7.0`)
- Production sites
- After migration changes

---

### 15. Monitor for 24–48 hours

**Set up monitoring:**

- External uptime check (`/health/`)
- Error tracking (Sentry or logs)
- Performance metrics (if available)

**Watch for:**

- Delayed errors (async tasks, cron jobs)
- Performance degradation
- User-reported issues

---

## Record Keeping

### 16. Update loop sites matrix

Open [`loop-sites-matrix.md`](loop-sites-matrix.md) and update:

- Current deployed version/tag
- Upgrade date
- Outcome: Success / Issues / Rolled back

---

### 17. Log issues (if any)

If anything went wrong:

Open [`what-broke-last-time.md`](what-broke-last-time.md) and append:

- **Site:** `<slug>`
- **Date:** `YYYY-MM-DD`
- **Version:** `vX.Y.Z` (from) → `vA.B.C` (to)
- **Symptoms:** `<description>`
- **Fix:** `<resolution>`
- **Follow-up:** `<automation ideas / process improvements>`

---

## Checklist Summary

- [ ] Current state verified (service running, health ok)
- [ ] Disk space checked
- [ ] Release notes reviewed
- [ ] Pre-upgrade backup created
- [ ] Client code pulled (new version)
- [ ] Dependencies upgraded (`pip install -r requirements.txt`)
- [ ] Migrations applied successfully
- [ ] Static files collected
- [ ] Services restarted
- [ ] Smoke tests pass
- [ ] No errors in logs
- [ ] Site functionality spot-checked
- [ ] Loop sites matrix updated
- [ ] Issues logged (if any)
- [ ] Monitoring active for 24–48 hours

---

## Common Issues

### Migrations fail: "relation already exists"

**Cause:** Migration state out of sync (fake migration or manual DB change).

**Fix:**

- Check `django_migrations` table for applied migrations
- May need to fake migration: `python manage.py migrate --fake <app> <migration>`
- **Dangerous:** only if you're certain the migration already applied manually

**Better:** rollback and investigate before re-attempting.

---

### Service won't start after upgrade

**Check logs:**

```bash
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -n 100 --no-pager
```

**Common causes:**

- Missing environment variable in `.env`
- Syntax error in Python code
- Dependency version conflict

**Fix:**

- Add missing env vars
- Check tracebacks in logs
- May need to rollback if not quickly fixable

---

### Static files 404

**Cause:** `collectstatic` not run or Caddy config incorrect.

**Fix:**

```bash
# Re-run collectstatic
python manage.py collectstatic --noinput --settings=<module>.settings.production

# Verify files exist
ls /srv/sum/${SITE_SLUG}/static/

# Restart Caddy
sudo systemctl reload caddy
```

---

### `/health/` returns `unhealthy` (503)

**Cause:** Redis down, database unreachable, or critical service failure.

**Check:**

```bash
# Redis
redis-cli ping

# Database
psql "postgresql://sum_site_user:PASSWORD@127.0.0.1:5432/sum_site_db" -c "SELECT 1;"

# Logs
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -n 50 --no-pager
```

**Fix:** Resolve underlying issue or **rollback**.

---

**END OF RUNBOOK**
