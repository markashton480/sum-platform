# SUM Core Wiring Inventory

> **Purpose**: This document answers "What must a client project do to consume SUM Core?" for each feature area.

---

## Quick Start Checklist

```python
# settings.py - Required INSTALLED_APPS
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Wagtail core
    "wagtail",
    "wagtail.admin",
    "wagtail.users",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.snippets",
    "wagtail.sites",
    "wagtail.search",
    "wagtail.contrib.forms",
    "wagtail.contrib.settings",
    "wagtail.contrib.redirects",
    # Wagtail dependencies
    "modelcluster",
    "taggit",
    # SUM Core apps
    "sum_core",
    "sum_core.pages",
    "sum_core.navigation",
    "sum_core.leads",
    "sum_core.forms",
    "sum_core.analytics",
    "sum_core.seo",
    # Your client-specific apps
    "home",  # or your homepage app
]
```

```python
# urls.py - Required URL includes
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("forms/", include("sum_core.forms.urls")),   # Form submissions
    path("", include("sum_core.ops.urls")),           # /health/ endpoint
    path("", include("sum_core.seo.urls")),           # sitemap.xml, robots.txt
    path("", include(wagtail_urls)),                  # Wagtail page serving (must be last)
]
```

---

## Theme Wiring (v0.6+)

### What Lives Where

- **Canonical themes (platform repo)**: `themes/<theme_slug>/...`
- **Active theme (client project)**: `clients/<client>/theme/active/...` (copied at `sum init` time)

### Template Resolution Order (Highest Priority First)

Configure Django templates so the theme wins, but core remains a fallback:

1. `clients/<client>/theme/active/templates/`
2. `clients/<client>/templates/overrides/`
3. `sum_core/templates/` (via `APP_DIRS=True`)

### Static Files Expectations

- Theme static assets live under: `theme/active/static/<theme_slug>/...`
- Theme CSS convention: `static/<theme_slug>/css/main.css` (compiled output, committed)
- Theme JS convention: `static/<theme_slug>/js/main.js` (optional)

In Django settings, ensure theme statics are included first (example pattern):

```python
THEME_STATIC_DIR = BASE_DIR / "theme" / "active" / "static"
STATICFILES_DIRS = [THEME_STATIC_DIR]
```

### Database Reminder (Dev Parity)

- Real development parity expects Postgres via `DJANGO_DB_*` env vars.
- `core/sum_core/test_project/` has an SQLite fallback for convenience, but it is not the target production parity.

---

## Feature Area: Branding & Design Tokens

### What Core Provides

- **SiteSettings model** (`sum_core.branding.models.SiteSettings`) with fields for:

  - Brand colours (primary, secondary, accent, background, text, surface)
  - Typography (heading_font, body_font - Google Fonts names)
  - Logos (header, footer, favicon, og_default_image)
  - Business info (company name, established year, phone, email, address)
  - Social links (Facebook, Instagram, LinkedIn, Twitter, YouTube, TikTok)

- **Template tags** (from `sum_core.templatetags.branding_tags`):

  - `{% branding_fonts %}` - Injects Google Fonts `<link>` tags
  - `{% branding_css %}` - Injects `<style>` block with CSS custom properties

- **CSS token system** (`sum_core/static/sum_core/css/tokens.css`)

### What Client Must Do

| Requirement       | How                                                                                              |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| Include app       | `"sum_core"` in INSTALLED_APPS                                                                   |
| Use template tags | `{% load branding_tags %}` then `{% branding_fonts %}` and `{% branding_css %}` in base template |
| Link main CSS     | `<link href="{% static 'sum_core/css/main.css' %}" rel="stylesheet">`                            |

### Per-Site vs Per-Project

| Setting                     | Location                                          |
| --------------------------- | ------------------------------------------------- |
| Brand colours, fonts, logos | **Per-site**: Wagtail Settings → Site settings    |
| CSS token defaults          | **Per-project**: Override in client CSS if needed |

---

## Feature Area: Navigation System

### What Core Provides

