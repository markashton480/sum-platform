# **SUM Platform — Post-MVP Expansion PRD (v1)**

**Status:** Draft (for review)
**Applies after:** Milestone 5 (Platform Factory)
**Audience:** Platform maintainer (you) + AI agents
**Purpose:** Define controlled expansion of SUM Platform after MVP freeze, without destabilising core guarantees.

---

## 1. Context & Motivation

Milestone 5 delivered a **stable, repeatable platform** capable of:

* scaffolding client sites
* validating structure
* deploying and upgrading safely
* supporting multiple themes (planned)
* enforcing correctness via contracts, not conventions

Post-MVP work must preserve this stability while allowing:

* feature growth (blog, forms, CRM)
* design evolution (themes)
* operational confidence (deploy & upgrade practice)
* AI-assisted review (not automation for automation’s sake)

---

## 2. Guiding Principles (Non-Negotiable)

1. **Core stability first**

   * `sum_core` remains installable, versioned, and backward-compatible by default.
   * No feature may “only work” in a harness or demo project.

2. **Real consumers only**

   * New features are exercised via *real client projects* scaffolded with `sum init`, not bespoke test projects.

3. **Practice before promises**

   * At least **3–4 full deploy + upgrade cycles** must be completed before onboarding external clients.

4. **AI is an auditor first**

   * AI integrations start as **read-only reviewers**, not content mutators.
   * Draft-only write actions may be added later, explicitly and narrowly.

5. **Themes are fixed per site**

   * Theme selection happens at init-time.
   * No Wagtail admin switching.
   * Changing a theme is a developer action.

---

## 3. Post-MVP Milestones Overview

### Milestone 6 — Themes & Delivery Pipeline

**Goal:** Prove the platform can deliver real sites safely.

**Includes:**

* Theme system v1 (Tailwind-first)
* Theme A (reference theme)
* Blog v1 (core feature)
* VPS golden-path deployment
* Staging + production workflow
* LINTEL site deployed “for real”

---

### Milestone 7 — Platform Practice & Feature Evolution

**Goal:** Build confidence through repetition and controlled expansion.

**Includes:**

* Dynamic Forms v1
* Theme B + Theme C
* Core upgrade propagation across multiple live sites
* CRM v2 (later in milestone)

---

### Milestone 8 — AI-Assisted Audit Layer (Optional but Planned)

**Goal:** Add AI as a correctness and completeness assistant, not a CMS replacement.

---

## 4. Feature Roadmap (Post-MVP)

### 4.1 Blog v1 (First Vertical Slice)

**Rationale**

* Exercises page models, listings, SEO, templates, feeds.
* Ideal for testing theme flexibility.

**Scope**

* BlogIndexPage
* BlogPostPage
* Category/tagging (minimal)
* SEO metadata
* RSS feed (optional)

**Non-Goals**

* Editorial workflow automation
* AI content generation (v1)

---

### 4.2 Dynamic Forms v1

**Rationale**

* Removes reliance on static forms.
* Critical for real client usage.

**Scope**

* Form builder UI (minimal)
* Submissions storage
* Email notifications
* Admin review

**Constraints**

* Backwards-compatible with existing forms
* Draft schema stability across upgrades

---

### 4.3 CRM v2 (Deferred)

**Rationale**

* Higher complexity, more surface area.
* Implement only after deploy/upgrade confidence is high.

---

## 5. Themes System (Post-MVP Contract)

Themes are:

* selected at `sum init`
* copied into the client project
* fixed per site
* Tailwind-based
* responsible for layout, typography, and vibe

**sum_core responsibilities**

* expose template hooks
* remain presentation-agnostic
* provide blocks and data

**Theme responsibilities**

* base templates
* component partials
* Tailwind config
* accessibility baseline

(Theme Architecture Spec v1 applies.)

---

## 6. Deployment & Upgrade Practice

Before onboarding external clients:

* At least **two live sites** must be running
* Each must undergo:

  * at least **two core upgrades**
  * migrations applied cleanly
  * zero data loss
* Rollback procedure must be rehearsed at least once

**Required artifacts**

* deploy script
* backup/restore script
* runbook
* “what broke last time” notes

---

## 7. AI-Assisted Audit Layer (Planned)

### 7.1 Purpose

Provide a **pre-publish and pre-deploy safety net** to answer:

> “Did I forget anything obvious?”

Not:

* auto-publishing
* schema mutation
* silent edits

---

### 7.2 Phase 1: Read-Only Introspection API

Expose structured, factual endpoints:

* `/api/introspection/site`
* `/api/introspection/pages`
* `/api/introspection/seo`
* `/api/introspection/content-gaps`

Examples:

* missing legal pages
* placeholder text still present
* missing meta descriptions
* empty hero sections
* orphaned nav items

---

### 7.3 Phase 2: Custom GPT Auditor

* Uses OpenAPI actions
* Authenticated
* Strict read-only
* Returns:

  * issues
  * warnings
  * suggestions
  * severity levels

Example prompts:

* “Run pre-publish audit”
* “Check SEO completeness”
* “Check legal compliance baseline”

---

### 7.4 Phase 3 (Optional): Draft-Only Write Actions

* Create draft content only
* Never publish
* Never delete
* Human must review

---

## 8. Risk Management

| Risk              | Mitigation                                      |
| ----------------- | ----------------------------------------------- |
| Platform drift    | Core frozen at tags, release checklist enforced |
| Theme instability | One reference theme first, others derive        |
| AI overreach      | Read-only first, explicit scopes                |
| Upgrade fear      | Repeated practice with live sites               |
| Over-engineering  | Features added only after real usage            |

---

## 9. Definition of “Client-Ready”

SUM Platform is considered **client-ready** when:

* 2+ sites deployed and upgraded successfully
* Blog + Forms proven in production
* Themes system used at least twice
* AI audit catches real mistakes at least once
* You no longer hesitate before deploying

---

## 10. Out of Scope (Explicit)

* Theme marketplace
* Real-time AI editing
* Per-page theme switching
* Multi-cloud deployment
* SaaS dashboard for clients

These are **deliberately deferred**.

---

## 11. Final Principle

> **Confidence comes from repetition, not architecture.**

This plan optimises for:

* muscle memory
* safe failure
* boring correctness
* long-term leverage

---
