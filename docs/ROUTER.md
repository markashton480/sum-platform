# SUM Platform Documentation Router

**Purpose:** Quick navigation to operational and reference documentation.  
**For:** Maintainers, operators, and contributors who need to do something specific without spelunking.

---

## 🚀 Hot Path: Operations (Day-to-Day)

These are the **operational runbooks** you use weekly/monthly in production.  
**Primary source:** [`docs/ops-pack/`](ops-pack/)

### Release a new version

**Primary:** [`docs/ops-pack/release-checklist.md`](ops-pack/release-checklist.md)  
Use this checklist end-to-end to cut a new tag and verify it.

**References:**

- [Release workflow (canonical)](dev/release-workflow.md) — versioning rules, tag discipline
- [Git strategy](dev/git_strategy.md) — branching and commit conventions
- [Hygiene standards](dev/hygiene.md) — lint/test/pre-release checks
- [CLI usage](dev/cli.md) — `sum init` and `sum check` behavior

---

### Deploy a fresh VPS

**Primary:** [`docs/ops-pack/deploy-runbook.md`](ops-pack/deploy-runbook.md)  
Step-by-step from bare VPS to running site.

**References:**

- [VPS Golden Path (canonical)](dev/deploy/vps-golden-path.md) — full deployment guide with all details

---

### Upgrade an existing site

**Primary:** [`docs/ops-pack/upgrade-runbook.md`](ops-pack/upgrade-runbook.md)  
Run this when upgrading a live site to a new core version.

**References:**

- [Post-MVP Practice Loop](dev/master-docs/POST-MVP_BIG-PLAN.md) — practice cycle expectations
- [Release workflow](dev/release-workflow.md) — version pinning discipline

---

### Rollback a broken deployment

**Primary:** [`docs/ops-pack/rollback-runbook.md`](ops-pack/rollback-runbook.md)  
When things go wrong, use this to get back to known-good state.

**References:**

- [VPS Golden Path: Rollback section](dev/deploy/vps-golden-path.md#10-upgrade-flow-tag-pinning-discipline)

---

### Verify nothing broke

**Quick smoke tests (10–15 min):**  
[`docs/ops-pack/smoke-tests.md`](ops-pack/smoke-tests.md)

**Full verification (30–60 min):**  
[`docs/ops-pack/full-verification.md`](ops-pack/full-verification.md)

Use smoke tests after every deploy/upgrade.  
Use full verification before declaring a site production-ready or after major changes.

---

### Track loop sites and deployment history

**Loop Sites Matrix:** [`docs/ops-pack/loop-sites-matrix.md`](ops-pack/loop-sites-matrix.md)  
**What Broke Log:** [`docs/ops-pack/what-broke-last-time.md`](ops-pack/what-broke-last-time.md)

Update these after every deploy/upgrade cycle to maintain institutional knowledge.

---

### Git policy (operational summary)

**Primary:** [`docs/ops-pack/git-policy.md`](ops-pack/git-policy.md)  
Quick operational guide to branching, tagging, and safe-to-ship rules.

**Reference:** [Git strategy (detailed)](dev/git_strategy.md)

---

## 📚 Reference: Implementation and Architecture

Use these when **building features** or **understanding the platform**, not for day-to-day ops.

### Platform architecture and structure

- **[SUM Platform SSOT](dev/master-docs/SUM-PLATFORM-SSOT.md)** — single source of truth for architecture, scope, features
- **[CODEBASE-STRUCTURE.md](dev/CODEBASE-STRUCTURE.md)** — directory tree and file organization
- **[AGENT-ORIENTATION.md](dev/AGENT-ORIENTATION.md)** — platform vs test harness distinction
- **[Overview](dev/master-docs/overview.md)** — LINTEL × SUM entity relationships

### Feature wiring and implementation

- **[WIRING-INVENTORY.md](dev/WIRING-INVENTORY.md)** — how to consume `sum_core` in client projects (URLs, settings, apps)
- **[Blocks reference](dev/blocks-reference.md)** — complete StreamField block catalog
- **[Page types reference](dev/page-types-reference.md)** — available page models and their fields
- **[Navigation tags reference](dev/navigation-tags-reference.md)** — header/footer/sticky CTA template tags

### Design system

- **[CSS Architecture and Tokens](dev/design/css-architecture-and-tokens.md)** — design token system and CSS structure
- **[Design system philosophy](dev/design/design_system.md)** — brand-agnostic "frame not paint" approach

### Development standards

- **[Hygiene standards](dev/hygiene.md)** — lint/test/formatting requirements
- **[Daily code review](dev/reviews/daily_code_review.md)** — review checklist and quality gates

---

## 🔍 Investigate / Audit Trail

When troubleshooting or researching **"why did we decide X?"** or **"what changed in milestone Y?"**

### Core Maintenance (CM) audits

- **`docs/dev/CM/`** — production readiness audits (CM-001 through CM-008, CM-M5-N1, CM-M6-01, etc.)
- Each CM includes `_followup.md` with implementation status

### Milestones and reports

- **`docs/dev/M0/` through `docs/dev/M6/`** — milestone work transcripts (audit trail)
- **`docs/dev/reports/`** — code reviews, technical analysis, status reports

### Strategic planning

- **[POST-MVP Big Plan](dev/master-docs/POST-MVP_BIG-PLAN.md)** — post-MVP feature roadmap and practice loop strategy

---

## 📖 Complete Documentation Map

For the definitive guide to the entire platform:

**[The SUM Platform Handbook](HANDBOOK.md)** — **Start here!**

For a comprehensive inventory of every document:

**[DDD.md (Documentation Documentation Document)](DDD.md)**

---

## Quick Decision Tree

**I want to…**

- **Ship a new version** → [`ops-pack/release-checklist.md`](ops-pack/release-checklist.md)
- **Deploy a fresh site** → [`ops-pack/deploy-runbook.md`](ops-pack/deploy-runbook.md)
- **Upgrade a live site** → [`ops-pack/upgrade-runbook.md`](ops-pack/upgrade-runbook.md)
- **Undo a bad deploy** → [`ops-pack/rollback-runbook.md`](ops-pack/rollback-runbook.md)
- **Check if things work** → [`ops-pack/smoke-tests.md`](ops-pack/smoke-tests.md)
- **Add a new block** → [`dev/blocks-reference.md`](dev/blocks-reference.md)
- **Wire core into a project** → [`dev/WIRING-INVENTORY.md`](dev/WIRING-INVENTORY.md)
- **Understand the platform** → [`dev/master-docs/SUM-PLATFORM-SSOT.md`](dev/master-docs/SUM-PLATFORM-SSOT.md)
- **Find any documentation** → [`DDD.md`](DDD.md)

---

## Notes

- **Ops Pack** = hot path operational docs (runbooks, checklists)
- **Canonical docs** = detailed reference documentation (SSOT, golden path, etc.)
- Always update `loop-sites-matrix.md` and `what-broke-last-time.md` after ops work
