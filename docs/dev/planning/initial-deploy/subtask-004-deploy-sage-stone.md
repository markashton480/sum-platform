# Subtask Template

**Title:** `GH-XXX: Deploy Sage & Stone to staging VPS`

---

## Parent

**Work Order:** #YYY — Initial Sage & Stone Deployment (v0.6.0)

---

## Branch

| Branch | Target |
| ------ | ------ |
| N/A    | N/A    |

**Note:** This is a manual operations task. No code changes to sum-platform.

---

## Deliverable

This subtask will deliver:

- Sage & Stone client project deployed to VPS
- systemd services configured and running (gunicorn)
- Caddy configured with TLS for `sage-and-stone.lintel.site`
- Site accessible via HTTPS
- Admin accessible (with auth protection)

---

## Boundaries

### Do

- Clone Sage & Stone client repository to VPS
- Configure systemd services per vps-golden-path.md section 7
- Configure Caddy per vps-golden-path.md section 8
- Run deploy.sh per section 9
- Verify site is accessible

### Do NOT

- ❌ Do not enable Celery (not required for initial launch)
- ❌ Do not configure production backups yet (smoke tests first)
- ❌ Do not onboard content editors yet
- ❌ Do not expose admin without auth protection

---

## Acceptance Criteria

- [ ] `https://sage-and-stone.lintel.site/` returns HTTP 200
- [ ] `https://sage-and-stone.lintel.site/health/` returns HTTP 200
- [ ] Homepage renders with correct theme
- [ ] Static files load (CSS, JS)
- [ ] Gunicorn service is running: `systemctl status sum-sage-and-stone-gunicorn.service`
- [ ] Caddy is serving TLS (valid certificate)

---

## Test Commands

Run these after deployment:

```bash
# From local machine
curl -I "https://sage-and-stone.lintel.site/"
curl -I "https://sage-and-stone.lintel.site/health/"
curl -I "https://sage-and-stone.lintel.site/static/"

# On VPS
sudo systemctl status sum-sage-and-stone-gunicorn.service
sudo journalctl -u sum-sage-and-stone-gunicorn.service -n 50 --no-pager
sudo journalctl -u caddy -n 20 --no-pager
```

---

## Files Expected to Change

No files in sum-platform repository.

**On VPS:**
```
/etc/systemd/system/sum-sage-and-stone-gunicorn.service
/etc/caddy/sites-enabled/sum-sage-and-stone.caddy
/srv/sum/sage-and-stone/app/                    # Client repo clone
/srv/sum/sage-and-stone/venv/                   # Python virtualenv
/srv/sum/sage-and-stone/static/                 # collectstatic output
```

---

## Dependencies

**Depends On:**

- [ ] Subtask #3 (VPS provisioning) must be complete
- [ ] Sage & Stone client repository must exist and be accessible
- [ ] DNS must be propagated

**Blocks:**

- Subtask #5 (Smoke tests) requires deployment complete

---

## Risk

**Level:** Medium

**Why:**
- First deployment execution
- Multiple integration points (gunicorn, Caddy, Django, Postgres, Redis)
- TLS provisioning depends on DNS

**Mitigation:**
- Follow vps-golden-path.md sections 7-9 exactly
- Check service logs immediately if issues
- Verify each component before proceeding

---

## Labels

- [ ] `type:task`
- [ ] `agent:human`
- [ ] `component:infra`
- [ ] `risk:med`
- [ ] Milestone: `v0.6.0`

---

## Project Fields

- [ ] Agent: human
- [ ] Model Planned: human
- [ ] Component: infra
- [ ] Change Type: chore
- [ ] Risk: med
- [ ] Release: `v0.6.0`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] Site accessible via HTTPS
- [ ] Health endpoint returns 200
- [ ] Service logs show no critical errors
- [ ] Parent Work Order updated

---

## Deployment Checklist (from vps-golden-path.md)

### Section 7: systemd Services

- [ ] Copy gunicorn service template
- [ ] Replace placeholders:
  - `__SITE_SLUG__` → `sage-and-stone`
  - `__DEPLOY_USER__` → `deploy`
  - `__PROJECT_MODULE__` → `sage_and_stone` (or actual module name)
- [ ] Install to `/etc/systemd/system/`
- [ ] `systemctl daemon-reload`
- [ ] `systemctl enable --now sum-sage-and-stone-gunicorn.service`
- [ ] Verify service running

### Section 8: Caddy Configuration

- [ ] Ensure main Caddyfile has `import /etc/caddy/sites-enabled/*.caddy`
- [ ] Copy Caddyfile.template to sites-enabled
- [ ] Replace `__DOMAIN__` → `sage-and-stone.lintel.site`
- [ ] Replace `__SITE_SLUG__` → `sage-and-stone`
- [ ] Add caddy to www-data group
- [ ] Validate config: `caddy validate --config /etc/caddy/Caddyfile`
- [ ] Reload Caddy: `systemctl reload caddy`
- [ ] Verify TLS certificate provisioned

### Section 9: Deploy Script

- [ ] Copy deploy scripts to `/srv/sum/bin/`
- [ ] Configure sudoers for deploy user
- [ ] Run deploy.sh:
  ```bash
  sudo -u deploy /srv/sum/bin/deploy.sh \
    --site-slug sage-and-stone \
    --ref v0.6.0 \
    --domain sage-and-stone.lintel.site
  ```
- [ ] Verify smoke checks pass

### Post-Deploy Verification

- [ ] Homepage loads
- [ ] Health endpoint returns 200
- [ ] No errors in gunicorn logs
- [ ] No errors in Caddy logs
