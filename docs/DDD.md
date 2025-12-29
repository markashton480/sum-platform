# Documentation Documentation Document (DDD)

**Document Version:** 1.1  
**Date:** December 29, 2025  
**Purpose:** Master index and overview of all documentation in the SUM Platform project  
**Location:** `docs/DDD.md`

---

## Overview

The SUM Platform has extensive documentation scattered across multiple directories and files. This document provides a comprehensive map of what documentation exists, what each piece covers, and where to find it.

## 📁 Documentation Structure

```
docs/
├── HANDBOOK.md                        # The master guide (Start here!)
├── DDD.md                              # This document
├── ROUTER.md                           # Quick operational links
├── WEBHOOKS.md                         # Lead/webhook integration notes
├── ops-pack/                          # Operational runbooks
│   ├── RELEASE_RUNBOOK.md             # Release process
│   ├── deploy-runbook.md              # VPS deployment
│   ├── upgrade-runbook.md             # Site upgrades
│   └── [other operational guides]     # Rollback, smoke tests, etc.
├── release/                           # Release automation
│   ├── RELEASE_AGENT_PROMPT.md        # Release agent instructions
│   ├── RELEASE_AUDIT_AGENT_PROMPT.md  # Release audit agent instructions
│   ├── prompts/                       # Human-facing prompts
│   │   ├── pre-release-prompt.md
│   │   └── release-prompt.md
│   └── declarations/                  # Version declaration records/templates
└── dev/                               # All development documentation
    ├── master-docs/                   # Core strategic documents
    ├── [individual reference files]   # Implementation guides
    ├── design/                        # Design references + wireframes
    ├── deploy/                        # Deployment guides
    ├── Archive/                       # Historical docs (CM, milestones, etc.)
    ├── reports/                       # Analysis & review documents
    ├── agents/reviews/                # Code review guidelines (moved; old reviews/ archived)
    ├── side_quests/                   # Experimental/task-specific docs
    └── [excluded: M0-M6, DOC, NAV]    # Audit trail directories (inside Archive/)
```

---

## 🎯 Entry Points & Essential Reading

### Main Repository Entry Point

- **Location:** `README.md` (repository root)
- **Purpose:** Primary "how the repo works" guide, quick start instructions
- **What it contains:**
  - Platform overview and current status
  - Quick start for local development
  - Overview of core features implemented
  - Prerequisites and setup instructions
  - Pointers to detailed documentation

### Single Source of Truth (SSOT)

- **Location:** `docs/dev/master-docs/SUM-PLATFORM-SSOT.md`
- **Purpose:** Consolidated platform specification replacing multiple scattered docs
- **What it contains:**
  - Complete project vision and scope
  - Technology stack and architecture
  - Repository structure explanation
  - Core package (`sum_core`) specification
  - StreamField blocks, page types, systems overview
  - Implementation milestones and critical path
  - Conventions and standards

---

## 📚 Core Platform Documentation

### Master Documents Directory (`docs/dev/master-docs/`)

#### Strategic Planning & Requirements

- **`overview.md`** - High-level LINTEL × SUM entity relationships, clarifies what SUM is/isn't
- **`prd-sum-platform-v1.1.md`** - Complete Product Requirements Document (3,169 lines)
  - User stories, functional requirements, technical specs
  - Design specifications and implementation guidelines
- **`POST-MVP_BIG-PLAN.md`** - Post-MVP expansion strategy (1,527 lines)
  - Future feature roadmap beyond core MVP
  - Blog system, multi-tenancy, advanced integrations

#### Architecture & Implementation

- **`THEME-ARCHITECTURE-SPECv1.md`** - Future theme system architecture
  - Multi-theme support strategy
  - Tailwind-based theme development workflow
- **`post-mvp-expansion-v1.md`** - Earlier version of post-MVP planning

### Core Reference Documents (`docs/dev/`)

#### Platform Architecture

- **`AGENT-ORIENTATION.md`** - Critical: "This is a platform, not a demo project"
  - Essential reading for understanding the repository's purpose
  - Explains platform vs. test project distinction
  - Guides structural decision-making
