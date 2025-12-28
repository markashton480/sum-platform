# Subtask Template

**Title:** `GH-XXX: Execute smoke tests and update operational tracking`

---

## Parent

**Work Order:** #YYY — Initial Sage & Stone Deployment (v0.6.0)

---

## Branch

| Branch | Target |
| ------ | ------ |
| N/A    | N/A    |

**Note:** This is a manual operations task with documentation updates.

---

## Deliverable

This subtask will deliver:

- Complete smoke test execution per `docs/ops-pack/smoke-tests.md`
- Initial database backup created
- `docs/ops-pack/loop-sites-matrix.md` updated with Sage & Stone entry
- Any issues documented in `docs/ops-pack/what-broke-last-time.md`

---

## Boundaries

### Do

- Run all smoke tests from smoke-tests.md
- Create initial backup using backup_db.sh
- Update loop-sites-matrix.md with deployment details
- Document any issues encountered during deployment process
- Record deployment date and outcome

### Do NOT

- ❌ Do not test restore procedure yet (optional for initial deploy)
- ❌ Do not configure automated backups yet (future scope)
- ❌ Do not onboard content editors yet
- ❌ Do not skip documenting issues — even small ones matter

---

## Acceptance Criteria

- [ ] All smoke tests from smoke-tests.md executed
- [ ] Health endpoint returns HTTP 200
- [ ] Homepage renders correctly
- [ ] Redis connectivity verified
- [ ] Backup file exists at `/srv/sum/sage-and-stone/backups/`
- [ ] `loop-sites-matrix.md` contains Sage & Stone entry
- [ ] Any deployment issues documented in `what-broke-last-time.md`

---

## Test Commands

```bash
# Smoke tests (from local machine)
curl -i "https://sage-and-stone.lintel.site/health/"
curl -i "https://sage-and-stone.lintel.site/"

# On VPS - Redis check
redis-cli ping

# On VPS - Service status
sudo systemctl status sum-sage-and-stone-gunicorn.service
sudo systemctl status caddy

# On VPS - Create backup
sudo -u deploy /srv/sum/bin/backup_db.sh --site-slug sage-and-stone

# On VPS - Verify backup
ls -lh /srv/sum/sage-and-stone/backups/
```

---

## Files Expected to Change

```
docs/ops-pack/loop-sites-matrix.md      # Add Sage & Stone entry
docs/ops-pack/what-broke-last-time.md   # Add issues if any
```

---

## Dependencies

**Depends On:**

- [ ] Subtask #4 (Deployment) must be complete

**Blocks:**

- Nothing — this is the final subtask

---

## Risk

**Level:** Low

**Why:** Verification and documentation only. No destructive operations.

---

## Labels

- [ ] `type:task`
- [ ] `agent:human`
- [ ] `component:docs`
- [ ] `component:infrastructure`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.0`

---

## Project Fields

- [ ] Agent: human
- [ ] Model Planned: human
- [ ] Component: docs, infrastructure
- [ ] Change Type: docs
- [ ] Risk: low
- [ ] Release: `v0.6.0`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] Smoke tests pass
- [ ] Backup created
- [ ] Loop sites matrix updated
- [ ] Issues documented (if any)
- [ ] Parent Work Order updated

---

## Smoke Test Checklist (from smoke-tests.md)

### 1. Health Endpoint
```bash
curl -i "https://sage-and-stone.lintel.site/health/"
```
- [ ] Returns HTTP 200 (ok or degraded acceptable)
- [ ] 503 = STOP and investigate

### 2. Redis Connectivity
```bash
# On VPS
redis-cli ping
```
- [ ] Returns PONG

### 3. Homepage
```bash
curl -I "https://sage-and-stone.lintel.site/"
```
- [ ] Returns HTTP 200
- [ ] Page renders with styling

### 4. Static Files
```bash
curl -I "https://sage-and-stone.lintel.site/static/css/styles.css"
```
- [ ] Static assets load (CSS, JS)

### 5. Admin Login (if accessible)
- [ ] Navigate to /admin/
- [ ] Login form appears
- [ ] Superuser can log in

### 6. Form Submission (if forms exist)
- [ ] Submit a test form
- [ ] Form submission recorded (check admin)

### 7. Service Status
```bash
# On VPS
sudo systemctl status sum-sage-and-stone-gunicorn.service
sudo systemctl status caddy
```
- [ ] Both services active (running)

---

## Loop Sites Matrix Entry Template

Add this entry to `docs/ops-pack/loop-sites-matrix.md`:

```markdown
| Sage & Stone | staging | sage-and-stone | v0.6.0 | YYYY-MM-DD | Initial deploy | First loop site |
```

---

## What-Broke-Last-Time Entry Template

If any issues occurred, add to `docs/ops-pack/what-broke-last-time.md`:

```markdown
## Sage & Stone Initial Deploy

**Site:** sage-and-stone
**Date:** YYYY-MM-DD
**Version:** v0.6.0 (initial)
**Symptom:** [Brief description of what went wrong]
**Fix:** [What you did to resolve it]
**Follow-up:** [Priority] — [Automation idea or prevention measure]
```

---

## Post-Completion

After all smoke tests pass and documentation is updated:

1. Close this subtask
2. Update Work Order status
3. Notify stakeholders that Sage & Stone staging is live
4. Plan first content update cycle (separate from this WO)
