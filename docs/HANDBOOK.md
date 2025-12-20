# SUM Platform Handbook

> The definitive guide to building, deploying, and maintaining lead-focused websites with the SUM Platform.

---

## 🧭 Introduction

The SUM Platform is a Django/Wagtail-based foundation designed for the rapid deployment of high-performance websites for the home improvement industry. This handbook serves as the central entry point for all contributors and operators.

### Core Philosophy

- **Speed to Value**: Launch a production-ready site in 2–3 days.
- **Lead-First Design**: Every feature is optimized for conversion.
- **Maintainability**: A shared core (`sum_core`) with individual client "skins".
- **AI-Native**: Structured for efficient assistance from AI coding agents.

---

## 🚀 Quick Start

For those ready to dive straight in.

1. **Environment Setup**:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   make install-dev
   ```
2. **Launch Development Server**:
   ```bash
   make run
   ```
3. **Access Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

See the [Root README](../README.md) for detailed setup requirements.

---

## 🏗️ Platform Architecture

SUM uses a **Core-Client pattern**.

- **`sum_core`**: The engine. Contains all models, blocks, logic, and base styles.
- **Client Projects**: The shell. Contains site-specific settings, overrides, and unique content.

### Key Links

- [Codebase Structure](dev/CODEBASE-STRUCTURE.md)
- [Agent Orientation](dev/AGENT-ORIENTATION.md)
- [Single Source of Truth (SSOT)](dev/master-docs/SUM-PLATFORM-SSOT.md)

---

## 🧩 Building Blocks & Pages

The platform is powered by Wagtail StreamField.

### [Block Reference](dev/blocks-reference.md)

A catalog of all available design elements (Hero, Services, Testimonials, etc.).

### [Page Types Reference](dev/page-types-reference.md)

The structural models used for sites (HomePage, ServicePage, Blog, etc.).

### Development Guidelines

- Always use the [Design Tokens](dev/design/css-architecture-and-tokens.md).
- Follow the [Hygiene Standards](dev/hygiene.md).
- Reference the [Navigation System](dev/NAV/navigation.md).

---

## 🎨 Design & Theming

SUM uses a proprietary theme system that allows brand injection without breaking core updates.

- **Theme System Architecture**: [THEME-ARCHITECTURE-SPECv1.md](dev/master-docs/THEME-ARCHITECTURE-SPECv1.md)
- **CSS Architecture**: [css-architecture-and-tokens.md](dev/design/css-architecture-and-tokens.md)
- **Token System**: Managed via Wagtail SiteSettings.

---

## 📥 Leads & Integrations

The "reason for being" for the platform.

- **Lead Capture Pipeline**: Persists every submission with full attribution (UTMs, Referrer).
- **Spam Protection**: Honeypots, rate-limiting, and timing checks.
- **Integrations**: Zapier webhooks and email notifications.

See the [SSOT section on Lead Management](dev/master-docs/SUM-PLATFORM-SSOT.md#8-lead-management-system) for technical details.

---

## 🛠️ Operations & Maintenance

Day-to-day operations are managed through the **Ops Pack**.

### [Operations Router](ROUTER.md)

The "hot path" for common tasks:

- [Release Checklist](ops-pack/release-checklist.md)
- [Deployment Runbook](ops-pack/deploy-runbook.md)
- [Upgrade Runbook](ops-pack/upgrade-runbook.md)
- [Verification / Smoke Tests](ops-pack/smoke-tests.md)

---

## 📚 Documentation Map (The "DDD")

For a full inventory of every document in this repository, see the **[Documentation Documentation Document (DDD.md)](DDD.md)**.

### Vital Strategic Documents

- [Post-MVP Expansion Plan](dev/master-docs/POST-MVP_BIG-PLAN.md)
- [Product Requirements (PRD)](dev/master-docs/prd-sum-platform-v1.1.md)
- [Release Workflow](dev/release-workflow.md)

---

## 🔮 Next Steps for Documentation

This handbook is currently a **scaffold**. To complete it, the following work is needed:

1. **Unified Search/Index**: Ensure all key headings in other docs are mirrored or summarized here.
2. **"Persona-Based" Paths**: Explicit sections for "I am a Designer", "I am a Content Editor", "I am a DevOps Engineer".
3. **Tutorials**: Add "How to build your first block" and "Launching your first site" tutorials directly into this handbook (or linked sub-docs).
4. **Visuals**: Use diagrams (Mermaid) to explain the Core-Client relationship and Lead flow visually.
5. **Glossary**: Define platform-specific terms like "Wiring", "The Loop", and "CM (Corrective Missions)".