- **`CODEBASE-STRUCTURE.md`** - Comprehensive codebase directory tree
  - Complete overview of all directories and their purposes
  - Module organization within `sum_core`

#### Implementation Guides

- **`WIRING-INVENTORY.md`** - How to consume `sum_core` in client projects
  - Required settings, installed apps, URL patterns
  - Step-by-step integration checklist
- **`blocks-reference.md`** - Authoritative StreamField blocks reference
  - Complete catalog of all available blocks
  - Field structures, usage examples, template requirements
- **`page-types-reference.md`** - Available page types documentation
  - StandardPage, ServiceIndexPage, ServicePage specifications
  - Field definitions and available blocks per page type
- **`navigation-tags-reference.md`** - Navigation template tags reference
  - Header, footer, sticky CTA template tag documentation
  - Usage examples and returned context structures

---

## 🎨 Design System Documentation

### Design Directory (`docs/dev/design/`)

#### Core Design System (Archived in `docs/dev/Archive/design/`)

- **`css-architecture-and-tokens.md`** - Primary CSS architecture guide (archived in `docs/dev/Archive/design/`)
- **`design_system.md`** - Brand-agnostic design philosophy (archived in `docs/dev/Archive/design/`)

**Current theming guidance:** `docs/dev/THEME-GUIDE.md`

#### Visual Design References

**Component-specific design files:**
  - `content_blocks_design.html`
  - `faq_and_process_design.html`
  - `form_design.html`
  - `gallery_design.html`
  - `portfolio_design.html`
  - `service_card_design.html`
  - `testimonials_design.html`

- **Wireframes (compiled HTML):** `wireframes/sage-and-stone/compiled/`

#### Archived Visual References

- **`premium-trade-website-v3-final.html`** - Legacy visual reference (archived)

---

## 🔧 Development & Contributor Documentation

### Development Standards

- **`hygiene.md`** - Repository hygiene standards

  - Code formatting and linting requirements
  - Dependency management rules
  - Testing standards and fixtures

- **`agents/reviews/daily_code_review.md`** - Daily code review guidelines
  - Review process for Django/Wagtail development
  - Quality standards and checkpoints

### Development Tools

- **`cli.md`** - SUM CLI documentation
  - `sum init` and `sum check` command specifications
  - Project scaffolding workflow
- **`THEME-GUIDE.md`** - Theme development and branding integration guide

### Development Decisions

- **`decisions.md`** - Architectural decisions log
  - Docker deferral decision and rationale
- **`GIT_STRATEGY.md`** - Git workflow and branching strategy

---

## 🚀 Operations & Deployment

### Ops Pack (`docs/ops-pack/`)

**Hot path operational runbooks** for day-to-day operations:

- **`RELEASE_RUNBOOK.md`** - Complete release process (unified)
  - Version selection, preparation, sync to public repo
  - Tag creation and verification
  - Replaces legacy `release-checklist.md` and `release-workflow.md`
- **`deploy-runbook.md`** - Fresh VPS deployment
  - Step-by-step from bare VPS to running site
- **`upgrade-runbook.md`** - Upgrade existing sites
  - Core version updates and migration workflow
- **`rollback-runbook.md`** - Rollback procedures
  - Recovery from failed deployments
- **`smoke-tests.md`** - Quick verification (10-15 min)
- **`full-verification.md`** - Complete verification (30-60 min)
- **`loop-sites-matrix.md`** - Loop sites tracking
- **`what-broke-last-time.md`** - Deployment issue log

### Release Automation (`docs/release/`)

Release prompts and declaration records:

- **`RELEASE_AGENT_PROMPT.md`** - Release agent instructions
- **`RELEASE_AUDIT_AGENT_PROMPT.md`** - Release audit agent instructions
- **`prompts/pre-release-prompt.md`** - Pre-release checklist prompt
- **`prompts/release-prompt.md`** - Release execution prompt
- **`declarations/`** - Version declaration templates and records

### Deployment Documentation (`docs/dev/deploy/`)

