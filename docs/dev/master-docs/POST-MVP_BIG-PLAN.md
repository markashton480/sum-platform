# **SUM Platform — Post-MVP Expansion PRD (v2)**

**Status:** Revised Draft  
**Version:** 2.0  
**Date:** December 16, 2025  
**Applies after:** Milestone 5 (Platform Factory)  
**Audience:** Platform maintainer + AI agents  
**Purpose:** Define controlled expansion of SUM Platform after MVP freeze, without destabilising core guarantees.

---

## Document Changes from v1

| Change | Category | Impact |
|--------|----------|--------|
| CSS transition strategy defined | Architecture | Prevents M5 destabilization |
| Theme/branding contract clarified | Architecture | Prevents system collision |
| LINTEL migration strategy added | Practice | Enables real-world validation |
| Feature freeze policy defined | Stability | Prevents moving target |
| Version mapping added | Operations | Enables confident pinning |
| Caddy locked as web server | Infrastructure | Nginx → Caddy |
| CRM naming clarified | Vocabulary | Removes ambiguity |
| Runbook templates added | Operations | Reduces deployment friction |
| Multi-version testing policy | Quality | Sustainable maintenance |
| AI layer scope tightened | Focus | Prevents distraction |

---

## 1. Context & Motivation

Milestone 5 delivered a **stable, repeatable platform** capable of:

* scaffolding client sites via `sum init`
* validating structure via `sum check`
* deploying and upgrading safely
* enforcing correctness via contracts, not conventions
* supporting token-based CSS and core page types

**The M5 freeze point (sum_core@0.5.x) is:**
- Production-ready
- Fully tested
- Stable and shippable
- **Frozen for feature work**

Post-MVP work must **preserve this stability** while allowing:

* feature growth (blog, forms, CRM)
* design evolution (themes)
* operational confidence (deploy & upgrade practice)
* AI-assisted review (read-only, not automation)

---

## 2. Guiding Principles (Non-Negotiable)

### 2.1 Core Stability First

* `sum_core@0.5.x` remains installable, versioned, and **frozen** for feature work
* Security and critical fixes only for 0.5.x line
* No feature may "only work" in a harness or demo project
* New features ship in new minor versions (0.6.x, 0.7.x, etc.)

### 2.2 Real Consumers Only

* New features are exercised via **real client projects** scaffolded with `sum init`
* "Real" means: actual business entity, production-grade content, real traffic intent
* May be internal (LINTEL) or external clients
* No bespoke test projects or synthetic demos

### 2.3 Practice Before Promises

* At least **3–4 full deploy + upgrade cycles** completed before onboarding external paying clients
* Each cycle must include: deploy, content updates, core upgrade, verification
* Rollback procedure rehearsed at least once per site
* "What broke last time" notes maintained

### 2.4 AI is an Auditor First

* AI integrations start as **read-only reviewers**, not content mutators
* Draft-only write actions may be added later, explicitly and narrowly
* Never auto-publish, never schema mutation, never silent edits

### 2.5 Themes are Fixed Per Site

* Theme selection happens at `sum init` time
* No Wagtail admin theme switching
* Changing a theme is a developer action (requires project setup change)
* Themes remain stable once selected

### 2.6 Breaking Changes Policy

* Breaking changes ONLY at major versions (0.x → 1.0, etc.)
* Minor version bumps (0.5.x → 0.6.0) may introduce incompatibilities if documented heavily
* Patch releases (0.5.1 → 0.5.2) NEVER break existing functionality
* All breaking changes require migration guide
* 1.0.0 = stability contract begins (semantic versioning enforced)

---

## 3. Post-MVP Milestones Overview

### Milestone 6 — Themes & Delivery Pipeline

**Goal:** Prove the platform can deliver real sites safely with new presentation layer.

**Core Deliverables:**
* Theme system v1 (Tailwind-first, init-time selection)
* Theme A (reference theme)
* Blog v1 (first vertical slice feature)
* Caddy deployment golden-path
* Staging + production workflow
* LINTEL-v2 site deployed "for real"

**Version:** `sum_core@0.6.x`

---

### Milestone 7 — Platform Practice & Feature Evolution

**Goal:** Build confidence through repetition and controlled feature expansion.

