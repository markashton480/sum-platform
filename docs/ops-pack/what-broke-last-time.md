# What Broke Last Time

**Purpose:** Append-only log of deployment/upgrade issues and resolutions.  
**Update:** After every incident, failed deploy, rollback, or issue discovered.

---

## Why This Document Exists

**Problem:** Repeating the same mistakes across deployments.

**Solution:** Document every issue, resolution, and follow-up idea.

**Goal:** Learn from mistakes, improve runbooks, automate recurring issues.

---

## How to Use

**After any deploy/upgrade:**

1. If something broke, append an entry below
2. Include: site, date, version transition, symptom, fix, follow-up
3. Never delete entries (append-only)
4. Review before next deploy to avoid repeating issues

---

## Template

```markdown
## Site: <site-slug>

**Date:** YYYY-MM-DD  
**Version:** vOLD → vNEW  
**Symptom:** <what went wrong>  
**Fix:** <what you did to resolve>  
**Follow-up:** <automation idea / process improvement>

---
```

---

## Log Entries

## Site: sum-platform (Core)

**Date:** 2025-12-18  
**Version:** v0.7.0-dev  
**Symptom:** `make lint` reported success despite 32 type errors and Zero Python files checked by Black.  
**Fix:** Restored Black `include` regex; updated `Makefile` to enforce root Ruff config and make Mypy failure gating; implemented `MYPY_SOFT=1` mode.  
**Follow-up:** Tools now truthfully fail. Ensure "QA Tooling Sanity" check is part of future toolchain audits.

---

_(No further entries)_

---

## Example Entries

### Example 1: Static Files Not Collected

```markdown
## Site: acme-kitchens

**Date:** 2025-12-17  
**Version:** v0.6.0 → v0.6.1  
**Symptom:** After upgrade, all CSS/JS returned 404. Site rendered without styling.  
**Fix:** Re-ran `python manage.py collectstatic --noinput`, reloaded Caddy.  
**Follow-up:** Add `collectstatic` check to deploy script to fail early if it doesn't run.

---
```

---

### Example 2: Migration Failure

```markdown
## Site: sage-and-stone

**Date:** 2025-12-18  
**Version:** v0.6.1 → v0.7.0  
**Symptom:** Migration failed with "relation already exists" error. Service wouldn't start.  
**Fix:** Rolled back to v0.6.1 using rollback runbook. Investigated migration state, found manual DB change from earlier. Faked migration in dev, re-attempted upgrade successfully next day.  
**Follow-up:** Document migration troubleshooting steps in runbook. Consider adding `showmigrations` check before running migrations.

---
```

---

### Example 3: Redis Not Running

```markdown
## Site: lintel-demo

**Date:** 2025-12-19  
**Version:** Initial deploy v0.6.2  
**Symptom:** `/health/` returned 503 (unhealthy), Redis connection refused.  
**Fix:** Redis service wasn't enabled on VPS. Ran `sudo systemctl enable --now redis-server`, health endpoint immediately returned 200.  
**Follow-up:** Add Redis service check to deploy runbook prerequisites. Consider adding to provision script.

---
```

---

### Example 4: Environment Variable Missing

```markdown
## Site: acme-kitchens

**Date:** 2025-12-20  
**Version:** v0.6.2 → v0.7.0  
**Symptom:** Service failed to start after upgrade. Logs showed `KeyError: 'NEW_SETTING'`.  
**Fix:** New version required `NEW_SETTING` env var. Added to `.env`, restarted service.  
**Follow-up:** Check release notes for required env vars before upgrade. Add env var validation to deploy script or health check.

---
```

---

## Follow-Up Tracking

**Automation ideas from this log:**

_(Extract from follow-up notes above and prioritize)_

**High priority:**

- [ ] Add `collectstatic` check to deploy script
- [ ] Add Redis service check to deploy runbook prerequisites

**Medium priority:**

- [ ] Document migration troubleshooting in runbook
- [ ] Add env var validation to deploy script

**Low priority / Future:**

- [ ] Automated smoke test script (covers most common issues)
- [ ] Pre-deploy checklist generator from release notes

---

## Review Cadence

**Before every deploy/upgrade:**

- Review this log for similar sites
- Check if any previous issues apply to current upgrade
- Implement follow-ups if time permits

**Monthly review:**

- Review all entries from last month
- Prioritize automation follow-ups
- Update runbooks with lessons learned

---

## Related Documentation

- [`loop-sites-matrix.md`](loop-sites-matrix.md) — Track site versions
- [`deploy-runbook.md`](deploy-runbook.md) — Fresh deploy process
- [`upgrade-runbook.md`](upgrade-runbook.md) — Upgrade process
- [`rollback-runbook.md`](rollback-runbook.md) — Rollback process

---

**Remember:** Every issue is a lesson. Document it.