- **HeaderSettings** (`sum_core.navigation.models.HeaderSettings`):

  - Menu structure (up to 3 levels)
  - Header CTA button
  - Phone number toggle
  - Mobile sticky CTA configuration

- **FooterSettings** (`sum_core.navigation.models.FooterSettings`):

  - Footer sections with links
  - Tagline override
  - Social links override

- **Template tags** (from `sum_core.templatetags.navigation_tags`):

  - `{% get_header_navigation %}` - Returns header menu data
  - `{% get_footer_navigation %}` - Returns footer data

- **Include templates**:
  - `sum_core/navigation/header.html`
  - `sum_core/navigation/footer.html`

### What Client Must Do

| Requirement              | How                                               |
| ------------------------ | ------------------------------------------------- |
| Include app              | `"sum_core.navigation"` in INSTALLED_APPS         |
| Include in base template | `{% include "sum_core/navigation/header.html" %}` |

### Per-Site vs Per-Project

| Setting                     | Location                                                  |
| --------------------------- | --------------------------------------------------------- |
| Menu items, CTAs, structure | **Per-site**: Wagtail Settings → Header/Footer Navigation |
| Template overrides          | **Per-project**: Override templates in client project     |

---

## Feature Area: Forms & Lead Pipeline

### What Core Provides

- **Form blocks** (`sum_core.blocks`):

  - `ContactFormBlock` - Simple contact form
  - `QuoteRequestFormBlock` - Quote request form

- **Submission endpoint**: `POST /forms/submit/`

  - CSRF protection
  - Honeypot spam protection
  - Timing token validation
  - Rate limiting (per-IP)

- **Lead model** (`sum_core.leads.models.Lead`):

  - Persists all submissions
  - Attribution capture (UTM, referrer, landing page)
  - Status tracking (new, contacted, qualified, converted)

- **Wagtail admin**: "Leads" section with list, detail, filters, CSV export

- **Async notifications** (via Celery):
  - Email notifications (HTML + plain text)
  - Webhook notifications (Zapier)

### What Client Must Do

| Requirement          | How                                                                              |
| -------------------- | -------------------------------------------------------------------------------- |
| Include apps         | `"sum_core.leads"`, `"sum_core.forms"` in INSTALLED_APPS                         |
| Include URLs         | `path("forms/", include("sum_core.forms.urls"))`                                 |
| Configure middleware | `"sum_core.ops.middleware.CorrelationIdMiddleware"` (recommended, early in list) |
| Set env vars         | See below                                                                        |

### Environment Variables

| Variable                         | Required  | Default               | Purpose                            |
| -------------------------------- | --------- | --------------------- | ---------------------------------- |
| `LEAD_NOTIFICATION_EMAIL`        | For email | `""`                  | Destination for lead notifications |
| `DEFAULT_FROM_EMAIL`             | For email | `noreply@example.com` | Sender address                     |
| `EMAIL_BACKEND`                  | No        | `console`             | Email backend class                |
| `EMAIL_HOST`, `EMAIL_PORT`, etc. | For SMTP  | localhost:25          | SMTP configuration                 |
| `CELERY_BROKER_URL`              | For async | `memory://`           | Celery broker (Redis recommended)  |
| `SUM_TRUSTED_PROXY_IPS`          | No        | `[]`                  | Trusted proxy IPs/CIDRs for client IP resolution |

### Per-Site vs Per-Project

| Setting                             | Location                                             |
| ----------------------------------- | ---------------------------------------------------- |
| Email From/Reply-To, subject prefix | **Per-site**: SiteSettings → Email Notifications     |
| SMTP credentials, Celery broker     | **Per-project**: Environment variables               |
| Rate limits, honeypot config        | **Per-project**: `FormConfiguration` in Django admin |

---

## Feature Area: SEO (Tags, Sitemap, Robots, Schema)

### What Core Provides

- **SEO template tags** (`sum_core.templatetags.seo_tags`):

  - `{% seo_tags page %}` - Meta title, description, canonical, robots, Open Graph

- **JSON-LD schema** (`sum_core.templatetags.seo_tags`):

  - `{% render_schema page %}` - LocalBusiness, Article, FAQ, Service, Breadcrumb

