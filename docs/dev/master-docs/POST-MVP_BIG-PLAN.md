# **SUM Platform — Post-MVP Expansion PRD (v4.1)**

**Status:** Final Pre-M6  
**Version:** 4.1  
**Date:** December 17, 2025  
**Applies after:** Milestone 5 (Platform Factory)  
**Audience:** Platform maintainer + AI agents  
**Purpose:** Define controlled expansion of SUM Platform after MVP freeze, without destabilising core guarantees.

---

## Document Changes from v4.0

| Change | Category | Impact |
|--------|----------|--------|
| **P0.1: Blog category locked to FK** | Critical | Removes CharField option, eliminates decision contradiction |
| **P0.2: Zero-downtime upgrades clarified** | Critical | Realistic pre-1.0 standard, defers blue/green to post-1.0 |
| **P1.1: Cross-reference fixed** | Documentation | Blog CTA reference corrected (6.1.1 → 7.1.1) |
| **P1.2: Per-client DB clarified** | Architecture | Operator default vs platform requirement explicit |
| **P1.3: File retention mechanism defined** | Operations | Policy-only in v1, automated cleanup deferred |
| **P1.4: Staging admin protection added** | Security | Admin exposure baseline for preview sites |
| **P1.5: Sage & Stone dual role clarified** | Practice | Consumer vs demo distinction preserved |

---

## 0. Naming & Roles Clarification

**Understanding the Distinction:**

