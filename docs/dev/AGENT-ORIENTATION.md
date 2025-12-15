# Agent Orientation: **This Is a Platform, Not a Demo Project**

> Read this before making structural decisions.

---

## 1. What You Are Working On

This repository is **SUM Platform**.

It is **not**:

- a single Django site
- a demo project
- a throwaway test harness

It **is**:

- a reusable **core platform** intended to power many client sites
- a set of installable Django/Wagtail apps (`core/sum_core`)
- surrounded by scaffolding (test projects, boilerplate, CLI)

**Primary product:**
`core/sum_core/`

Everything else exists to:

- test it
- scaffold it
- demonstrate it

If something “works” only inside a test project, it is **not finished**.

---

## 2. The Test Project Is a Harness

You will see a `test_project/`.

This exists to:

- run pytest
- simulate a client environment
- verify behaviour

It is **not**:

- the production configuration
- the place where features “live”
- a valid target for permanent settings

### Rule of thumb

> If the test project disappeared tomorrow, SUM Core should still make sense.

If your change only touches:

- `test_project/settings.py`
- `test_project/urls.py`

…you should ask yourself:

> “Where would a real client configure this?”

If the answer is unclear, stop and reassess.

---

## 3. Where Things Belong

### Persistent behaviour belongs in:

- `core/sum_core/*`
- installable Django apps
- reusable settings or SiteSettings
- documented defaults

### Test-only behaviour belongs in:

- `test_project/`
- pytest fixtures
- mocks and overrides

### Red flag patterns

- “Fixing” a feature by only adjusting test settings
- Registering apps only in test INSTALLED_APPS
- Adding env vars that exist only in tests
- URLs wired only in the test URLConf

These are **incomplete implementations**, not solutions.

---

## 4. Configuration Philosophy

SUM Platform is designed so that:

- **Core** provides:

  - sane defaults
  - installable apps
  - clear extension points

- **Client projects** provide:

  - overrides
  - credentials
  - site-specific values

When adding a setting, ask:

1. Is this persistent across sites?
   → belongs in core (or SiteSettings)

2. Is this per-site?
   → SiteSettings (not test settings)

3. Is this purely for tests?
   → test_project only

If a setting is added **only** to make tests pass, it is probably in the wrong place.

---

## 5. Mental Model to Use

Think of SUM Platform like this:

- `sum_core` = a Python package someone installs
- `test_project` = one consumer of that package
- `boilerplate/` = another consumer
- `cli/` = a generator of consumers

Your job is to improve the **package**, not the demo.

---

## 6. What Happens at the End of Every Milestone

At the end of each milestone, a **Corrective Mission (CORE audit)** will run to answer one question:

> “Did we actually build SUM Core — or did we just make the test project happy?”

Anything that fails that audit **will be moved**, refactored, or corrected.

You do not need to pre-empt this perfectly — but you _do_ need to avoid baking test-only assumptions into core code.

---

## 7. Final Guiding Principle

> **Tests passing is necessary, but not sufficient.**

The real success condition is:

> “Could a second, clean client project use this without copying the test harness?”

If yes — you’re doing it right.
If not — it will be caught in the CM.

---

### Relationship to existing rules

This document complements (and does not replace) the existing agent rules and project structure defined in the repository’s agent configuration files .

---