**Core Deliverables:**
* Dynamic Forms v1 (backwards compatible with lead capture)
* Theme B + Theme C (prove multi-theme architecture)
* Core upgrade propagation across multiple live sites (minimum 2 sites, 2 upgrades each)
* Lead Management v1 (pipeline, status, notes) — later in milestone

**Version:** `sum_core@0.7.x`

---

### Milestone 8 — AI-Assisted Audit Layer (Optional)

**Goal:** Add AI as a correctness and completeness assistant, not a CMS replacement.

**Scope (if pursued):**
* Read-only introspection API
* Custom GPT auditor using OpenAPI actions
* Phase 3 (draft writes) explicitly deferred beyond client-ready

**Version:** `sum_core@0.8.x` (optional)

---

## 4. Architecture & Transition Strategy

### 4.1 CSS Transition Strategy

**Current State (M5):**
- Token-based CSS system in `sum_core/static/sum_core/css/tokens.css`
- Working, tested, production-ready
- Used by all M0–M5 templates

**New State (M6+):**
- Tailwind-first theme system
- Greenfield only (no M5 template retrofitting)
- Theme A is first implementation

**Transition Contract:**
```
✓ M5 stack (token CSS) is legacy + stable + FROZEN
✓ New Tailwind themes are greenfield only (Theme A+)
✓ No retrofitting existing M5 templates into Tailwind during M6
✓ M5 sites remain on 0.5.x; new sites use 0.6.x with themes
✓ Rollback plan: if Tailwind fails perf/a11y gates, Theme A is dropped or reworked without touching M5 CSS
```

**Why this matters:** Guarantees M5 remains shippable while you experiment with theme infrastructure.

**Performance Gate:** Tailwind-based Theme A must meet same Lighthouse targets as M5:
- Performance: ≥90
- Accessibility: ≥90
- SEO: ≥90
- Bundle size: CSS ≤100kb (compressed)

---

### 4.2 Theme vs Branding Contract

**Problem Solved:** Prevent collision between "theme selection at init" and "branding in SiteSettings".

**Architecture:**

```
SiteSettings (Wagtail admin, editable)
├─ Logo
├─ Brand colours (as CSS variables)
├─ Fonts (if kept here)
└─ Contact details

Themes (selected at init, fixed)
├─ Layout templates
├─ Component styling patterns
├─ Tailwind build + preset
└─ Must consume SiteSettings vars (do not replace)
```

**Contract:**
- SiteSettings remains source of truth for **branding identity**
- Themes control **layout & structure** only
- Themes **consume** branding vars; do not replace them in v1
- Result: init-time theme selection remains fixed, branding stays editable

**Example Theme File Structure:**
```
sum_core/themes/theme_a/
├── templates/
│   ├── base.html
│   ├── home_page.html
│   └── components/
├── static/
│   ├── css/
│   │   └── theme_a.css (Tailwind build output)
│   └── js/
└── tailwind.config.js
```

---

### 4.3 Version → Capability Mapping

| Version | Capabilities | Status | Notes |
|---------|-------------|--------|-------|
| **0.5.x** | MVP platform factory (M0–M5) | FROZEN | Token CSS, static forms, core pages only |
| **0.6.x** | Theme system + Blog v1 | Active | First deploy practice loops |
| **0.7.x** | Dynamic Forms v1 | Planned | Backwards compatible with lead capture |
| **1.0.0** | Client-ready declaration | Future | After repeated deploy+upgrade cycles proven |

**Core Stability Contract:**
- `0.5.x` = frozen; only security/critical fixes
- `0.6.x` = new features allowed (themes, blog)
- `0.7.x` = new features allowed (forms)
- No feature backports to older lines unless explicitly approved (rare)
- Anything experimental ships behind a flag or in a new minor line, not in patch releases

---

### 4.4 LINTEL Strategy

**Purpose:** Use LINTEL as real-world validation without destabilizing reference implementation.

**Approach:**

```
LINTEL-v1 (exists now)
├─ Stays on M5 stack (sum_core@0.5.x)
├─ Token CSS, existing branding, static forms
├─ Purpose: rollback reference + "M5 is stable" proof
└─ Not migrated until LINTEL-v2 proven

LINTEL-v2 (new in M6)
├─ Scaffolded via CLI using M6+ stack
├─ Theme A + Tailwind + Blog v1
├─ sum_core@0.6.x
├─ Purpose: dogfood new stack end-to-end
└─ Must complete 2+ upgrade cycles before LINTEL-v1 migration considered
```

