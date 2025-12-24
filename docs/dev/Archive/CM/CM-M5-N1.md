# **[CM-M5-N1] End-of-Milestone-5 Niggles & Release Hardening**

**Objective**
Close all known and emerging “niggle-level” issues from Milestone 5, eliminate ambiguity across CLI / boilerplate / core boundaries, and harden the platform so M5 can be formally signed off and frozen.

This CM exists to ensure **the platform behaves deterministically for a second, third, and tenth client**, not just the current one.

---

## Context (from SSOT / PRD)

**Business requirement excerpt**

> “The platform must allow Straight Up Marketing to spin up new client websites reliably in 2–3 days, with minimal bespoke engineering and no reliance on internal test harnesses.”
> Reference: SSOT §1.1, §1.4

**Relevant platform principles**

- Core vs consumer separation must be explicit
- Boilerplate is a _consumer_, not a privileged project
- CLI is scaffolding + validation only
- Test harnesses must not leak into production assumptions
  Reference: SSOT §4, §5, §12; Agent Orientation

---

## Scope (What This CM Covers)

This CM is explicitly **limited** to:

1. **Health check behaviour correctness**
2. **Boilerplate completeness & ownership clarity**
3. **Dependency pinning & versioning convergence**
4. **Docs & CLI consistency pass**
5. **Release-readiness verification**

No new features. No refactors unless required to close a correctness gap.

---

## Detailed Work Items

### 1️⃣ Health Endpoint Nuance (Ops Contract Hardening)

**Problem to resolve**
The `/health/` endpoint must clearly distinguish:

- _“Celery not configured”_ (neutral)
- _“Celery configured but unreachable”_ (degraded, not unhealthy)

**Requirements**

- If **no Celery broker is configured**:

  - Celery check is skipped
  - Overall status remains `ok`

- If **Celery is configured but unavailable**:

  - Celery check reports failure
  - Overall status is `degraded`
  - HTTP status remains `200`

- Only DB / cache failures may trigger `unhealthy` + `503`

**Constraints**

- No test-only conditionals
- Behaviour must be consistent across:

  - test_project
  - boilerplate
  - real client projects

**Acceptance Criteria**

- Health JSON reflects the correct status in all three cases
- At least one explicit test covers each branch
- Behaviour matches Wiring Inventory expectations
  Reference: Ops / Observability, Wiring Inventory

---

### 2️⃣ Client-Owned HomePage & Boilerplate Completeness

**Problem to resolve**
Client projects must never start in an ambiguous “blank tree” state or rely on test harness assumptions.

**Requirements**

- Canonical client boilerplate must include:

  - Client-owned `HomePage` model
  - Initial migrations for that app

- Documentation must clearly state:

  - HomePage is **client-owned**
  - Core does not ship a production HomePage

- No implicit reliance on `test_project.home`

**Acceptance Criteria**

- Fresh `sum init <client>` → migrations apply cleanly
- Wagtail admin allows HomePage creation without hacks
- Docs and code agree on ownership model
  Reference: Page Types Reference

---

### 3️⃣ Dependency Pinning Convergence

**Problem to resolve**
Multiple valid-looking dependency approaches exist today. Only **one** may be blessed for clients.

**Requirements**

- Boilerplate must pin `sum_core` using:

  - **Git tag pinning only** (per M5 decision)

- Docs must clearly distinguish:

  - monorepo dev mode
  - standalone client mode

- CLI scaffolding must not contradict release workflow

**Explicit Non-Goals**

- Do not introduce PyPI or private registry
- Do not add auto-upgrade logic

**Acceptance Criteria**

- `requirements.txt` in boilerplate is unambiguous
- `release-workflow.md` matches actual behaviour
- `sum check` messaging reinforces the correct model
  Reference: Release Workflow

---

### 4️⃣ CLI & Docs Consistency Sweep

**Problem to resolve**
Small mismatches between CLI behaviour, docs, and mental model compound over time.

**Requirements**

- Review:

  - `cli.md`
  - README routing
  - Agent Orientation

- Remove or clarify any wording that implies:

  - test_project is a valid production target
  - CLI performs environment setup or magic

- Ensure CLI error messages are:

  - explicit
  - actionable
  - aligned with documentation

**Acceptance Criteria**

- Docs tell a single, coherent story
- CLI output reinforces that story
- No “it works but I don’t know why” paths remain
  Reference: CLI docs

---

### 5️⃣ Release-Readiness Gate

**Problem to resolve**
Before freezing M5, we must verify the factory works end-to-end.

**Required Checks**

- `make lint`
- `make test`
- `make check-cli-boilerplate`
- `make release-check`

**Smoke Validation**

- `sum init test-client`
- install deps
- `sum check` passes
- `runserver` boots
- `/health/` behaves correctly

**Acceptance Criteria**

- All checks pass without manual intervention
- No undocumented steps required
- No warnings deferred “to later”

---

## Implementation Guidelines

- **Do not add features**
- Prefer small, explicit changes over clever abstractions
- If behaviour differs between environments, document _why_
- If something feels “obvious but undocumented”, document it

---

## Dependencies & Prerequisites

- Milestone 5 implementation tasks complete
- CLI boilerplate sync mechanism already in place
- SSOT updated and authoritative
  Reference: SSOT §16 Definition of Done

---

## Testing Requirements (from test-strategy-v1.1)

- Unit tests where logic branches exist (health checks)
- No snapshot-only tests
- Tests must assert **behavioural intent**, not just coverage
- ≥80% coverage preserved
  Reference: test-strategy-v1.1

---

## Estimated Complexity

- **Time**: M
- **Risk**: Low–Medium (logic + clarity, not architecture)
- **Suggested Model**: GPT-5.2 (high reasoning, low hallucination tolerance)

---

## Definition of Success

> “If we scaffolded five new clients tomorrow, none of them would trip over invisible platform assumptions.”
