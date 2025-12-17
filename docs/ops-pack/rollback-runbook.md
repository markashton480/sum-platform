# Rollback Runbook

**Purpose:** Revert a site to a known-good state after a failed deployment or upgrade.  
**When to use:** Deployment/upgrade failures, critical bugs, or data issues.

---

## When to Rollback

**Trigger rollback immediately if:**

- ❌ Migrations fail and can't be resolved quickly
- ❌ Service won't start after upgrade
- ❌ `/health/` returns `unhealthy` (503) and can't be fixed in < 15 minutes
- ❌ Critical functionality broken (forms, payments, core user flows)
- ❌ Data corruption or loss detected
- ❌ Security vulnerability introduced

**Do NOT wait to see if it fixes itself.**

---

## Rollback Strategy

In the SUM Platform ecosystem, **rollback = redeploy a previous known-good tag**.

**What this means:**

- Git checkout previous version
- Restore database from backup (if migrations ran)
- Reinstall dependencies
- Restart services

**Not a "magic undo button"** — requires deliberate steps.

---

## Prerequisites

Before starting rollback:

- [ ] Know the previous known-good version (check [`loop-sites-matrix.md`](loop-sites-matrix.md))
- [ ] Have recent backup available (verify via `ls /srv/sum/<slug>/backups/`)
- [ ] Maintenance window active (site may be briefly down)

---

## Rollback Steps

### 1. Identify known-good version

**Check loop sites matrix:**

```bash
cat /path/to/docs/ops-pack/loop-sites-matrix.md
```

**Or check Git tags:**

```bash
cd /srv/sum/<SITE_SLUG>/app
git tag -l "v*" --sort=-version:refname | head -10
```

**Record known-good version:**  
`ROLLBACK_VERSION=v0.5.0`

---

### 2. Stop services

```bash
export SITE_SLUG="acme-kitchens"
sudo systemctl stop "sum-${SITE_SLUG}-gunicorn.service"

# If using Celery:
sudo systemctl stop "sum-${SITE_SLUG}-celery.service"
```

---

### 3. Checkout previous version

```bash
cd /srv/sum/${SITE_SLUG}/app
sudo -u deploy git fetch origin
sudo -u deploy git checkout <ROLLBACK_VERSION>
```

**Replace `<ROLLBACK_VERSION>`** with known-good tag (e.g., `v0.5.0`).

---

### 4. Restore database (if migrations ran)

**Only restore if:**

- Migrations were applied during failed upgrade
- Database state is inconsistent

**Skip if:**

- No migrations ran
- Database is still in good state

**Restore command:**

```bash
# Identify backup file (take most recent before upgrade)
ls -lht /srv/sum/${SITE_SLUG}/backups/ | head -5

# Restore
sudo -u deploy /srv/sum/bin/restore_db.sh \
  --site-slug "$SITE_SLUG" \
  --file "/srv/sum/${SITE_SLUG}/backups/<BACKUP_FILE>.sql.gz" \
  --i-know-this-will-overwrite
```

**Replace `<BACKUP_FILE>`** with actual filename.

**⚠️ WARNING:** This will **overwrite** the current database. Any data created after the backup will be lost.

---

### 5. Reinstall dependencies

```bash
cd /srv/sum/${SITE_SLUG}
source venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
```

**Stop if:** Dependency installation fails.

---

### 6. Collect static files

```bash
cd /srv/sum/${SITE_SLUG}/app
python manage.py collectstatic --noinput --settings=<project_module>.settings.production
```

---

### 7. Restart services

