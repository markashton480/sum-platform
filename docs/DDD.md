# Documentation Documentation Document (DDD)

**Document Version:** 1.0  
**Date:** December 17, 2025  
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
└── dev/                               # All development documentation
    ├── master-docs/                   # Core strategic documents
    ├── [individual reference files]   # Implementation guides
    ├── design/                        # Design system & UI specs
    ├── deploy/                        # Deployment guides
    ├── CM/                            # Corrective Missions audit reports
    ├── reports/                       # Analysis & review documents
    ├── reviews/                       # Code review guidelines
    ├── side_quests/                   # Experimental/task-specific docs
    └── [excluded: M0-M6, DOC, NAV]    # Audit trail directories
```

---

## 🎯 Entry Points & Essential Reading

### Main Repository Entry Point

- **Location:** `README.md` (repository root)
- **Purpose:** Primary "how the repo works" guide, quick start instructions
- **What it contains:**
  - Current platform status (end of Milestone 5)
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

#### Core Design System

- **`css-architecture-and-tokens.md`** - Primary CSS architecture guide

  - Token system explanation
  - CSS file organization and structure
  - Brand injection via Wagtail settings
  - Implementation guidelines for developers/AI agents

- **`design_system.md`** - Brand-agnostic design philosophy
  - "The Frame, Not The Paint" approach
  - HSL relationship model for dynamic theming
  - Token system architecture

#### Visual Design References

- **`premium-trade-website-v3-final.html`** - Visual design reference
- **Component-specific design files:**
  - `content_blocks_design.html`
  - `faq_and_process_design.html`
  - `form_design.html`
  - `gallery_design.html`
  - `portfolio_design.html`
  - `service_card_design.html`
  - `testimonials_design.html`

---

## 🔧 Development & Contributor Documentation

### Development Standards

- **`hygiene.md`** - Repository hygiene standards

  - Code formatting and linting requirements
  - Dependency management rules
  - Testing standards and fixtures

- **`reviews/daily_code_review.md`** - Daily code review guidelines
  - Review process for Django/Wagtail development
  - Quality standards and checkpoints

### Development Tools

- **`cli.md`** - SUM CLI documentation
  - `sum init` and `sum check` command specifications
  - Project scaffolding workflow

### Development Decisions

- **`decisions.md`** - Architectural decisions log
  - Docker deferral decision and rationale
- **`git_strategy.md`** - Git workflow and branching strategy
- **`release-workflow.md`** - Release process documentation

---

## 🚀 Operations & Deployment

### Deployment Documentation (`docs/dev/deploy/`)

- **`vps-golden-path.md`** - Production deployment guide
  - Ubuntu + Caddy + systemd + Postgres setup
  - Complete VPS configuration walkthrough
  - Security, backups, and monitoring setup

---

## 📊 Audit Trail & Analysis

### Core Monitoring (`docs/dev/CM/`)

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

- `docs/dev/M0/` through `docs/dev/M6/` - Milestone work transcripts
- `docs/dev/DOC/` - Documentation work sessions
- `docs/dev/NAV/` - Navigation work sessions

These are preserved for audit purposes but excluded from this functional documentation index.

---

## 🗺️ Documentation Usage Guide

### For New Contributors

1. **Start here:** `README.md`
2. **Understand the platform:** `AGENT-ORIENTATION.md`
3. **Learn the architecture:** `SUM-PLATFORM-SSOT.md`
4. **Follow standards:** `hygiene.md`

### For Implementation Work

1. **Block development:** `blocks-reference.md`
2. **Page development:** `page-types-reference.md`
3. **CSS work:** `css-architecture-and-tokens.md`
4. **Client integration:** `WIRING-INVENTORY.md`

### For Operations & Deployment

1. **Production setup:** `deploy/vps-golden-path.md`
2. **CLI usage:** `cli.md`
3. **Quality standards:** `reviews/daily_code_review.md`

### For Strategic Planning

1. **Current state:** `SUM-PLATFORM-SSOT.md`
2. **Future roadmap:** `POST-MVP_BIG-PLAN.md`
3. **Architecture evolution:** `THEME-ARCHITECTURE-SPECv1.md`

---

## 📈 Documentation Statistics

- **Total documentation files:** 50+ active files
- **Key strategic documents:** 6 in master-docs/
- **Implementation references:** 8 core reference files
- **Design system docs:** 10+ files
- **Audit trail documents:** 30+ CM and report files
- **Lines of documentation:** ~15,000+ lines total

---

## ✅ Maintenance Notes

This DDD should be updated when:

- New documentation files are added
- Major documentation is restructured
- Documentation purposes or scopes change
- New documentation directories are created

**Last comprehensive review:** December 17, 2025
