# WO: Consent + Legal Pages + Starter Homepage (v0.6.0)

## Objective

- [ ] Cookie consent banner exists, is accessible, themeable, and supports Accept/Reject + “Manage cookies”
- [ ] Analytics (GTM/GA) are **never shipped in server-rendered HTML**; they load client-side **only** after consent (cache-safe)
- [ ] Legal pages (Terms/Privacy/Cookie Policy) are Wagtail-managed “article-style” pages with ToC support
- [ ] Starter homepage + seed routines create a decent first-run site (showroom + test_project) including legal pages + footer links
- [ ] Theme contracts, docs, and automated checks prevent regressions (banner DOM contract, ToC contract, etc.)

## Scope Boundaries

### In Scope

- Cookie banner UI + consent cookies + “Manage cookies”
- SiteSettings fields for banner + policy page links + consent version
- Client-side analytics loader (GTM/GA) gated by consent; HTML stays consent-neutral
- Legal pages as Wagtail pages (section-based ToC recommended)
- Seeder updates for showroom/test_project + starter profile
- Docs: wiring inventory + theme guide updates + dev notes

### Out of Scope

- Granular categories/preferences UI (CMP-style)
- Server-side consent audit logging / server-set HttpOnly consent endpoint
- Edge/CDN worker logic (made unnecessary by “no analytics scripts in HTML”)
- Full blog feature work (only reuse shared “article” layout patterns if already present)

## Affected Paths

```

core/sum_core/branding/models.py
core/sum_core/analytics/templatetags/analytics_tags.py
core/sum_core/templates/theme/base.html
core/sum_core/templates/sum_core/includes/cookie_banner.html
core/sum_core/static/sum_core/js/cookie_consent.js
core/sum_core/static/sum_core/js/analytics_loader.js  (or similar)
themes/theme_a/templates/... (banner + legal page template)
management commands (seed_showroom / starter seeding)
docs/... (wiring inventory / theme guide)
tests/...

```

## Subtasks

- [ ] #GH-0601 - Add consent-related fields to SiteSettings (per-site) + admin wiring
- [ ] #GH-0602 - Implement cookie banner include + a11y baseline + theme override contract
- [ ] #GH-0603 - Implement consent cookies + banner behavior + “Manage cookies” flow (JS)
- [ ] #GH-0604 - Implement client-side analytics loader (no scripts in HTML) + config emission
- [ ] #GH-0605 - Automated tests: consent flows, multisite settings, theme contract checks (+ optional E2E)
- [ ] #GH-0606 - Legal pages as CMS “article” pages with Section-based ToC + Theme A template support
- [ ] #GH-0607 - Seeder/starter profile updates: starter homepage + legal pages + footer links + idempotency
- [ ] #GH-0608 - Docs updates: wiring inventory + theme guide + developer notes for contracts

## Merge Plan

### Merge Order

1. **First:** #GH-0601 - SiteSettings fields (foundation for banner + policy links)
2. **Second:** #GH-0602 - Banner include + contracts (depends on settings fields)
3. **Third:** #GH-0603 - Consent JS + cookies + manage flow (depends on banner markup contract)
4. **Fourth:** #GH-0604 - Analytics loader + tag changes (depends on consent cookies + settings)
5. **Fifth:** #GH-0606 - Legal page type + templates/blocks (parallel OK, but easier after settings exist)
6. **Sixth:** #GH-0607 - Seeder updates (depends on legal page type + banner links)
7. **Seventh:** #GH-0605 - Tests (can be partial earlier; finalise once everything landed)
8. **Eighth:** #GH-0608 - Docs (final polish; update as contracts stabilise)

### Merge Ownership

- **Primary Merger:** Mark
- **Backup:** (agent name)

### Dependency Notes

- Consent cookies + banner DOM contract must be stable before analytics loader lands.
- Legal page model/template must stabilise before seeding changes.
- Theme override contract checks should land before the release cut to prevent regressions.

## Verification Focus

### Smoke Tests