```bash
sudo systemctl start "sum-${SITE_SLUG}-gunicorn.service"

# If using Celery:
sudo systemctl start "sum-${SITE_SLUG}-celery.service"
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

## Verification After Rollback

### 8. Run smoke tests

Follow [`smoke-tests.md`](smoke-tests.md):

- [ ] `/health/` returns 200 (ok)
- [ ] Homepage renders
- [ ] Admin login works
- [ ] Form submission works

**If smoke tests still fail:** Escalate. May need manual intervention or deeper investigation.

---

### 9. Check logs for errors

```bash
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -f --no-pager
```

**Watch for:**

- No 500 errors
- No database connection errors
- No missing static files

---

### 10. Notify stakeholders

**If production site:**

- Notify users/clients (site temporarily unavailable during rollback)
- Update status page (if applicable)
- Document downtime duration

---

## Record Keeping

### 11. Update loop sites matrix

Open [`loop-sites-matrix.md`](loop-sites-matrix.md) and update:

- Current deployed version (rolled back version)
- Rollback date
- Outcome: Rolled back from `vX.Y.Z` to `vA.B.C`

---

### 12. Log the incident

**CRITICAL:** Document what happened.

Open [`what-broke-last-time.md`](what-broke-last-time.md) and append:

- **Site:** `<slug>`
- **Date:** `YYYY-MM-DD`
- **Attempted upgrade:** `vOLD` → `vNEW`
- **Symptoms:** `<what went wrong>`
- **Rolled back to:** `vOLD`
- **Fix applied:** `<what you did to recover>`
- **Follow-up:** `<what to fix before re-attempting upgrade>`

---

## Post-Rollback

### 13. Investigate root cause

**Before re-attempting upgrade:**

- [ ] Review logs from failed upgrade
- [ ] Identify what caused failure
- [ ] Test fix in staging/dev environment
- [ ] Update runbooks if process issue discovered

**Do not re-attempt upgrade until root cause resolved.**

---

### 14. Plan re-upgrade

**Once issue resolved:**

- [ ] Create new release if code fix required
- [ ] Test in non-production environment first
- [ ] Schedule maintenance window
- [ ] Follow [`upgrade-runbook.md`](upgrade-runbook.md) with lessons learned

---

## Checklist Summary

- [ ] Known-good version identified
- [ ] Services stopped
- [ ] Code checked out to previous version
- [ ] Database restored (if migrations ran)
- [ ] Dependencies reinstalled
- [ ] Static files collected
- [ ] Services restarted
- [ ] Smoke tests pass
- [ ] Logs checked (no errors)
- [ ] Stakeholders notified (if production)
- [ ] Loop sites matrix updated
- [ ] Incident logged in "what broke" log
- [ ] Root cause investigated
- [ ] Re-upgrade plan created

---

## Alternative: Partial Rollback

**If only specific changes need reverting:**

### Code-only rollback (no database restore)

**When to use:**

- No migrations ran
- Database state is fine
- Only code/template/static issues

**Steps:**

1. Checkout previous version (step 3)
2. Reinstall dependencies (step 5)
3. Collect static (step 6)
4. Restart services (step 7)

**Skip:** Database restore (step 4)

---

### Database-only restore (keep new code)

**When to use:**

- Code is fine
- Data corruption occurred
- Migration introduced bad data

**Steps:**

1. Stop services (step 2)
2. Restore database (step 4)
3. Restart services (step 7)

**Skip:** Code checkout and dependency reinstall

**⚠️ WARNING:** Only safe if no schema changes between versions.

---

## Emergency Contacts

**If rollback fails or site remains down:**

- [ ] Escalate to platform maintainer
- [ ] Check backup integrity: `gunzip -t /srv/sum/<slug>/backups/<file>.sql.gz`
- [ ] Consider restoring from older backup if most recent is corrupted
- [ ] Document all actions taken

---

## Prevention

**Reduce rollback frequency by:**

- ✅ Always run [`upgrade-runbook.md`](upgrade-runbook.md) pre-checks
- ✅ Test upgrades in staging first
- ✅ Create backups before every upgrade
- ✅ Review release notes for breaking changes
- ✅ Maintain "what broke" log to avoid repeating mistakes

---

**END OF RUNBOOK**
