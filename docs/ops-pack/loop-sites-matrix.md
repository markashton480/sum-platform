# Loop Sites Matrix

**Purpose:** Track all deployed SUM client sites and their versions.  
**Update:** After every deploy, upgrade, or rollback.

---

## Active Sites

| Site Name | Environment | Slug      | Current Version | Last Deploy Date | Last Upgrade Outcome | Notes          |
| --------- | ----------- | --------- | --------------- | ---------------- | -------------------- | -------------- |
| (example) | staging     | acme-test | v0.6.0          | 2025-12-10       | Success              | Initial deploy |
|           |             |           |                 |                  |                      |                |
|           |             |           |                 |                  |                      |                |
|           |             |           |                 |                  |                      |                |
|           |             |           |                 |                  |                      |                |

---

## How to Use This Matrix

### When deploying a new site:

1. Add a new row
2. Fill in: Site Name, Environment, Slug, Version, Date
3. Set "Last Upgrade Outcome" to `Initial deploy`

### When upgrading an existing site:

1. Find the site row
2. Update "Current Version" to new version
3. Update "Last Deploy Date" to today
4. Update "Last Upgrade Outcome" to:
   - `Success` (no issues)
   - `Success (minor issues)` (issues resolved during deploy)
   - `Rolled back` (if rollback occurred)

### Notes column:

- Document special configurations
- Link to incident reports (if applicable)
- Note deferred issues or follow-ups

---

## Site Definitions

**Site Name:** Human-readable name (e.g., "Sage & Stone Kitchens", "LINTEL Marketing Site")

**Environment:**

- `production` — live client site
- `staging` — preview/demo site
- `dev` — development/testing

**Slug:** Server directory slug (e.g., `acme-kitchens` for `/srv/sum/acme-kitchens/`)

**Current Version:** Git tag of `sum-core` deployed (e.g., `v0.6.0`)

**Last Deploy Date:** `YYYY-MM-DD` format

**Last Upgrade Outcome:**

- `Success` — no issues
- `Success (minor issues)` — issues fixed during deploy
- `Rolled back` — deploy failed, rolled back to previous version
- `Initial deploy` — first deployment

---

## Example Entries

### Example: Successful initial deploy

| Site Name     | Environment | Slug          | Current Version | Last Deploy Date | Last Upgrade Outcome | Notes                     |
| ------------- | ----------- | ------------- | --------------- | ---------------- | -------------------- | ------------------------- |
| Acme Kitchens | staging     | acme-kitchens | v0.6.0          | 2025-12-15       | Initial deploy       | First staging site for M6 |

---

### Example: Successful upgrade

| Site Name     | Environment | Slug          | Current Version | Last Deploy Date | Last Upgrade Outcome | Notes                           |
| ------------- | ----------- | ------------- | --------------- | ---------------- | -------------------- | ------------------------------- |
| Acme Kitchens | staging     | acme-kitchens | v0.6.1          | 2025-12-17       | Success              | Upgraded from v0.6.0, no issues |

---

### Example: Upgrade with minor issues

| Site Name     | Environment | Slug          | Current Version | Last Deploy Date | Last Upgrade Outcome   | Notes                                  |
| ------------- | ----------- | ------------- | --------------- | ---------------- | ---------------------- | -------------------------------------- |
| Acme Kitchens | staging     | acme-kitchens | v0.6.2          | 2025-12-18       | Success (minor issues) | Static files 404, re-ran collectstatic |

---

### Example: Rollback

| Site Name     | Environment | Slug          | Current Version | Last Deploy Date | Last Upgrade Outcome    | Notes                                 |
| ------------- | ----------- | ------------- | --------------- | ---------------- | ----------------------- | ------------------------------------- |
| Acme Kitchens | staging     | acme-kitchens | v0.6.1          | 2025-12-19       | Rolled back from v0.7.0 | Migration failure, see what-broke log |

---

## Site Lifecycle States

**Track site progression:**

1. **Initial deploy** → staging environment
2. **Upgrade practice** → multiple upgrades in staging
3. **Production promotion** → deployed to production environment
4. **Ongoing upgrades** → regular version updates

**Example progression:**

| Date       | Version | Outcome        | Environment |
| ---------- | ------- | -------------- | ----------- |
| 2025-12-15 | v0.6.0  | Initial deploy | staging     |
| 2025-12-17 | v0.6.1  | Success        | staging     |
| 2025-12-20 | v0.6.2  | Success        | staging     |
| 2025-12-22 | v0.6.2  | Initial deploy | production  |

---

## Archival

**When a site is decommissioned:**

1. Move row to "Archived Sites" section below
2. Add decommission date to Notes
3. Document reason (if applicable)

---

## Archived Sites

| Site Name | Environment | Slug | Last Version | Last Deploy Date | Decommission Date | Notes |
| --------- | ----------- | ---- | ------------ | ---------------- | ----------------- | ----- |
|           |             |      |              |                  |                   |       |

---

## Automation Opportunities

**Future enhancements:**

- Script to auto-update this file after deploy
- Parse from systemd service names or site directories
- Generate from deployment script output

**For now:** Manual updates required after every deploy/upgrade.

---

## Related Documentation

- [`what-broke-last-time.md`](what-broke-last-time.md) — Incident log
- [`deploy-runbook.md`](deploy-runbook.md) — Fresh deploy process
- [`upgrade-runbook.md`](upgrade-runbook.md) — Upgrade process
- [`rollback-runbook.md`](rollback-runbook.md) — Rollback process

---

**Keep this matrix current. If you deployed something, update the matrix.**
