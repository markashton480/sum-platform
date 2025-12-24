# **[CM-04-CORE]: Core vs Test Project Alignment Audit**

## **Objective**

Audit Milestone 4 work to ensure all implemented functionality truly belongs to **SUM Core** and is consumable by **real client projects**, not just the `test_project` harness.

This mission answers one question:

> _“If the test project disappeared, would Milestone 4 still exist?”_

---

## **Context**

During Milestone 4, multiple features were added that required:

- settings
- app registration
- URL wiring
- environment configuration

Because development is driven via a test harness (`test_project`), there is a known risk that:

- configuration lives only in test settings
- behaviour works “by accident” in tests
- core assumptions are implicit rather than explicit

This CM is **not a refactor** and **not new feature work**.
It is an **alignment and correction pass** to ensure platform correctness.

## More details in `AGENT-ORIENTATION.md`.

## **In Scope (strictly bounded)**

### 1. **Settings & Configuration Audit**

For every new setting introduced in Milestone 4, determine:

- Does it live in **core** (or a reusable module)?
- Is `test_project/settings.py` only _overriding_, not _defining_ behaviour?
- Would a client project reasonably know how to configure this?

**Examples to explicitly audit**

- Email backend configuration
- Observability toggles (Sentry, logging)
- Zapier webhook configuration
- SEO-related flags / behaviour
- Cache TTL defaults

**Fix if needed**

- Move definitions to core defaults
- Document required settings
- Reduce test-only assumptions

---

### 2. **App Registration Audit**

Confirm that all Milestone 4 apps/components:

- are correctly registered in core expectations
- do not rely on test-only `INSTALLED_APPS`

**Explicitly review**

- `sum_core.seo`
- `sum_core.ops`
- analytics/admin panels

If registration requirements exist:

- they must be **explicit and documented**
- not implicit via test harness behaviour

---

### 3. **URL Routing Audit**

Verify that new endpoints introduced in M4:

- are wired in a way suitable for client projects
- do not rely on test-only URLConfs

**Endpoints to check**

- `/health/`
- `/sitemap.xml`
- `/robots.txt`

Confirm how a client project would include these routes.

---

### 4. **Environment Variable Audit**

For every env var referenced in Milestone 4 code:

- Is it documented?
- Does it have a safe default?
- Is it referenced only in tests?

Remove or relocate any env assumptions that exist purely to satisfy tests.

---

### 5. **Documentation Delta**

Ensure that persistent platform behaviour introduced in M4 is reflected in:

- README / platform docs
- configuration guidance (where appropriate)

This is **not** full documentation polish — only correctness.

---

## **Explicitly Out of Scope**

- New features
- Refactors unrelated to alignment
- Performance optimisation
- UX changes
- Boilerplate/CLI generation (future milestone)

If something feels “too big”, it should be **noted, not fixed**.

---

## **Implementation Guidelines**

- Treat `test_project` as **disposable**
- Prefer small, surgical changes
- When in doubt, add a TODO note rather than invent architecture
- Do **not** delete tests to “fix” alignment

---

## **Acceptance Criteria**

- [ ] All Milestone 4 configuration is consumable outside `test_project`
- [ ] No feature relies on test-only settings to function
- [ ] App registration expectations are explicit and correct
- [ ] URL routing assumptions are sane for client sites
- [ ] Findings are summarised in a short **CM-04-CORE report**

---

## **Deliverables**

1. **Code changes** (if required) to correct misplacement
2. **CM-04-CORE report** including:

   - What was checked
   - What was changed
   - What was intentionally left as-is
   - Any follow-ups deferred to later milestones

3. File the report under docs/dev/CM/CM-04-CORE_followup.md

This report becomes part of the permanent audit trail.

---

## **Estimated Complexity**

- **Time:** S–M
- **Risk:** Low
- **Nature:** Corrective / alignment (no feature risk)

---