```bash
make lint
make test
python manage.py test
# optional if used in your flow:
sum init test-project
sum check
```

### Delta Checks

- [ ] With no consent cookie: banner visible; analytics scripts not present; no network calls to GTM/GA
- [ ] After Accept: consent cookie set; analytics scripts load dynamically; banner hidden
- [ ] After Reject: consent cookie set; analytics does not load; banner hidden
- [ ] “Manage cookies” re-opens banner and allows changing decision
- [ ] Legal pages render with ToC + section anchors; print button works
- [ ] Seeder runs twice without duplicating pages (idempotent)

## Risk Assessment

**Risk Level:** Med

**Risk Factors:**

- Consent + analytics is compliance-sensitive
- Theme overrides can silently break banner contract if not enforced
- Seeding can accidentally modify existing content if not slug-scoped

**Mitigation:**

- Keep analytics out of HTML entirely (cache-safe)
- Add contract tests for banner + ToC
- Make seeding strictly slug-scoped under intended parent

## Notes

- Default cookie expiry: 180 days
- Cookie domain: host-only by default (no Domain attribute)
- Consent is invalid if version mismatches: re-prompt by bumping `cookie_consent_version`

````

---

```markdown
# GH-0601: Add cookie consent settings to SiteSettings (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- SiteSettings fields required for consent + legal links + versioning
- Admin UI wiring (panels/help text) and per-site correctness

## Boundaries

### Do
- Add consent/banner fields to the existing SiteSettings model (per-site)
- Add clear admin help text for compliance behavior

### Do NOT
- ❌ Do not implement JS behavior here
- ❌ Do not change analytics injection behavior here
- ❌ Do not add audit logging / endpoints

## Acceptance Criteria
- [ ] SiteSettings includes:
  - `cookie_banner_enabled` (bool)
  - `cookie_consent_version` (string, default "1")
  - `privacy_policy_page` (Page chooser, nullable)
  - `cookie_policy_page` (Page chooser, nullable)
  - (optional) `terms_page` (Page chooser, nullable)
- [ ] Settings are retrieved per-site (Wagtail multisite)
- [ ] Admin help text explains: banner enabled => analytics loads only after consent; banner disabled => immediate analytics load (until GH-0604 changes behavior)

## Test Commands
```bash
make lint
make test
python manage.py test
````

**Expected Results:**

- No migrations errors
- Tests pass
- Settings appear in Wagtail admin and save per site

## Files/Paths Expected to Change

```
core/sum_core/branding/models.py
core/sum_core/branding/wagtail_settings.py (if applicable)
core/sum_core/branding/migrations/XXXX_*.py
tests/... (settings tests if added here)
```

## Dependencies

**Depends On:** none
**Blocks:** GH-0602, GH-0604, GH-0607

## Implementation Notes

### Approach

- Add fields to the existing SiteSettings model where GTM/GA IDs already live.
- Ensure retrieval uses request site context (Wagtail settings best practice).

### Constraints

- Keep defaults safe for dev: cookie banner can default ON for showroom/test_project if desired.

## Risk Assessment

**Risk Level:** Low

## Labels Checklist

- [ ] `type:task`
- [ ] `agent:*`
- [ ] `component:branding`
- [ ] `risk:low`
- [ ] `model:*`
- [ ] Milestone: `v0.6.0`

````

---

