# Product Requirements Document (PRD)
## SUM Platform - Client Website Deployment System

**Document Version:** 1.1  
**Date:** December 7, 2025  
**Status:** Final Draft  
**Related Documents:** Discovery Brief v1.1, Project Initiation Packet v1.1

**Changelog:**
- **v1.1 (Dec 7, 2025):**
  - Clarified brand separation: client sites use client branding, not Straight Up Marketing's brand
  - Added Design Scope section (6.1) clarifying scope and admin theming approach
  - Restructured Section 6 to separate high-level requirements from implementation details
  - Added Design Implementation Guardrails (6.6) with token-only styling rules and AI constraints
  - Moved detailed CSS/HTML specifications to Appendix C: Design System Reference
  - Updated US-BR03 Theme Presets to clarify as internal admin tool, not client-facing
  - Removed Oswald/Source Sans as defaults; fonts now explicitly set per client
  - Added visual reference note for `premium-trade-website-v3-final.html`
- **v1.0 (Dec 7, 2025):** Initial draft

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [User Stories & Acceptance Criteria](#2-user-stories--acceptance-criteria)
3. [Functional Requirements](#3-functional-requirements)
4. [Technical Requirements](#4-technical-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Design Specifications](#6-design-specifications)
7. [Integration Requirements](#7-integration-requirements)
8. [Data Requirements](#8-data-requirements)
9. [Testing Strategy](#9-testing-strategy)
10. [Deployment & Launch](#10-deployment--launch)
11. [Future Roadmap](#11-future-roadmap)

**Appendices:**
- [Appendix A: Glossary](#appendix-a-glossary)
- [Appendix B: File Path Reference](#appendix-b-file-path-reference)
- [Appendix C: Design System Reference](#appendix-c-design-system-reference)

---

## 1. Product Overview

### 1.1 Product Vision

The SUM Platform (Straight Up Marketing Client Website Platform) is a scalable website deployment system that enables rapid creation and maintenance of high-quality, conversion-focused websites for home improvement businesses. The platform delivers professional websites in 2-3 days through a template-based architecture built on Django and Wagtail CMS.

### 1.2 Product Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Deployment Speed | 2-3 days per new client site | Time from signed contract to live site |
| Scale | 20 client websites in 12 months | Active site count |
| Lead Generation | Measurable increase in client enquiries | Form submissions tracked per site |
| SEO Performance | Client sites ranking for target keywords | Search Console data within 3-6 months |
| Client Retention | 90%+ monthly retainer retention | Churn rate tracking |
| Platform Maintainability | Updates deployed to all sites within 1 day | Deployment time tracking |

### 1.3 Target Users

#### 1.3.1 Internal Development Team (Admin Users)
- **Role:** Create, deploy, and maintain client websites
- **Technical Level:** Proficient with Django, Wagtail, and web development
- **Primary Goals:** Fast deployment, easy customisation, efficient maintenance
- **Key Workflows:** Site scaffolding, branding configuration, content population, multi-site updates

#### 1.3.2 Client Content Editors (End Clients)
- **Role:** Update website content, view leads, manage basic settings
- **Technical Level:** Limited technical expertise
- **Primary Goals:** Simple content updates, lead visibility, site "just works"
- **Key Workflows:** Edit services, upload photos, write blog posts, view enquiries

#### 1.3.3 Website Visitors (End Customers)
- **Role:** Research and contact home improvement service providers
- **Technical Level:** General public, mobile-first browsing
- **Primary Goals:** Find information quickly, establish trust, easy contact
- **Key Workflows:** Browse services, view portfolio, read reviews, submit enquiries

### 1.4 Success Metrics

| Category | Metric | Target | Phase |
|----------|--------|--------|-------|
| **Platform** | New site deployment time | ≤3 days | Phase 1 |
| **Platform** | Core package test coverage | ≥80% | Phase 1 |
| **Performance** | Lighthouse Performance score | ≥90 (reference pages) | Phase 1 |
| **Performance** | Page load time (4G mobile) | <3 seconds | Phase 1 |
| **Quality** | Lighthouse Accessibility score | ≥90 (reference pages) | Phase 1 |
| **Quality** | Lighthouse SEO score | ≥90 (reference pages) | Phase 1 |
| **Reliability** | Platform uptime | ≥99.5% | Phase 1 |
| **Business** | Client site lead conversion | Baseline + improvement tracking | Phase 2 |

---

## 2. User Stories & Acceptance Criteria

### 2.1 Priority Definitions

| Priority | Definition | Phase Impact |
|----------|------------|--------------|
| **P0** | Must-have for Phase 1 launch | Blocks release if incomplete |
| **P1** | Should-have, can slip to Phase 1.1 | Desirable but not blocking |
| **P2** | Nice-to-have, Phase 2+ | Explicitly deferred |

### 2.2 Epic: Platform Foundation

#### US-F01: Repository & Development Environment
> As a developer, I want a properly configured monorepo with Docker-based local development so that I can develop the platform with consistent, reproducible tooling.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | Monorepo initialised with directory structure: `core/`, `boilerplate/`, `clients/`, `cli/`, `docs/`, `scripts/`, `infrastructure/` | P0 |
| AC2 | Git hooks configured via pre-commit (Black, isort, flake8) | P0 |
| AC3 | `pyproject.toml` configured for linting and type checking | P0 |
| AC4 | Makefile with commands: `make lint`, `make test`, `make run`, `make format` | P0 |
| AC5 | Docker Compose configuration with Django, PostgreSQL 17, Redis 7/8, Node.js 24 | P0 |
| AC6 | `docker-compose up` brings up working Wagtail admin at localhost:8000 | P0 |
| AC7 | Volume mounts enable hot-reloading during development | P0 |
| AC8 | README with quick-start guide for new developers | P0 |

#### US-F02: Core Package Structure
> As a developer, I want a well-organised core package (`sum_core`) so that shared functionality can be maintained centrally and imported by client projects.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `sum_core` package installable via `pip install -e ./core` | P0 |
| AC2 | App structure: `blocks/`, `pages/`, `leads/`, `branding/`, `analytics/`, `seo/`, `integrations/`, `utils/` | P0 |
| AC3 | Version defined in `__init__.py`: `__version__ = "X.Y.Z"` | P0 |
| AC4 | `pyproject.toml` with package metadata, dependencies, and optional dev dependencies | P0 |
| AC5 | Test project (`sum_core.test_project`) for CI testing | P0 |
| AC6 | Templates namespaced under `sum_core/templates/sum_core/` | P0 |
| AC7 | Static files namespaced under `sum_core/static/sum_core/` | P0 |

#### US-F03: Client Boilerplate Project
> As a developer, I want a template Django/Wagtail project so that new client sites can be scaffolded quickly with consistent configuration.

| ID  | Acceptance Criteria                                                   | Priority |
| --- | --------------------------------------------------------------------- | -------- |
| AC1 | Django 5.2.x project with Wagtail 7.0.x pre-configured                | P0       |
| AC2 | Settings split: `base.py`, `local.py`, `production.py`                | P0       |
| AC3 | Environment variables loaded via `DATABASE_URL` (12-factor style)     | P0       |
| AC4 | `requirements.txt` with pinned `sum-core==X.Y.Z` and all dependencies | P0       |
| AC5 | CSS build pipeline with Node.js (e.g. PostCSS)                        | P0       |
| AC6 | Template override directory structure: `templates/overrides/`         | P0       |
| AC7 | Client-specific static files directory: `static/client/`              | P0       |
| AC8 | `.env.example` with all required environment variables documented     | P0       |

---

### 2.3 Epic: StreamField Blocks

#### US-B01: Hero Blocks
> As a content editor, I want hero section blocks so that I can create impactful page headers with flexible layouts.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `HeroImageBlock`: Full-width image background with configurable overlay opacity | P0 |
| AC2 | `HeroGradientBlock`: Gradient background using brand colours | P0 |
| AC3 | Configurable fields: headline (required), subheadline (optional), CTA buttons (0-2) | P0 |
| AC4 | CTA button options: text, URL, style (primary/secondary/outline), open in new tab | P0 |
| AC5 | Image field with required alt text for `HeroImageBlock` | P0 |
| AC6 | Responsive: Text stacks properly on mobile, image scales appropriately | P0 |
| AC7 | Preview renders correctly in Wagtail admin | P0 |
| AC8 | Unit tests validate block structure and required fields | P0 |

#### US-B02: Service Cards Block
> As a content editor, I want service card blocks so that I can showcase services in an attractive grid layout.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `ServiceCardsBlock`: Configurable grid (3-column desktop, 2-column tablet, 1-column mobile) | P0 |
| AC2 | Each card: icon (SVG or image), title, description (rich text), link (optional) | P0 |
| AC3 | Minimum 1 card, maximum 12 cards per block | P0 |
| AC4 | Hover states with smooth transitions (transform, shadow) | P0 |
| AC5 | Cards maintain equal height within rows | P0 |
| AC6 | Unit tests for block structure and card count validation | P0 |

#### US-B03: Testimonials Block
> As a content editor, I want testimonial blocks so that I can display customer reviews and build trust.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `TestimonialsBlock`: Card-based layout with configurable display count | P0 |
| AC2 | Each testimonial: quote text (required), author name (required), company (optional), photo (optional), rating (1-5 stars, optional) | P0 |
| AC3 | Star rating renders as filled/empty star icons | P0 |
| AC4 | Responsive grid: 3-column desktop, 2-column tablet, 1-column mobile | P0 |
| AC5 | Quote marks styled appropriately (large decorative or subtle) | P0 |
| AC6 | Unit tests for testimonial data validation | P0 |

#### US-B04: Call-to-Action Blocks
> As a content editor, I want CTA blocks so that I can drive conversions throughout pages.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `CTAInlineBlock`: Inline CTA with headline, description, and button(s) | P0 |
| AC2 | `CTAFullWidthBlock`: Full-width banner CTA with background colour/image option | P0 |
| AC3 | Configurable: headline, description (optional), up to 2 buttons | P0 |
| AC4 | Button styles: primary, secondary, outline (uses brand colours) | P0 |
| AC5 | Background options: brand colour, custom colour, or image with overlay | P0 |
| AC6 | Unit tests for both CTA variants | P0 |

#### US-B05: Trust & Social Proof Blocks
> As a content editor, I want trust-building blocks so that I can establish credibility with visitors.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `TrustStripBlock`: Horizontal row of logos/badges (e.g., certifications, associations) | P0 |
| AC2 | Trust strip: minimum 2, maximum 8 items; each item has image and optional link | P0 |
| AC3 | `StatsBlock`: Number statistics with labels (e.g., "500+ Projects", "15 Years Experience") | P0 |
| AC4 | Stats block: 2-4 stat items; each has number, label, optional prefix/suffix | P0 |
| AC5 | Number animation on scroll into view (optional, can be disabled) | P1 |
| AC6 | Unit tests for both block types | P0 |

#### US-B06: Process & FAQ Blocks
> As a content editor, I want process and FAQ blocks so that I can explain services clearly.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `ProcessStepsBlock`: Numbered timeline/steps layout | P0 |
| AC2 | Process steps: 3-8 steps; each has number (auto or manual), title, description | P0 |
| AC3 | Visual connector lines between steps | P0 |
| AC4 | `FAQBlock`: Accordion-style expandable questions/answers | P0 |
| AC5 | FAQ: minimum 1, maximum 20 items; each has question and answer (rich text) | P0 |
| AC6 | Accordion allows multiple open or single open (configurable) | P0 |
| AC7 | FAQ generates FAQ schema markup (JSON-LD) | P1 |
| AC8 | Unit tests for both block types | P0 |

#### US-B07: Gallery Block
> As a content editor, I want a gallery block so that I can showcase project photos.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `GalleryBlock`: Responsive image grid | P0 |
| AC2 | Minimum 1, maximum 20 images per gallery | P0 |
| AC3 | Each image: image file (required), alt text (required), caption (optional) | P0 |
| AC4 | Grid layout: 3-column desktop, 2-column tablet, 1-column mobile | P0 |
| AC5 | Images lazy-loaded for performance | P0 |
| AC6 | Lightbox zoom on click | P1 |
| AC7 | Before/after image slider variant | P1 |
| AC8 | Unit tests for gallery validation | P0 |

#### US-B08: Content Blocks
> As a content editor, I want standard content blocks for flexible page building.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `RichTextBlock`: Enhanced rich text with heading styles (H2-H4), lists, links, bold/italic | P0 |
| AC2 | Rich text: No H1 allowed (reserved for page title), limited formatting options | P0 |
| AC3 | `QuoteBlock`: Styled blockquote with attribution | P0 |
| AC4 | `ButtonGroupBlock`: 1-3 buttons with configurable styles and alignment | P0 |
| AC5 | `SpacerBlock`: Configurable vertical spacing (small/medium/large/custom) | P0 |
| AC6 | `DividerBlock`: Horizontal rule with style options (solid, dashed, branded) | P0 |
| AC7 | `ImageBlock`: Single image with alt text, caption, alignment options | P0 |
| AC8 | Unit tests for all content blocks | P0 |

#### US-B09: Form Blocks
> As a content editor, I want form blocks so that visitors can submit enquiries.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `ContactFormBlock`: Pre-configured contact form (name, email, phone, message) | P0 |
| AC2 | `QuoteRequestFormBlock`: Quote form with configurable fields | P0 |
| AC3 | Quote form configurable fields: project type, budget range, timeline, service area, additional details | P0 |
| AC4 | All forms: required field validation, email format validation, phone format validation | P0 |
| AC5 | Spam protection: honeypot field + rate limiting | P0 |
| AC6 | reCAPTCHA v3 integration (optional, configurable per site) | P1 |
| AC7 | Success message customisable per form | P0 |
| AC8 | Form submissions create Lead records (see Lead Management) | P0 |
| AC9 | Unit tests for form validation and submission | P0 |

---

### 2.4 Epic: Page Types

#### US-P01: Homepage
> As a content editor, I want a flexible homepage so that I can create an engaging entry point for visitors.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `HomePage` model with StreamField body accepting all homepage blocks | P0 |
| AC2 | Available blocks: Hero, ServiceCards, Testimonials, CTA (both), TrustStrip, Stats, ProcessSteps, FAQ, Gallery, RichText, Quote, ButtonGroup, Spacer, Divider, Image, ContactForm, QuoteRequestForm | P0 |
| AC3 | SEO fields: meta title, meta description, OG image | P0 |
| AC4 | Only one HomePage allowed per site (enforced) | P0 |
| AC5 | Template renders all blocks with proper spacing | P0 |

#### US-P02: Service Pages
> As a content editor, I want service pages so that I can describe each service offering in detail.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `ServiceIndexPage`: Parent page listing all services with intro content | P0 |
| AC2 | Service index: StreamField intro area + automatic child page grid | P0 |
| AC3 | `ServicePage`: Individual service with StreamField body | P0 |
| AC4 | Service page fields: title, featured image, short description, StreamField body | P0 |
| AC5 | Service page: Related services section (automatic or manual selection) | P1 |
| AC6 | Page hierarchy enforced: ServicePage must be child of ServiceIndexPage | P0 |
| AC7 | Service schema markup (JSON-LD) on service pages | P1 |

#### US-P03: Standard Pages
> As a content editor, I want standard pages for general content like About and legal pages.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `StandardPage`: General-purpose page with StreamField body | P0 |
| AC2 | Available blocks: All content blocks, CTA blocks, FAQ, Gallery | P0 |
| AC3 | Optional sidebar toggle for two-column layout | P1 |
| AC4 | Can be used for: About, Privacy Policy, Terms, generic content | P0 |

#### US-P04: Contact Page
> As a content editor, I want a contact page template so that visitors have a clear contact point.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `ContactPage` model with dedicated contact template | P0 |
| AC2 | Configurable display: business name, address, phone, email, hours | P0 |
| AC3 | Form selection: choose which form block to display | P0 |
| AC4 | Google Map embed via embed code field (optional) | P1 |
| AC5 | Social media links display | P1 |
| AC6 | LocalBusiness schema markup | P0 |

#### US-P05: Blog Pages
> As a content editor, I want blog functionality so that I can publish articles for SEO and engagement.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `BlogIndexPage`: Paginated list of posts (10 per page default) | P0 |
| AC2 | Blog index: Filter by category, newest first ordering | P0 |
| AC3 | `BlogPostPage`: Full article with StreamField body | P0 |
| AC4 | Blog post fields: title, featured image, excerpt, author (optional), published date | P0 |
| AC5 | `BlogCategory` model with default categories: "Tips & Guides", "Project Showcase", "Industry News", "Company Updates" | P0 |
| AC6 | Categories: Removable and customisable per site | P0 |
| AC7 | Post scheduling: Published date field with draft/scheduled/published status | P0 |
| AC8 | RSS feed at `/blog/feed/` | P0 |
| AC9 | Article schema markup on posts | P1 |
| AC10 | Tags with filtering | P1 |
| AC11 | Related posts section | P1 |
| AC12 | Social sharing buttons | P1 |

#### US-P06: Portfolio/Case Study Pages
> As a content editor, I want portfolio pages so that I can showcase completed projects.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `PortfolioIndexPage`: Grid of project cards with filtering | P0 |
| AC2 | `PortfolioPage`: Individual project showcase | P0 |
| AC3 | Portfolio page fields: title, client name (optional), date, services provided, location, featured image, gallery | P0 |
| AC4 | StreamField body for project description | P0 |
| AC5 | Related projects section | P1 |
| AC6 | Before/after image slider | P1 |
| AC7 | Embedded testimonial option | P1 |

#### US-P07: Service Area Pages
> As a content editor, I want location-specific pages so that I can target local SEO.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `ServiceAreaPage`: Location-specific landing page | P0 |
| AC2 | Fields: location name, region/county, service list for area | P0 |
| AC3 | LocalBusiness schema with location data | P0 |
| AC4 | Template inherits service page styling with location context | P0 |
| AC5 | Map embed showing service area | P1 |

#### US-P08: Landing Pages (Ads)
> As a marketing manager, I want distraction-free landing pages for ad campaigns.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `LandingPage`: Minimal template with reduced navigation | P0 |
| AC2 | Header: Logo only, no navigation menu | P0 |
| AC3 | Footer: Essential links only (privacy, terms), no sitemap | P0 |
| AC4 | Focused CTA with prominent form | P0 |
| AC5 | UTM parameters preserved and captured in form submissions | P0 |
| AC6 | Page excluded from XML sitemap | P0 |

---

### 2.5 Epic: Lead Management

#### US-L01: Lead Capture & Storage
> As a site owner, I want all form submissions stored so that I never lose a potential customer.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `Lead` model stores all form submissions with timestamp | P0 |
| AC2 | Lead fields: name, email, phone, message, form_type, page_url, submitted_at | P0 |
| AC3 | Dynamic form fields stored in JSON field (`form_data`) | P0 |
| AC4 | Lead linked to source page via ForeignKey | P0 |
| AC5 | All leads persisted regardless of email/webhook success | P0 |
| AC6 | Soft delete capability (archived flag, not hard delete) | P0 |

#### US-L02: Lead Source Attribution
> As a site owner, I want to know where each lead came from so that I can measure marketing effectiveness.

| ID  | Acceptance Criteria                                                                                                                                                                                                | Priority |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| AC1 | Raw UTM fields captured: `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`                                                                                                                     | P0       |
| AC2 | URL fields captured: `landing_page_url`, `page_url`, `referrer_url`                                                                                                                                                | P0       |
| AC3 | AC3: Derived `lead_source` field with normalised values (`google_ads`, `meta_ads`, `bing_ads`, `seo`, `direct`, `referral`, `offline`, `other`, `unknown` — displayed in the UI as “Google Ads”, “Meta Ads”, etc.) | P0       |
| AC4 | `LeadSourceRule` model for configurable derivation rules                                                                                                                                                           | P0       |
| AC5 | Default rules: utm_source=google + utm_medium=cpc → "Google Ads"; referrer contains google.com + no utm → "SEO"; no referrer + no utm → "Direct"                                                                   | P0       |
| AC6 | Manual `lead_source` override via dropdown in lead detail view                                                                                                                                                     | P0       |
| AC7 | Free-text `lead_source_detail` field for additional context                                                                                                                                                        | P0       |
| AC8 | All raw UTM fields and URLs visible in lead detail view                                                                                                                                                            | P0       |
| AC9 | UTM parameters captured from URL on page load, persisted in hidden form fields or session                                                                                                                          | P0       |

#### US-L03: Lead Status Workflow
> As a site owner, I want to track lead progress so that I can manage my sales pipeline.

| ID  | Acceptance Criteria                                                     | Priority |
| --- | ----------------------------------------------------------------------- | -------- |
| AC1 | `status` field with values: "New", "Contacted", "Quoted", "Won", "Lost" | P0       |
| AC2 | Default status: "New" on submission                                     | P0       |
| AC3 | Status change logged with timestamp and user                            | P0       |
| AC4 | Status changeable via inline dropdown in list view and detail view      | P0       |
| AC5 | Status filtering in lead list                                           | P0       |

#### US-L04: Lead Notifications
> As a client, I want to be notified immediately when a new lead arrives so that I can respond quickly.

| ID  | Acceptance Criteria                                                                                                   | Priority |
| --- | --------------------------------------------------------------------------------------------------------------------- | -------- |
| AC1 | Email notification sent to configured address on form submission                                                      | P0       |
| AC2 | Notification recipient configured via `SiteSettings.lead_notification_email` (with optional global fallback env var). | P0       |
| AC3 | Email template includes: lead details, form data, source information, link to admin                                   | P0       |
| AC4 | Email template customisable per site                                                                                  | P1       |
| AC5 | Failed email sends logged but don't block form submission                                                             | P0       |
| AC6 | Test email command: `python manage.py test_lead_notification`                                                         | P1       |

#### US-L05: Lead Admin Interface
> As a site owner, I want to manage leads in Wagtail admin so that I can track and respond to enquiries.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | Lead listing in Wagtail admin (not Django admin) | P0 |
| AC2 | List columns: name, email, phone, source, status, date | P0 |
| AC3 | Search by name, email, phone, message content | P0 |
| AC4 | Filter by: status, lead_source, date range, form_type | P0 |
| AC5 | Lead detail view showing all captured data including raw UTM fields | P0 |
| AC6 | Inline status update in list view | P0 |
| AC7 | CSV export of filtered leads with all fields | P0 |
| AC8 | Permission: Content Editors can view leads, Admins can edit status | P0 |
| AC9 | Lead count badge in Wagtail menu (new leads) | P1 |

---

### 2.6 Epic: Branding & Customisation

#### US-BR01: Site Settings Model
> As an admin, I want to configure site branding so that each client site has unique styling.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `SiteSettings` model using Wagtail Site Settings | P0 |
| AC2 | Colour fields: primary, secondary, accent, background, text colours | P0 |
| AC3 | Logo uploads: header logo, footer logo, favicon (with size recommendations) | P0 |
| AC4 | Typography: heading font, body font (Google Fonts dropdown) | P0 |
| AC5 | Business info: company name, tagline, phone, email, address, business hours | P0 |
| AC6 | Social links: Facebook, Instagram, LinkedIn, Twitter/X, YouTube, TikTok | P0 |
| AC7 | Settings accessible in all templates via `{% get_site_settings %}` tag | P0 |
| AC8 | Settings cached appropriately for performance | P0 |

#### US-BR02: Dynamic CSS Generation
> As a developer, I want CSS variables generated from branding settings so that styles update automatically.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | Template tag `{% branding_css %}` outputs CSS custom properties in `<head>` | P0 |
| AC2 | CSS variables: `--color-primary`, `--color-secondary`, `--color-accent`, `--color-background`, `--color-text`, etc. | P0 |
| AC3 | All component styles use CSS variables (no hardcoded colours) | P0 |
| AC4 | Google Fonts `<link>` tags generated dynamically based on selected fonts | P0 |
| AC5 | Font variables: `--font-heading`, `--font-body` | P0 |
| AC6 | Changes reflect immediately in development (no caching issues) | P0 |
| AC7 | Production: CSS output cached, invalidated on settings change | P0 |

#### US-BR03: Theme Presets (Internal Tool)
> As a platform admin, I want to apply a theme preset as a starting point for a new client site so that I can quickly establish a professional colour palette before customising to match the client's brand guidelines.

**Note:** Theme presets are an internal convenience for initial site setup. Clients do not select themes themselves—the admin configures branding to match each client's specific brand identity.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | 5 preset themes defined: "Premium Trade", "Professional Blue", "Modern Green", "Warm Earth", "Clean Slate" | P0 |
| AC2 | Each preset: primary, secondary, accent colours + recommended font pairing | P0 |
| AC3 | One-click preset application in SiteSettings admin (internal use only) | P0 |
| AC4 | Preset populates colour/font fields as starting point; always customised to client brand | P0 |
| AC5 | All fields remain manually editable after preset application | P0 |

---

### 2.7 Epic: Analytics & SEO

#### US-A01: Google Analytics Integration
> As a site owner, I want Google Analytics tracking so that I can measure website performance.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | GA4 Measurement ID field in SiteSettings | P0 |
| AC2 | GA4 script injected in `<head>` when Measurement ID present | P0 |
| AC3 | GTM Container ID field in SiteSettings (optional) | P0 |
| AC4 | GTM script injected when Container ID present | P0 |
| AC5 | GTM takes precedence if both GA4 and GTM configured | P0 |
| AC6 | No scripts loaded when IDs are empty | P0 |
| AC7 | Scripts respect cookie consent (when implemented) | P1 |

#### US-A02: Event Tracking
> As a site owner, I want key events tracked so that I can measure conversions.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | Form submission events pushed to dataLayer: `form_submission`, form_type, page_url | P0 |
| AC2 | Phone click events: `phone_click` with phone number | P0 |
| AC3 | Email click events: `email_click` with email address | P0 |
| AC4 | CTA button click events: `cta_click` with button text and destination | P0 |
| AC5 | Event tracking code in shared JavaScript module | P0 |

#### US-A03: Simple Analytics Dashboard
> As a site owner, I want a simple analytics summary in Wagtail so that I can see key metrics at a glance.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | Dashboard panel on Wagtail home showing summary metrics | P0 |
| AC2 | Display: Total leads (last 30 days) from database | P0 |
| AC3 | Display: Leads by status breakdown (pie or bar) | P0 |
| AC4 | Display: Leads by source breakdown | P0 |
| AC5 | Link to external GA dashboard | P0 |
| AC6 | Clear label: "For detailed analytics, visit Google Analytics" | P0 |

#### US-A04: SEO Foundation
> As a content editor, I want SEO fields and tools so that pages rank well in search.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | All page types have: meta title field, meta description field | P0 |
| AC2 | Meta title default: page title + site name | P0 |
| AC3 | Character count indicators for meta fields (title: 60, description: 160) | P0 |
| AC4 | Open Graph tags: og:title, og:description, og:image, og:url, og:type | P0 |
| AC5 | OG image field on pages, falls back to featured image, then site default | P0 |
| AC6 | Twitter Card tags: twitter:card, twitter:title, twitter:description, twitter:image | P1 |
| AC7 | Canonical URL tag on all pages | P0 |

#### US-A05: Structured Data
> As a site owner, I want schema markup so that search engines better understand my content.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `LocalBusinessSchemaMixin` applied to HomePage and ContactPage | P0 |
| AC2 | LocalBusiness schema includes: name, address, phone, email, hours, geo coordinates | P0 |
| AC3 | Article schema on BlogPostPage: headline, author, datePublished, image | P1 |
| AC4 | Service schema on ServicePage | P1 |
| AC5 | FAQ schema on pages with FAQBlock | P1 |
| AC6 | BreadcrumbList schema on all pages | P1 |
| AC7 | Schema output as JSON-LD in `<head>` | P0 |

#### US-A06: Technical SEO
> As a site owner, I want technical SEO elements configured correctly.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | XML sitemap auto-generated at `/sitemap.xml` | P0 |
| AC2 | Sitemap excludes: LandingPages, unpublished pages, noindex pages | P0 |
| AC3 | Sitemap includes: lastmod, changefreq, priority | P0 |
| AC4 | `robots.txt` configurable via admin or file | P0 |
| AC5 | Default robots.txt allows all, references sitemap | P0 |
| AC6 | Noindex option per page | P0 |
| AC7 | 301 redirects manageable via Wagtail redirects | P0 |

---

### 2.8 Epic: Integrations

#### US-I01: Zapier Webhook Integration
> As a site owner, I want form submissions sent to Zapier so that I can automate workflows.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | Webhook URL field in SiteSettings | P0 |
| AC2 | Lead data POSTed to webhook URL on form submission | P0 |
| AC3 | Webhook triggered asynchronously via Celery task | P0 |
| AC4 | Failed webhooks: logged, retried up to 3 times with exponential backoff | P0 |
| AC5 | Webhook payload follows defined schema (see Section 7.2) | P0 |
| AC6 | Webhook success/failure status logged on Lead record | P0 |
| AC7 | Test webhook button in admin | P1 |

#### US-I02: HubSpot Integration (Optional)
> As a site owner, I want leads synced to HubSpot so that I can manage them in my CRM.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | HubSpot Access Token field in SiteSettings | P1 |
| AC2 | Lead creates/updates HubSpot Contact on submission | P1 |
| AC3 | Field mapping: email (primary), name, phone, message, source | P1 |
| AC4 | HubSpot sync triggered asynchronously via Celery | P1 |
| AC5 | Sync errors logged, don't block form submission | P1 |

#### US-I03: Email Delivery
> As a developer, I want reliable email delivery for notifications.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | SMTP configuration via environment variables | P0 |
| AC2 | Support for SendGrid, Mailgun, or generic SMTP | P0 |
| AC3 | HTML email templates with text fallback | P0 |
| AC4 | Email sending via Django's email backend | P0 |
| AC5 | Failed sends logged with error details | P0 |

---

### 2.9 Epic: CLI & Deployment

#### US-D01: CLI Init Command
> As a developer, I want a CLI to scaffold new client projects so that I can deploy sites quickly.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `sum init <project-name>` creates new client directory in `clients/` | P0 |
| AC2 | Copies boilerplate with project name substituted in settings | P0 |
| AC3 | Generates unique `SECRET_KEY` | P0 |
| AC4 | Creates `.env` file from `.env.example` template | P0 |
| AC5 | Sets `sum-core==X.Y.Z` in `requirements.txt` (current core version) | P0 |
| AC6 | Validates project name: lowercase, alphanumeric + hyphens, no spaces | P0 |
| AC7 | Outputs next steps instructions | P0 |
| AC8 | Refuses to overwrite existing project directory | P0 |

#### US-D02: CLI Check Command
> As a developer, I want to validate project setup before deployment.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `sum check <project-path>` validates project structure | P0 |
| AC2 | Verifies `sum-core` version is pinned in requirements.txt | P0 |
| AC3 | Verifies required environment variables are set | P0 |
| AC4 | Verifies settings files exist and are valid Python | P0 |
| AC5 | Reports warnings and errors with actionable messages | P0 |
| AC6 | Exit code 0 on success, 1 on errors | P0 |

#### US-D03: Server Deployment Script
> As a developer, I want deployment scripts so that I can deploy client sites to production.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `deploy-client.sh` script handles initial deployment and updates | P0 |
| AC2 | Creates Python venv if not exists | P0 |
| AC3 | Installs dependencies from pinned `requirements.txt` | P0 |
| AC4 | Runs database migrations | P0 |
| AC5 | Collects static files | P0 |
| AC6 | Restarts Gunicorn service via systemd | P0 |
| AC7 | Optional backup before update (flag: `--backup`) | P0 |
| AC8 | Health check after restart | P0 |

#### US-D04: Infrastructure Templates
> As a developer, I want infrastructure configuration templates.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | Nginx config template with SSL, security headers, static file serving | P0 |
| AC2 | Systemd service template for Gunicorn | P0 |
| AC3 | Systemd service template for Celery worker | P0 |
| AC4 | Systemd service template for Celery beat (if needed) | P0 |
| AC5 | Documentation for initial VPS setup | P0 |

#### US-D05: Backup System
> As a developer, I want automated backups for disaster recovery.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | `backup.sh` script performs PostgreSQL dump per database | P0 |
| AC2 | Backup compressed with gzip | P0 |
| AC3 | Backup uploaded to off-site storage (S3/Spaces/B2) | P0 |
| AC4 | 30-day retention with automatic cleanup | P0 |
| AC5 | Cron job configuration for nightly backups | P0 |
| AC6 | `restore.sh` script with confirmation prompt | P0 |
| AC7 | Restore documentation with step-by-step guide | P0 |

#### US-D06: Monitoring Setup
> As a developer, I want monitoring so that I know when things break.

| ID | Acceptance Criteria | Priority |
|----|---------------------|----------|
| AC1 | UptimeRobot (or similar) monitoring configured per site | P0 |
| AC2 | Sentry integration for error tracking | P0 |
| AC3 | Sentry DSN configurable via environment variable | P0 |
| AC4 | Alert notifications configured (email) | P0 |
| AC5 | Health check endpoint at `/health/` returning JSON status | P0 |

---

## 3. Functional Requirements

### 3.1 Form System

#### 3.1.1 Form Configuration

Forms are configurable per site and per form instance. The system supports two primary form types with extensible field configurations.

**Contact Form Fields (Default):**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `name` | CharField | Yes | Max 100 characters |
| `email` | EmailField | Yes | Valid email format |
| `phone` | CharField | No | UK phone format (regex) |
| `message` | TextField | Yes | Max 2000 characters |

**Quote Request Form Fields (Configurable):**
| Field | Type | Required | Configurable |
|-------|------|----------|--------------|
| `name` | CharField | Yes | No |
| `email` | EmailField | Yes | No |
| `phone` | CharField | Yes | No |
| `project_type` | ChoiceField | Configurable | Yes - options defined per site |
| `budget_range` | ChoiceField | No | Yes - options defined per site |
| `timeline` | ChoiceField | No | Yes - options: ASAP, 1-3 months, 3-6 months, 6+ months, Flexible |
| `service_area` | CharField | No | Yes - postcode or area |
| `details` | TextField | Yes | No |

**Configurable Options Model:**
```python
class FormConfiguration(models.Model):
    """Per-site form configuration"""
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    
    # Project type options (newline-separated)
    project_types = models.TextField(
        help_text="One option per line",
        default="Kitchen Renovation\nBathroom Installation\nExtension\nLoft Conversion\nGeneral Enquiry"
    )
    
    # Budget range options (newline-separated)
    budget_ranges = models.TextField(
        help_text="One option per line",
        default="Under £5,000\n£5,000 - £15,000\n£15,000 - £30,000\n£30,000 - £50,000\n£50,000+\nNot sure yet"
    )
    
    # Required fields
    phone_required = models.BooleanField(default=True)
    project_type_required = models.BooleanField(default=False)
```

#### 3.1.2 Form Submission Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Form Submission Flow                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. User submits form                                                    │
│         │                                                                │
│         ▼                                                                │
│  2. Server-side validation                                               │
│         │                                                                │
│         ├─── Invalid ──► Return form with errors                        │
│         │                                                                │
│         ▼ Valid                                                          │
│  3. Spam check (honeypot + rate limit)                                  │
│         │                                                                │
│         ├─── Spam detected ──► Silent discard + log                     │
│         │                                                                │
│         ▼ Pass                                                           │
│  4. Create Lead record (always succeeds)                                │
│         │                                                                │
│         ▼                                                                │
│  5. Queue async tasks (Celery)                                          │
│         │                                                                │
│         ├──► Email notification task                                    │
│         │                                                                │
│         └──► Webhook task (if configured)                               │
│                                                                          │
│  6. Return success response to user                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3.1.3 Spam Protection

**Honeypot Field:**
- Hidden field named `website` (generic name)
- If filled, submission silently discarded
- Logged for analysis but no error shown to user

**Rate Limiting:**
- Maximum 5 submissions per IP per hour
- Configurable per site
- Exceeded submissions return generic error

**reCAPTCHA v3 (Optional):**
- Site key and secret key in SiteSettings
- Score threshold configurable (default: 0.5)
- Falls back gracefully if not configured

### 3.2 Lead Attribution System

#### 3.2.1 Attribution Data Capture

On every page load, the system captures and stores attribution data in the user's session:

```python
# Captured on page load (JavaScript)
attribution_data = {
    # UTM Parameters (from URL)
    'utm_source': request.GET.get('utm_source'),
    'utm_medium': request.GET.get('utm_medium'),
    'utm_campaign': request.GET.get('utm_campaign'),
    'utm_term': request.GET.get('utm_term'),
    'utm_content': request.GET.get('utm_content'),
    
    # URL Data
    'landing_page_url': first_page_url_in_session,
    'page_url': current_page_url,
    'referrer_url': request.META.get('HTTP_REFERER'),
    
    # Timestamp
    'first_touch_at': session_start_timestamp,
}
```

**Attribution Persistence:**
- First-touch attribution: Landing page URL and initial UTM params stored in session
- Last-touch attribution: Current page URL captured on form submission
- Session-based storage prevents loss on page navigation
- Hidden form fields as fallback if session unavailable

#### 3.2.2 Lead Source Derivation Rules

The system derives a normalised `lead_source` value from raw attribution data using configurable rules evaluated in priority order:

**Default Rules:**
| Priority | Condition | Derived Source |
|----------|-----------|----------------|
| 1 | `utm_source=google` AND `utm_medium=cpc` | Google Ads |
| 2 | `utm_source=facebook` OR `utm_source=fb` OR `utm_source=instagram` | Meta Ads |
| 3 | `utm_source=bing` AND `utm_medium=cpc` | Bing Ads |
| 4 | `referrer_url` contains `google.` AND no UTM params | SEO |
| 5 | `referrer_url` contains `bing.` AND no UTM params | SEO |
| 6 | `referrer_url` present AND not search engine | Referral |
| 7 | No `referrer_url` AND no UTM params | Direct |
| 8 | Manual entry (no page_url) | Offline |
| 9 | None of the above | Unknown |

**Rule Model:**
```python
class LeadSourceRule(models.Model):
    """Configurable lead source derivation rules"""
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    priority = models.PositiveIntegerField()
    
    # Conditions (all must match)
    utm_source_contains = models.CharField(max_length=100, blank=True)
    utm_medium_contains = models.CharField(max_length=100, blank=True)
    referrer_contains = models.CharField(max_length=200, blank=True)
    referrer_not_contains = models.CharField(max_length=200, blank=True)
    
    # Result
    derived_source = models.CharField(max_length=50, choices=LEAD_SOURCE_CHOICES)
    
    class Meta:
        ordering = ['site', 'priority']
```

#### 3.2.3 Manual Source Management

For leads created manually or where attribution is unclear:

- Dropdown in lead detail view to override `lead_source`
- Free-text `lead_source_detail` field for context (e.g., "Referred by existing client John Smith", "Met at trade show")
- Override logged with timestamp and user
- Original derived source preserved in `lead_source_original` field

### 3.3 Content Editor Permissions

#### 3.3.1 Role Definitions

**Content Editor Role:**
- Can create, edit, publish pages (within assigned sections)
- Can view all leads
- Can upload images and documents
- Cannot change site settings or branding
- Cannot edit lead status (view only)
- Cannot access user management

**Admin Role:**
- Full access to all CMS features
- Can manage site settings and branding
- Can manage leads (view, edit status, export)
- Can manage users and permissions
- Can access all Wagtail admin features

#### 3.3.2 Implementation

```python
# Wagtail group permissions
CONTENT_EDITOR_PERMISSIONS = [
    'add_page', 'change_page', 'publish_page',
    'add_image', 'change_image',
    'add_document', 'change_document',
    'view_lead',  # Custom permission
]

ADMIN_PERMISSIONS = CONTENT_EDITOR_PERMISSIONS + [
    'change_site_settings',
    'change_lead',
    'export_leads',
    'manage_users',
]
```

### 3.4 Image Handling

#### 3.4.1 Image Optimisation Pipeline

**On Upload:**
1. Validate file type (JPEG, PNG, WebP, GIF)
2. Validate maximum dimensions (4096x4096)
3. Validate maximum file size (10MB)
4. Strip EXIF data (privacy)
5. Generate renditions (Wagtail built-in)

**Rendition Sizes:**
| Name | Max Width | Max Height | Quality | Format |
|------|-----------|------------|---------|--------|
| thumbnail | 150 | 150 | 80 | Original |
| small | 400 | 400 | 80 | Original |
| medium | 800 | 800 | 80 | WebP + fallback |
| large | 1200 | 1200 | 80 | WebP + fallback |
| full | 1920 | 1920 | 85 | WebP + fallback |
| og_image | 1200 | 630 | 85 | JPEG (OG requirement) |

**Template Usage:**
```django
{% image page.featured_image fill-800x600 format-webp as img %}
<img src="{{ img.url }}" 
     alt="{{ page.featured_image.alt_text }}"
     width="{{ img.width }}" 
     height="{{ img.height }}"
     loading="lazy">
```

#### 3.4.2 Alt Text Enforcement

- Alt text field required on all image uploads
- Validation prevents saving image without alt text
- Placeholder reminder shown in admin if empty
- Alt text character limit: 125 characters (recommended max for screen readers)

---

## 4. Technical Requirements

### 4.1 Technology Stack

| Component      | Technology             | Version    | Notes                                  |
| -------------- | ---------------------- | ---------- | -------------------------------------- |
| Language       | Python                 | 3.12.x     | Security support until October 2028    |
| Framework      | Django                 | 5.2.x LTS  | Security support until April 2028      |
| CMS            | Wagtail                | 7.0.x LTS  | Security support until November 2026   |
| Database       | PostgreSQL             | 17.x       | Mainstream support until November 2029 |
| DB Driver      | psycopg                | 3.3.x      | psycopg[binary,pool]                   |
| Task Queue     | Celery                 | 5.6.x      | With Redis broker                      |
| Task Scheduler | django-celery-beat     | 2.8.x      | For scheduled tasks                    |
| Cache/Broker   | Redis                  | 7.x or 8.x | Shared instance                        |
| Frontend       | HTMX                   | Latest     | Progressive enhancement                |
| Styling        | CSS with design tokens | N/A        | PostCSS                                |
| JavaScript     | Vanilla JS             | ES6+       | Minimal, no framework                  |
| Node.js        | Node.js                | 24.x LTS   | For asset compilation                  |
| Web Server     | Nginx                  | Latest     | Reverse proxy + static files           |
| App Server     | Gunicorn               | Latest     | WSGI server                            |

### 4.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SUM Platform Architecture                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         Core Package                             │    │
│  │                        (sum_core)                                │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │    │
│  │  │  blocks/ │ │  pages/  │ │  leads/  │ │    branding/     │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │    │
│  │  │analytics/│ │   seo/   │ │integrations│ │     utils/      │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │               templates/ + static/                        │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                               │                                          │
│                    pip install sum-core==X.Y.Z                          │
│                               │                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Client    │  │   Client    │  │   Client    │  │   Client    │    │
│  │  Project A  │  │  Project B  │  │  Project C  │  │  Project N  │    │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │    │
│  │ │settings │ │  │ │settings │ │  │ │settings │ │  │ │settings │ │    │
│  │ │overrides│ │  │ │overrides│ │  │ │overrides│ │  │ │overrides│ │    │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │    │
│  │      │      │  │      │      │  │      │      │  │      │      │    │
│  │      ▼      │  │      ▼      │  │      ▼      │  │      ▼      │    │
│  │ PostgreSQL  │  │ PostgreSQL  │  │ PostgreSQL  │  │ PostgreSQL  │    │
│  │  Database   │  │  Database   │  │  Database   │  │  Database   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Data Models

#### 4.3.1 Lead Model

```python
class Lead(models.Model):
    """
    Stores all form submissions with full attribution data.
    
    File: sum_core/leads/models.py
    Dependencies: Django, Wagtail
    """
    
    # Core Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    
    # Form Data (JSON for flexible fields)
    form_type = models.CharField(max_length=50, choices=FORM_TYPE_CHOICES)
    form_data = models.JSONField(default=dict, blank=True)
    
    # Source Attribution - Raw Data
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=200, blank=True)
    utm_term = models.CharField(max_length=200, blank=True)
    utm_content = models.CharField(max_length=200, blank=True)
    
    # Source Attribution - URLs
    landing_page_url = models.URLField(max_length=500, blank=True)
    page_url = models.URLField(max_length=500, blank=True)
    referrer_url = models.URLField(max_length=500, blank=True)
    
    # Source Attribution - Derived
    lead_source = models.CharField(
        max_length=50, 
        choices=LEAD_SOURCE_CHOICES,
        default='unknown'
    )
    lead_source_original = models.CharField(max_length=50, blank=True)
    lead_source_detail = models.CharField(max_length=200, blank=True)
    lead_source_override_at = models.DateTimeField(null=True, blank=True)
    lead_source_override_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='lead_source_overrides'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=LEAD_STATUS_CHOICES,
        default='new'
    )
    
    # Relationships
    source_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='leads'
    )
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Integration Status
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    webhook_sent = models.BooleanField(default=False)
    webhook_sent_at = models.DateTimeField(null=True, blank=True)
    webhook_response_code = models.IntegerField(null=True, blank=True)
    
    # Soft Delete
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['lead_source']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['source_page']),
        ]


# Choice Constants
FORM_TYPE_CHOICES = [
    ('contact', 'Contact Form'),
    ('quote', 'Quote Request'),
    ('callback', 'Callback Request'),
    ('manual', 'Manual Entry'),
]

LEAD_STATUS_CHOICES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('quoted', 'Quoted'),
    ('won', 'Won'),
    ('lost', 'Lost'),
]

LEAD_SOURCE_CHOICES = [
    ('google_ads', 'Google Ads'),
    ('meta_ads', 'Meta Ads'),
    ('bing_ads', 'Bing Ads'),
    ('seo', 'SEO'),
    ('direct', 'Direct'),
    ('referral', 'Referral'),
    ('offline', 'Offline'),
    ('other', 'Other'),
    ('unknown', 'Unknown'),
]
```

#### 4.3.2 SiteSettings Model

```python
class SiteSettings(BaseSiteSetting):
    """
    Per-site configuration for branding, business info, and integrations.
    
    File: sum_core/branding/models.py
    Dependencies: Wagtail
    """
    
    # Business Information
    company_name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    business_hours = models.TextField(
        blank=True,
        help_text="e.g., Mon-Fri: 9am-5pm"
    )
    
    # Branding - Colours (no platform defaults - always set per client)
    color_primary = ColorField(default='#2563eb')  # Neutral blue placeholder
    color_secondary = ColorField(default='#1e40af')
    color_accent = ColorField(default='#f59e0b')
    color_background = ColorField(default='#ffffff')
    color_text = ColorField(default='#1f2937')
    color_text_light = ColorField(default='#6b7280')
    
    # Branding - Typography (always configured per client)
    font_heading = models.CharField(
        max_length=100,
        default='',  # Required: admin must set per client
        blank=True,
        help_text="Google Font name for headings (e.g., 'Montserrat', 'Playfair Display')"
    )
    font_body = models.CharField(
        max_length=100,
        default='',  # Required: admin must set per client
        blank=True,
        help_text="Google Font name for body text (e.g., 'Open Sans', 'Roboto')"
    )
    
    # Branding - Logos
    logo_header = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    logo_footer = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    favicon = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    og_default_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Default image for social sharing"
    )
    
    # Social Links
    social_facebook = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_linkedin = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_youtube = models.URLField(blank=True)
    social_tiktok = models.URLField(blank=True)
    
    # Analytics
    ga_measurement_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="Google Analytics 4 Measurement ID (G-XXXXXXXXXX)"
    )
    gtm_container_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="Google Tag Manager Container ID (GTM-XXXXXXX)"
    )
    
    # Integrations
    zapier_webhook_url = models.URLField(blank=True)
    hubspot_access_token = models.CharField(max_length=200, blank=True)
    
    # Notifications
    lead_notification_email = models.EmailField(
        blank=True,
        help_text="Email address for lead notifications"
    )
    
    # SEO
    schema_geo_latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True
    )
    schema_geo_longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True
    )
    
    # Spam Protection
    recaptcha_site_key = models.CharField(max_length=100, blank=True)
    recaptcha_secret_key = models.CharField(max_length=100, blank=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel('company_name'),
            FieldPanel('tagline'),
            FieldPanel('phone'),
            FieldPanel('email'),
            FieldPanel('address'),
            FieldPanel('business_hours'),
        ], heading="Business Information"),
        
        MultiFieldPanel([
            FieldPanel('color_primary'),
            FieldPanel('color_secondary'),
            FieldPanel('color_accent'),
            FieldPanel('color_background'),
            FieldPanel('color_text'),
            FieldPanel('color_text_light'),
        ], heading="Brand Colours"),
        
        MultiFieldPanel([
            FieldPanel('font_heading'),
            FieldPanel('font_body'),
        ], heading="Typography"),
        
        MultiFieldPanel([
            FieldPanel('logo_header'),
            FieldPanel('logo_footer'),
            FieldPanel('favicon'),
            FieldPanel('og_default_image'),
        ], heading="Logos & Images"),
        
        MultiFieldPanel([
            FieldPanel('social_facebook'),
            FieldPanel('social_instagram'),
            FieldPanel('social_linkedin'),
            FieldPanel('social_twitter'),
            FieldPanel('social_youtube'),
            FieldPanel('social_tiktok'),
        ], heading="Social Media"),
        
        MultiFieldPanel([
            FieldPanel('ga_measurement_id'),
            FieldPanel('gtm_container_id'),
        ], heading="Analytics"),
        
        MultiFieldPanel([
            FieldPanel('zapier_webhook_url'),
            FieldPanel('hubspot_access_token'),
        ], heading="Integrations"),
        
        MultiFieldPanel([
            FieldPanel('lead_notification_email'),
        ], heading="Notifications"),
        
        MultiFieldPanel([
            FieldPanel('schema_geo_latitude'),
            FieldPanel('schema_geo_longitude'),
        ], heading="Schema / SEO"),
        
        MultiFieldPanel([
            FieldPanel('recaptcha_site_key'),
            FieldPanel('recaptcha_secret_key'),
        ], heading="Spam Protection"),
    ]
```

#### 4.3.3 Blog Models

```python
class BlogCategory(models.Model):
    """
    Blog post categories. Default categories provided, customisable per site.
    
    File: sum_core/pages/models.py
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='blog_categories'
    )
    
    class Meta:
        verbose_name_plural = "Blog categories"
        unique_together = ['slug', 'site']
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Default categories created on site setup
DEFAULT_BLOG_CATEGORIES = [
    {'name': 'Tips & Guides', 'slug': 'tips-guides'},
    {'name': 'Project Showcase', 'slug': 'project-showcase'},
    {'name': 'Industry News', 'slug': 'industry-news'},
    {'name': 'Company Updates', 'slug': 'company-updates'},
]


class BlogPostPage(Page):
    """Individual blog post."""
    
    # Core Fields
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    excerpt = models.TextField(
        max_length=300,
        help_text="Brief summary for listings"
    )
    category = models.ForeignKey(
        BlogCategory,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    author_name = models.CharField(max_length=100, blank=True)
    published_date = models.DateField(default=date.today)
    
    # Content
    body = StreamField(BLOG_BLOCKS, use_json_field=True)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    og_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('featured_image'),
        FieldPanel('excerpt'),
        FieldPanel('category'),
        FieldPanel('author_name'),
        FieldPanel('published_date'),
        FieldPanel('body'),
    ]
    
    promote_panels = [
        MultiFieldPanel([
            FieldPanel('meta_title'),
            FieldPanel('meta_description'),
            FieldPanel('og_image'),
        ], heading="SEO"),
    ] + Page.promote_panels
    
    parent_page_types = ['pages.BlogIndexPage']
    
    class Meta:
        ordering = ['-published_date']
```

### 4.4 API Specifications

#### 4.4.1 Internal APIs

**Lead Creation (Internal Form Handler):**
```python
# POST /forms/submit/
# Content-Type: application/x-www-form-urlencoded

# Request
{
    "form_type": "quote",
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "07700 900123",
    "project_type": "Kitchen Renovation",
    "budget_range": "£15,000 - £30,000",
    "timeline": "1-3 months",
    "details": "Looking to renovate our kitchen...",
    "website": "",  # Honeypot - must be empty
    
    # Attribution (hidden fields)
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "kitchens-london",
    "landing_page_url": "https://example.com/services/kitchens/?utm_source=...",
    "page_url": "https://example.com/contact/",
    "referrer_url": "https://www.google.com/"
}

# Response (Success)
HTTP 200
{
    "success": true,
    "message": "Thank you for your enquiry. We'll be in touch shortly."
}

# Response (Validation Error)
HTTP 400
{
    "success": false,
    "errors": {
        "email": ["Enter a valid email address."],
        "phone": ["Enter a valid UK phone number."]
    }
}

# Response (Rate Limited)
HTTP 429
{
    "success": false,
    "message": "Too many requests. Please try again later."
}
```

**Health Check Endpoint:**
```python
# GET /health/

# Response
HTTP 200
{
    "status": "healthy",
    "timestamp": "2025-12-07T10:30:00Z",
    "version": "0.3.2",
    "checks": {
        "database": "ok",
        "redis": "ok",
        "celery": "ok"
    }
}
```

### 4.5 Security Requirements

#### 4.5.1 Authentication & Authorisation

| Requirement | Implementation |
|-------------|----------------|
| Password hashing | Django's PBKDF2 (default) |
| Session management | Database-backed sessions |
| CSRF protection | Django CSRF middleware (enabled) |
| Admin URL | Non-obvious path (`/cms/`) |
| Rate limiting | django-ratelimit on login, forms |
| Two-factor auth | Phase 2 consideration |

#### 4.5.2 Data Protection

| Requirement | Implementation |
|-------------|----------------|
| HTTPS enforcement | Nginx redirect + HSTS header |
| SSL certificates | Let's Encrypt (auto-renewal) |
| SQL injection | Django ORM (parameterised queries) |
| XSS prevention | Django template auto-escaping |
| Content Security Policy | Nginx headers |
| Clickjacking protection | X-Frame-Options: SAMEORIGIN |

#### 4.5.3 Security Headers

```nginx
# Nginx security headers
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com;" always;
```

#### 4.5.4 Dependency Security

- Regular dependency updates (monthly minimum)
- Automated vulnerability scanning (Dependabot or similar)
- Pinned dependency versions in requirements.txt
- Security advisory monitoring for Django, Wagtail, Python

### 4.6 Performance Requirements

#### 4.6.1 Response Time Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Server response time (TTFB) | <200ms | 95th percentile |
| Full page load (4G mobile) | <3 seconds | Lighthouse |
| First Contentful Paint | <1.5 seconds | Lighthouse |
| Time to Interactive | <3.5 seconds | Lighthouse |
| Largest Contentful Paint | <2.5 seconds | Lighthouse |

#### 4.6.2 Database Performance

| Metric | Target | Implementation |
|--------|--------|----------------|
| Query time | <100ms | Proper indexing |
| N+1 query prevention | Zero N+1 queries | select_related, prefetch_related |
| Connection pooling | Enabled | psycopg connection pool |

#### 4.6.3 Caching Strategy

```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
    }
}

# Cache timeouts
CACHE_MIDDLEWARE_SECONDS = 60 * 15  # 15 minutes for pages
TEMPLATE_FRAGMENT_CACHE = 60 * 60  # 1 hour for fragments
SITE_SETTINGS_CACHE = 60 * 60 * 24  # 24 hours for settings
```

**Cached Items:**
- Site settings (invalidated on save)
- Navigation structure (invalidated on page publish)
- Template fragments (header, footer)
- Rendered blocks (where appropriate)

---

## 5. Non-Functional Requirements

### 5.1 Scalability

#### 5.1.1 Year 1 Targets (0-20 Sites)

| Resource | Specification |
|----------|---------------|
| VPS | 4 vCPU, 8GB RAM, 80-160GB SSD |
| Database | Single PostgreSQL instance (one DB per client) |
| Redis | Shared instance for cache + Celery |
| Expected capacity | 5-10 sites before scaling review |

#### 5.1.2 Year 2 Targets (20-50 Sites)

| Resource | Specification |
|----------|---------------|
| VPS | Multiple servers or larger instance |
| Database | Consider managed PostgreSQL (RDS, DO Managed) |
| Redis | Dedicated Redis instance |
| CDN | Cloudflare or CloudFront for static assets |

### 5.2 Reliability

| Metric | Target |
|--------|--------|
| Uptime | ≥99.5% |
| Recovery Time Objective (RTO) | <4 hours |
| Recovery Point Objective (RPO) | <24 hours (nightly backups) |
| Backup retention | 30 days |

### 5.3 Browser & Device Support

#### 5.3.1 Supported Browsers

| Browser | Versions |
|---------|----------|
| Chrome | Latest 2 |
| Firefox | Latest 2 |
| Safari | Latest 2 |
| Edge | Latest 2 |

#### 5.3.2 Supported Devices

| Device Type | Breakpoints |
|-------------|-------------|
| Mobile | 320px - 767px |
| Tablet | 768px - 1023px |
| Desktop | 1024px - 1439px |
| Large Desktop | 1440px+ |

### 5.4 Accessibility

**Target:** WCAG 2.1 Level AA compliance on platform-provided templates and components.

**Built-in Features:**
- Semantic HTML structure
- Proper heading hierarchy (H1-H6)
- Skip to content link
- Keyboard navigation support
- Focus indicators on interactive elements
- Form labels and error messages
- Color contrast ratios (4.5:1 minimum for text)
- Alt text required for all images
- ARIA labels where appropriate

**Shared Responsibility:**
- Platform provides accessible components
- Client content must follow guidelines (alt text, heading structure, link text)
- Client-uploaded images must meet contrast requirements

### 5.5 SEO Requirements

**Technical SEO Checklist:**
- [ ] Clean URL structure (no query params for core pages)
- [ ] XML sitemap auto-generated
- [ ] robots.txt configurable
- [ ] Canonical URLs on all pages
- [ ] 301 redirect management
- [ ] Page speed optimised (<3s load time)
- [ ] Mobile-friendly (responsive)
- [ ] HTTPS enforced

**On-Page SEO:**
- [ ] Unique meta titles per page
- [ ] Unique meta descriptions per page
- [ ] H1 tag on every page (single)
- [ ] Image alt text required
- [ ] Internal linking structure
- [ ] Schema markup (LocalBusiness, Article, FAQ, Service)

---

## 6. Design Specifications

### 6.1 Design Scope

This section describes the design system for **client-facing websites** built on the SUM Platform. Each client site is styled according to the client's brand identity, configured via SiteSettings (colours, fonts, logos).

**In Scope:**
- Client website design system (tokens, components, templates)
- Responsive layouts and component specifications
- Design principles and visual guidelines
- Implementation constraints for consistency

**Out of Scope for v1:**
- Full Wagtail admin UI re-skin or white-labelling
- Custom client portals or dashboards
- Straight Up Marketing's own brand application to client sites

**Wagtail Admin Theming (Minimal):**
The Wagtail admin interface uses the standard Wagtail UI with minimal Straight Up Marketing branding:
- Custom logo in admin header
- Accent colour adjustment
- No deep UI customisation in v1

### 6.2 Design Principles

#### 6.2.1 Design Goals

Client websites built on the SUM Platform should embody:

| Principle | Description |
|-----------|-------------|
| **Premium & Professional** | High-quality aesthetic that reflects well on home improvement trades; builds trust with homeowners |
| **Conversion-Focused** | Clear CTAs, prominent contact options, trust signals above the fold |
| **Calm & Trustworthy** | Clean layouts, generous whitespace, no visual clutter or aggressive sales tactics |
| **Mobile-First** | Designed for the majority use case: homeowners researching on mobile devices |
| **Accessible** | WCAG 2.1 AA compliant components; readable, navigable, inclusive |
| **Client-Branded** | Every site reflects the specific client's brand identity, not a generic template look |

#### 6.2.2 Visual Reference

The `premium-trade-website-v3-final.html` template serves as the canonical visual reference for v1 implementation. This reference demonstrates:

- Section rhythm and spacing
- Component styling and interactions
- Typography hierarchy
- Trust signal placement
- Mobile responsive behaviour

All new templates and blocks should achieve visual consistency with this reference.

### 6.3 Design System Overview

#### 6.3.1 Token-Driven Architecture

All visual properties are defined as CSS custom properties (design tokens), populated dynamically from each client's SiteSettings:

**Colour Tokens:**
- `--color-primary` — Client's primary brand colour
- `--color-secondary` — Client's secondary brand colour  
- `--color-accent` — Accent/highlight colour
- `--color-background` — Page background
- `--color-text` — Primary text colour
- `--color-text-light` — Secondary/muted text
- Semantic colours: `--color-success`, `--color-warning`, `--color-error`, `--color-info`
- Surface colours: `--color-surface`, `--color-surface-elevated`
- Border colours: `--color-border`, `--color-border-dark`

**Typography Tokens:**
- `--font-heading` — Client's heading font (Google Fonts)
- `--font-body` — Client's body font (Google Fonts)
- Size scale: `--text-xs` through `--text-6xl`
- Weight scale: `--font-normal`, `--font-medium`, `--font-semibold`, `--font-bold`
- Line heights: `--leading-tight`, `--leading-normal`, `--leading-relaxed`

**Spacing Tokens:**
- Scale from `--space-1` (4px) to `--space-24` (96px)
- Consistent spacing creates visual rhythm across all client sites

**Full token definitions are provided in Appendix C: Design System Reference.**

#### 6.3.2 Component Library

The platform provides a library of pre-built, token-driven components:

| Component | Variants | Usage |
|-----------|----------|-------|
| **Buttons** | Primary, Secondary, Outline, Ghost | CTAs, form submissions, navigation |
| **Cards** | Standard, Hover, Featured | Services, testimonials, portfolio items |
| **Form Inputs** | Text, Email, Phone, Textarea, Select | Contact forms, quote requests |
| **Navigation** | Desktop menu, Mobile drawer, Sticky header | Site navigation |
| **Section Wrappers** | Full-width, Contained, Split | Page layout structure |
| **Typography** | Headings (H1-H6), Body, Caption, Label | Content hierarchy |

All components use design tokens exclusively—no hardcoded colours, fonts, or spacing values.

### 6.4 Responsive Design

#### 6.4.1 Breakpoint System

| Breakpoint | Min Width | Target Devices |
|------------|-----------|----------------|
| Base | 0px | Mobile phones (default) |
| `sm` | 640px | Large phones, small tablets |
| `md` | 768px | Tablets |
| `lg` | 1024px | Laptops, small desktops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large displays |

#### 6.4.2 Responsive Behaviour

- **Mobile-first:** Base styles target mobile; larger screens add complexity
- **Fluid typography:** Font sizes scale smoothly between breakpoints
- **Flexible grids:** Column counts reduce gracefully (3→2→1)
- **Touch targets:** Minimum 44px for interactive elements on mobile
- **Content priority:** Most important content visible without scrolling on mobile

### 6.5 Accessibility Requirements

All platform components must meet WCAG 2.1 Level AA:

| Requirement | Standard | Implementation |
|-------------|----------|----------------|
| Colour contrast | 4.5:1 (text), 3:1 (UI) | Enforced in theme presets; admin guidance for custom colours |
| Focus indicators | Visible on all interactive elements | 3px outline using `--color-primary` |
| Keyboard navigation | Full site navigable via keyboard | Tab order, skip links, focus management |
| Screen reader support | Semantic HTML, ARIA where needed | Proper headings, labels, landmarks |
| Text sizing | No fixed pixel sizes for body text | Relative units (rem) throughout |
| Motion | Respect `prefers-reduced-motion` | Disable animations when preference set |

### 6.6 Design Implementation Guardrails

#### 6.6.1 Token-Only Styling Rule

**All colours, typography, spacing, border-radii, and shadows must come from defined CSS variables / design tokens.**

Templates and components must not contain:
- Inline hex colour codes (e.g., `color: #ff0000`)
- Arbitrary pixel values for spacing (e.g., `margin: 37px`)
- Hardcoded font families (e.g., `font-family: Arial`)
- Custom shadows not defined in the token system

**Correct:**
```css
.component {
    background: var(--color-surface);
    padding: var(--space-6);
    font-family: var(--font-body);
}
```

**Incorrect:**
```css
.component {
    background: #f5f5f5;
    padding: 23px;
    font-family: 'Helvetica Neue', sans-serif;
}
```

#### 6.6.2 Component Reuse Rule

New templates and blocks must reuse existing components from the component library:

- Buttons → Use existing button component with variant prop
- Cards → Use existing card component
- Forms → Use existing form input components
- Navigation → Use existing nav components
- Section layouts → Use existing section wrapper components

Do not create duplicate or near-duplicate components. If a new variant is needed, extend the existing component.

#### 6.6.3 Grid and Spacing Consistency

- All layouts use the defined spacing scale
- Section padding follows consistent patterns (e.g., `--space-16` or `--space-20` vertical)
- Component internal spacing uses smaller scale values
- Grid gaps use spacing tokens

#### 6.6.4 AI-Generated Code Constraints

When AI tools generate templates, blocks, or styles, the output must:

1. **Use only defined design tokens** — No new colours, shadows, or arbitrary values
2. **Reuse existing components** — No reinventing buttons, cards, or form inputs
3. **Match the reference template** — Visual consistency with `premium-trade-website-v3-final.html`
4. **Follow spacing scale** — No arbitrary margins or padding
5. **Maintain accessibility** — Proper contrast, focus states, semantic HTML

AI-generated code that introduces visual inconsistency or breaks the design system must be rejected and regenerated.

### 6.7 Page Template Requirements

#### 6.7.1 Base Template Structure

All pages share a common structure:

1. **Document head:** Meta tags, branding CSS injection, fonts, analytics
2. **Skip link:** Accessibility navigation aid
3. **Header:** Logo, navigation, optional CTA button
4. **Main content:** Page-specific StreamField blocks
5. **Footer:** Contact info, sitemap links, social links, legal links
6. **Scripts:** Deferred JavaScript, analytics body tags

#### 6.7.2 Section Types

Pages are composed of full-width sections with consistent structure:

| Section Type | Background | Typical Content |
|--------------|------------|-----------------|
| Hero | Image/gradient/colour | Headline, subheadline, CTAs |
| Content | White/light | Text, images, standard blocks |
| Feature | Light surface | Service cards, stats, process steps |
| Testimonial | Subtle background | Customer quotes, reviews |
| CTA | Primary/accent colour | Conversion-focused call to action |
| Contact | White/light | Form, contact details, map |

Each section type has defined padding, max-width, and responsive behaviour.

**Detailed template markup is provided in Appendix C: Design System Reference.**

---

## 7. Integration Requirements

### 7.1 Google Analytics 4

**Implementation:**
```html
<!-- GA4 Script (injected via template tag) -->
{% if settings.ga_measurement_id %}
<script async src="https://www.googletagmanager.com/gtag/js?id={{ settings.ga_measurement_id }}"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{{ settings.ga_measurement_id }}', {
        'anonymize_ip': true
    });
</script>
{% endif %}
```

**Event Tracking:**
```javascript
// Form submission event
function trackFormSubmission(formType, pagePath) {
    gtag('event', 'form_submission', {
        'form_type': formType,
        'page_path': pagePath
    });
}

// Phone click event
function trackPhoneClick(phoneNumber) {
    gtag('event', 'phone_click', {
        'phone_number': phoneNumber
    });
}

// CTA click event
function trackCTAClick(buttonText, destination) {
    gtag('event', 'cta_click', {
        'button_text': buttonText,
        'destination': destination
    });
}
```

### 7.2 Zapier Webhook

#### 7.2.1 Webhook Payload Schema

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "SUM Platform Lead Webhook Payload",
    "type": "object",
    "required": ["event_type", "timestamp", "lead"],
    "properties": {
        "event_type": {
            "type": "string",
            "enum": ["lead.created"],
            "description": "Type of event"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp of event"
        },
        "site": {
            "type": "object",
            "properties": {
                "domain": { "type": "string" },
                "name": { "type": "string" }
            }
        },
        "lead": {
            "type": "object",
            "required": ["id", "name", "email", "submitted_at"],
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Unique lead identifier"
                },
                "name": { "type": "string" },
                "email": { "type": "string", "format": "email" },
                "phone": { "type": "string" },
                "message": { "type": "string" },
                "form_type": {
                    "type": "string",
                    "enum": ["contact", "quote", "callback"]
                },
                "status": {
                    "type": "string",
                    "enum": ["new", "contacted", "quoted", "won", "lost"]
                },
                "submitted_at": {
                    "type": "string",
                    "format": "date-time"
                }
            }
        },
        "attribution": {
            "type": "object",
            "properties": {
                "lead_source": { "type": "string" },
                "lead_source_detail": { "type": "string" },
                "utm_source": { "type": "string" },
                "utm_medium": { "type": "string" },
                "utm_campaign": { "type": "string" },
                "utm_term": { "type": "string" },
                "utm_content": { "type": "string" },
                "landing_page_url": { "type": "string", "format": "uri" },
                "page_url": { "type": "string", "format": "uri" },
                "referrer_url": { "type": "string", "format": "uri" }
            }
        },
        "form_fields": {
            "type": "object",
            "additionalProperties": true,
            "description": "Additional form-specific fields (project_type, budget_range, etc.)"
        }
    }
}
```

#### 7.2.2 Example Payload

```json
{
    "event_type": "lead.created",
    "timestamp": "2025-12-07T14:30:00Z",
    "site": {
        "domain": "acmekitchens.co.uk",
        "name": "Acme Kitchens"
    },
    "lead": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "07700 900123",
        "message": "Looking to renovate our kitchen. Would like a modern design with island.",
        "form_type": "quote",
        "status": "new",
        "submitted_at": "2025-12-07T14:30:00Z"
    },
    "attribution": {
        "lead_source": "google_ads",
        "lead_source_detail": "",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "kitchens-london-2025",
        "utm_term": "kitchen renovation london",
        "utm_content": "ad-v2",
        "landing_page_url": "https://acmekitchens.co.uk/services/kitchen-renovation/?utm_source=google&utm_medium=cpc&utm_campaign=kitchens-london-2025",
        "page_url": "https://acmekitchens.co.uk/contact/",
        "referrer_url": "https://www.google.com/"
    },
    "form_fields": {
        "project_type": "Kitchen Renovation",
        "budget_range": "£15,000 - £30,000",
        "timeline": "1-3 months",
        "service_area": "SW1"
    }
}
```

#### 7.2.3 Webhook Retry Logic

```python
# Celery task for webhook delivery
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute initial delay
    retry_backoff=True,      # Exponential backoff
    retry_backoff_max=3600,  # Max 1 hour between retries
)
def send_lead_webhook(self, lead_id: str):
    """
    Send lead data to configured webhook URL.
    
    Retry schedule: 1 min, ~2 min, ~4 min (exponential backoff)
    """
    try:
        lead = Lead.objects.get(id=lead_id)
        site_settings = SiteSettings.for_site(lead.source_page.get_site())
        
        if not site_settings.zapier_webhook_url:
            return  # No webhook configured
        
        payload = build_webhook_payload(lead)
        
        response = requests.post(
            site_settings.zapier_webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        
        # Update lead record
        lead.webhook_sent = True
        lead.webhook_sent_at = timezone.now()
        lead.webhook_response_code = response.status_code
        lead.save(update_fields=[
            'webhook_sent', 'webhook_sent_at', 'webhook_response_code'
        ])
        
    except requests.RequestException as exc:
        # Log failure and retry
        logger.warning(f"Webhook failed for lead {lead_id}: {exc}")
        raise self.retry(exc=exc)
```

### 7.3 Email Notification

#### 7.3.1 Email Configuration

```python
# settings/base.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@sumplatform.com')
```

#### 7.3.2 Lead Notification Email Template

```html
<!-- sum_core/templates/sum_core/emails/lead_notification.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: {{ site_settings.color_primary }}; color: white; padding: 20px; }
        .content { padding: 20px; background: #f9f9f9; }
        .field { margin-bottom: 15px; }
        .label { font-weight: bold; color: #666; }
        .value { margin-top: 5px; }
        .cta { display: inline-block; padding: 12px 24px; background: {{ site_settings.color_primary }}; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }
        .footer { padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Lead Received</h1>
        </div>
        <div class="content">
            <div class="field">
                <div class="label">Name</div>
                <div class="value">{{ lead.name }}</div>
            </div>
            <div class="field">
                <div class="label">Email</div>
                <div class="value"><a href="mailto:{{ lead.email }}">{{ lead.email }}</a></div>
            </div>
            {% if lead.phone %}
            <div class="field">
                <div class="label">Phone</div>
                <div class="value"><a href="tel:{{ lead.phone }}">{{ lead.phone }}</a></div>
            </div>
            {% endif %}
            <div class="field">
                <div class="label">Message</div>
                <div class="value">{{ lead.message }}</div>
            </div>
            
            {% if lead.form_data %}
            <h3>Additional Details</h3>
            {% for key, value in lead.form_data.items %}
            <div class="field">
                <div class="label">{{ key|title }}</div>
                <div class="value">{{ value }}</div>
            </div>
            {% endfor %}
            {% endif %}
            
            <h3>Source Information</h3>
            <div class="field">
                <div class="label">Source</div>
                <div class="value">{{ lead.get_lead_source_display }}</div>
            </div>
            <div class="field">
                <div class="label">Page</div>
                <div class="value">{{ lead.page_url }}</div>
            </div>
            
            <a href="{{ admin_url }}" class="cta">View in Admin</a>
        </div>
        <div class="footer">
            <p>This email was sent from {{ site_settings.company_name }} website.</p>
            <p>Submitted at: {{ lead.submitted_at|date:"F j, Y, g:i a" }}</p>
        </div>
    </div>
</body>
</html>
```

---

## 8. Data Requirements

### 8.1 Data Collection

| Data Type | Source | Storage | Retention |
|-----------|--------|---------|-----------|
| Lead submissions | Web forms | PostgreSQL | 3 years (default) |
| User accounts | Admin creation | PostgreSQL | Account lifetime |
| Page content | CMS editing | PostgreSQL | Indefinite |
| Media files | CMS uploads | Filesystem/S3 | Indefinite |
| Analytics | GA4 | Google (external) | Per GA settings |
| Session data | Website visits | Redis | 24 hours |
| Logs | Application | Filesystem | 90 days |

### 8.2 Data Privacy & Compliance

#### 8.2.1 GDPR Compliance

| Requirement | Implementation |
|-------------|----------------|
| Lawful basis | Legitimate interest (form submissions) |
| Data minimisation | Collect only necessary fields |
| Purpose limitation | Lead management only |
| Storage limitation | 3-year default retention |
| Right to access | Export functionality in admin |
| Right to erasure | Soft delete + hard delete option |
| Right to rectification | Edit capability in admin |
| Privacy notice | Required on all forms |
**Lead Retention Task**

- A scheduled Celery task runs daily and purges or archives leads older than the configured retention period (default 3 years).
    
- Retention period is configured globally (Phase 1) and may later be made per-site.
    
- The task logs how many leads were removed per run.
#### 8.2.2 Cookie Consent

**Essential Cookies (No Consent Required):**
- Session ID
- CSRF token
- Language preference

**Non-Essential Cookies (Consent Required):**
- Google Analytics
- Google Tag Manager
- Marketing pixels (Phase 2)

**Implementation:** Cookie consent banner with accept/reject options. Non-essential scripts blocked until consent given.

### 8.3 Backup & Recovery

#### 8.3.1 Backup Schedule

| Backup Type | Frequency | Retention | Storage |
|-------------|-----------|-----------|---------|
| Database (full) | Nightly | 30 days | S3/Spaces/B2 |
| Media files | Weekly | 30 days | S3/Spaces/B2 |
| Configuration | On change | 90 days | Git repository |

#### 8.3.2 Recovery Procedures

**Database Recovery:**
1. Stop application service
2. Identify backup file to restore
3. Run restore script with confirmation
4. Verify data integrity
5. Restart application service
6. Test critical functionality

**Estimated Recovery Time:** <2 hours for database restore

---

## 9. Testing Strategy

### 9.1 Testing Pyramid

```
           ╱╲
          ╱  ╲
         ╱ E2E╲           ← Few, critical paths only (Phase 2)
        ╱──────╲
       ╱        ╲
      ╱Integration╲       ← Page rendering, form flows, admin
     ╱──────────────╲
    ╱                ╲
   ╱    Unit Tests    ╲   ← Blocks, models, forms, utilities
  ╱────────────────────╲
```

### 9.2 Coverage Targets

| Layer | Target | Focus Areas |
|-------|--------|-------------|
| Unit | ≥85% | Blocks, models, forms, validators, utilities |
| Integration | ≥70% | Page rendering, form submission, lead workflow |
| E2E | Critical paths | Homepage, contact form, admin login (Phase 2) |

### 9.3 Test Categories

#### 9.3.1 Unit Tests

**Block Tests:**
```python
# tests/unit/test_blocks/test_hero.py

class TestHeroImageBlock:
    def test_required_fields(self):
        """Headline is required, subheadline is optional."""
        block = HeroImageBlock()
        
        # Valid: headline only
        value = block.clean({'headline': 'Welcome', 'image': mock_image})
        assert value['headline'] == 'Welcome'
        
        # Invalid: missing headline
        with pytest.raises(ValidationError):
            block.clean({'image': mock_image})
    
    def test_cta_buttons_max_two(self):
        """Maximum 2 CTA buttons allowed."""
        block = HeroImageBlock()
        
        with pytest.raises(ValidationError):
            block.clean({
                'headline': 'Test',
                'cta_buttons': [
                    {'text': 'CTA 1', 'url': '/1'},
                    {'text': 'CTA 2', 'url': '/2'},
                    {'text': 'CTA 3', 'url': '/3'},  # Third button
                ]
            })
```

**Form Tests:**
```python
# tests/unit/test_forms/test_contact.py

class TestContactForm:
    def test_valid_submission(self):
        form = ContactForm(data={
            'name': 'John Smith',
            'email': 'john@example.com',
            'phone': '07700 900123',
            'message': 'Test message',
            'website': '',  # Honeypot empty
        })
        assert form.is_valid()
    
    def test_honeypot_detection(self):
        form = ContactForm(data={
            'name': 'Bot',
            'email': 'bot@spam.com',
            'message': 'Spam',
            'website': 'http://spam.com',  # Honeypot filled
        })
        assert not form.is_valid()
        assert 'honeypot' in form.errors
    
    def test_email_validation(self):
        form = ContactForm(data={
            'name': 'Test',
            'email': 'invalid-email',
            'message': 'Test',
        })
        assert not form.is_valid()
        assert 'email' in form.errors
```

#### 9.3.2 Integration Tests

**Page Rendering Tests:**
```python
# tests/integration/test_page_rendering.py

class TestHomePageRendering:
    @pytest.fixture
    def homepage(self, site):
        return HomePageFactory(parent=site.root_page)
    
    def test_homepage_renders(self, client, homepage):
        response = client.get(homepage.url)
        assert response.status_code == 200
        assert homepage.title in response.content.decode()
    
    def test_homepage_with_hero_block(self, client, homepage):
        homepage.body = [
            ('hero_image', {
                'headline': 'Welcome to Our Site',
                'image': ImageFactory(),
            })
        ]
        homepage.save()
        
        response = client.get(homepage.url)
        assert 'Welcome to Our Site' in response.content.decode()
```

**Form Submission Tests:**
```python
# tests/integration/test_form_submission.py

class TestContactFormSubmission:
    def test_successful_submission_creates_lead(self, client, contact_page):
        response = client.post(contact_page.url, {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone': '07700 900456',
            'message': 'I need a new kitchen',
            'website': '',
        })
        
        assert response.status_code == 200
        assert Lead.objects.filter(email='jane@example.com').exists()
        
        lead = Lead.objects.get(email='jane@example.com')
        assert lead.name == 'Jane Doe'
        assert lead.status == 'new'
        assert lead.source_page == contact_page
    
    @pytest.mark.django_db
    def test_submission_triggers_email_task(self, client, contact_page, mocker):
        mock_task = mocker.patch('sum_core.leads.tasks.send_lead_notification.delay')
        
        client.post(contact_page.url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test',
            'website': '',
        })
        
        mock_task.assert_called_once()
```

### 9.4 Test Fixtures & Factories

```python
# tests/factories.py

import factory
from wagtail_factories import PageFactory, ImageFactory

class HomePageFactory(PageFactory):
    class Meta:
        model = HomePage
    
    title = factory.Sequence(lambda n: f'Home Page {n}')
    body = []


class LeadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lead
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number', locale='en_GB')
    message = factory.Faker('paragraph')
    form_type = 'contact'
    status = 'new'
    lead_source = 'direct'


class SiteSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SiteSettings
    
    company_name = factory.Faker('company')
    color_primary = '#2563eb'  # Test placeholder
    color_secondary = '#1e40af'
    font_heading = 'Montserrat'  # Generic test font
    font_body = 'Open Sans'  # Generic test font
```

### 9.5 Pre-Deployment Checklist

```markdown
## Pre-Deployment Test Checklist

### Automated Tests
- [ ] All unit tests passing (`make test-unit`)
- [ ] All integration tests passing (`make test-integration`)
- [ ] Coverage threshold met (>80%)
- [ ] No linting errors (`make lint`)
- [ ] Type checking passes (`make typecheck`)

### Manual Smoke Tests
- [ ] Homepage loads correctly
- [ ] All navigation links work
- [ ] Service pages render properly
- [ ] Contact form submits successfully
- [ ] Lead appears in admin
- [ ] Notification email received
- [ ] Branding settings apply correctly
- [ ] Mobile responsive (test on device)

### Performance & Accessibility
- [ ] Lighthouse Performance: 90+ (reference pages)
- [ ] Lighthouse Accessibility: 90+ (reference pages)
- [ ] Lighthouse SEO: 90+ (reference pages)
- [ ] No console errors
- [ ] Images optimised and lazy-loaded

### SEO Verification
- [ ] Meta titles unique per page
- [ ] Meta descriptions present
- [ ] OG tags rendering correctly
- [ ] Schema markup valid (Rich Results Test)
- [ ] XML sitemap accessible
- [ ] robots.txt correct
```

---

## 10. Deployment & Launch

### 10.1 Environment Strategy

| Environment | Purpose | URL Pattern | Branch |
|-------------|---------|-------------|--------|
| Local | Development | localhost:8000 | feature/* |
| CI | Automated testing | N/A | All branches |
| Staging | Platform testing | staging.example.com | develop |
| Production | Live client sites | *.clientdomain.com | main |

### 10.2 Deployment Process

#### 10.2.1 New Client Deployment

```bash
# 1. Create project (developer machine)
sum init acme-kitchens

# 2. Configure client
cd clients/acme-kitchens
# Edit .env with client-specific values
# Edit settings if needed

# 3. Validate
sum check .

# 4. Push to repository
git add .
git commit -m "feat: add acme-kitchens client project"
git push

# 5. Deploy to server (on VPS)
./deploy-client.sh acme-kitchens deploy

# 6. Configure Nginx
sudo cp /var/www/sum-platform/infrastructure/nginx/nginx.conf.template \
    /etc/nginx/sites-available/acme-kitchens
# Edit domain, paths
sudo ln -s /etc/nginx/sites-available/acme-kitchens \
    /etc/nginx/sites-enabled/
sudo certbot --nginx -d acmekitchens.co.uk -d www.acmekitchens.co.uk
sudo nginx -t && sudo systemctl reload nginx

# 7. Configure monitoring
# Add site to UptimeRobot
# Verify Sentry DSN in .env

# 8. Populate content and go live
```

#### 10.2.2 Core Package Update

```bash
# 1. Update core package
cd /var/www/sum-platform/core
git pull origin main

# 2. Update each client (selective, one at a time)
cd /var/www/clients/acme-kitchens
# Edit requirements.txt: sum-core==0.3.3
./deploy-client.sh acme-kitchens update --backup

# 3. Verify functionality
curl https://acmekitchens.co.uk/health/

# 4. Repeat for other clients as needed
```

### 10.3 Launch Checklist

```markdown
## Client Site Launch Checklist

### Pre-Launch (Development)
- [ ] All pages created and content populated
- [ ] Contact forms working, leads capturing
- [ ] Branding configured (colours, logos, fonts)
- [ ] SEO fields completed (meta titles, descriptions)
- [ ] Images optimised with alt text
- [ ] Mobile responsive testing complete
- [ ] Cross-browser testing complete

### Pre-Launch (Technical)
- [ ] SSL certificate installed and valid
- [ ] HTTPS redirect working
- [ ] Security headers configured
- [ ] Backup system running
- [ ] Monitoring configured
- [ ] Google Analytics connected
- [ ] Zapier webhook tested (if applicable)

### Pre-Launch (SEO)
- [ ] XML sitemap generated and accessible
- [ ] robots.txt configured
- [ ] Schema markup validated
- [ ] Google Search Console verified
- [ ] Old URL redirects configured (if migration)

### Launch Day
- [ ] DNS updated to point to server
- [ ] DNS propagation verified
- [ ] SSL certificate active
- [ ] All pages loading correctly
- [ ] Forms submitting successfully
- [ ] Email notifications working
- [ ] Analytics tracking verified

### Post-Launch
- [ ] Client handover documentation provided
- [ ] Client admin access created
- [ ] Ongoing support channel confirmed
- [ ] First week monitoring intensive
- [ ] Performance baseline recorded
```

### 10.4 Rollback Procedure

```markdown
## Emergency Rollback Procedure

### Symptoms Requiring Rollback
- Site completely down after update
- Critical functionality broken (forms, admin)
- Security vulnerability discovered
- Data corruption

### Rollback Steps

1. **Stop affected service**
   ```bash
   sudo systemctl stop sum-<client-name>
   ```

2. **Restore database (if needed)**
   ```bash
   ./restore.sh <client-name> /backups/<client>/db_YYYYMMDD.sql.gz
   ```

3. **Revert sum-core version**
   Edit `requirements.txt`:
   ```
   sum-core==0.2.0  # Previous working version
   ```

4. **Reinstall dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Restart service**
   ```bash
   sudo systemctl start sum-<client-name>
   ```

6. **Verify recovery**
   ```bash
   curl https://<domain>/health/
   ```

7. **Document incident**
   - Time of issue
   - Symptoms observed
   - Rollback actions taken
   - Root cause (if known)
   - Prevention measures

### Communication
- Notify affected client immediately
- Update status page (if applicable)
- Post-mortem within 24 hours
```

---

## 11. Future Roadmap

### 11.1 Phase 1.1 (Post-MVP)

Features deferred from Phase 1 MVP but planned for near-term:

| Feature | Description | Priority |
|---------|-------------|----------|
| reCAPTCHA v3 | Enhanced spam protection | P1 |
| Blog tags | Tag filtering on blog | P1 |
| Related posts | Automatic/manual related content | P1 |
| Social sharing | Share buttons on blog posts | P1 |
| Before/after slider | Gallery enhancement | P1 |
| Lightbox zoom | Gallery image zoom | P1 |
| Email templates | Customisable notification emails | P1 |
| Article schema | Blog post structured data | P1 |
| FAQ schema | FAQ block structured data | P1 |

### 11.2 Phase 2 (Platform as Product)

| Feature | Description |
|---------|-------------|
| Enhanced CRM | Notes, assignment, pipeline, revenue tracking |
| Advanced Analytics | Full dashboard with charts, trends, comparisons |
| Multiple CRM integrations | Beyond Zapier/HubSpot |
| Email marketing | Mailchimp, ConvertKit integration |
| Review management | Google, Trustpilot, Facebook APIs |
| Appointment booking | Integrated calendar system |
| Live chat widget | Customer chat integration |
| A/B testing | Conversion optimisation framework |
| Multi-site dashboard | Manage all clients from one view |
| Automated updates | Push core updates automatically |

### 11.3 Phase 3+ (Future Considerations)

| Feature | Description |
|---------|-------------|
| Web-based control panel | GUI for managing deployments |
| Automated domain/SSL | One-click domain configuration |
| White-label client portal | Branded client dashboards |
| Content AI assistance | AI-powered content suggestions |
| Mobile app | Native app for lead management |
| E-commerce integration | Quote-to-invoice, payments |
| Advanced reporting | Custom report builder |
| Marketplace | Third-party plugins and themes |

### 11.4 Technical Debt Tracking

| Item | Description | Priority | Target |
|------|-------------|----------|--------|
| Test coverage gaps | Areas below 80% coverage | Medium | Phase 1.1 |
| Performance optimisation | Query optimisation, caching improvements | Low | Phase 2 |
| Documentation gaps | Missing or outdated docs | Medium | Ongoing |
| Dependency updates | Security and feature updates | High | Monthly |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Block** | Wagtail StreamField component for building page content |
| **CLI** | Command-Line Interface for developer tools |
| **CMS** | Content Management System (Wagtail) |
| **Core Package** | Shared `sum_core` Python package |
| **Lead** | Form submission / customer enquiry |
| **Lead Source** | Normalised attribution category (Google Ads, SEO, etc.) |
| **LTS** | Long-Term Support (software version) |
| **Rendition** | Resized/optimised version of an image |
| **Schema Markup** | Structured data for search engines (JSON-LD) |
| **Site Settings** | Per-site configuration model in Wagtail |
| **StreamField** | Wagtail's flexible content block system |
| **UTM Parameters** | URL tracking parameters for campaign attribution |
| **VPS** | Virtual Private Server for hosting |
| **WCAG** | Web Content Accessibility Guidelines |

---

## Appendix B: File Path Reference

| Purpose | Path |
|---------|------|
| Core package | `/core/sum_core/` |
| Block definitions | `/core/sum_core/blocks/` |
| Page models | `/core/sum_core/pages/` |
| Lead models | `/core/sum_core/leads/` |
| Branding models | `/core/sum_core/branding/` |
| Core templates | `/core/sum_core/templates/sum_core/` |
| Core static files | `/core/sum_core/static/sum_core/` |
| Client boilerplate | `/boilerplate/` |
| Client projects | `/clients/<client-name>/` |
| CLI tool | `/cli/sum_cli/` |
| Documentation | `/docs/` |
| Server scripts | `/scripts/` |
| Infrastructure templates | `/infrastructure/` |

---

## Appendix C: Design System Reference

This appendix contains detailed CSS token definitions, component specifications, and template markup for implementation reference.

### C.1 Complete Token Definitions

#### C.1.1 Colour Tokens

```css
:root {
    /* Brand Colours - Populated from SiteSettings per client */
    --color-primary: /* from SiteSettings.color_primary */;
    --color-secondary: /* from SiteSettings.color_secondary */;
    --color-accent: /* from SiteSettings.color_accent */;
    
    /* Background & Surface */
    --color-background: /* from SiteSettings.color_background */;
    --color-surface: #f9fafb;
    --color-surface-elevated: #ffffff;
    
    /* Text */
    --color-text: /* from SiteSettings.color_text */;
    --color-text-light: /* from SiteSettings.color_text_light */;
    --color-text-inverse: #ffffff;
    
    /* Semantic - Fixed across all sites */
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-error: #ef4444;
    --color-info: #3b82f6;
    
    /* Borders */
    --color-border: #e5e7eb;
    --color-border-dark: #d1d5db;
}
```

#### C.1.2 Typography Tokens

```css
:root {
    /* Font Families - Populated from SiteSettings per client */
    --font-heading: /* from SiteSettings.font_heading */, sans-serif;
    --font-body: /* from SiteSettings.font_body */, sans-serif;
    
    /* Font Sizes - Fixed scale */
    --text-xs: 0.75rem;      /* 12px */
    --text-sm: 0.875rem;     /* 14px */
    --text-base: 1rem;       /* 16px */
    --text-lg: 1.125rem;     /* 18px */
    --text-xl: 1.25rem;      /* 20px */
    --text-2xl: 1.5rem;      /* 24px */
    --text-3xl: 1.875rem;    /* 30px */
    --text-4xl: 2.25rem;     /* 36px */
    --text-5xl: 3rem;        /* 48px */
    --text-6xl: 3.75rem;     /* 60px */
    
    /* Line Heights */
    --leading-tight: 1.25;
    --leading-normal: 1.5;
    --leading-relaxed: 1.75;
    
    /* Font Weights */
    --font-normal: 400;
    --font-medium: 500;
    --font-semibold: 600;
    --font-bold: 700;
}
```

#### C.1.3 Spacing Tokens

```css
:root {
    --space-1: 0.25rem;   /* 4px */
    --space-2: 0.5rem;    /* 8px */
    --space-3: 0.75rem;   /* 12px */
    --space-4: 1rem;      /* 16px */
    --space-5: 1.25rem;   /* 20px */
    --space-6: 1.5rem;    /* 24px */
    --space-8: 2rem;      /* 32px */
    --space-10: 2.5rem;   /* 40px */
    --space-12: 3rem;     /* 48px */
    --space-16: 4rem;     /* 64px */
    --space-20: 5rem;     /* 80px */
    --space-24: 6rem;     /* 96px */
}
```

#### C.1.4 Shadow Tokens

```css
:root {
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.15);
    --shadow-xl: 0 10px 25px rgba(0, 0, 0, 0.15);
}
```

#### C.1.5 Border Radius Tokens

```css
:root {
    --radius-sm: 0.25rem;   /* 4px */
    --radius-md: 0.375rem;  /* 6px */
    --radius-lg: 0.5rem;    /* 8px */
    --radius-xl: 0.75rem;   /* 12px */
    --radius-full: 9999px;  /* Pill shape */
}
```

### C.2 Component CSS Specifications

#### C.2.1 Buttons

```css
/* Base button */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-body);
    font-weight: var(--font-semibold);
    border-radius: var(--radius-md);
    transition: background-color 0.15s, transform 0.1s, box-shadow 0.15s;
    cursor: pointer;
    text-decoration: none;
}

.btn:focus-visible {
    outline: 3px solid var(--color-primary);
    outline-offset: 2px;
}

/* Sizes */
.btn--sm { padding: var(--space-2) var(--space-4); font-size: var(--text-sm); min-height: 36px; }
.btn--md { padding: var(--space-3) var(--space-6); font-size: var(--text-base); min-height: 44px; }
.btn--lg { padding: var(--space-4) var(--space-8); font-size: var(--text-lg); min-height: 52px; }

/* Variants */
.btn--primary {
    background: var(--color-primary);
    color: var(--color-text-inverse);
    border: none;
}
.btn--primary:hover { filter: brightness(0.9); }

.btn--secondary {
    background: var(--color-secondary);
    color: var(--color-text-inverse);
    border: none;
}
.btn--secondary:hover { filter: brightness(0.9); }

.btn--outline {
    background: transparent;
    color: var(--color-primary);
    border: 2px solid var(--color-primary);
}
.btn--outline:hover {
    background: var(--color-primary);
    color: var(--color-text-inverse);
}

.btn--ghost {
    background: transparent;
    color: var(--color-text);
    border: none;
}
.btn--ghost:hover { background: var(--color-surface); }
```

#### C.2.2 Form Inputs

```css
.form-input {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    font-family: var(--font-body);
    font-size: var(--text-base);
    color: var(--color-text);
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    transition: border-color 0.15s, box-shadow 0.15s;
}

.form-input::placeholder {
    color: var(--color-text-light);
}

.form-input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.form-input--error {
    border-color: var(--color-error);
}

.form-input--error:focus {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-label {
    display: block;
    margin-bottom: var(--space-2);
    font-family: var(--font-body);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--color-text);
}

.form-error {
    margin-top: var(--space-1);
    font-size: var(--text-sm);
    color: var(--color-error);
}
```

#### C.2.3 Cards

```css
.card {
    background: var(--color-surface-elevated);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-6);
}

.card--hover {
    transition: transform 0.2s, box-shadow 0.2s;
}

.card--hover:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.card--bordered {
    box-shadow: none;
    border: 1px solid var(--color-border);
}
```

### C.3 Base Template Markup

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Meta Tags -->
    {% include "sum_core/includes/meta_tags.html" %}
    
    <!-- Dynamic Branding CSS (generates CSS custom properties) -->
    {% branding_css %}
    
    <!-- Stylesheets -->
    <link rel="stylesheet" href="{% static 'sum_core/css/main.css' %}">
    
    <!-- Google Fonts (dynamically loaded based on SiteSettings) -->
    {% branding_fonts %}
    
    <!-- Analytics (GA4/GTM from SiteSettings) -->
    {% analytics_head %}
</head>
<body>
    <!-- Skip Link (Accessibility) -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <!-- Header -->
    {% include "sum_core/includes/header.html" %}
    
    <!-- Main Content -->
    <main id="main-content">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include "sum_core/includes/footer.html" %}
    
    <!-- Scripts -->
    <script src="{% static 'sum_core/js/main.js' %}" defer></script>
    {% analytics_body %}
</body>
</html>
```

### C.4 Section Wrapper Pattern

```html
<!-- Standard section wrapper -->
<section class="section section--{{ variant }}">
    <div class="container">
        {% if section_heading %}
        <header class="section__header">
            <h2 class="section__title">{{ section_heading }}</h2>
            {% if section_subtitle %}
            <p class="section__subtitle">{{ section_subtitle }}</p>
            {% endif %}
        </header>
        {% endif %}
        
        <div class="section__content">
            {{ content }}
        </div>
    </div>
</section>
```

```css
.section {
    padding: var(--space-16) 0;
}

@media (min-width: 768px) {
    .section { padding: var(--space-20) 0; }
}

.section--light { background: var(--color-surface); }
.section--dark { background: var(--color-secondary); color: var(--color-text-inverse); }
.section--primary { background: var(--color-primary); color: var(--color-text-inverse); }

.container {
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 var(--space-4);
}

@media (min-width: 640px) {
    .container { padding: 0 var(--space-6); }
}

.section__header {
    text-align: center;
    margin-bottom: var(--space-12);
}

.section__title {
    font-family: var(--font-heading);
    font-size: var(--text-3xl);
    font-weight: var(--font-bold);
    margin-bottom: var(--space-4);
}

@media (min-width: 768px) {
    .section__title { font-size: var(--text-4xl); }
}

.section__subtitle {
    font-size: var(--text-lg);
    color: var(--color-text-light);
    max-width: 600px;
    margin: 0 auto;
}
```

### C.5 Theme Preset Definitions

Theme presets are internal starting points for new client sites. Each preset is customised to match the specific client's brand.

| Preset | Primary | Secondary | Accent | Heading Font | Body Font |
|--------|---------|-----------|--------|--------------|-----------|
| Premium Trade | #1e3a5f | #0f172a | #f59e0b | Montserrat | Open Sans |
| Professional Blue | #2563eb | #1e40af | #f97316 | Poppins | Inter |
| Modern Green | #059669 | #064e3b | #fbbf24 | DM Sans | Source Sans 3 |
| Warm Earth | #92400e | #78350f | #dc2626 | Playfair Display | Lato |
| Clean Slate | #374151 | #1f2937 | #6366f1 | Work Sans | Roboto |

**Note:** These are starting points only. Every client site receives custom branding configuration to match their specific brand guidelines.

---

## Document Approval

**Prepared By:** Development Team  
**Document Version:** 1.1  
**Date:** December 7, 2025  

| Role | Signature | Date |
|------|-----------|------|
| Project Lead | | |
| Business Owner | | |

---

*This Product Requirements Document serves as the technical blueprint for Phase 1 development of the SUM Platform. All implementation should reference this document for feature specifications, data models, and acceptance criteria.*