- **Endpoints**:

  - `GET /sitemap.xml` - Auto-generated XML sitemap (per-site, excludes noindex)
  - `GET /robots.txt` - Configurable per site via SiteSettings

- **Page mixins**:
  - `SeoFieldsMixin` - seo_title, search_description
  - `OpenGraphMixin` - og_title, og_description, og_image
  - `BreadcrumbMixin` - Automatic breadcrumb generation

### What Client Must Do

| Requirement          | How                                                          |
| -------------------- | ------------------------------------------------------------ |
| Include app          | `"sum_core.seo"` in INSTALLED_APPS                           |
| Include URLs         | `path("", include("sum_core.seo.urls"))`                     |
| Add to base template | `{% load seo_tags %}` then `{% seo_tags page %}` in `<head>` |
| Add schema           | `{% render_schema page %}` in `<head>`                       |

### Per-Site vs Per-Project

| Setting                  | Location                                     |
| ------------------------ | -------------------------------------------- |
| robots.txt content       | **Per-site**: SiteSettings → Technical SEO   |
| Default OG image         | **Per-site**: SiteSettings → Logos & Favicon |
| Page-specific SEO fields | **Per-page**: Page edit screen in Wagtail    |

---

## Feature Area: Consent & Cookie Banner (v0.6+)

### What Core Provides

- **SiteSettings fields** (`sum_core.branding.models.SiteSettings`):

  - `cookie_banner_enabled` (bool) - When enabled, analytics require consent
  - `cookie_consent_version` (str) - Bump to force re-prompt (e.g., "2024-01")
  - `privacy_policy_page`, `cookie_policy_page`, `terms_page` - Page links for banner/footer

- **Cookie banner template** (`sum_core/includes/cookie_banner.html`):

  - Renders only when `cookie_banner_enabled=True`
  - DOM contract (required for JS to function):
    - Container: `.cookie-banner` with `aria-hidden`, `aria-label`
    - Accept button: `[data-cookie-consent="accept"]`
    - Reject button: `[data-cookie-consent="reject"]`
    - Status element: `.cookie-banner__status` with `aria-live="polite"`

- **Cookie consent JS** (`sum_core/static/sum_core/js/cookie_consent.js`):

  - Cookie names: `sum_cookie_consent` (values: `accepted` | `rejected`)
  - Version cookie: `sum_cookie_consent_v` (stores consent version)
  - Expiry: 180 days (no Domain attribute = host-only)
  - Events: Dispatches `cookieConsentChanged` on consent change
  - Public API: `window.SumCookieConsent` for testing/debugging

- **Footer "Manage cookies" link**:
  - Rendered when `cookie_banner_enabled=True`
  - Uses `data-cookie-consent="manage"` attribute
  - Clears cookies and re-shows banner

### Cookie Contract

| Cookie Name           | Values                | Purpose              | Expiry   |
| --------------------- | --------------------- | -------------------- | -------- |
| `sum_cookie_consent`  | `accepted`, `rejected`| User's consent choice| 180 days |
| `sum_cookie_consent_v`| Version string        | Consent version      | 180 days |

### Re-prompting Users

To force all users to re-consent (e.g., after updating cookie policy):

1. Go to Wagtail Admin → Settings → Site settings
2. Increment `cookie_consent_version` (e.g., "2024-01" → "2024-02")
3. Save - existing cookies with old version become invalid

### What Client Must Do

| Requirement                | How                                                           |
| -------------------------- | ------------------------------------------------------------- |
| Include banner in template | `{% include "sum_core/includes/cookie_banner.html" %}`        |
| Include cookie_consent.js  | `<script src="{% static 'sum_core/js/cookie_consent.js' %}">` |
| Emit consent version meta  | `<meta name="sum:cookie-consent-version" content="...">`      |

**Note**: The core `theme/base.html` handles all of this automatically.

### Per-Site vs Per-Project

