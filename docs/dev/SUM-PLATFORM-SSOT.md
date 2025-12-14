# SUM Platform – Single Source of Truth

**Document Version:** 1.0  
**Date:** December 14, 2025  
**Consolidates:** PRD v1.1, Project Initiation Packet v1.1, Technical Specification v0.2, Implementation Plan v1.1

---

## Quick Reference

| Item | Value |
|------|-------|
| **Project Code** | `sum-platform` |
| **Target** | 20 client websites in 12 months |
| **Deployment Time** | 2-3 days per new client site |
| **Phase 1 Completion** | March 2026 (12 weeks from December 2025) |
| **Total Estimated Hours** | 185-240 hours |

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Repository Structure](#3-repository-structure)
4. [Architecture](#4-architecture)
5. [Core Package (`sum_core`)](#5-core-package-sum_core)
6. [StreamField Blocks](#6-streamfield-blocks)
7. [Page Types](#7-page-types)
8. [Lead Management System](#8-lead-management-system)
9. [Branding & Design System](#9-branding--design-system)
10. [Analytics & SEO](#10-analytics--seo)
11. [Integrations](#11-integrations)
12. [CLI & Deployment](#12-cli--deployment)
13. [Implementation Milestones](#13-implementation-milestones)
14. [Critical Path & Dependencies](#14-critical-path--dependencies)
15. [Conventions & Standards](#15-conventions--standards)
16. [Definition of Done](#16-definition-of-done)
17. [Appendices](#appendices)

---

## 1. Project Overview

### 1.1 Vision

Build a scalable website deployment platform enabling Straight Up Marketing to deliver professional, conversion-focused websites for home improvement businesses in 2-3 days. The platform prioritizes lead generation, SEO optimization, and long-term maintainability.

### 1.2 Design Principles

1. **Hyper-modular**: Small, focused Django apps with clear responsibilities
2. **Hyper-documented**: All modules documented for AI-driven maintenance
3. **Future-oriented**: Designed to scale to distributed architecture
4. **Safe defaults**: Security, performance, and reliability baked in

### 1.3 Target Users

| User | Role | Technical Level |
|------|------|-----------------|
| **Internal Dev Team** | Create, deploy, maintain sites | Django/Wagtail proficient |
| **Client Content Editors** | Update content, view leads | Limited technical expertise |
| **Website Visitors** | Research and contact businesses | General public, mobile-first |

### 1.4 Success Metrics

| Metric | Target | Phase |
|--------|--------|-------|
| New site deployment time | ≤3 days | Phase 1 |
| Core package test coverage | ≥80% | Phase 1 |
| Lighthouse Performance | ≥90 (reference pages) | Phase 1 |
| Page load (4G mobile) | <3 seconds | Phase 1 |
| Lighthouse Accessibility | ≥90 | Phase 1 |
| Lighthouse SEO | ≥90 | Phase 1 |
| Platform uptime | ≥99.5% | Phase 1 |

---

## 2. Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.12.x |
| Framework | Django (LTS) | 5.2.x |
| CMS | Wagtail (LTS) | 7.0.x |
| Database | PostgreSQL | 17.x |
| Cache/Broker | Redis | 7.x/8.x |
| Task Queue | Celery | 5.6.x |
| Frontend Build | Node.js (LTS) | 24.x |
| Web Server | Nginx | Latest |
| App Server | Gunicorn | Latest |
| CSS | Token-based system (no Tailwind in templates) | — |

### 2.1 Development vs Production

| Environment | Stack |
|-------------|-------|
| **Local Dev** | Docker Compose (Django, PostgreSQL, Redis, Node.js) |
| **CI** | Docker (GitHub Actions) |
| **Staging** | Host-based (venv + Gunicorn + Nginx + systemd) |
| **Production** | Host-based (venv + Gunicorn + Nginx + systemd) |

> **Decision:** Docker is for local dev and CI only. Production uses host-based deployment.

---

## 3. Repository Structure

```
sum-platform/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-staging.yml
│       └── deploy-production.yml
│
├── core/                              # Shared platform package
│   ├── sum_core/
│   │   ├── __init__.py               # __version__ = "X.Y.Z"
│   │   ├── blocks/                   # StreamField blocks
│   │   ├── pages/                    # Page models
│   │   ├── leads/                    # Lead management
│   │   ├── branding/                 # Theme/branding system
│   │   ├── analytics/                # Analytics integration
│   │   ├── seo/                      # SEO utilities
│   │   ├── integrations/             # Third-party integrations
│   │   ├── utils/                    # Shared utilities
│   │   ├── templates/sum_core/       # Base templates
│   │   ├── static/sum_core/          # Static assets (CSS, JS)
│   │   └── test_project/             # Minimal project for CI
│   ├── tests/
│   └── pyproject.toml
│
├── boilerplate/                       # Client project template
│   ├── project_name/
│   │   └── settings/
│   │       ├── base.py
│   │       ├── local.py
│   │       └── production.py
│   ├── templates/overrides/
│   ├── static/client/
│   ├── docker-compose.yml            # LOCAL DEV ONLY
│   ├── requirements.txt              # Pins sum-core==X.Y.Z
│   └── .env.example
│
├── clients/                           # Deployed client projects
│   └── <client-name>/
│
├── cli/                               # Platform CLI
│   └── sum_cli/
│       ├── main.py
│       └── commands/
│           ├── init.py
│           └── check.py
│
├── scripts/
│   ├── deploy-client.sh
│   ├── backup.sh
│   └── restore.sh
│
├── infrastructure/
│   ├── nginx/
│   └── systemd/
│
├── docs/
├── Makefile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### 3.1 Key File Paths

| Purpose | Path |
|---------|------|
| Core package | `core/sum_core/` |
| Boilerplate | `boilerplate/` |
| Client projects | `clients/<client-name>/` |
| CLI tool | `cli/sum_cli/` |
| CSS tokens | `core/sum_core/static/sum_core/css/tokens.css` |
| Base templates | `core/sum_core/templates/sum_core/` |
| Block templates | `core/sum_core/templates/sum_core/blocks/` |

---

## 4. Architecture

### 4.1 Logical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Monorepo                              │
│                                                                 │
│  core/sum_core/                                                 │
│    ├─ blocks/        StreamField blocks                         │
│    ├─ pages/         Abstract + concrete page types             │
│    ├─ leads/         Lead model, attribution, admin, tasks      │
│    ├─ branding/      SiteSettings, branding CSS/fonts           │
│    ├─ analytics/     GA/GTM integration, event tracking         │
│    ├─ seo/           SEO fields, meta, structured data          │
│    ├─ integrations/  Zapier, HubSpot, email helpers             │
│    └─ utils/         Shared helpers, base mixins                │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Runtime Architecture (Per Client)

```
Browser
  │
  ▼
Nginx (TLS, security headers, static/media)
  │
  ▼
Gunicorn (Django + Wagtail app)
  │
  ├── PostgreSQL (per-client database)
  ├── Redis (cache + Celery broker)
  └── Celery workers (email, webhooks, retention)
```

### 4.3 Multisite Strategy

- **Per-client project**: Each client = one Django/Wagtail project in `clients/<slug>/`
- **Separate databases**: `sum_<client_slug>` per client
- **Version pinning**: Each client pins `sum-core==X.Y.Z` explicitly

---

## 5. Core Package (`sum_core`)

The `sum_core` package is installable via `pip install -e ./core` and contains all shared functionality.

### 5.1 App Structure

```
sum_core/
├── blocks/           # All StreamField blocks
├── pages/            # All page type models
├── leads/            # Lead model, forms, admin, tasks
├── branding/         # SiteSettings, templatetags
├── analytics/        # GA/GTM templatetags, JS
├── seo/              # SEO mixins, schema builders
├── integrations/     # Zapier, HubSpot, email
├── utils/            # Shared helpers
├── templates/        # Base templates
├── static/           # CSS, JS assets
└── test_project/     # CI test project
```

### 5.2 Version Management

- Version defined in `core/sum_core/__init__.py`: `__version__ = "X.Y.Z"`
- Clients pin version in `requirements.txt`: `sum-core==0.3.2`
- **Critical**: No automatic upgrades; explicit version pinning always

---

## 6. StreamField Blocks

### 6.1 Block Catalogue

| Category | Blocks | Priority |
|----------|--------|----------|
| **Hero** | `HeroImageBlock`, `HeroGradientBlock` | P0 |
| **Services** | `ServiceCardsBlock` | P0 |
| **Testimonials** | `TestimonialsBlock` | P0 |
| **CTA** | `CTAInlineBlock`, `CTAFullWidthBlock` | P0 |
| **Trust** | `TrustStripBlock`, `StatsBlock` | P0 |
| **Process/FAQ** | `ProcessStepsBlock`, `FAQBlock` | P0 |
| **Gallery** | `GalleryBlock` | P0 |
| **Content** | `RichTextBlock`, `QuoteBlock`, `ButtonGroupBlock`, `SpacerBlock`, `DividerBlock`, `ImageBlock` | P0 |
| **Forms** | `ContactFormBlock`, `QuoteRequestFormBlock` | P0 |

### 6.2 Block File Structure

```
sum_core/blocks/
├── __init__.py          # BLOCKS registry
├── base.py              # BaseBlock mixins & validation
├── hero.py              # HeroImageBlock, HeroGradientBlock
├── services.py          # ServiceCardsBlock
├── testimonials.py      # TestimonialsBlock
├── cta.py               # CTAInlineBlock, CTAFullWidthBlock
├── trust.py             # TrustStripBlock, StatsBlock
├── process_faq.py       # ProcessStepsBlock, FAQBlock
├── gallery.py           # GalleryBlock
├── content.py           # RichText, Quote, ButtonGroup, etc.
└── forms.py             # ContactFormBlock, QuoteRequestFormBlock
```

### 6.3 Block Specifications

#### HeroImageBlock
- Full-width image background with configurable overlay opacity
- Fields: headline (required), subheadline (optional), CTA buttons (0-2)
- Image with required alt text

#### HeroGradientBlock
- Gradient background using brand colours
- Same fields as HeroImageBlock

#### ServiceCardsBlock
- Grid: 3-column desktop, 2-column tablet, 1-column mobile
- Each card: icon (SVG/image), title, description (rich text), link (optional)
- Min 1, Max 12 cards

#### TestimonialsBlock
- Card-based layout with configurable display count
- Each testimonial: quote (required), author (required), company (optional), photo (optional), rating (1-5 stars, optional)

#### CTAInlineBlock / CTAFullWidthBlock
- Headline, description (optional), up to 2 buttons
- Button styles: primary, secondary, outline
- Full-width variant supports background image with overlay

#### TrustStripBlock
- Horizontal row of logos/badges (2-8 items)
- Each item: image, optional link

#### StatsBlock
- Number statistics (2-4 items)
- Each: number, label, optional prefix/suffix

#### ProcessStepsBlock
- Numbered timeline (3-8 steps)
- Each: number (auto/manual), title, description
- Visual connector lines

#### FAQBlock
- Accordion-style (1-20 items)
- Each: question, answer (rich text)
- Configurable: multiple open or single open
- Generates FAQ schema (P1)

#### GalleryBlock
- Responsive grid (1-20 images)
- Each: image (required), alt text (required), caption (optional)
- Images lazy-loaded
- Lightbox zoom (P1)

#### ContactFormBlock
- Fields: name, email, phone, message
- Creates Lead record on submission

#### QuoteRequestFormBlock
- Configurable fields: project type, budget range, timeline, service area
- Creates Lead record on submission

### 6.4 Block Design Rules

**CRITICAL - All blocks MUST:**
- Use design tokens exclusively (no hardcoded values)
- Use `var(--token-name)` format for all CSS values
- Follow BEM naming convention
- Have `Meta.template` pointing to namespaced templates
- Include validation for min/max items
- Have unit tests with ≥80% coverage

---

## 7. Page Types

### 7.1 Page Hierarchy

```
HomePage (root, only one per site)
├── ServiceIndexPage
│   └── ServicePage (children)
├── StandardPage (About, Privacy, Terms)
├── ContactPage
├── BlogIndexPage
│   └── BlogPostPage (children)
├── PortfolioIndexPage
│   └── PortfolioPage (children)
├── ServiceAreaPage
└── LandingPage (noindex by default)
```

### 7.2 Page File Structure

```
sum_core/pages/
├── __init__.py
├── base.py             # SumBasePage, mixins
├── home.py             # HomePage
├── services.py         # ServiceIndexPage, ServicePage
├── standard.py         # StandardPage
├── contact.py          # ContactPage
├── blog.py             # BlogIndexPage, BlogPostPage
├── portfolio.py        # PortfolioIndexPage, PortfolioPage
├── service_area.py     # ServiceAreaPage
└── landing.py          # LandingPage
```

### 7.3 Base Page Mixins

```python
class SumBasePage(
    SeoFieldsMixin,
    OpenGraphMixin,
    BreadcrumbMixin,
    Page,
):
    pass
```

### 7.4 Page Specifications

| Page Type | Key Fields | Allowed Blocks | Parent/Child Rules |
|-----------|------------|----------------|-------------------|
| `HomePage` | StreamField body | All blocks | Only one per site |
| `ServiceIndexPage` | Intro area | Content blocks | Parent of ServicePage |
| `ServicePage` | Featured image, short desc, body | All blocks | Child of ServiceIndexPage |
| `StandardPage` | StreamField body | Content, CTA, FAQ, Gallery | Any parent |
| `ContactPage` | Business info, form selector | Contact form blocks | Any parent |
| `BlogIndexPage` | Intro content | Content blocks | Parent of BlogPostPage |
| `BlogPostPage` | Author, date, featured image, body | Content blocks | Child of BlogIndexPage |
| `PortfolioIndexPage` | Intro content | Content blocks | Parent of PortfolioPage |
| `PortfolioPage` | Gallery, description | Gallery, content | Child of PortfolioIndexPage |
| `ServiceAreaPage` | Location-specific content | All blocks | Any parent |
| `LandingPage` | Streamlined for campaigns | Hero, CTA, Form | Any parent, noindex default |

---

## 8. Lead Management System

### 8.1 Lead Model

```python
class Lead(models.Model):
    # Core fields
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    form_type = models.CharField(max_length=50)  # 'contact', 'quote'
    form_data = models.JSONField(default=dict)   # Dynamic fields
    
    # Attribution
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_term = models.CharField(max_length=100, blank=True)
    utm_content = models.CharField(max_length=100, blank=True)
    landing_page_url = models.URLField(blank=True)
    page_url = models.URLField()
    referrer_url = models.URLField(blank=True)
    
    # Derived source
    lead_source = models.CharField(max_length=50)  # google_ads, seo, direct, etc.
    lead_source_detail = models.TextField(blank=True)
    
    # Status workflow
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('quoted', 'Quoted'),
            ('won', 'Won'),
            ('lost', 'Lost'),
        ],
        default='new'
    )
    
    # Metadata
    source_page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)  # Soft delete
```

### 8.2 Lead Source Attribution Rules

| Condition | Derived Source |
|-----------|----------------|
| utm_source=google + utm_medium=cpc | `google_ads` |
| utm_source=facebook/instagram + utm_medium=cpc | `meta_ads` |
| utm_source=bing + utm_medium=cpc | `bing_ads` |
| referrer contains google.com + no utm | `seo` |
| No referrer + no utm | `direct` |
| Has referrer + no utm | `referral` |
| utm_source starts with offline | `offline` |
| All else | `unknown` |

### 8.3 Form Submission Flow

```
1. User submits form
       │
       ▼
2. Server-side validation
       │
       ├─── Invalid → Return form with errors
       │
       ▼ Valid
3. Spam check (honeypot + rate limit)
       │
       ├─── Spam → Silent discard + log
       │
       ▼ Pass
4. Create Lead record (ALWAYS succeeds)
       │
       ▼
5. Queue async tasks (Celery)
       │
       ├──► send_lead_notification
       └──► send_lead_webhook (if configured)
       
6. Return success response
```

### 8.4 Spam Protection

- **Honeypot**: Hidden field named `website`; if filled, silently discard
- **Rate limiting**: 5 submissions per IP per hour (configurable)
- **reCAPTCHA v3**: Optional, site key/secret in SiteSettings (P1)

### 8.5 Lead Admin Interface (Wagtail ModelAdmin)

- List columns: name, email, phone, source, status, date
- Search: name, email, phone, message content
- Filters: status, lead_source, date range, form_type
- Inline status update
- CSV export
- Permissions: Editors=view, Admins=view+edit+export

### 8.6 Celery Tasks

```python
# sum_core/leads/tasks.py
send_lead_notification(lead_id)   # Email to configured address
send_lead_webhook(lead_id)         # POST to Zapier/webhook URL
purge_old_leads()                  # Daily, enforces retention policy

# sum_core/integrations/hubspot/tasks.py
sync_lead_to_hubspot(lead_id)      # Optional, P1
```

---

## 9. Branding & Design System

### 9.1 SiteSettings Model

```python
class SiteSettings(BaseSiteSetting):
    # Colours
    color_primary = models.CharField(max_length=7)      # #1e3a5f
    color_secondary = models.CharField(max_length=7)
    color_accent = models.CharField(max_length=7)
    color_background = models.CharField(max_length=7)
    color_text = models.CharField(max_length=7)
    
    # Typography
    font_heading = models.CharField(max_length=100)     # Google Font name
    font_body = models.CharField(max_length=100)
    
    # Logos
    logo_header = models.ForeignKey(Image, ...)
    logo_footer = models.ForeignKey(Image, ...)
    favicon = models.ForeignKey(Image, ...)
    
    # Business Info
    company_name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    business_hours = models.TextField(blank=True)
    
    # Social Links
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    
    # Analytics
    ga_measurement_id = models.CharField(max_length=20, blank=True)
    gtm_container_id = models.CharField(max_length=20, blank=True)
    
    # Integrations
    zapier_webhook_url = models.URLField(blank=True)
    lead_notification_email = models.EmailField()
```

### 9.2 Template Tags

```django
{% load branding_tags %}
{% branding_css %}         {# Outputs CSS custom properties #}
{% branding_fonts %}       {# Outputs Google Fonts <link> tags #}
{% get_site_settings as settings %}
```

### 9.3 CSS Token System

**Location:** `core/sum_core/static/sum_core/css/tokens.css`

```css
:root {
  /* Colours (overridden by branding_css) */
  --color-primary: #1e3a5f;
  --color-secondary: #0f172a;
  --color-accent: #f59e0b;
  --color-background: #ffffff;
  --color-text: #1f2937;
  --color-text-light: #6b7280;
  --color-text-inverse: #ffffff;
  --color-surface: #f9fafb;
  --color-surface-elevated: #ffffff;
  --color-border: #e5e7eb;
  --color-error: #ef4444;
  --color-success: #10b981;
  
  /* Typography */
  --font-heading: 'Montserrat', system-ui, sans-serif;
  --font-body: 'Open Sans', system-ui, sans-serif;
  --font-bold: 700;
  --font-semibold: 600;
  --font-medium: 500;
  --font-normal: 400;
  
  /* Font Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;
  
  /* Spacing Scale */
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
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}
```

### 9.4 Design System Rules

**CRITICAL - NEVER:**
- Use hex colors (use `var(--color-*)`)
- Use `font-family:` declarations (use `var(--font-*)`)
- Use raw font-size values (use `var(--text-*)`)
- Use pixel/rem spacing (use `var(--space-*)`)
- Add inline `style=""` attributes

**ALWAYS:**
- Use typography classes (`.heading-xl`, `.text-body`, etc.)
- Use section wrapper pattern (`.section` + `.container`)
- Use HSL token format: `hsla(var(--primary), 1)`
- Follow BEM naming convention

### 9.5 Theme Presets (Internal Admin Tool)

| Preset | Primary | Secondary | Accent | Heading Font | Body Font |
|--------|---------|-----------|--------|--------------|-----------|
| Premium Trade | #1e3a5f | #0f172a | #f59e0b | Montserrat | Open Sans |
| Professional Blue | #2563eb | #1e40af | #f97316 | Poppins | Inter |
| Modern Green | #059669 | #064e3b | #fbbf24 | DM Sans | Source Sans 3 |
| Warm Earth | #92400e | #78350f | #dc2626 | Playfair Display | Lato |
| Clean Slate | #374151 | #1f2937 | #6366f1 | Work Sans | Roboto |

> These are starting points. Every client site receives custom branding.

---

## 10. Analytics & SEO

### 10.1 Analytics Template Tags

```django
{% load analytics_tags %}
{% analytics_head %}  {# GTM/GA4 head scripts #}
{% analytics_body %}  {# GTM noscript fallback #}
```

**Priority Logic:**
1. If GTM Container ID present → inject GTM
2. Else if GA4 Measurement ID present → inject GA4
3. Neither present → no scripts

### 10.2 Event Tracking

Events pushed to dataLayer:
- `form_submission` - form_type, page_url
- `phone_click` - phone number
- `email_click` - email address
- `cta_click` - button text, destination

### 10.3 SEO Template Tags

```django
{% load seo_tags %}
{% render_meta page %}    {# meta title, description, robots #}
{% render_og page %}      {# Open Graph tags #}
{% render_schema page %}  {# JSON-LD structured data #}
```

### 10.4 SEO Fields on Pages

All pages include:
- `seo_title` (default: page title + site name)
- `seo_description` (character count indicators)
- `og_image` (fallback chain: page → featured → site default)
- `seo_noindex` / `seo_nofollow` flags
- Canonical URL

### 10.5 Structured Data Schemas

| Schema | Applied To |
|--------|-----------|
| LocalBusiness | HomePage, ContactPage |
| Article | BlogPostPage |
| Service | ServicePage (P1) |
| FAQ | Pages with FAQBlock (P1) |
| BreadcrumbList | All pages (P1) |

### 10.6 Technical SEO

- Sitemap at `/sitemap.xml` (auto-generated)
- `robots.txt` at `/robots.txt`
- 301 redirects via Wagtail redirects
- Canonical URLs on all pages

---

## 11. Integrations

### 11.1 Zapier Webhook

**Configuration:** `SiteSettings.zapier_webhook_url`

**Payload Schema:**
```json
{
  "lead_id": 123,
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "07700 900000",
  "message": "Interested in kitchen renovation",
  "form_type": "quote",
  "form_data": {},
  "lead_source": "google_ads",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "kitchens-2024",
  "page_url": "https://example.com/services/kitchens/",
  "submitted_at": "2025-12-14T10:30:00Z"
}
```

**Retry Policy:** 3 attempts with exponential backoff (1, 2, 4 minutes)

### 11.2 Email Delivery

**Configuration:** Environment variables
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-api-key
DEFAULT_FROM_EMAIL=noreply@example.com
LEAD_NOTIFICATION_EMAIL=leads@example.com
```

### 11.3 HubSpot (P1, Optional)

- Access token in SiteSettings
- Creates/updates Contact on lead submission
- Field mapping: email (primary), name, phone, message, source

---

## 12. CLI & Deployment

### 12.1 CLI Commands

```bash
# Initialize new client project
sum init <project-name>
# Creates clients/<project-name>/ from boilerplate
# Generates SECRET_KEY, creates .env
# Pins sum-core version in requirements.txt

# Validate project setup
sum check <project-path>
# Verifies structure, settings, requirements
# Exit code 0 on success, 1 on errors
```

### 12.2 Deployment Scripts

```bash
# Deploy/update client site
./scripts/deploy-client.sh <client> deploy|update [--backup]

# Backup database
./scripts/backup.sh

# Restore database
./scripts/restore.sh <client> /path/to/backup.sql.gz
```

### 12.3 Server Infrastructure

**Per-Client Setup:**
- Nginx vhost (SSL via certbot)
- Gunicorn systemd service
- Celery worker systemd service
- Celery beat systemd service (if scheduled tasks)
- PostgreSQL database
- Python virtualenv

**Health Check:** `GET /health/` returns JSON with DB/Redis/Celery status

---

## 13. Implementation Milestones

### Milestone 0: Repository & Foundation (15-20 hours)

**Deliverables:**
- Monorepo with prescribed directory structure
- Docker Compose configuration
- Pre-commit hooks (Black, isort, flake8/ruff)
- Makefile with lint, test, run, format
- `sum_core` package skeleton
- Test project for CI
- README with quickstart

**Done When:**
- `docker-compose up` → Wagtail admin at localhost:8000
- `make lint` and `make test` execute successfully
- `pip install -e ./core` succeeds
- Pre-commit hooks trigger on commit

### Milestone 1: Design System & Base Templates (25-35 hours)

**Deliverables:**
- CSS token system (colours, typography, spacing, shadows, radii)
- Component CSS using tokens
- `SiteSettings` model
- Template tags: `branding_css`, `branding_fonts`, `get_site_settings`
- Base templates: `base.html`, header, footer, navigation
- Theme preset system

**Done When:**
- Test project shows styled base site
- Changing SiteSettings reflects immediately
- All CSS uses `var(--token-name)` format
- Templates validate with no HTML errors

### Milestone 2: StreamField Blocks (40-50 hours)

**Deliverables:**
- All hero, service, testimonial, CTA, trust, process/FAQ, gallery blocks
- All content blocks
- All form blocks
- Block templates using design tokens
- Unit tests for all blocks

**Done When:**
- All blocks render in Wagtail admin preview
- Blocks use tokens exclusively
- Validation enforces min/max items
- Responsive layouts work across breakpoints
- ≥80% test coverage on blocks module

### Milestone 3: Page Types & Lead Management (50-60 hours)

**Deliverables:**
- All page types with StreamField integration
- Page mixins (SEO, OG, Breadcrumb)
- Lead model with attribution
- LeadSourceRule model
- FormConfiguration model
- Lead admin interface
- Form submission handler with spam protection
- Lead notification email templates
- Celery tasks

**Done When:**
- All page types creatable with correct hierarchy
- Form submissions create Lead records with attribution
- Spam protection works
- Lead admin shows list/detail with status workflow
- CSV export works
- Email notifications send
- ≥80% test coverage

### Milestone 4: Analytics, SEO & Integrations (30-40 hours)

**Deliverables:**
- Analytics template tags
- Event tracking JavaScript
- SEO template tags
- Structured data schemas
- Sitemap and robots.txt
- Zapier webhook integration
- Email delivery configuration
- Health check endpoint

**Done When:**
- GA4/GTM scripts inject correctly
- Events fire on form submit, CTA click, phone/email click
- Meta tags, OG tags render correctly
- JSON-LD validates
- Sitemap includes all published pages
- Webhook POSTs to Zapier on lead creation
- Health endpoint returns status JSON
- ≥80% test coverage

### Milestone 5: CLI, Boilerplate & Deployment (25-35 hours)

**Deliverables:**
- `sum init` and `sum check` commands
- Client boilerplate with settings split
- `.env.example`
- Template override structure
- Nginx configuration template
- Systemd service templates
- Deployment scripts
- Backup/restore scripts
- VPS setup documentation

**Done When:**
- `sum init test-client` creates valid project
- `sum check` passes validations
- Client project runs with runserver
- Nginx template generates valid config
- Deploy script migrates, collects static, restarts
- Backup creates gzipped PostgreSQL dump
- Documentation covers VPS setup

---

## 14. Critical Path & Dependencies

```
M0: Repository Setup
       │
       ▼
M1: Design System & Base Templates
       │
       ▼
M2: StreamField Blocks
       │
       ▼
M3: Page Types & Lead Management
       │
       ▼
M4: Analytics, SEO & Integrations
       │
       ▼
M5: CLI, Boilerplate & Deployment
```

**Critical Path:**
Repository Setup → Core Package → Design System/CSS Tokens → Base Templates → StreamField Blocks → Page Types → Lead Management → Integrations → CLI/Deployment

---

## 15. Conventions & Standards

### 15.1 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Python packages | `snake_case` | `sum_core`, `sum_cli` |
| Django apps | `snake_case` | `leads`, `branding` |
| Templates | `snake_case.html` | `home_page.html` |
| CSS classes | `kebab-case` (BEM) | `hero-section__title` |
| JavaScript files | `kebab-case` | `form-handler.js` |
| Client directories | `kebab-case` | `acme-kitchens` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `DATABASE_URL` |
| Models | `PascalCase` | `Lead`, `ServicePage` |
| Block classes | `PascalCase` + Block | `HeroImageBlock` |

### 15.2 Canonical Vocabulary

| Concept | Use This | NOT This |
|---------|----------|----------|
| Form submission | `Lead` | Enquiry, Contact, Submission |
| Lead origin | `LeadSource` | Source, Origin, Channel |
| Service listing | `ServiceIndexPage` | ServicesPage, ServiceListPage |
| Individual service | `ServicePage` | ServiceDetailPage |
| Site configuration | `SiteSettings` | SiteConfig, Settings |

### 15.3 Git Conventions

**Branch Naming:**
- `feature/<scope>-<description>` → `feature/blocks-hero-section`
- `fix/<scope>-<description>` → `fix/leads-email-notification`
- `hotfix/<description>` → `hotfix/xss-vulnerability`
- `chore/<description>` → `chore/update-wagtail-7.1`

**Commit Messages (Conventional Commits):**
```
<type>(<scope>): <short description>

[optional body]
```
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

### 15.4 Environment Variables

```bash
# Django
DEBUG=False
SECRET_KEY=generate-unique-key
ALLOWED_HOSTS=example.com,www.example.com

# Database (canonical source)
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-api-key
DEFAULT_FROM_EMAIL=noreply@example.com
LEAD_NOTIFICATION_EMAIL=leads@example.com

# Analytics
GA_MEASUREMENT_ID=G-XXXXXXXXXX
GTM_CONTAINER_ID=GTM-XXXXXXX

# Integrations
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/...

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## 16. Definition of Done

### 16.1 Task Definition of Done

- [ ] Code implements all acceptance criteria
- [ ] Unit tests written and passing
- [ ] Test coverage meets threshold (≥80% for critical paths)
- [ ] Code follows naming conventions
- [ ] No hardcoded values (uses tokens/config)
- [ ] Templates validate (no HTML errors)
- [ ] Responsive design verified
- [ ] Documentation updated if needed

### 16.2 Milestone Definition of Done

**Milestone 0:**
- [ ] Monorepo matches structure
- [ ] `pip install -e ./core` succeeds
- [ ] `docker-compose up` → Wagtail admin accessible
- [ ] CI pipeline runs lint + test

**Milestone 1:**
- [ ] Token system complete
- [ ] SiteSettings model works
- [ ] Base templates render
- [ ] Branding changes reflect immediately

**Milestone 2:**
- [ ] All 15+ blocks implemented
- [ ] Blocks use tokens only
- [ ] Validation works
- [ ] 80%+ test coverage

**Milestone 3:**
- [ ] All page types creatable
- [ ] Forms capture to Lead model
- [ ] Attribution works
- [ ] Lead admin complete
- [ ] Notifications send

**Milestone 4:**
- [ ] GA4/GTM working
- [ ] SEO tags rendering
- [ ] Schema validates
- [ ] Webhooks sending

**Milestone 5:**
- [ ] CLI commands work
- [ ] Deployment tested
- [ ] Backup/restore tested
- [ ] First client site live

---

## Appendices

### Appendix A: Base Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    {% include "sum_core/includes/meta_tags.html" %}
    {% branding_css %}
    <link rel="stylesheet" href="{% static 'sum_core/css/main.css' %}">
    {% branding_fonts %}
    {% analytics_head %}
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {% include "sum_core/includes/header.html" %}
    
    <main id="main-content">
        {% block content %}{% endblock %}
    </main>
    
    {% include "sum_core/includes/footer.html" %}
    
    <script src="{% static 'sum_core/js/main.js' %}" defer></script>
    {% analytics_body %}
</body>
</html>
```

### Appendix B: Section Wrapper Pattern

```html
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

Section modifiers: `.section--light`, `.section--dark`, `.section--primary`

### Appendix C: Typography Classes

| Design Element | CSS Class |
|----------------|-----------|
| Hero headline | `.heading-display` |
| Page/section title | `.heading-xl` |
| Section heading | `.heading-lg` |
| Card/item title | `.heading-md` |
| Minor heading | `.heading-sm` |
| Lead paragraph | `.text-lg` |
| Body copy | `.text-body` |
| Small text | `.text-sm` |
| Meta/timestamps | `.text-xs` |
| Eyebrow/kicker | `.section__eyebrow` |
| Muted text | `.text-muted` |

### Appendix D: Priority Definitions

| Priority | Definition | Impact |
|----------|------------|--------|
| **P0** | Must-have for Phase 1 | Blocks release |
| **P1** | Should-have, can slip to Phase 1.1 | Desirable |
| **P2** | Nice-to-have, Phase 2+ | Deferred |

### Appendix E: Effort Sizing

| Size | Hours | Examples |
|------|-------|----------|
| XS | 1-2h | Config change, simple fix |
| S | 2-3h | Single component, simple feature |
| M | 3-5h | Multi-file feature, integration |
| L | 5-7h | Complex feature, major component |
| XL | 8+h | Large system, multiple integrations |

### Appendix F: Quick Command Reference

```bash
# Local Development
make run          # Start Docker dev environment
make test         # Run all tests
make lint         # Run linters
make format       # Auto-format code

# CLI
sum init acme     # Create new client project
sum check ./clients/acme  # Validate project

# Server (production)
./deploy-client.sh acme deploy   # Initial deployment
./deploy-client.sh acme update   # Update existing
./backup.sh                       # Manual backup
./restore.sh acme /path/to/backup.sql.gz  # Restore
```

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 14, 2025 | Initial consolidated document |

**Source Documents:**
- PRD v1.1 (December 7, 2025)
- Project Initiation Packet v1.1 (December 7, 2025)
- Technical Specification v0.2
- Implementation Plan v1.1 (December 11, 2025)

---

*This Single Source of Truth consolidates all SUM Platform planning documents. For implementation, reference this document. Update this document when architectural decisions change.*