**Decision Gate:** LINTEL-v1 is not migrated to new stack until:
- [ ] LINTEL-v2 has completed at least 2 successful upgrade cycles
- [ ] Theme system proven stable
- [ ] Performance targets met or exceeded
- [ ] No regressions in lead capture or SEO

This preserves "themes at init" principle while enabling real rehearsal.

---

## 5. Feature Roadmap (Post-MVP)

### 5.1 Blog v1 (First Vertical Slice)

**Rationale:** Chosen first because it exercises the full templating + theme system with minimal business-critical risk, allowing the theme architecture to stabilize before touching lead capture.

**Scope:**
- `BlogIndexPage` (listing with pagination)
- `BlogPostPage` (individual posts)
- Category/tagging (minimal, single taxonomy)
- SEO metadata (reuses existing `sum_core/seo/`)
- RSS feed (optional)
- Sitemap integration

**Technical Notes:**
- Uses existing SEO system from M4 (no new SEO infrastructure)
- Templates in theme layer (Theme A responsibility)
- Blog pages reuse StreamField blocks from M2
- No editorial workflow automation in v1
- No AI content generation in v1

**Non-Goals:**
- Multi-author support
- Comment system
- Editorial calendar
- Content versioning beyond Wagtail default

**Definition of Done:**
- [ ] Blog pages creatable in Wagtail admin
- [ ] Listing pagination works
- [ ] Category filtering works
- [ ] RSS feed validates
- [ ] SEO tags render correctly
- [ ] Lighthouse targets met (≥90 across all metrics)
- [ ] Deployed to LINTEL-v2 and used for real blog posts

---

### 5.2 Dynamic Forms v1

**Rationale:** Removes reliance on static forms, critical for real client usage where form requirements vary.

**Scope:**
- Form builder UI (minimal, Wagtail admin)
- Field types: text, email, phone, textarea, select, checkbox, file upload
- Form submissions storage
- Email notifications (to admin + optional auto-reply)
- Admin review interface
- Export to CSV

**Backwards Compatibility Contract:**
```
✓ Existing static forms remain supported and untouched
✓ Dynamic Forms v1 writes to the same Lead model (no Lead schema change in v1)
✓ Form builder creates new form types only
✓ Migration of existing forms is out of scope for v1
```

**Technical Notes:**
- Uses `wagtail.contrib.forms` as foundation
- Extends Lead model with polymorphic pattern if needed (investigate)
- Email sending via existing `sum_core/integrations/email.py`
- Webhook integration preserved (Zapier, HubSpot)

**Non-Goals:**
- Multi-step forms
- Conditional logic
- Payment integration
- CAPTCHA (consider for v1.1)
- A/B testing

**Definition of Done:**
- [ ] Form builder accessible in Wagtail admin
- [ ] All field types work
- [ ] Submissions save to Lead model
- [ ] Email notifications send
- [ ] Webhooks fire correctly
- [ ] CSV export works
- [ ] Backwards compatible with existing static forms
- [ ] Deployed to at least 2 client sites

---

### 5.3 Lead Management v1 (Deferred to Late M7)

**Rationale:** Higher complexity, more surface area. Implement only after deploy/upgrade confidence is high.

**Scope:**
- Lead status pipeline (New → Contacted → Qualified → Converted/Lost)
- Notes/comments per lead
- Lead assignment (assign to team member)
- Status change history
- Simple filtering/search in admin

**Non-Goals:**
- Full CRM capabilities
- Email campaigns
- Task management
- Calendar integration
- Deal tracking

**Previous Naming Confusion:** Was called "CRM v2" in v1 draft.

**Corrected Roadmap Labels:**
```
✓ Lead Capture (MVP) = M3 deliverable, working now
✓ Lead Capture Enhancement = Dynamic Forms v1 (M7)
✓ Lead Management v1 = Status pipeline, notes (late M7)
✓ Lead Management v2 = Future, TBD
```

---

## 6. Deployment & Upgrade Practice

### 6.1 Practice Requirements

Before onboarding external **paying clients**:

**Minimum Practice Requirements:**
- [ ] At least **two live sites** running (LINTEL-v2 + one other)
- [ ] Each site undergoes **minimum 2 core upgrades** (0.6.0 → 0.6.1 → 0.6.2, etc.)
- [ ] All migrations apply cleanly (zero data loss)
- [ ] Rollback procedure rehearsed at least once per site
- [ ] "What broke last time" notes maintained and reviewed
- [ ] Runbooks proven and updated after each cycle

**Each Deploy/Upgrade Cycle Must Include:**
1. Pre-deployment checklist completion
2. Database backup
3. Deployment execution
4. Smoke tests (health, homepage, admin login)
5. Verification checklist
6. Post-deployment notes (what went well, what didn't)

---

### 6.2 Infrastructure Updates

**Web Server:** Caddy (locked decision)
- Replaces Nginx from SSOT
- Automatic HTTPS via Let's Encrypt
- Simpler configuration for reverse proxy
- Built-in security defaults

**Stack (Updated):**
```
Browser
  │
  ▼
Caddy (TLS, security headers, static/media)
  │
  ▼
Gunicorn (Django + Wagtail app)
  │
  ├── PostgreSQL (per-client database)
  ├── Redis (cache + Celery broker)
  └── Celery workers (email, webhooks, retention)
```

---

### 6.3 Required Operational Artifacts

**Before M6 Complete:**

1. **Deployment Scripts:**
   - `deploy-client.sh` (initial deploy)
   - `upgrade-client.sh` (upgrade existing)
   - `backup.sh` (manual backup)
   - `restore.sh` (disaster recovery)

2. **Runbooks** (see Appendix B for templates):
   - Deployment runbook
   - Upgrade runbook
   - Rollback runbook

3. **Monitoring:**
   - Health check endpoint (`/health/`)
   - Uptime monitoring (external service)
   - Error tracking (Sentry or equivalent)

4. **Documentation:**
   - "What broke last time" log per site
   - Post-mortem template for incidents
   - Common issues + solutions knowledge base

---

### 6.4 Multi-Version Testing Policy

**Current Line (e.g., 0.6.x during M6):**
- Full test suite (unit + integration)
- CI runs on every commit
- Manual testing on staging before production

**Older Lines (e.g., 0.5.x after M6 ships):**
- Weekly smoke checks:
  - Health endpoint returns 200
  - Homepage renders without errors
  - Admin login works
  - Lead submission works
- Security patches applied within 7 days
- No new feature work
- Release-check gate mandatory for any patch

**Rationale:** Maintains confidence without carrying full regression burden forever.

---

## 7. AI-Assisted Audit Layer (Optional — M8)

### 7.1 Purpose

Provide a **pre-publish and pre-deploy safety net** to answer:

> "Did I forget anything obvious?"

**NOT:**
* Auto-publishing
* Schema mutation
* Silent edits
* Content generation

---

### 7.2 Minimal Viable Scope (If Pursued)

**Phase 1: Read-Only Introspection API**

Expose structured, factual endpoints:

```
GET /api/introspection/site
GET /api/introspection/pages
GET /api/introspection/seo-completeness
GET /api/introspection/content-gaps
```

**Example Response:**
```json
{
  "issues": [
    {
      "severity": "warning",
      "category": "seo",
      "message": "3 pages missing meta descriptions",
      "pages": ["/about/", "/services/kitchens/", "/contact/"]
    },
    {
      "severity": "info",
      "category": "content",
      "message": "Home page hero section contains placeholder text",
      "location": "HomePage.hero_section"
    }
  ]
}
```

**Security Model:**
- API key authentication (one key per client project)
- Rate limiting: 100 requests/hour per key
- Audit logging: all requests logged
- Read-only: cannot modify data
- Scoped to single site (no cross-client access)

---

**Phase 2: Custom GPT Auditor**

- Uses OpenAPI actions spec
- Authenticated via API key
- Returns structured checklist:
  - Issues (must fix)
  - Warnings (should fix)
  - Suggestions (consider)
  - Severity levels (critical, high, medium, low, info)

**Example Prompts:**
- "Run pre-publish audit"
- "Check SEO completeness"
- "Check legal compliance baseline"
- "Find placeholder content"

**Out of Scope for Phase 2:**
- Any write operations
- Content suggestions
- Publishing automation

---

**Phase 3: Draft-Only Write Actions (Explicitly Deferred)**

If pursued (future):
- Create draft content only (never published)
- Never delete existing content
- Human must review and approve
- Audit trail of AI-generated content

**Gate:** Only consider Phase 3 after:
- [ ] Phase 1 + 2 proven valuable
- [ ] 6+ months production use
- [ ] Client feedback gathered
- [ ] Ethics review completed

---

## 8. Risk Management

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Platform drift** | Medium | High | Core frozen at 0.5.x, release checklist enforced |
| **Theme instability** | Medium | Medium | One reference theme first, others derive; performance gates |
| **M5 destabilization** | Low | Critical | No retrofitting; M5 frozen; LINTEL-v1 stays on M5 |
| **Tailwind bundle bloat** | Medium | Medium | PurgeCSS mandatory, bundle size budget, performance gates |
| **AI overreach** | Low | Medium | Read-only first, explicit scopes, optional feature |
| **Upgrade fear** | High | High | Repeated practice with live sites, runbooks, rollback rehearsals |
| **Over-engineering** | Medium | Medium | Features added only after real usage, strict scope discipline |
| **Theme/branding collision** | Low | Medium | Clear contract: SiteSettings for branding, themes for layout |
| **Breaking changes** | Medium | High | Strict versioning policy, migration guides mandatory |

---

## 9. Definition of "Client-Ready"

SUM Platform is considered **client-ready for external paying clients** when:

**Technical Gates:**
- [ ] 2+ sites deployed and upgraded successfully (minimum 2 upgrades per site)
- [ ] Blog + Dynamic Forms proven in production
- [ ] Themes system used by at least 2 sites
- [ ] Performance targets met consistently (Lighthouse ≥90 across all metrics)
- [ ] Zero critical bugs open for 30+ days

**Operational Gates:**
- [ ] Rollback procedure tested and documented
- [ ] Runbooks complete and proven
- [ ] Monitoring and alerting active
- [ ] "What broke last time" log shows declining issues
- [ ] Support process defined

**Confidence Gate:**
- [ ] You no longer hesitate before deploying
- [ ] You can explain upgrade process confidently
- [ ] You have recent example of successful recovery from failure

**Minimum Timeline:** 
- No earlier than 8 weeks after M7 completion
- No exceptions for "special" clients

---

## 10. Out of Scope (Explicit)

These are **deliberately deferred** beyond client-ready declaration:

* Theme marketplace
* Real-time AI editing
* Per-page theme switching
* Multi-cloud deployment (AWS, GCP, Azure)
* SaaS dashboard for clients
* Multi-tenant architecture
* White-label reselling
* Mobile app
* E-commerce integration
* Membership/login system
* Multi-language support

**Why Deferred:** Each would introduce significant complexity and distract from core stability goals. May be reconsidered post-1.0.0 based on client demand.

---

## 11. Open Questions / Decision Points

### 🟡 Needs Decision Before M6 Start:

1. **Tailwind PurgeCSS Strategy:**
   - Which purge mode? (production only vs always)
   - Which files to scan for class usage?
   - Safelist patterns for dynamic classes?

2. **Theme Distribution Method:**
   - Themes as part of sum_core package? (current assumption)
   - OR themes as separate packages (sum_theme_a, sum_theme_b)?
   - Affects init command and versioning

3. **Blog Category Depth:**
   - Single-level categories only? (simpler)
   - OR hierarchical categories? (more flexible)
   - Impacts data model

4. **Form File Upload Storage:**
   - Where do uploaded files go?
   - Size limits per file?
   - Retention policy?

### 🟢 Can Decide During Implementation:

5. **Dynamic Forms Field Validation:**
   - Use Wagtail's built-in validation?
   - OR custom validation rules system?

6. **AI Introspection API Authentication:**
   - API keys stored where? (env vars? database?)
   - Key rotation policy?

7. **Lead Management Status Pipeline:**
   - Fixed statuses or customizable per client?
   - Status change notifications?

---

## 12. Success Metrics (Post-MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **New site deployment time** | ≤2 days | From init to production (M6+) |
| **Core upgrade time** | ≤1 hour | Full upgrade including testing |
| **Theme performance** | ≥90 Lighthouse | All metrics, mobile |
| **Rollback time** | ≤30 minutes | From detection to restored |
| **Zero-downtime upgrades** | 100% | Via blue-green or similar |
| **Failed deployments** | <5% | Across all upgrade attempts |
| **Client satisfaction** | ≥4.5/5 | Post-delivery survey (when applicable) |

---

## 13. Final Principle

> **Confidence comes from repetition, not architecture.**

This plan optimizes for:

* **Muscle memory** — Do the same deploy process until boring
* **Safe failure** — Practice rollbacks, expect things to break
* **Boring correctness** — Prefer tested patterns over clever solutions
* **Long-term leverage** — Every hour spent on stability saves ten later

**Key Mindset:** You're building operational confidence, not just features.

---

## Appendix A: Compatibility Matrix

| Feature | 0.5.x (M5) | 0.6.x (M6) | 0.7.x (M7) |
|---------|------------|------------|------------|
| Token CSS | ✅ | ❌ | ❌ |
| Tailwind Themes | ❌ | ✅ | ✅ |
| Theme System | ❌ | ✅ | ✅ |
| Static Forms | ✅ | ✅ | ✅ |
| Dynamic Forms | ❌ | ❌ | ✅ |
| Blog | ❌ | ✅ | ✅ |
| Lead Management Pipeline | ❌ | ❌ | ✅ (late) |
| Core Pages | ✅ | ✅ | ✅ |
| StreamField Blocks | ✅ | ✅ | ✅ |
| Lead Capture | ✅ | ✅ | ✅ |
| SEO System | ✅ | ✅ | ✅ |
| Analytics | ✅ | ✅ | ✅ |

**Key:**
- ✅ = Available and supported
- ❌ = Not available
- 🚧 = In development
- ⚠️ = Deprecated

---

## Appendix B: Runbook Templates

### B.1 Deployment Runbook Template

```markdown
# Deployment Runbook: [CLIENT-NAME]

## Pre-Deployment

- [ ] Backup database
- [ ] Verify sum_core version in requirements.txt
- [ ] Check migration status locally
- [ ] Review changelog for breaking changes
- [ ] Notify stakeholders (if applicable)

## Deployment Steps

1. SSH into server: `ssh user@server`
2. Navigate to project: `cd /var/www/[client]/`
3. Activate venv: `source venv/bin/activate`
4. Pull latest code: `git pull origin main`
5. Install dependencies: `pip install -r requirements.txt`
6. Collect static files: `python manage.py collectstatic --noinput`
7. Run migrations: `python manage.py migrate`
8. Restart services: `sudo systemctl restart [client]-gunicorn`
9. Check logs: `sudo journalctl -u [client]-gunicorn -n 50`

## Verification

- [ ] Health endpoint returns 200: `curl https://[domain]/health/`
- [ ] Homepage loads without errors
- [ ] Admin login works
- [ ] Lead form submission works
- [ ] Check Sentry for new errors

## Post-Deployment

- [ ] Update deployment log
- [ ] Note any issues encountered
- [ ] Update "what broke last time" if applicable

## Rollback Procedure

If deployment fails:
1. Restore from backup: `./restore.sh [client] [backup-file]`
2. Revert code: `git reset --hard [previous-commit]`
3. Restart services
4. Verify health
5. Document failure reason
```

---

### B.2 Upgrade Runbook Template

```markdown
# Upgrade Runbook: [CLIENT-NAME]

## Pre-Upgrade

- [ ] Review sum_core changelog: [LINK]
- [ ] Check for breaking changes
- [ ] Backup database: `./backup.sh [client]`
- [ ] Note current version: `pip show sum-core`
- [ ] Test upgrade in staging first

## Upgrade Steps

1. SSH into server
2. Navigate to project directory
3. Activate venv
4. Update requirements.txt: `sum-core==X.Y.Z`
5. Install new version: `pip install -r requirements.txt`
6. Review new migrations: `python manage.py showmigrations`
7. Run migrations: `python manage.py migrate`
8. Collect static files (if needed)
9. Restart services
10. Check logs for errors

## Verification

- [ ] Health check passes
- [ ] No new errors in Sentry
- [ ] Admin accessible
- [ ] Key pages render correctly
- [ ] Forms still submit
- [ ] No console errors

## Post-Upgrade

- [ ] Update version log
- [ ] Document any issues
- [ ] Monitor for 24 hours

## Rollback Procedure

If upgrade fails:
1. Stop services
2. Restore database backup
3. Revert requirements.txt to previous version
4. Reinstall dependencies
5. Restart services
6. Verify restoration successful
7. Document failure for investigation
```

---

### B.3 "What Broke Last Time" Log Template

```markdown
# Incident Log: [CLIENT-NAME]

## [Date] — [Brief Description]

**What Happened:**
[Describe the issue]

**Root Cause:**
[What actually caused it]

**Resolution:**
[How it was fixed]

**Prevention:**
[How to avoid this in future]

**Time to Resolve:**
[Duration from detection to fix]

**Impact:**
[Downtime, users affected, etc.]

---
```

---

### B.4 Post-Mortem Template

```markdown
# Post-Mortem: [INCIDENT-NAME]

**Date:** [Date]  
**Duration:** [X hours/minutes]  
**Severity:** [Critical/High/Medium/Low]  
**Responders:** [Names]

## Timeline

- **[Time]** — Issue detected
- **[Time]** — Investigation began
- **[Time]** — Root cause identified
- **[Time]** — Fix applied
- **[Time]** — Service restored
- **[Time]** — Monitoring confirmed stable

## What Went Wrong

[Detailed explanation]

## What Went Well

[What worked in the response]

## Action Items

- [ ] [Action 1] — Owner: [Name] — Due: [Date]
- [ ] [Action 2] — Owner: [Name] — Due: [Date]

## Lessons Learned

[Key takeaways]
```

---

## Appendix C: Frozen Components (Do Not Touch During M6-M7)

During M6-M7 feature development, the following remain **untouched** unless security-critical:

### Frozen in sum_core@0.5.x:
- [ ] `sum_core/leads/` — Lead model, forms, admin
- [ ] `sum_core/pages/` — Page type models (HomePage, ServicePage, etc.)
- [ ] `sum_core/blocks/` — All StreamField blocks
- [ ] `sum_core/seo/` — SEO mixins and meta tag generation
- [ ] `sum_core/analytics/` — GA4/GTM integration
- [ ] Token CSS system — Legacy, stable, do not modify
- [ ] Base templates (unless new theme system requires hooks)

### Rationale: 
Moving targets kill confidence. Features ship in new versions; core stays stable.

---

## Appendix D: Version Tagging Convention

```bash
# Example version progression

0.5.0  # MVP complete (M5)
0.5.1  # Security fix
0.5.2  # Bug fix (Lead email notification)

0.6.0  # Theme system + Blog (M6)
0.6.1  # Theme A refinements
0.6.2  # Blog pagination fix

0.7.0  # Dynamic Forms (M7)
0.7.1  # Form validation improvements
0.7.2  # Security update

1.0.0  # Client-ready declaration
```

**Tagging Rules:**
- Every release gets a git tag: `git tag -a v0.6.0 -m "Release 0.6.0: Theme system + Blog"`
- Tag message includes changelog summary
- Tags pushed to remote: `git push origin v0.6.0`
- Releases published on GitHub with full changelog

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | [Original date] | Initial post-MVP expansion draft |
| 2.0 | December 16, 2025 | Comprehensive revision with patch corrections |

**Changelog (v2.0):**
- Added CSS transition strategy (prevents M5 destabilization)
- Clarified theme/branding architecture contract
- Added LINTEL migration strategy
- Defined feature freeze policy and version mapping
- Added multi-version testing policy
- Updated infrastructure (Caddy vs Nginx)
- Clarified CRM/Lead Management naming
- Added comprehensive runbook templates
- Tightened AI layer scope (truly optional)
- Added compatibility matrix
- Added frozen components list
- Added open questions section
- Added detailed operational requirements

---

**Review Status:** ✅ Ready for implementation planning

**Next Steps:**
1. Review open questions (Appendix 11) and make decisions
2. Begin M6 planning with Theme A design
3. Set up LINTEL-v2 project structure
4. Create deployment scripts and runbooks from templates

---

*This document represents the authoritative post-MVP expansion plan. Reference this document when planning M6+ work. Update when architectural decisions change.*