| Setting                | Location                                   |
| ---------------------- | ------------------------------------------ |
| Banner enabled toggle  | **Per-site**: SiteSettings → Consent & Legal |
| Consent version        | **Per-site**: SiteSettings → Consent & Legal |
| Policy page links      | **Per-site**: SiteSettings → Consent & Legal |

---

## Feature Area: Analytics (GA4/GTM + Events)

### What Core Provides

- **Template tags** (`sum_core.templatetags.analytics_tags`):

  - `{% analytics_head %}` - Emits JSON config as `<script id="sum-analytics-config" type="application/json">`
  - `{% analytics_body %}` - Reserved for compatibility (returns empty string)

- **Analytics loader JS** (`sum_core/static/sum_core/js/analytics_loader.js`):

  - Reads config from `#sum-analytics-config`
  - Loads GTM/GA4 scripts **dynamically** (never in server-rendered HTML)
  - Respects consent: only loads if `cookie_banner_enabled=false` OR consent accepted
  - Listens for `cookieConsentChanged` event to load after consent

- **Event tracking** (`sum_core/static/sum_core/js/tracking.js`):

  - Form submission events → `dataLayer.push()`
  - CTA click events
  - Phone/email link clicks

- **Admin dashboard**: Lead analytics panel in Wagtail admin home

### Cache-Safe Analytics

Analytics scripts are **never** included in server-rendered HTML. This means:

- Pages are cache-safe (same HTML regardless of consent state)
- No edge/CDN worker logic required
- Consent checking happens entirely client-side

### What Client Must Do

| Requirement              | How                                                              |
| ------------------------ | ---------------------------------------------------------------- |
| Include app              | `"sum_core.analytics"` in INSTALLED_APPS                         |
| Add to base template     | `{% analytics_head %}` in `<head>`                               |
| Include analytics loader | `<script src="{% static 'sum_core/js/analytics_loader.js' %}">` when GA/GTM configured |

### Per-Site vs Per-Project

| Setting            | Location                               |
| ------------------ | -------------------------------------- |
| GTM Container ID   | **Per-site**: SiteSettings → Analytics |
| GA4 Measurement ID | **Per-site**: SiteSettings → Analytics |

**Note**: GTM takes priority over GA4 if both are configured.

---

## Feature Area: Integrations (Zapier)

### What Core Provides

- **Webhook delivery** (via Celery task):
  - Sends lead data to configured Zapier webhook
  - Automatic retries on failure
  - Status tracking on Lead model

### What Client Must Do

| Requirement      | How                                                        |
| ---------------- | ---------------------------------------------------------- |
| Include apps     | `"sum_core.leads"` in INSTALLED_APPS (already covers this) |
| Configure Celery | Broker URL for async delivery                              |

### Per-Site vs Per-Project

| Setting               | Location                                        |
| --------------------- | ----------------------------------------------- |
| Zapier enabled toggle | **Per-site**: SiteSettings → Zapier Integration |
| Zapier webhook URL    | **Per-site**: SiteSettings → Zapier Integration |
| Celery broker         | **Per-project**: `CELERY_BROKER_URL` env var    |

---

## Feature Area: Legal Pages (v0.6+)

### What Core Provides

- **LegalPage model** (`sum_core.pages.LegalPage`):

  - `last_updated` (DateField) - Optional date displayed near title
  - `sections` (StreamField) - LegalSectionBlock instances for structured content
  - Template: `theme/legal_page.html` (theme-owned)

- **LegalSectionBlock** (`sum_core.blocks.LegalSectionBlock`):

  - `anchor` (CharBlock) - ID for in-page links (lowercase with hyphens)
  - `heading` (CharBlock) - Section heading
  - `body` (RichTextBlock) - Section content with H3/H4, lists, links

- **Table of Contents**:
  - Desktop: Sticky sidebar ToC
  - Mobile: Collapsible dropdown ToC
  - Driven by `page.sections` field automatically

### Template Contract

Themes implementing `theme/legal_page.html` should:

- Render breadcrumbs if `page.get_breadcrumbs` is available
- Display `page.title` and optionally `page.search_description` as intro
- Show `page.last_updated` with a print button
- Generate ToC from `page.sections` with anchor links
- Render each section with `id="{{ section.value.anchor }}"` for linking

