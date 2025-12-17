# LINTEL × SUM Overview

## Purpose

This document is the shared mental model for anyone working on the ecosystem: 

It clarifies:

* what **SUM** is (and isn’t),
* what **LINTEL Digital** is (and isn’t),
* how **domains + namespaces** map to environments,
* what **Sage & Stone Kitchens** is used for (demo vs validation vs design reference),
* and how all of this prevents confusion and scope creep.

---

## The Entities

### SUM

**SUM** is the platform.

* **Repo / codebase identity:** `sum-platform`
* **Core package name:** `sum_core`
* **CLI namespace:** `sum` (e.g. `sum init`, `sum check`)
* **Purpose:** enable fast, repeatable delivery of high-quality Wagtail websites with consistent patterns (themes, blog, forms, ops).

**Important:** SUM does **not** stand for anything. It’s just the name.

SUM is designed to be:

* stable,
* repeatable,
* distribution-friendly (tagged versions),
* capable of supporting multiple consumers (client sites, LINTEL sites, demo sites).

---

### LINTEL Digital

**LINTEL Digital** is the company that uses SUM.

* It is a **digital marketing agency** delivering websites/services to clients.
* It uses SUM as the delivery platform to build and operate client sites.

LINTEL is an **operator** on top of SUM, not part of SUM itself.

---

## What Counts as a “Site” in This World

A “site” is any Wagtail project that consumes `sum_core` and is deployed somewhere.

There are multiple kinds of sites:

1. **Client production sites**

   * Real client domain (e.g. `clientdomain.com`)
   * Owned by the client
   * Powered by SUM

2. **Client preview / staging sites**

   * Used during delivery before launch
   * Lives under LINTEL-controlled staging namespace

3. **LINTEL’s own public website**

   * The agency’s marketing site (owned by LINTEL)
   * Also can be powered by SUM, but it is still just “a site” (a consumer)

4. **Sales demo site**

   * A live, editable demo used to demonstrate funnels + Wagtail editing
   * Resets periodically
   * This is **LINTEL Ops/Sales tooling**, not SUM platform development scope

---

## Domains, Namespaces, and Environment Meaning

### Canonical principle

Domains are not just URLs—they’re **workflow boundaries**. Each domain (or suffix) should strongly imply what kind of environment it is.

### LINTEL public identity

* **Company website:** `linteldigital.com`
* **Company email:** `@linteldigital.com`

Optional brand domain:

* `lintel.digital` may exist as a redirect/alias, but the canonical “agency legitimacy” anchor is `linteldigital.com`.

---

### Staging / client preview namespace

* **Staging namespace:** `lintel.site`
* Pattern: `clientname.lintel.site`

Rules:

* Auth-protected by default
* `noindex` by default
* Disposable by design (can be rebuilt without ceremony)

Intent:

* This is where client sites live **before** they go live on the client’s real domain.

---

### Internal dev / experimental namespace

* **Internal namespace:** `lintel.live`
* Pattern: `dev.lintel.live`, `themes.lintel.live`, `experiments.lintel.live`

Rules:

* Never client-facing
* Allowed to be messy
* Allowed to break

Intent:

* Fast iteration, testing, spike work, experiments that should not leak into delivery or sales.

---

### Sales demo namespace

Recommended:

* **Demo site:** `demo.linteldigital.com`

Rules:

* Intended to be shared with prospects
* Must be stable and polished
* Safe sandboxing (limited permissions) and periodic reset strategy

Intent:

* A live environment to show:

  * design quality,
  * conversion patterns (CTAs/funnels),
  * “you can edit this yourself” Wagtail experience.

---

## Sage & Stone Kitchens Demo Concept

### What it is

**Sage & Stone Kitchens** is the canonical “high-end example site” concept.

It serves three roles:

1. **Sales demo**

* A polished, aspirational site that sells the LINTEL service
* Prospects can explore it like a real site
* Prospects can log into Wagtail and try editing

2. **UI reference**

* The “wireframe → compiled HTML” outputs are treated as the **design reference**
* When implementing in SUM/Wagtail, we build against the HTML reference (like implementing from Figma or a static prototype)

3. **Practice consumer**

* It can be used as the *first real consumer site* to validate new platform capabilities (themes, blog, dynamic forms) before rolling them into broader production use.

### What it is not

* It is not “the platform.”
* It is not a client site.
* It is not an excuse to add agency-specific hacks into `sum_core`.

---

## SUM Platform vs LINTEL Ops Scope Boundary

### SUM platform development includes

* `sum_core` features: themes, blog system, dynamic forms, lead capture, SEO, ops endpoints
* CLI, boilerplate, drift guard, release workflow
* predictable upgrade paths and stability lanes

### LINTEL Ops / Sales includes

* the demo environment
* reset mechanisms / demo content seeding
* prospect access controls
* any tooling that exists purely to sell services

This boundary exists to prevent “platform roadmap” from getting polluted by “agency tooling” needs.

---

## Workflow: Wireframes → Wagtailification

### Canonical approach

Wireframes are built as **static HTML outputs** (any toolchain: builder/Jinja/etc.).

Those outputs are treated as **design artefacts**.

Wagtailification means:

* implementing the design in Wagtail + `sum_core` templates/themes directly,
* not performing mechanical “template conversion.”

This is equivalent to implementing from:

* a SPA prototype,
* a static marketing site handed off by a designer,
* or a Figma design system.

---

## Vocabulary and Defaults

### Terms

* **Platform:** SUM (codebase + `sum_core` + CLI)
* **Operator:** LINTEL Digital (company delivering sites)
* **Consumer site:** any Wagtail project using `sum_core`
* **Demo site:** prospect-facing sandbox site
* **Staging:** client preview environment (`*.lintel.site`)
* **Internal dev:** experimentation environment (`*.lintel.live`)

### Default assumptions for agents

When an agent sees:

* `linteldigital.com` → public agency identity
* `demo.linteldigital.com` → sales demo (stable/polished)
* `*.lintel.site` → staging/preview (auth/noindex/disposable)
* `*.lintel.live` → internal-only (breakable)

When an agent sees:

* `sum_core` → platform code (must be stable, reusable, not agency-specific)
* “Sage & Stone” → demo/reference consumer site (LINTEL Ops unless explicitly being used as a practice consumer for platform capability validation)

---

## Practical Guardrails

* Don’t describe LINTEL as “the platform.”
* Don’t treat demo tooling as a platform milestone deliverable.
* Don’t hardcode domain assumptions into `sum_core` unless explicitly required by platform architecture.
* Do keep environment boundaries obvious through domain conventions.
* Do keep consumer sites (demo, staging, prod) as separate concerns from platform code.

---

## One-paragraph summary for quick pasting

SUM is the platform (`sum_core`, `sum` CLI) used to build Wagtail sites; LINTEL Digital is the agency operating on top of SUM to deliver sites for clients. Domains communicate environment: `linteldigital.com` is the agency, `demo.linteldigital.com` is a prospect-facing demo that resets, `clientname.lintel.site` is staging/preview (auth + noindex + disposable), and `*.lintel.live` is internal dev/experiments only. Sage & Stone Kitchens is the canonical high-end demo/reference site: compiled HTML outputs are treated as design artefacts, and Wagtailification is direct implementation against that reference, not template conversion.