- **`vps-golden-path.md`** - Production deployment guide
  - Ubuntu + Caddy + systemd + Postgres setup
  - Complete VPS configuration walkthrough
  - Security, backups, and monitoring setup

---

## 📊 Audit Trail & Analysis

### Core Monitoring (`docs/dev/Archive/CM/`)

Production readiness audits and corrective missions:

- **CM-001 through CM-008** - Core production hardening audits
- **CM-M5-N1, CM-M6-01, CM-M6-02** - Milestone-specific audits
- Each includes main audit document and `_followup.md` with implementation status

### Reports Directory (`docs/dev/reports/`)

#### Code Quality Analysis

- **`sum_core_code_review_2025-12-10.md`** - Comprehensive code review report
  - Full package analysis and recommendations
  - Security, performance, and maintainability assessment

#### Technical Analysis

- **`site-settings-duplication-analysis.md`** - Settings architecture analysis
- **`db-loss.md`** - Database loss incident report and recovery
- **`end-of-milestone-review.md`** - Milestone completion analysis

#### Status Reports

- **`daily/`** - Daily development progress reports
- **`status/`** - Project status snapshots
- **`M2/`, `M3/`, `M4/`** - Milestone-specific reports

---

## 🎯 Side Projects & Experiments

### Side Quests Directory (`docs/dev/side_quests/`)

Task-specific documentation for experimental or secondary work:

- **`css_modular_task.md`** - CSS architecture refactoring task
- **`db_relation_issue.md`** - Database relationship troubleshooting
- **`db_relation_issue_chat.md`** - Related technical discussion

---

## 📋 Excluded Documentation (Audit Trail Only)

The following directories contain milestone transcripts and work reports that serve as audit trail but are not functional documentation:

- `docs/dev/Archive/M0/` through `docs/dev/Archive/M6/` - Milestone work transcripts
- `docs/dev/Archive/DOC/` - Documentation work sessions
- `docs/dev/Archive/NAV/` - Navigation work sessions

These are preserved for audit purposes but excluded from this functional documentation index.

Note: Archive documents are historical snapshots and may contain stale paths or dead links.

---

## 🗺️ Documentation Usage Guide

### For New Contributors

1. **Start here:** `README.md`
2. **Understand the platform:** `dev/AGENT-ORIENTATION.md`
3. **Learn the architecture:** `dev/master-docs/SUM-PLATFORM-SSOT.md`
4. **Follow standards:** `dev/hygiene.md`

### For Implementation Work

1. **Block development:** `dev/blocks-reference.md`
2. **Page development:** `dev/page-types-reference.md`
3. **Theme/CSS work:** `dev/THEME-GUIDE.md`
4. **Client integration:** `dev/WIRING-INVENTORY.md`

### For Operations & Deployment

1. **Release a new version:** `ops-pack/RELEASE_RUNBOOK.md`
2. **Deploy fresh site:** `ops-pack/deploy-runbook.md`
3. **Upgrade existing site:** `ops-pack/upgrade-runbook.md`
4. **Production setup (detailed):** `dev/deploy/vps-golden-path.md`
5. **Git workflow:** `dev/GIT_STRATEGY.md`
6. **CLI usage:** `dev/cli.md`

### For Strategic Planning

1. **Current state:** `dev/master-docs/SUM-PLATFORM-SSOT.md`
2. **Future roadmap:** `dev/master-docs/POST-MVP_BIG-PLAN.md`
3. **Architecture evolution:** `dev/master-docs/THEME-ARCHITECTURE-SPECv1.md`

---

## 📈 Documentation Statistics

- **Total markdown files:** 485 (including Archive/)
- **Active markdown files:** 118 (excluding Archive/)
- **Key strategic documents:** 6 in master-docs/
- **Implementation references:** 8 core reference files
- **Design system docs:** 10+ files
- **Audit trail documents:** 30+ CM and report files
- **Lines of documentation:** ~156,000+ lines total (including Archive/)

---

## ✅ Maintenance Notes

This DDD should be updated when:

- New documentation files are added
- Major documentation is restructured
- Documentation purposes or scopes change
- New documentation directories are created

**Last comprehensive review:** December 29, 2025