### Section Anchor Contract

| Element           | Requirement                                              |
| ----------------- | -------------------------------------------------------- |
| Section ID        | `id="{{ section.value.anchor\|slugify }}"`               |
| ToC link          | `href="#{{ section.value.anchor\|slugify }}"`            |
| Scroll margin     | `.scroll-mt-24` or similar for fixed header offset       |

### What Client Must Do

| Requirement                    | How                                           |
| ------------------------------ | --------------------------------------------- |
| Include pages app              | `"sum_core.pages"` in INSTALLED_APPS          |
| Create legal pages in Wagtail  | Add LegalPage children under site root        |
| Link in SiteSettings           | Set privacy_policy_page, cookie_policy_page, terms_page |

### Per-Site vs Per-Project

| Setting                | Location                                      |
| ---------------------- | --------------------------------------------- |
| Legal page content     | **Per-site**: Edit LegalPage in Wagtail       |
| Policy page links      | **Per-site**: SiteSettings → Consent & Legal  |
| Template styling       | **Per-project**: Theme template override      |

---

## Feature Area: Seeder & Starter Profiles (v0.6+)

### What Core Provides

- **seed_showroom command** (`python manage.py seed_showroom`):

  - Creates a complete site tree with example content
  - Idempotent: safe to run multiple times
  - Slug-scoped: only modifies pages with known seeder slugs

- **Profiles**:

  | Profile     | Flag                | Content                                    |
  | ----------- | ------------------- | ------------------------------------------ |
  | `starter`   | `--profile starter` | Minimal homepage, services, contact, legal |
  | `showroom`  | `--profile showroom`| Full block showcase + kitchen sink page    |

### Seeder Slug Contract

Pages created by the seeder use fixed slugs to enable safe re-runs:

| Page Type       | Slug                | Purpose                        |
| --------------- | ------------------- | ------------------------------ |
| HomePage        | `showroom-home`     | Site root                      |
| Contact         | `contact`           | Contact page                   |
| Services Index  | `services`          | Services listing               |
| Service 1       | `solar-installation`| Example service                |
| Service 2       | `roofing`           | Example service                |
| Terms           | `terms`             | Terms & conditions legal page  |
| Privacy         | `privacy`           | Privacy notice legal page      |
| Cookies         | `cookies`           | Cookie policy legal page       |
| Showroom        | `showroom`          | Block showcase (showroom only) |
| Kitchen Sink    | `kitchen-sink`      | All blocks (showroom only)     |

### Branding & Navigation Seeded

The seeder also configures:

- **SiteSettings**: company_name, logos, contact info, consent settings
- **HeaderNavigation**: Menu items, header CTA
- **FooterNavigation**: Link sections including Legal (Terms/Privacy/Cookies)
- **Consent**: `cookie_banner_enabled=True`, policy page links

### Command Options

```bash
# Basic usage
python manage.py seed_showroom

# Clear and re-seed
python manage.py seed_showroom --clear

# Use showroom profile (more content)
python manage.py seed_showroom --profile showroom

# Custom hostname/port
python manage.py seed_showroom --hostname example.com --port 80

# Custom homepage model
python manage.py seed_showroom --homepage-model myapp.HomePage
```

---

## Feature Area: Ops/Observability

### What Core Provides

- **Health endpoint**: `GET /health/`

  - Returns JSON with an overall `status` and per-dependency `checks`.
  - Overall status contract:
    - `ok` -> HTTP 200
    - `degraded` -> HTTP 200 (non-critical dependency issues, e.g. Celery down)
    - `unhealthy` -> HTTP 503 (critical dependency outage, e.g. DB/cache down)
  - Checks: database, cache, Celery (non-critical; skipped if not configured)

- **Request correlation**: `CorrelationIdMiddleware`

  - Adds `X-Request-ID` header to responses
  - Available in logs as `request_id`

- **Sentry integration** (`sum_core.ops.sentry.init_sentry()`):

  - Automatically initializes if `SENTRY_DSN` is set
  - No-ops gracefully if not configured

