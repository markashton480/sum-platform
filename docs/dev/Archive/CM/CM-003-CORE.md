# **[CM-003]: Full Platform Core Audit (M0–M4) + Consumer Smoke Project**

## **Objective**

Perform a one-time, repo-wide **Core vs Harness** audit covering **Milestones 0–4**, and prove the result by bootstrapping a **second minimal consumer project** (separate from `test_project`) that can run core endpoints and key flows.

This task answers:

> “Is SUM Core actually consumable as a package, or are we accidentally depending on the test harness?”

---

## **Context** (from SSOT / README / Test Strategy)

- Repo is explicitly structured as **installable `sum_core` + minimal `test_project/` harness**.
- Test strategy expects platform-level readiness including health endpoint, monitoring, deployment flows, and smoke checks suitable for client projects.
- CM-04-CORE already passed for M4 with doc updates only, but we want the stronger, proof-based checks applied **across all milestones**.

### Agent Orientation

- Please see `@AGENT-ORIENTATION.md` for general guidance.

---

## **Scope**

### A) Core vs Harness Audit (M0–M4)

For each milestone area, confirm:

1. **Configuration location**

- If a setting is needed for real usage, it must be:

  - in core defaults (where appropriate), or
  - explicitly documented for client settings / env vars

- `test_project/settings.py` may override, but must not be the _only_ source of truth.

2. **App registration**

- Required `INSTALLED_APPS` are either:

  - minimal and obvious, or
  - documented clearly (especially any SEO/analytics modules).

3. **URL wiring**

- Endpoints introduced so far must be includable in a client project via standard `include()` patterns.

4. **Hidden coupling**

- Core modules must not import from `sum_core.test_project.*` (except test-only utilities).
- Templates in core must not assume test_project-specific context processors/settings.

Deliverable: a short “Audit Findings” section listing **any** coupling found and how it was addressed.

---

### B) New: “Where is it wired?” Wiring Inventory

Create a concise inventory (markdown) that answers, for each major feature area:

- **What the client must do** (apps, middleware, URLs, env vars)
- **What core provides automatically**
- **What is per-site SiteSettings vs per-project settings**

At minimum cover:

- Branding / tokens injection
- Navigation system
- Forms + Lead pipeline
- SEO (tags + sitemap/robots + schema)
- Analytics (GA4/GTM + events)
- Integrations (Zapier)
- Ops/observability (`/health/`, request_id, Sentry, logging)

---

### C) New: Core-Only Consumer Smoke Project (proof)

Create a second minimal Django/Wagtail project in-repo **purely for validation** (not as “the new main project”), e.g.:

- `clients/_smoke_consumer/` (or `clients/smoke-consumer/`)

It must:

- install `sum_core` (editable install is fine)
- have a minimal settings module
- include required URLs
- run:

  - `./manage.py check`
  - `./manage.py migrate`
  - start server and verify at least `/health/` returns 200 JSON

**Stretch (if cheap):**

- create minimal Wagtail `Site` + HomePage and assert sitemap/robots endpoints respond.

This is the “proof harness” that prevents future regressions.

---

## **Explicitly Out of Scope**

- Major refactors
- New features
- Boilerplate generator (that’s M5)
- Deployment scripts work (that’s M5)
- UI redesign

If something is “bigger than alignment”, document it as a follow-up item for M5+.

---

## **Implementation Guidelines**

- Keep changes small and reversible.
- Prefer **documentation + minimal wiring helpers** over sweeping setting rewrites.
- No deleting tests to “fix” failures (add/adjust tests if behaviour changes).
- When complete, file a full, comprehensive work report in docs/dev/CM/CM-003-CORE_followup.md

---

## **Acceptance Criteria**

- [ ] No core feature introduced in M0–M4 depends on `test_project` to exist.
- [ ] Wiring Inventory doc exists and is accurate.
- [ ] A separate “smoke consumer” project can:

  - `manage.py check`
  - `migrate`
  - serve `/health/` successfully

- [ ] Any coupling discovered is either fixed or explicitly recorded as follow-up.
- [ ] `make lint` + `make test` still pass.

---

## **Testing Requirements** (from test-strategy-v1.1.md)

- This CM adds **system-level confidence** consistent with the strategy’s emphasis on repeatable regression and client-site smoke checks.
- Add at least one minimal test or script (docs is fine) that confirms the smoke consumer remains runnable in CI (even if you don’t run it in CI yet).

---

## **Estimated Complexity**

- **Time:** M–L
- **Risk:** Medium (touches wiring/config)
- **Value:** Extremely high (de-risks M5 and real client launches)