```markdown
# GH-0602: Cookie banner include + a11y baseline + theme contract (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- Base template includes a cookie banner snippet
- Default banner markup is accessible and theme-overridable
- Contracted DOM hooks required by event_tracking ignore + consent JS

## Boundaries

### Do
- Add include to base template(s)
- Implement default banner snippet with required hooks
- Add “Manage cookies” entry point hook (UI element; JS in GH-0603)

### Do NOT
- ❌ Do not implement analytics loader or script tags here
- ❌ Do not implement cookie set/reject logic here (GH-0603)
- ❌ Do not trap focus / modal-dialog behavior (keep simple)

## Acceptance Criteria
- [ ] Base template includes `sum_core/includes/cookie_banner.html`
- [ ] Default banner renders with:
  - root `.cookie-banner`
  - `aria-label` containing “cookie”
  - Accept button: `[data-cookie-consent="accept"]`
  - Reject button: `[data-cookie-consent="reject"]`
  - Live announcement region: `aria-live="polite"` (or `role="status"`)
- [ ] Banner includes links to Privacy/Cookie Policy pages if configured (else hides link(s) gracefully)
- [ ] “Manage cookies” link exists in footer/header (or a standard place), with hook:
  - `[data-cookie-consent="manage"]`

## Test Commands
```bash
make lint
make test
python manage.py test
````

## Files/Paths Expected to Change

```
core/sum_core/templates/theme/base.html
core/sum_core/templates/sum_core/includes/cookie_banner.html
themes/theme_a/templates/... (override optional)
```

## Dependencies

**Depends On:**

- [ ] GH-0601 (settings fields for policy links + enable flag)

**Blocks:**

- GH-0603 (needs stable DOM hooks)
- GH-0605 (contract tests)

## Implementation Notes

### Approach

- Keep markup minimal and semantic (no role=dialog).
- Ensure `.cookie-banner` is present so `event_tracking.js` ignores banner clicks.

## Risk Assessment

**Risk Level:** Med

## Labels Checklist

- [ ] `type:task`
- [ ] `agent:*`
- [ ] `component:templates`
- [ ] `risk:med`
- [ ] `model:*`
- [ ] Milestone: `v0.6.0`

````

---

```markdown
# GH-0603: Consent cookies + banner behavior + manage flow (JS) (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- cookie_consent.js that:
  - shows banner only when consent is unknown/version-mismatched
  - sets consent cookies on Accept/Reject
  - supports “Manage cookies” to re-open + change choice
  - does NOT emit analytics/tracking events itself

## Boundaries

### Do
- Implement consent cookie set/update/delete logic
- Implement banner show/hide
- Implement manage flow

### Do NOT
- ❌ Do not load GTM/GA here (that’s GH-0604)
- ❌ Do not add server endpoints or audit logging
- ❌ Do not add granular categories/preferences

## Acceptance Criteria
- [ ] Cookie names:
  - `sum_cookie_consent` = `accepted|rejected`
  - `sum_cookie_consent_v` = SiteSettings.cookie_consent_version
- [ ] Expiry: 180 days; Path=/; SameSite=Lax; Secure only on https
- [ ] Unknown state if missing OR version mismatch => banner visible
- [ ] Clicking Accept sets cookies and hides banner
- [ ] Clicking Reject sets cookies and hides banner
- [ ] Clicking “Manage cookies” re-shows banner and allows changing decision
- [ ] JS-disabled: banner includes `<noscript>` copy (implemented in GH-0602)

## Test Commands
```bash
make lint
make test
python manage.py test
````

## Files/Paths Expected to Change

```
core/sum_core/static/sum_core/js/cookie_consent.js
core/sum_core/templates/... (only if adding data attributes/hook refinements)
```

## Dependencies

**Depends On:**

- [ ] GH-0602 (DOM hooks + markup in place)
- [ ] GH-0601 (consent version + enable flag accessible to template/JS)

**Blocks:**

- GH-0604 (needs reliable consent cookie state)

## Implementation Notes

### Approach

- Store consent in cookies so it persists without server endpoints.
- Prefer “no reload required” for manage flow; allow reload if needed for older pages, but the analytics loader will be client-side anyway.

## Risk Assessment

**Risk Level:** Med

````

---