- **Structured logging** (`sum_core.ops.logging.get_logging_config()`):
  - JSON format for production
  - Human-readable for development
  - Request correlation IDs included

### What Client Must Do

| Requirement       | How                                                                 |
| ----------------- | ------------------------------------------------------------------- |
| Include URLs      | `path("", include("sum_core.ops.urls"))`                            |
| Add middleware    | `"sum_core.ops.middleware.CorrelationIdMiddleware"` (first in list) |
| Initialize Sentry | Call `init_sentry()` in settings.py                                 |
| Configure logging | `LOGGING = get_logging_config(debug=DEBUG)`                         |

### Environment Variables

| Variable                    | Required | Default       | Purpose                        |
| --------------------------- | -------- | ------------- | ------------------------------ |
| `SENTRY_DSN`                | No       | `""`          | Sentry DSN (disabled if empty) |
| `SENTRY_ENVIRONMENT`        | No       | `development` | Environment tag                |
| `SENTRY_TRACES_SAMPLE_RATE` | No       | `0.0`         | Performance monitoring rate    |
| `LOG_LEVEL`                 | No       | `INFO`        | Logging verbosity              |
| `LOG_FORMAT`                | No       | `auto`        | `json`, `auto`, or blank       |

### Per-Site vs Per-Project

| Setting                 | Location                                     |
| ----------------------- | -------------------------------------------- |
| Sentry DSN, environment | **Per-project**: Environment variables       |
| Log level, format       | **Per-project**: Environment variables       |
| Health endpoint content | **Automatic**: Core provides standard checks |

---

## Middleware Stack (Recommended Order)

```python
MIDDLEWARE = [
    "sum_core.ops.middleware.CorrelationIdMiddleware",  # Must be early
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]
```

---

## Complete Environment Variable Reference

| Variable                                 | Feature       | Required       | Default               |
| ---------------------------------------- | ------------- | -------------- | --------------------- |
| `DJANGO_DB_*`                            | Database      | For Postgres   | SQLite fallback       |
| `EMAIL_BACKEND`                          | Leads         | No             | `console`             |
| `EMAIL_HOST`, `EMAIL_PORT`               | Leads         | For SMTP       | localhost:25          |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Leads         | For SMTP       | empty                 |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL`         | Leads         | No             | `False`               |
| `DEFAULT_FROM_EMAIL`                     | Leads         | No             | `noreply@example.com` |
| `LEAD_NOTIFICATION_EMAIL`                | Leads         | For email      | empty                 |
| `CELERY_BROKER_URL`                      | Async tasks   | For production | `memory://`           |
| `CELERY_RESULT_BACKEND`                  | Async tasks   | No             | `cache+memory://`     |
| `SENTRY_DSN`                             | Observability | No             | empty (disabled)      |
| `SENTRY_ENVIRONMENT`                     | Observability | No             | `development`         |
| `SENTRY_TRACES_SAMPLE_RATE`              | Observability | No             | `0.0`                 |
| `LOG_LEVEL`                              | Observability | No             | `INFO`                |
| `LOG_FORMAT`                             | Observability | No             | `auto`                |
| `GIT_SHA`, `BUILD_ID`, `RELEASE`         | Observability | No             | empty                 |

---

## Summary: What's Automatic vs What Needs Configuration

### Automatic (Zero Config)

- Design token CSS variables
- Navigation caching & invalidation
- Lead persistence & admin UI
- Sitemap generation from published pages
- Health endpoint checks
- Request correlation IDs
- Cookie consent JS behaviour (when banner enabled)
- Analytics consent gating (client-side)
- Legal page ToC generation

### Requires SiteSettings (Per-Site in Wagtail)

- Brand colours, fonts, logos
- Menu structure, CTAs
- Analytics IDs (GA4/GTM)
- Zapier webhook
- robots.txt content
- Email From/Reply-To
- Cookie banner toggle & consent version
- Legal page links (privacy, cookies, terms)

### Requires Environment Variables (Per-Project)

- Database connection
- SMTP credentials
- Celery broker
- Sentry DSN
- Logging configuration
