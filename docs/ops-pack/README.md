# SUM Platform Ops Pack

**Purpose:** Hot-path operational documentation for daily/weekly platform management.  
**Audience:** Maintainers and operators running the SUM Platform in production.

---

## What is the Ops Pack?

The **Ops Pack** is a collection of **short, action-oriented runbooks and checklists** for platform operations:

- **Release** a new version
- **Deploy** fresh sites
- **Upgrade** existing sites
- **Rollback** broken deployments
- **Verify** nothing broke
- **Track** deployment history and lessons learned

These documents are:

- ✅ **Checklist-first** (not essays)
- ✅ **Operational** (for doing work, not reading theory)
- ✅ **Always current** (updated after every cycle)
- ✅ **Self-contained** (usable without reading the entire repo)

---

## What the Ops Pack is NOT

- ❌ **Not a replacement for canonical docs** — it links to them for details
- ❌ **Not architectural reference** — see SSOT and master docs for that
- ❌ **Not implementation guides** — see blocks/pages/wiring references for that
- ❌ **Not audit trail** — see milestone docs and CM reports for that

**Think of it as:** the laminated cards you keep at your desk for "how do I X again?"

---

## Ops Pack Files

### Core Runbooks

1. **[release-checklist.md](release-checklist.md)** — Ship a new version of `sum_core`
2. **[deploy-runbook.md](deploy-runbook.md)** — Deploy a fresh VPS from scratch
3. **[upgrade-runbook.md](upgrade-runbook.md)** — Upgrade an existing site to new core version
4. **[rollback-runbook.md](rollback-runbook.md)** — Revert to known-good state

### Verification

5. **[smoke-tests.md](smoke-tests.md)** — 10–15 minute post-deploy sanity checks
6. **[full-verification.md](full-verification.md)** — 30–60 minute comprehensive verification

### Tracking & Record-Keeping

7. **[loop-sites-matrix.md](loop-sites-matrix.md)** — Track deployed sites and versions
8. **[what-broke-last-time.md](what-broke-last-time.md)** — Append-only incident log

### Policy

9. **[git-policy.md](git-policy.md)** — Operational Git policy (branching, tagging, safe-to-ship)

---

## How to Use the Ops Pack

### For Releases

1. Follow **[release-checklist.md](release-checklist.md)**
2. Record outcome in **loop-sites-matrix.md**
3. Update **what-broke-last-time.md** if issues occurred

### For Deployments

1. Use **[deploy-runbook.md](deploy-runbook.md)** (fresh) or **[upgrade-runbook.md](upgrade-runbook.md)** (existing)
2. Run **[smoke-tests.md](smoke-tests.md)** immediately after
3. Run **[full-verification.md](full-verification.md)** before declaring production-ready
4. Update **loop-sites-matrix.md** and **what-broke-last-time.md**

### For Rollbacks

1. Follow **[rollback-runbook.md](rollback-runbook.md)**
2. Document what triggered rollback in **what-broke-last-time.md**
3. Run **smoke-tests.md** after rollback

---

## Maintenance

**These docs must be kept current.**

After every deploy/upgrade cycle:

- ✅ Update matrix and log
- ✅ Note any deviations from runbooks
- ✅ Update runbooks if process changed
- ✅ Add to "what broke" log if issues occurred

**If a runbook doesn't match reality, fix the runbook.**

---

## Canonical References

For detailed background, see:

- **[docs/dev/release-workflow.md](../dev/release-workflow.md)** — Full release process
- **[docs/dev/deploy/vps-golden-path.md](../dev/deploy/vps-golden-path.md)** — Complete VPS setup guide
- **[docs/dev/master-docs/POST-MVP_BIG-PLAN.md](../dev/master-docs/POST-MVP_BIG-PLAN.md)** — Practice loop strategy
- **[docs/dev/git_strategy.md](../dev/git_strategy.md)** — Git workflow details

**Start here for ops work, link to canonical docs for deep dives.**

---

## Quick Start

**New to the Ops Pack?**

1. Read this README
2. Skim **[git-policy.md](git-policy.md)**
3. Try a dry-run of **[release-checklist.md](release-checklist.md)** (without pushing tags)
4. Bookmark **[smoke-tests.md](smoke-tests.md)** — you'll use it constantly

**Ready for real work:**

- Releasing? → **release-checklist.md**
- Deploying? → **deploy-runbook.md** or **upgrade-runbook.md**
- Verifying? → **smoke-tests.md** → **full-verification.md**
- Tracking? → **loop-sites-matrix.md** + **what-broke-last-time.md**