```markdown
# GH-0604: Client-side analytics loader (no scripts in HTML) + config emission (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- Analytics scripts are never included in server-rendered HTML (cache-safe)
- Loader injects GTM/GA only after consent=accepted
- Analytics tag(s) emit only configuration data (IDs) in a safe, cacheable way

## Boundaries

### Do
- Replace analytics tag behavior:
  - from “render GTM/GA scripts”
  - to “emit IDs/config only”
- Add analytics_loader.js:
  - reads IDs/config
  - checks consent cookie + version
  - injects third-party scripts only after consent

### Do NOT
- ❌ Do not implement CDN Vary-by-cookie logic (not needed if HTML has no scripts)
- ❌ Do not add inline JS that would break strict CSP (keep logic in external JS files)

## Acceptance Criteria
- [ ] With unknown/rejected consent: no GTM/GA `<script src=...>` present and no network calls
- [ ] With accepted consent: loader injects correct script tags and initialises safely
- [ ] Server-rendered HTML contains no GTM/GA script tags in any consent state
- [ ] IDs are emitted per-site (multisite safe) and only when configured
- [ ] If banner is disabled in settings: define desired behavior explicitly:
  - either still require consent cookies OR treat as “always accepted”
  - (pick one and document; recommended: “banner disabled => treat as always accepted” for dev parity)

## Test Commands
```bash
make lint
make test
python manage.py test
````

## Files/Paths Expected to Change

```
core/sum_core/analytics/templatetags/analytics_tags.py
core/sum_core/templates/theme/base.html
core/sum_core/static/sum_core/js/analytics_loader.js
```

## Dependencies

**Depends On:**

- [ ] GH-0601 (settings fields)
- [ ] GH-0603 (consent cookie semantics)

**Blocks:**

- GH-0605 (tests)

## Implementation Notes

### Approach

- Emit config as:

  - `<script type="application/json" id="sum-analytics-config">{"gtm":"...","ga":"..."}</script>`
  - or `<meta name="sum:gtm" content="...">` etc

- Loader reads config and injects scripts only if consent accepted.

## Risk Assessment

**Risk Level:** Med/High (compliance-sensitive + third-party scripts)

````

---

```markdown
# GH-0605: Tests for consent + analytics loader + theme contracts (+ optional E2E) (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- Automated tests that prevent regressions in consent + analytics gating
- Theme contract checks for banner DOM hooks
- Multisite correctness tests for SiteSettings resolution

## Boundaries

### Do
- Add unit tests for:
  - settings resolution per site
  - analytics config emission only (no scripts)
- Add template/DOM contract tests for:
  - `.cookie-banner`
  - data-cookie-consent attributes (accept/reject/manage)
- Optional: minimal E2E (Playwright/Cypress) if already present in repo

### Do NOT
- ❌ Do not expand into full accessibility automation if toolchain isn’t already present
- ❌ Do not add heavy snapshot suites

## Acceptance Criteria
- [ ] Tests cover unknown/accepted/rejected + version mismatch logic (server-side config + JS semantics as feasible)
- [ ] Tests fail if theme override removes required cookie banner hooks
- [ ] Tests prove analytics scripts are not present in rendered HTML
- [ ] All tests pass in CI

## Test Commands
```bash
make lint
make test
python manage.py test
````

## Files/Paths Expected to Change

```
tests/... (new/updated)
themes/theme_a/... (only if required for contract fixtures)
```

## Dependencies

**Depends On:**

- [ ] GH-0602, GH-0603, GH-0604 (features must exist)

## Risk Assessment

**Risk Level:** Low/Med

````

---

```markdown
# GH-0606: Legal pages as CMS “article” pages with Section-based ToC + Theme A support (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- A Wagtail page type (e.g., `LegalPage`) that supports:
  - last_updated
  - sections (id/title/body) to drive ToC + anchors (single source of truth)
- Templates that render:
  - hero/breadcrumbs (if your article layout supports it)
  - desktop + mobile ToC (aria-expanded etc)
  - print button
- Theme A template can mirror the existing `terms.html` look/structure

## Boundaries

### Do
- Implement Section-based legal content (recommended for programmatic seeding)
- Implement templates with stable DOM contract for ToC anchors

### Do NOT
- ❌ Do not build a full blog system here
- ❌ Do not add auto-ToC HTML parsing (avoid time sink)

## Acceptance Criteria
- [ ] LegalPage exists and is creatable/publishable in admin
- [ ] Sections render as `<article id="...">` (or equivalent) with ToC links to `#id`
- [ ] Mobile ToC uses accessible toggle (aria-expanded + aria-controls)
- [ ] Print action exists and works
- [ ] Theme A override works (or core template is sufficient if Theme A is not overriding yet)