- **SUM** is the platform name. It does **not** stand for anything.
- `sum_core` is the core package within the SUM platform repository.
- **LINTEL Digital** is the company/operator that uses SUM to deliver websites and marketing services to clients.
- Client sites (e.g., Sage & Stone, LINTEL's own marketing site, future client sites) are **consumers of SUM**, not part of the platform itself.

**Why This Matters:**

This distinction prevents conflation between:
- **Platform roadmap concerns** (SUM capabilities, features, stability)
- **Operator/agency concerns** (LINTEL Digital's business operations, sales tooling, client delivery)

**Clear Conceptual Boundary:**
```
SUM = Platform (the product we're building)
LINTEL Digital = Operator (the company using SUM)
Sage & Stone, LINTEL's site, etc. = Consumers (sites built with SUM)
```

When discussing roadmap, features, and technical decisions, we're talking about **SUM**. When discussing deployment to clients, marketing, or sales processes, we're talking about **LINTEL Digital's operations**.

---

## 1. Critical Correction: LINTEL Launch Reality

### ❌ Previous Assumption (WRONG)
- "LINTEL-v1 exists now on M5 stack"
- "LINTEL-v1 serves as rollback reference"
- "LINTEL-v2 migrates from LINTEL-v1"

### ✅ Reality
- **LINTEL is not launched yet** (no production site exists)
- Therefore: **no v1 → v2 migration path**
- Therefore: **no existing rollback reference site**

### Impact on Plan
This correction eliminates false dependency chains and imaginary rollback baselines. The plan now reflects actual sequencing and uses a different site as the first real consumer.

---

## 2. Context & Motivation

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

* feature growth (blog, forms, lead management)
* design evolution (themes)
* operational confidence (deploy & upgrade practice)
* AI-assisted review (read-only, not automation)

---

## 3. Guiding Principles (Non-Negotiable)

### 3.1 Core Stability First

* `sum_core@0.5.x` remains installable, versioned, and **frozen** for feature work
* Security and critical fixes only for 0.5.x line
* No feature may "only work" in a harness or demo project
* New features ship in new minor versions (0.6.x, 0.7.x, etc.)

### 3.2 Real Consumers Only

* New features are exercised via **real client projects** scaffolded with `sum init`
* "Real" means: actual business entity, production-grade content, real traffic intent
* **First real consumer is Sage & Stone Kitchens** (not LINTEL)
* No bespoke test projects or synthetic demos

### 3.3 Practice Before Promises

* At least **3–4 full deploy + upgrade cycles** completed before onboarding external paying clients
* Each cycle must include: deploy, content updates, core upgrade, verification
* Rollback procedure rehearsed at least once per site
* "What broke last time" notes maintained

### 3.4 AI is an Auditor First

* AI integrations start as **read-only reviewers**, not content mutators
* Draft-only write actions may be added later, explicitly and narrowly
* Never auto-publish, never schema mutation, never silent edits

### 3.5 Themes are Fixed Per Site

* Theme selection happens at `sum init` time
* No Wagtail admin theme switching
* Changing a theme is a developer action (requires project setup change)
* Themes remain stable once selected

### 3.6 Breaking Changes Policy

* Breaking changes ONLY at major versions (0.x → 1.0, etc.)
* Minor version bumps (0.5.x → 0.6.0) may introduce incompatibilities if documented heavily
* Patch releases (0.5.1 → 0.5.2) NEVER break existing functionality
* All breaking changes require migration guide
* 1.0.0 = stability contract begins (semantic versioning enforced)

---

## 4. Loop Sites Model (Replaces LINTEL v1/v2 Narrative)

### 4.1 The Problem with Previous Plan

The v2 plan incorrectly assumed LINTEL-v1 was live and could serve as a rollback reference. This created a false dependency chain and imaginary migration path.

### 4.2 Loop Sites Strategy

**Purpose:** Validate end-to-end pipeline through real consumer sites in controlled sequence.

---

### Loop Site A: Sage & Stone Kitchens (FIRST REAL CONSUMER)

**Purpose:** First site to receive Wagtail + Theme + Blog + Dynamic Forms treatment.

**Why First:**
- Real business with real content requirements
- Validates the complete pipeline: theme wiring, blog UI, dynamic forms, deploy, backups, upgrade paths
- Lower stakes than LINTEL (internal client vs showcase site)
- Designed UI artifacts already exist (blog_list.html, blog_article.html)

**Important:** Sage & Stone is treated as a **real consumer site for platform validation**, regardless of whether it is later reused as a **sales demo concept**. This ensures Loop Sites model remains stable and validation genuine.

**Deliverables from Sage & Stone Loop:**
- [ ] Theme A proven with real content
- [ ] Blog listing + article pages working
- [ ] Dynamic Forms in multiple placements (homepage CTA, newsletter, callback, quote)
- [ ] First successful deploy cycle
- [ ] First successful upgrade cycle (0.6.0 → 0.6.1)
- [ ] Rollback rehearsal completed
- [ ] Documentation of "what broke" and resolutions

**Gate to Loop Site C:** Must complete minimum 2 deploy + upgrade cycles successfully.

---

### Loop Site B: test_project v2 (HARNESS ONLY — NOT A REAL CONSUMER)

**Purpose:** Fast validation of integration wiring in CI/development.

**Explicitly NOT:**
- A real site
- A rollback reference
- A consumer for practice purposes

**Why Separate:** Keeps test harness distinct from real consumer validation.

**Usage:**
- CI integration tests
- Local development
- Quick validation of new blocks/pages
- Never deployed as a real site

---

### Loop Site C: LINTEL (LAUNCH LAST)

**Purpose:** Internal showcase site, built after pipeline is proven boring.

**Why Last:**
- Benefits from hardened theming/blog/forms patterns learned from Sage & Stone
- No false v1/v2 migration narrative
- Higher stakes (showcase vs internal client) means higher quality bar

**Prerequisites:**
- [ ] Sage & Stone completed minimum 2 successful upgrade cycles
- [ ] Theme system validated as stable
- [ ] Blog system validated as stable
- [ ] Dynamic Forms validated in production
- [ ] Performance targets consistently met
- [ ] Deploy/upgrade process is boring (not stressful)

**Gate:** LINTEL does not launch until operational confidence is high.

---

### 4.3 Version Naming Clarification

**Design/Wireframe Iterations:**
- Use "wireframe v1", "wireframe v2", "design iteration 3"
- These are design artifacts, not released sites

**Released Site Versions:**
- Reserve "v1", "v2" for actual production launches
- Example: "LINTEL v1" only applies after LINTEL is launched
- Before launch, refer to "LINTEL project" or "LINTEL build"

**Rationale:** Prevents "wireframe v2" from becoming "production v2" by linguistic drift.

---

### 4.4 Environment & Domain Conventions

**Purpose:** Lock in shared mental model for deployment environments.

**Convention Tiers:**

| Environment | Domain Pattern | Purpose | Security |
|-------------|----------------|---------|----------|
| **Company/Public Site** | `linteldigital.com` | LINTEL Digital's marketing site | Public |
| **Client Preview/Staging** | `clientname.lintel.site` | Auth-protected client previews | Auth + noindex |
| **Internal Dev/Experiments** | `*.lintel.live` | Development and testing | Never client-facing |
| **Production Client Sites** | Client-owned domains | Final production sites | Client-controlled |

**Key Properties:**

**Client Preview (`*.lintel.site`):**
- HTTP Basic Auth protected
- `<meta name="robots" content="noindex, nofollow">`
- Disposable (can be torn down and rebuilt)
- Used for client review and approval
- May share infrastructure with other preview sites
- **Wagtail admin must not be publicly exposed without protection** (basic auth, IP allowlist, VPN, or equivalent)

**Internal Dev (`*.lintel.live`):**
- Developer access only
- Never shown to clients
- Used for experimental features, testing, CI/CD
- Can be unstable

**Note:** These conventions support the SUM platform workflow but are **not hard platform requirements**. They represent LINTEL Digital's operational choices as the platform operator.

---

### 4.5 Demo Site Scope Clarification

**Important Boundary:**

A **"live demo site"** where prospects can log into Wagtail, edit content, with periodic resets is planned.

**However:**
- This is **LINTEL Digital Ops / Sales tooling**
- It is **out of scope** for the SUM platform Post-MVP roadmap
- SUM will enable it (as it enables any site), but does not explicitly deliver it as a platform milestone

**Why This Matters:**

Agency sales tooling should not leak into platform scope. SUM's job is to provide the capabilities; LINTEL Digital's job is to use those capabilities for sales, marketing, and client delivery.

**Platform enablement ≠ Platform deliverable**

---

## 5. Post-MVP Milestones Overview

### Milestone 6 — Themes & Delivery Pipeline

**Goal:** Prove the platform can deliver real sites safely with new presentation layer.

**Core Deliverables:**
* Theme system v1 (Tailwind-first, init-time selection)
* Theme A (reference theme, powers Sage & Stone)
* Blog v1 (first vertical slice feature, satisfies Sage & Stone UI contract)
* Dynamic Forms v1 (rapid iteration, multi-placement)
* Caddy deployment golden-path
* Staging + production workflow
* **Sage & Stone deployed "for real"** (first consumer loop)

**Version:** `sum_core@0.6.x`

---

### Milestone 7 — Platform Practice & Feature Evolution

**Goal:** Build confidence through repetition and controlled feature expansion.

**Core Deliverables:**
* Theme B + Theme C (prove multi-theme architecture)
* Core upgrade propagation across Sage & Stone (minimum 2 upgrades)
* Lead Management v1 (pipeline, status, notes) — later in milestone
* **LINTEL project initiated** (if Sage & Stone proven)

**Version:** `sum_core@0.7.x`

---

### Milestone 8 — LINTEL Launch & AI Audit (Optional)

**Goal:** Launch showcase site and optionally add AI audit layer.

**Core Deliverables:**
* LINTEL launched to production (after proven patterns)
* AI-Assisted Audit Layer (optional) - read-only introspection

**Version:** `sum_core@0.8.x` (optional)

---

## 6. Architecture & Transition Strategy

### 6.1 CSS Transition Strategy

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
✓ No M5 sites exist yet; new sites in M6+ use themes
✓ Rollback plan: if Tailwind fails perf/a11y gates, Theme A is dropped or reworked without touching M5 CSS
```

**Why this matters:** Guarantees M5 remains shippable while experimenting with theme infrastructure.

**Performance Gate:** Tailwind-based Theme A must meet same Lighthouse targets as M5:
- Performance: ≥90
- Accessibility: ≥90
- SEO: ≥90
- Bundle size: CSS ≤100kb (compressed)

---

### 6.2 Theme vs Branding Contract

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
themes/theme_a/
├── theme.json
├── templates/
│   ├── theme/
│   │   ├── base.html
│   │   ├── home_page.html
│   │   └── includes/
│   └── sum_core/                  # optional theme-level overrides for core templates
├── static/
│   └── theme_a/
│       ├── css/
│       │   ├── input.css          # Tailwind source (do not edit main.css directly)
│       │   └── main.css           # compiled Tailwind output (committed)
│       └── js/
│           └── main.js
└── tailwind/
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── package.json
    └── npm-shrinkwrap.json
```

---

### 6.3 Codebase Structure Alignment

**Critical Constraint:** All Post-MVP additions must fit existing repo layout from `CODEBASE-STRUCTURE.md`.

**Where Features Live:**

| Feature | Location | Notes |
|---------|----------|-------|
| **Blog Pages** | `sum_core/pages/` | BlogIndexPage, BlogPostPage models |
| **Blog Templates** | `sum_core/templates/sum_core/pages/` | blog_index_page.html, blog_post_page.html |
| **Dynamic Forms Model** | `sum_core/forms/` | FormDefinition as Wagtail Snippet |
| **DynamicFormBlock** | `sum_core/blocks/` | StreamField block for form placement |
| **Theme Templates** | `themes/theme_a/templates/` | Theme-specific layouts (copied into client at init) |
| **Theme Styles** | `themes/theme_a/static/` | Tailwind builds (copied into client at init) |

**Forbidden:**
- ❌ New top-level packages like `sum_blog` or `sum_forms_dynamic`
- ❌ Parallel directory structures that duplicate existing concerns
- ❌ Feature-specific apps outside `sum_core/` structure

**Rationale:** Prevents architectural drift and maintains coherent codebase evolution.

---

### 6.4 Version → Capability Mapping

| Version | Capabilities | Status | Notes |
|---------|-------------|--------|-------|
| **0.5.x** | MVP platform factory (M0–M5) | FROZEN | Token CSS, static forms, core pages only |
| **0.6.x** | Theme system + Blog v1 + Dynamic Forms v1 | Active | Sage & Stone launch, first deploy practice loops |
| **0.7.x** | Multi-theme validation + Lead Management v1 | Planned | LINTEL initiated if gates passed |
| **0.8.x** | LINTEL launch + AI Audit (optional) | Future | After proven patterns |
| **1.0.0** | Client-ready declaration | Future | After repeated deploy+upgrade cycles proven |

**Core Stability Contract:**
- `0.5.x` = frozen; only security/critical fixes
- `0.6.x` = new features allowed (themes, blog, dynamic forms)
- `0.7.x` = feature refinement (multi-theme, lead management)
- No feature backports to older lines unless explicitly approved (rare)
- Anything experimental ships behind a flag or in a new minor line, not in patch releases

---

## 7. Feature Roadmap (Post-MVP)

### 7.1 Blog v1 (First Vertical Slice)

**Rationale:** Chosen first because it exercises the full templating + theme system with minimal business-critical risk, allowing the theme architecture to stabilize before touching lead capture.

**UI Contract (Sage & Stone HTML Artifacts):**

Must support these UI elements from compiled HTML design:

**Listing UI (blog_list.html):**
- [ ] Category label/badge on cards (single-level taxonomy)
- [ ] Published date displayed on cards
- [ ] Reading time displayed on cards
- [ ] Title, excerpt/summary on cards
- [ ] Featured image on cards
- [ ] Pagination controls

**Article UI (blog_article.html):**
- [ ] Featured image/hero section
- [ ] Title rendering
- [ ] Published date display
- [ ] Category label display
- [ ] Reading time display
- [ ] Body content (StreamField)
- [ ] CTA placements (using DynamicFormBlock — see Section 7.1.1)

**Data Model:**
- `BlogIndexPage` (listing with pagination)
- `BlogPostPage` (individual posts)
- **Category:** ForeignKey to Category snippet (single-level only; no parent/child hierarchy)
- Published date (DateTimeField)
- Reading time (IntegerField, calculated or stored)
- Featured image (ImageField)
- Excerpt/summary (TextField, optional, fallback to first N chars of body)
- Body (StreamField, reuses existing blocks)

**Technical Implementation:**
- Pages live in `sum_core/pages/blog_index_page.py`, `sum_core/pages/blog_post_page.py`
- Templates in `sum_core/templates/sum_core/pages/`
- Reading time can be calculated on save or computed property
- Reuses existing SEO system from M4 (no new SEO infrastructure)
- RSS feed via Wagtail contrib (optional)
- Sitemap integration automatic via existing system

**Non-Goals for v1:**
- Multi-author support
- Comment system
- Editorial calendar
- Content versioning beyond Wagtail default
- Hierarchical categories
- Tag system beyond single category

**Definition of Done:**
- [ ] Blog pages creatable in Wagtail admin
- [ ] Listing pagination works
- [ ] Category filtering works (if implemented)
- [ ] Featured images display correctly
- [ ] Reading time displays correctly
- [ ] SEO tags render correctly (reuses existing system)
- [ ] Lighthouse targets met (≥90 across all metrics)
- [ ] Deployed to Sage & Stone and used for real blog posts
- [ ] Templates match Sage & Stone UI contract

---

#### 7.1.1 Blog CTAs Must Use Dynamic Forms

**Critical Constraint:** Blog pages embed CTAs (newsletter/waitlist, callback, quote requests) using **DynamicFormBlock selecting FormDefinition**, not blog-specific form code.

**Rationale:**
- Avoids fragmentation
- Keeps lead capture consistent across platform
- One forms system serves all placements (homepage, blog, service pages, etc.)

**Implementation:**
- BlogPostPage.body includes DynamicFormBlock as one of its available blocks
- DynamicFormBlock selects from available FormDefinitions (site-scoped)
- No special "blog form" model or handling
- All blog form submissions follow same Lead capture pipeline

---

### 7.2 Dynamic Forms v1 (Enhanced Scope)

**Rationale:** Removes reliance on static forms; enables rapid iteration across multiple form placements per site. Critical for real client usage where form requirements vary and evolve.

**Driver:** Rapid iteration — add/remove/reorder questions and sections based on feedback without code changes.

**Use Cases (Multiple Placements Per Site):**
- Homepage CTA form
- Newsletter/waitlist signup
- Callback request
- Quote request
- Service-specific inquiry forms
- Blog newsletter signup
- Footer contact form

**Scope:**

**FormDefinition Model** (Wagtail Snippet, site-scoped):
- Name (for admin reference)
- Form fields (StreamField of field blocks)
- Success message
- Email notification settings
- Webhook settings
- Active/inactive toggle
- Created/modified timestamps

**Field Types (StreamField Blocks):**
- Text input (single line)
- Email input (with validation)
- Phone input (with optional formatting)
- Textarea (multi-line)
- Select/dropdown
- Checkbox (single)
- Checkbox group (multiple)
- Radio buttons
- File upload (basic, with size limits)
- Section heading (for organization)
- Help text block (for instructions)

**First-Class v1 Capabilities (Elevated):**
- [ ] **Clone/Duplicate FormDefinition** — Copy existing form as template for new one
- [ ] **Active toggle** — Deactivate forms without deleting (audit trail)
- [ ] **Multiple forms on same page** — No technical limitation on placement count
- [ ] **Form versioning** — Keep old definitions for audit/rollback (via active toggle + timestamps)

**Rendering:**
- Runtime Django Form generation (always current; no codegen)
- Forms rendered via DynamicFormBlock in page StreamFields
- DynamicFormBlock selects FormDefinition + local presentation config (inline, modal, sidebar, etc.)

**Submission Handling:**
- Writes to same Lead model (no Lead schema change in v1)
- Attribution captured (UTM, referrer, landing page)
- Email notifications (to admin + optional auto-reply)
- Webhook firing (Zapier, HubSpot)
- Admin review interface (reuses existing Lead admin)

**Backwards Compatibility Contract:**
```
✓ Existing static forms remain supported and untouched
✓ Dynamic Forms v1 writes to the same Lead model (no Lead schema change in v1)
✓ Form builder creates new form types only
✓ Migration of existing forms is out of scope for v1
✓ Static forms and dynamic forms coexist peacefully
```

**Technical Notes:**
- FormDefinition as Wagtail Snippet (site-scoped, reusable)
- Lives in `sum_core/forms/models.py` (alongside existing form handling)
- DynamicFormBlock lives in `sum_core/blocks/forms.py`
- Uses `wagtail.contrib.forms` patterns as foundation
- Email sending via existing `sum_core/integrations/email.py`
- Webhook integration preserved (existing infrastructure)

**Non-Goals for v1:**
- Multi-step forms
- Conditional logic (show field X if field Y = value)
- Payment integration
- Advanced CAPTCHA (consider for v1.1, basic honeypot/rate limit sufficient)
- A/B testing
- Heavy UI form builder (StreamField provides editor-friendly UX)

**Definition of Done:**
- [ ] FormDefinition creatable as Wagtail Snippet
- [ ] All field types work and validate
- [ ] DynamicFormBlock selectable in page StreamFields
- [ ] Submissions save to Lead model
- [ ] Email notifications send
- [ ] Webhooks fire correctly
- [ ] Clone/duplicate form works
- [ ] Active toggle works (forms can be deactivated)
- [ ] Multiple forms on same page tested
- [ ] Backwards compatible with existing static forms
- [ ] Deployed to Sage & Stone with at least 3 distinct form placements
- [ ] Used in blog (via DynamicFormBlock)

---

### 7.3 Lead Management v1 (Deferred to Late M7)

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

**Corrected Roadmap Labels:**
```
✓ Lead Capture (MVP) = M3 deliverable, working now (static forms)
✓ Lead Capture Enhancement = Dynamic Forms v1 (M6)
✓ Lead Management v1 = Status pipeline, notes (late M7)
✓ Lead Management v2 = Future, TBD
```

---

## 8. Deployment & Upgrade Practice

### 8.1 Practice Requirements

Before onboarding external **paying clients**:

**Minimum Practice Requirements:**
- [ ] Sage & Stone site running (Loop Site A)
- [ ] Sage & Stone undergoes **minimum 2 core upgrades** (0.6.0 → 0.6.1 → 0.6.2, etc.)
- [ ] All migrations apply cleanly (zero data loss)
- [ ] Rollback procedure rehearsed at least once on Sage & Stone
- [ ] "What broke last time" notes maintained and reviewed
- [ ] Runbooks proven and updated after each cycle
- [ ] At least **one additional site** launched (LINTEL or another client) before external paying clients

**Each Deploy/Upgrade Cycle Must Include:**
1. Pre-deployment checklist completion
2. Database backup
3. Deployment execution
4. Smoke tests (health, homepage, admin login, form submission)
5. Verification checklist
6. Post-deployment notes (what went well, what didn't)

---

### 8.2 Infrastructure Updates

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

**Database Policy:** LINTEL Digital Ops uses **one database per site by default** for isolation, but SUM as a platform supports either **per-site database** or **shared database** deployments. The platform is agnostic; database strategy is an operator choice.

**Infrastructure Location:** `infrastructure/caddy/`, `infrastructure/systemd/`, `infrastructure/scripts/`

---

### 8.3 Required Operational Artifacts

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

### 8.4 Multi-Version Testing Policy

**Current Line (e.g., 0.6.x during M6):**
- Full test suite (unit + integration)
- CI runs on every commit
- Manual testing on staging before production

**Older Lines (e.g., 0.5.x after M6 ships):**
- Weekly smoke checks:
  - Health endpoint returns 200
  - Test project homepage renders without errors
  - Admin login works
  - Lead submission works (if applicable)
- Security patches applied within 7 days
- No new feature work
- Release-check gate mandatory for any patch

**Rationale:** Maintains confidence without carrying full regression burden forever.

---

## 9. Workflow: Static HTML Wireframes are Design Artifacts

**Critical Clarification:** Static HTML wireframes (produced via builder/Jinja/any tool) are **design references**, not conversion targets.

**Workflow:**

```
1. Design Phase
   ├─ Create static HTML wireframes (Jinja, builder, hand-coded, etc.)
   ├─ These are design artifacts showing layout, content, interactions
   └─ Purpose: visual reference, client approval, content structure

2. Wagtailification Phase
   ├─ Implement directly in Django/Wagtail templates
   ├─ Reference HTML design artifacts (like referencing Figma)
   ├─ No requirement to "convert Jinja → Django"
   └─ Build templates against the design reference
```

**No Conversion Requirement:**
- Wireframes may use Jinja, static site generators, page builders, or any prototyping tool
- Wagtail templates are **direct implementation** against the HTML reference
- Conversions are optional convenience, not a required plan step

**Rationale:**
- Keeps prototyping lightweight
- Avoids costly translation work that doesn't create product value
- Same approach as designing in Figma then implementing in React

**Example (Sage & Stone):**
- `blog_list.html` and `blog_article.html` are design artifacts (compiled HTML)
- Wagtail templates (`blog_index_page.html`, `blog_post_page.html`) implement the design
- No Jinja → Django conversion; just reference the HTML for layout/structure

---

## 10. AI-Assisted Audit Layer (Optional — M8)

### 10.1 Purpose

Provide a **pre-publish and pre-deploy safety net** to answer:

> "Did I forget anything obvious?"

**NOT:**
* Auto-publishing
* Schema mutation
* Silent edits
* Content generation

---

### 10.2 Minimal Viable Scope (If Pursued)

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

## 11. Risk Management

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Platform drift** | Medium | High | Core frozen at 0.5.x, release checklist enforced |
| **Theme instability** | Medium | Medium | One reference theme first, others derive; performance gates |
| **M5 destabilization** | Low | Critical | No retrofitting; M5 frozen; no live M5 sites to break |
| **Tailwind bundle bloat** | Medium | Medium | PurgeCSS mandatory, bundle size budget, performance gates |
| **Sage & Stone delays** | Medium | High | Start parallel work on test_project; LINTEL can absorb delays |
| **Dynamic Forms scope creep** | Medium | Medium | Strict v1 scope; defer conditional logic, multi-step, A/B testing |
| **Blog UI contract mismatch** | Low | Medium | Explicit checklist from HTML artifacts; validation before launch |
| **AI overreach** | Low | Medium | Read-only first, explicit scopes, optional feature |
| **Upgrade fear** | High | High | Repeated practice with live sites, runbooks, rollback rehearsals |
| **Over-engineering** | Medium | Medium | Features added only after real usage, strict scope discipline |
| **Theme/branding collision** | Low | Medium | Clear contract: SiteSettings for branding, themes for layout |
| **Breaking changes** | Medium | High | Strict versioning policy, migration guides mandatory |

---

## 12. Definition of "Client-Ready"

SUM Platform is considered **client-ready for external paying clients** when:

**Technical Gates:**
- [ ] Sage & Stone deployed and upgraded successfully (minimum 2 upgrades)
- [ ] LINTEL deployed (or second client site, if LINTEL delayed)
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
- No earlier than 8 weeks after M6 completion (Sage & Stone launch)
- No exceptions for "special" clients

---

## 13. Out of Scope (Explicit)

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

## 14. Resolved Decisions & Remaining Questions

### ✅ DECIDED (Locked for M6):

**1. Tailwind PurgeCSS Strategy**

**Decision:**
- Purge in **production builds only**
- Scan all Django templates (including themes) and any JS that contains class strings
- Use a **minimal safelist** only where dynamic class generation is unavoidable

**Rationale:** Keeps development experience fast while ensuring production bundle is optimized.

---

**2. Theme Distribution Method**

**Decision:**
- Canonical theme sources live at repo root `themes/` (Theme Architecture Spec v1).
- `sum init --theme <slug>` copies the selected theme into the client project at `clients/<client>/theme/active/`.
- Bundling themes inside the CLI package is optional later (once multiple themes exist and real friction is felt).

**Rationale:** Simpler distribution and versioning; avoids premature abstraction.

---

**3. Blog Category Implementation**

**Decision:**
- Use a **single-level Category snippet** (FK to Category model)
- No hierarchical categories in v1
- Category model: name, slug, description (optional)

**Rationale:** Flexible enough for real use; simple enough to ship quickly.

---

**4. Form File Upload Storage (Dynamic Forms v1)**

**Decision:**
- Store under `MEDIA_ROOT/form-uploads/`
- Default **5MB per file limit**
- Max **3 files per submission** (configurable)
- Default **90-day retention**, configurable via settings
- Admin warning text when viewing old submissions past retention period

**Retention Enforcement (v1):** Retention is a **documented policy** in v1; automated cleanup (via Celery beat or cron) is explicitly **deferred** to post-v1. Manual cleanup can be performed via Django management command if needed.

**Rationale:** Balances utility with storage management; clear expectations for users. Automated cleanup adds complexity; policy-first approach keeps v1 scope tight.

---

**5. Reading Time Calculation**

**Decision:**
- **Compute on save** and store as integer (minutes)
- Recompute automatically when article body changes (via save signal)
- Based on 200 words per minute (configurable via settings)

**Rationale:** Fast rendering; negligible staleness risk; simple implementation.

---

### 🟢 CAN DECIDE DURING IMPLEMENTATION:

**6. Dynamic Forms Field Validation**
- Use Wagtail's built-in validation?
- OR custom validation rules system?
- **Decision:** Implementation-time based on Wagtail patterns discovered

**7. AI Introspection API Authentication**
- API keys stored where? (env vars? database?)
- Key rotation policy?
- **Decision:** Implementation-time based on security requirements

**8. Lead Management Status Pipeline**
- Fixed statuses or customizable per client?
- Status change notifications?
- **Decision:** Implementation-time based on real client needs

**Rationale:** These are implementation details that don't block M6 start and benefit from seeing the code context.

---

## 15. Success Metrics (Post-MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **New site deployment time** | ≤2 days | From init to production (M6+) |
| **Core upgrade time** | ≤1 hour | Full upgrade including testing |
| **Theme performance** | ≥90 Lighthouse | All metrics, mobile |
| **Rollback time** | ≤30 minutes | From detection to restored |
| **Upgrade experience (pre-1.0)** | Predictable and low-risk | Brief restarts acceptable (<30-60s); near-zero perceived downtime where feasible |
| **Failed deployments** | <5% | Across all upgrade attempts |
| **Client satisfaction** | ≥4.5/5 | Post-delivery survey (when applicable) |
| **Forms per site** | 3-5 average | Multiple placements working |
| **Blog adoption** | 100% | All sites use blog feature |

**Note on Zero-Downtime:** True zero-downtime (blue/green deployments) is explicitly **deferred until post-1.0** unless a specific client requirement forces it. Pre-1.0 focus is on predictable, low-risk upgrades with clear rollback/runbook steps.

---

## 16. Final Principle

> **Confidence comes from repetition, not architecture.**

This plan optimizes for:

* **Muscle memory** — Do the same deploy process until boring
* **Safe failure** — Practice rollbacks, expect things to break
* **Boring correctness** — Prefer tested patterns over clever solutions
* **Long-term leverage** — Every hour spent on stability saves ten later

**Key Mindset:** You're building operational confidence, not just features.

---

## Appendix A: Compatibility Matrix

| Feature | 0.5.x (M5) | 0.6.x (M6) | 0.7.x (M7) | 0.8.x (M8) |
|---------|------------|------------|------------|------------|
| Token CSS | ✅ Active | 🟡 Legacy | 🟡 Legacy | 🟡 Legacy |
| Tailwind Themes | ❌ | ✅ | ✅ | ✅ |
| Theme System | ❌ | ✅ | ✅ | ✅ |
| Static Forms | ✅ | ✅ | ✅ | ✅ |
| Dynamic Forms | ❌ | ✅ | ✅ | ✅ |
| Blog | ❌ | ✅ | ✅ | ✅ |
| Lead Management Pipeline | ❌ | ❌ | ✅ | ✅ |
| AI Audit API | ❌ | ❌ | ❌ | ✅ (opt) |
| Core Pages | ✅ | ✅ | ✅ | ✅ |
| StreamField Blocks | ✅ | ✅ | ✅ | ✅ |
| Lead Capture | ✅ | ✅ | ✅ | ✅ |
| SEO System | ✅ | ✅ | ✅ | ✅ |
| Analytics | ✅ | ✅ | ✅ | ✅ |

**Legend:**
- ✅ = Available and actively used
- 🟡 = Available but legacy (not used for new themes; kept for compatibility)
- ❌ = Not available
- 🚧 = In development
- ⚠️ = Deprecated (will be removed)
- (opt) = Optional feature

**Token CSS Status:**
- **0.5.x:** Active and used by all templates
- **0.6.x+:** Legacy/available but not used by Tailwind themes
- Tailwind theme output is canonical for Theme A+
- Token CSS remains in codebase for backward compatibility
- No deletion planned; simply not used for new work

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
- [ ] Form submission works (test one form)
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
- [ ] Blog pages load (if applicable)
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

## Appendix C: Stability Guarantees & Additive Evolution

**The Stability Contract:**

### The 0.5.x Line is Frozen:
- The **`sum_core@0.5.x` release line** is in maintenance mode
- Only security and critical bug fixes
- No new features
- No breaking changes
- No refactors

**Why:** Sites pinned to 0.5.x must remain stable indefinitely.

---

### The 0.6.x+ Lines Support Additive Evolution:

The **0.6.x and later** release lines **may add new modules** under existing directories as long as:

✅ **Existing behavior does not change retroactively**
✅ **New code is additive, not mutative**
✅ **No breaking changes to existing APIs**

**Examples of Allowed Additive Work in 0.6.x+:**

| Directory | Frozen (0.5.x) | Additive (0.6.x+) |
|-----------|----------------|-------------------|
| `sum_core/pages/` | StandardPage, ServicePage (untouched) | BlogIndexPage, BlogPostPage (new models) |
| `sum_core/blocks/` | Existing blocks (untouched) | DynamicFormBlock (new block) |
| `sum_core/forms/` | Existing form handling (untouched) | FormDefinition model (new feature) |
| `themes/` | N/A | New directory (additive) |

**Examples of Forbidden Work:**

❌ Changing StandardPage field names  
❌ Modifying existing block schemas  
❌ Removing or renaming existing methods  
❌ Changing base template structure that breaks client overrides

---

### What This Means in Practice:

**For M6-M7 Development:**
- You **CAN** add new page types to `sum_core/pages/`
- You **CAN** add new blocks to `sum_core/blocks/`
- You **CAN** add new models to `sum_core/forms/`
- You **CANNOT** modify existing 0.5.x page types, blocks, or models
- You **CANNOT** delete or rename anything from 0.5.x

**Rationale:**

This approach provides:
- **Stability** for sites on 0.5.x (they never break)
- **Evolution** for new features in 0.6.x+ (additive growth)
- **Confidence** that upgrades are safe (backward compatible)

**Moving targets kill confidence. Additive evolution builds it.**

---

## Appendix D: Version Tagging Convention

```bash
# Example version progression

0.5.0  # MVP complete (M5)
0.5.1  # Security fix
0.5.2  # Bug fix (Lead email notification)

0.6.0  # Theme system + Blog + Dynamic Forms (M6)
0.6.1  # Theme A refinements + blog UI fixes
0.6.2  # Dynamic Forms clone feature + form validation improvements

0.7.0  # Multi-theme validation + Lead Management v1 (M7)
0.7.1  # Lead Management improvements
0.7.2  # Security update

0.8.0  # LINTEL launch + AI Audit (optional) (M8)

1.0.0  # Client-ready declaration
```

**Tagging Rules:**
- Every release gets a git tag: `git tag -a v0.6.0 -m "Release 0.6.0: Theme system + Blog + Dynamic Forms"`
- Tag message includes changelog summary
- Tags pushed to remote: `git push origin v0.6.0`
- Releases published on GitHub with full changelog

---

## Appendix E: Loop Sites Progression Checklist

### Sage & Stone (Loop Site A) — First Consumer

**Phase 1: Initial Launch**
- [ ] Project scaffolded via `sum init sage-and-stone`
- [ ] Theme A applied
- [ ] Blog pages created (minimum 3 posts)
- [ ] Dynamic Forms in 3+ placements (homepage, blog, footer)
- [ ] Content migrated from wireframes
- [ ] SEO configured
- [ ] Analytics wired
- [ ] Staging deployed
- [ ] Production deployed

**Phase 2: First Upgrade Cycle**
- [ ] Pre-upgrade backup taken
- [ ] Upgrade 0.6.0 → 0.6.1 completed
- [ ] Verification checklist passed
- [ ] "What broke" documented
- [ ] Rollback rehearsed (optional, but recommended once)

**Phase 3: Second Upgrade Cycle**
- [ ] Pre-upgrade backup taken
- [ ] Upgrade 0.6.1 → 0.6.2 completed
- [ ] Verification checklist passed
- [ ] "What broke" documented
- [ ] Lessons from first upgrade applied

**Gate Passed:** After Phase 3, Sage & Stone is validated consumer. LINTEL can begin.

---

### LINTEL (Loop Site C) — Launch Last

**Prerequisites (Must All Be True):**
- [ ] Sage & Stone completed Phase 3
- [ ] Theme system validated as stable
- [ ] Blog system validated as stable
- [ ] Dynamic Forms validated in production
- [ ] Performance targets consistently met on Sage & Stone
- [ ] Deploy/upgrade process is boring (not stressful)
- [ ] Runbooks proven and updated

**Launch Phases:**
- [ ] Project scaffolded via `sum init lintel`
- [ ] Theme selection (A, B, or C based on design)
- [ ] Content creation
- [ ] Staging deployment
- [ ] Production deployment
- [ ] First upgrade cycle
- [ ] Second upgrade cycle

**Result:** LINTEL benefits from proven patterns, launches with confidence.

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | [Original date] | Initial post-MVP expansion draft |
| 2.0 | December 16, 2025 | Comprehensive revision with patch corrections |
| 3.0 | December 17, 2025 | Critical corrections: LINTEL launch sequence, Loop Sites model, Dynamic Forms scope, Blog UI contract, workflow clarification, repo structure alignment |
| **4.0** | **December 17, 2025** | **Final alignment: Naming clarification, environment conventions, resolved decisions, fixed contradictions** |
| **4.1** | **December 17, 2025** | **Precision tightening: Fixed contradictions, clarified aspirations, locked decision consistency** |

**Changelog (v4.1 — Final Pre-M6):**
- **P0.1:** Fixed blog category inconsistency — removed CharField option, locked to FK to Category snippet (Section 7.1)
- **P0.2:** Clarified zero-downtime upgrades — changed from hard commitment to realistic pre-1.0 standard; brief restarts acceptable, blue/green deferred to post-1.0 (Section 15)
- **P1.1:** Fixed cross-reference typo — Blog CTA section reference corrected from 6.1.1 to 7.1.1 (Section 7.1)
- **P1.2:** Clarified per-client database as operator default vs platform requirement (Section 8.2)
- **P1.3:** Defined file retention enforcement mechanism — policy-only in v1, automated cleanup deferred (Section 14, Q4)
- **P1.4:** Added staging admin protection baseline — admin must not be publicly exposed on preview sites (Section 4.4)
- **P1.5:** Clarified Sage & Stone dual role — consumer validation vs sales demo distinction preserved (Section 4.2)

**Key Improvements:**
- Eliminated all "either/or" decisions for locked questions (Q1-Q5 and blog category)
- Realistic upgrade expectations set (no hidden blue/green infrastructure mandate)
- Prevents agent invention on ambiguous points (retention mechanism, DB policy, admin security)
- All cross-references accurate
- Sage & Stone validation purpose preserved

**Status:** ✅ **Final pre-M6** — No remaining contradictions or decision ambiguity

---

**Changelog (v4.0):**
- **Added Section 0:** Naming & Roles Clarification (SUM vs LINTEL Digital distinction)
- **Added Section 4.4:** Environment & Domain Conventions (linteldigital.com, *.lintel.site, *.lintel.live)
- **Added Section 4.5:** Demo Site Scope Clarification (sales tooling out of platform scope)
- **Resolved Section 14:** All Open Questions 1-5 decided and locked for M6
  - Q1: Tailwind PurgeCSS (production only, scan templates/JS, minimal safelist)
  - Q2: Theme distribution (inside sum_core for 0.6-0.7)
  - Q3: Blog categories (single-level FK to Category snippet)
  - Q4: Form file uploads (media/form-uploads/, 5MB limit, 90-day retention)
  - Q5: Reading time (compute on save, store as integer)
- **Fixed Appendix C:** "Frozen Components" → "Stability Guarantees" (clarifies 0.5.x frozen, 0.6+ additive)
- **Fixed Appendix A:** Compatibility Matrix (Token CSS shows as 🟡 Legacy in 0.6+, not ❌)
- Renumbered all sections after inserting new Section 0

**Key Improvements:**
- Clear conceptual boundary: SUM (platform) ≠ LINTEL Digital (operator)
- Explicit domain/environment conventions for deployment
- All blocking decisions made; M6 can proceed without ambiguity
- Internal contradictions resolved (additive evolution vs frozen directories)
- Token CSS correctly shown as legacy/available, not removed

---

## Conflicts/Risks from v2 → v3 Changes

### Low Risk Changes:
- ✅ LINTEL sequence correction (no code impact, planning only)
- ✅ Loop Sites model (clarifies, doesn't contradict)
- ✅ Workflow clarification (removes false requirement)
- ✅ Repo structure alignment (constraint, not change)

### Medium Risk Changes:
- ⚠️ Dynamic Forms scope expansion (more features in v1)
  - **Mitigation:** All new features (clone, active toggle) are low-complexity additions
  - **Benefit:** Higher leverage from v1, matches real operational needs

- ⚠️ Blog UI contract explicit requirements (reading time, category badges)
  - **Mitigation:** These are standard blog features, not complex
  - **Benefit:** Prevents "technically has blog but can't satisfy UI" mismatch

### No Conflicts with M5:
- All changes are additive (M6+)
- M5 remains frozen and untouched
- No retroactive requirements on completed work

---

**Review Status:** ✅ Ready for M6 implementation

**Next Steps:**
1. ~~Review Section 14 (Resolved Decisions) and make decisions~~ ✅ DONE (All Q1-Q5 locked)
2. Begin M6 planning with Theme A design (targeting Sage & Stone UI)
3. Set up Sage & Stone project — `sum init sage-and-stone`
4. Identify 5 form placements for Sage & Stone (homepage CTA, newsletter, callback, quote, blog)
5. Create deployment scripts from Appendix B templates
6. Set up domain infrastructure (sage-and-stone.lintel.site for preview)

---

*This document represents the authoritative post-MVP expansion plan. Reference this document when planning M6+ work. Update when architectural decisions change.*