## Test Commands
```bash
make lint
make test
python manage.py test
````

## Files/Paths Expected to Change

```
core/sum_core/... (pages/models/blocks)
core/sum_core/templates/... (legal page template)
themes/theme_a/templates/... (optional override)
core/sum_core/migrations/...
```

## Dependencies

**Depends On:**

- [ ] GH-0601 (optional: policy page choosers point to LegalPages)

**Blocks:**

- GH-0607 (seeder creates these pages)

## Risk Assessment

**Risk Level:** Med

````

---

```markdown
# GH-0607: Seeder + starter profile updates (starter homepage + legal pages + footer links) (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- Updated seeding to create:
  - starter homepage (not “Welcome to Wagtail”)
  - legal pages (Terms/Privacy/Cookies) using LegalPage sections
  - footer “Legal” links + “Manage cookies” link
- Idempotent behavior (no duplication; slug-scoped under intended parent)
- Optional: `--profile starter|showroom` flag or a dedicated starter command

## Boundaries

### Do
- Keep seeding strictly slug-scoped under the target parent
- Ensure pages are published and Site root page is set correctly
- Ensure reruns do not duplicate or nuke non-seeded content

### Do NOT
- ❌ Do not delete arbitrary pages outside known slugs (even with --clear)
- ❌ Do not modify blog seeding beyond linking to a BlogIndex if it exists

## Acceptance Criteria
- [ ] Running seeder twice produces identical tree (no duplicates)
- [ ] Starter home renders with theme header/footer + at least hero + 2 sections
- [ ] Legal pages exist, published, and linked in footer
- [ ] Showroom/test_project are updated to match new baseline

## Test Commands
```bash
make lint
make test
python manage.py test
python manage.py seed_showroom --profile starter
python manage.py seed_showroom --profile starter
````

## Files/Paths Expected to Change

```
seed_showroom.py (or management/commands/seed_*.py)
core/sum_core/... (if seeding helpers added)
tests/... (seeding idempotency tests if added here)
```

## Dependencies

**Depends On:**

- [ ] GH-0606 (LegalPage model/template)
- [ ] GH-0602 (banner markup if seeder wires links)
- [ ] GH-0601 (settings page choosers if seeder sets them)

## Risk Assessment

**Risk Level:** Med

````

---

```markdown
# GH-0608: Docs updates — wiring inventory + theme guide + contracts (v0.6.0)

## Parent Work Order
Part of: #WO-060 (WO: Consent + Legal Pages + Starter Homepage v0.6.0)

## Deliverable
This subtask will deliver:
- Documentation updates so consent/legal/starter behavior is not tribal knowledge

## Boundaries

### Do
- Update wiring inventory and theme guide with explicit contracts:
  - cookie banner include path
  - required DOM hooks/classes/data attributes
  - consent cookie names/values/expiry/version behavior
  - analytics loader behavior (no scripts in HTML)
  - legal page section/ToC contracts
  - seeder slug contracts + profiles

### Do NOT
- ❌ Do not add new product features here; docs-only change

## Acceptance Criteria
- [ ] Docs clearly specify the non-negotiable DOM + cookie contracts
- [ ] Docs explain how to bump `cookie_consent_version` to force re-prompt
- [ ] Docs explain how themes override banner + legal templates safely

## Test Commands
```bash
# If docs linting exists:
make lint
````

## Files/Paths Expected to Change

```
docs/... (wiring inventory, theme guide, dev notes)
```

## Dependencies

**Depends On:**

- [ ] GH-0602/3/4/6/7 (final contracts)

## Risk Assessment

**Risk Level:** Low

```

```
