# SUM Platform Theme Development Guide

> **From Messy Wireframe to Production-Ready Theme**
>
> This guide walks you through converting an HTML wireframe into a fully-functional SUM Platform theme that integrates with SiteSettings branding, Wagtail blocks, and the Tailwind design token system.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Phase 1: Setup & Scaffolding](#2-phase-1-setup--scaffolding)
3. [Phase 2: Design Token Extraction](#3-phase-2-design-token-extraction)
4. [Phase 3: Tailwind Configuration](#4-phase-3-tailwind-configuration)
5. [Phase 4: Base Template & Branding Integration](#5-phase-4-base-template--branding-integration)
6. [Phase 5: Component Classes (input.css)](#6-phase-5-component-classes-inputcss)
7. [Phase 6: Block Template Conversion](#7-phase-6-block-template-conversion)
8. [Phase 7: Navigation & Footer](#8-phase-7-navigation--footer)
9. [Phase 8: JavaScript Interactions](#9-phase-8-javascript-interactions)
10. [Phase 9: Build, Test & Polish](#10-phase-9-build-test--polish)
11. [Phase 10: Cookie Banner & Legal Page Templates](#11-phase-10-cookie-banner--legal-page-templates-v06)
12. [Quick Reference](#12-quick-reference)

---

## 1. Architecture Overview

### The "Frame, Not The Paint" Philosophy

SUM Platform themes are **structure-first**. The premium feel comes from architecture (spacing, typography hierarchy, animations) - not specific colors. Colors are injected at runtime via CSS variables from SiteSettings, meaning:

- **One theme, infinite brand variations** - no CSS rebuild needed
- **Client provides primary color** - system derives the full palette
- **Fonts configurable per-site** - Google Fonts loaded dynamically

### How Themes Slot Into SUM Platform

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Project                          │
├─────────────────────────────────────────────────────────────┤
│  SiteSettings (Wagtail Admin)                                │
│  ├── Brand Colors (primary, secondary, accent, etc.)        │
│  ├── Typography (heading_font, body_font)                   │
│  ├── Logos (header_logo, footer_logo, favicon)              │
│  └── Business Info (company_name, phone, email, etc.)       │
├─────────────────────────────────────────────────────────────┤
│  Theme (from themes/ directory)                              │
│  ├── templates/theme/base.html      ← Loads branding_css    │
│  ├── templates/sum_core/blocks/     ← Block overrides       │
│  ├── static/theme_x/css/main.css    ← Compiled Tailwind     │
│  └── static/theme_x/js/main.js      ← Interactions          │
├─────────────────────────────────────────────────────────────┤
│  sum_core (shared infrastructure)                            │
│  ├── Branding template tags ({% branding_css %})            │
│  ├── Navigation template tags ({% header_nav %})            │
│  └── StreamField blocks (HeroBlock, ServiceCardsBlock...)   │
└─────────────────────────────────────────────────────────────┘
```

### Theme Distribution Repository

Theme sources are published to `markashton480/sum-themes` for versioned distribution and client consumption. Treat `sum-platform/themes/` as the source of truth during development, and only sync to the distribution repo when the publishing workflow says so.

### Key Files You'll Create

| File | Purpose |
|------|---------|
| `theme.json` | Theme manifest (name, slug, version) |
| `tailwind/tailwind.config.js` | Colors, fonts, breakpoints, animations |
| `static/theme_x/css/input.css` | Tailwind directives + component classes |
| `static/theme_x/css/main.css` | **Generated** - compiled CSS output |
| `static/theme_x/js/main.js` | Theme interactions (menus, animations) |
| `templates/theme/base.html` | Master layout template |
| `templates/theme/includes/*.html` | Header, footer, sticky CTA |
| `templates/sum_core/blocks/*.html` | Block template overrides |

---

## 2. Phase 1: Setup & Scaffolding

### Step 1.1: Create Theme Directory Structure

```bash
# Replace 'theme_b' with your theme slug (lowercase, underscores)
mkdir -p themes/theme_b/{tailwind,static/theme_b/{css,js},templates/{theme/includes,sum_core/blocks}}
```

### Step 1.2: Create theme.json Manifest

```json
{
  "slug": "theme_b",
  "name": "Your Theme Name",
  "description": "Brief description of theme style and features",
  "version": "1.0.0"
}
```

**Rules:**
- `slug` MUST match the directory name exactly
- `slug` uses lowercase with underscores (e.g., `sage_stone`, `modern_minimal`)
- Theme discovery scans `themes/*/theme.json` - invalid manifests are skipped

### Step 1.3: Copy Tailwind Toolchain

Copy the build infrastructure from an existing theme:

```bash
cp themes/theme_a/tailwind/package.json themes/theme_b/tailwind/
cp themes/theme_a/tailwind/npm-shrinkwrap.json themes/theme_b/tailwind/
cp themes/theme_a/tailwind/postcss.config.js themes/theme_b/tailwind/
cp themes/theme_a/build_fingerprint.py themes/theme_b/
```

### Step 1.4: Initialize npm Dependencies

```bash
cd themes/theme_b/tailwind
npm ci  # Use ci, not install - respects shrinkwrap
```

**Important:** We pin Tailwind v3.4.x. Do NOT upgrade to v4 without reviewing CSS variable compatibility.

### Step 1.5: Copy Your Wireframe Reference

Place your compiled wireframe HTML in a scannable location:

```bash
mkdir -p docs/dev/design/wireframes/your-theme/compiled/
cp /path/to/wireframe/*.html docs/dev/design/wireframes/your-theme/compiled/
```

This serves two purposes:
1. Tailwind scans it to preserve all utility classes used
2. Reference for copy-pasting markup during template creation

---

## 3. Phase 2: Design Token Extraction

### Step 2.1: Audit Your Wireframe's Color Palette

Open your wireframe HTML and extract every unique color. Create a color inventory:

```
WIREFRAME COLOR AUDIT
=====================
Background:     #F7F5F1  (warm linen - will map to --background-*)
Text Primary:   #1A2F23  (dark green - will map to --text-*)
Text Muted:     #6B7280  (gray - will map to text opacity)
Primary/CTA:    #A0563B  (terra cotta - will map to --brand-*)
Secondary:      #556F61  (moss green - will map to --secondary-*)
Surface/Cards:  #E3DED4  (oat - will map to --surface-*)
Borders:        #D1D5DB  (light gray)
```

### Step 2.2: Map to SiteSettings Variables

SiteSettings injects these CSS variables (via `{% branding_css %}`):

| SiteSettings Field | CSS Variables Generated | Purpose |
|--------------------|------------------------|---------|
| `primary_color` | `--brand-h`, `--brand-s`, `--brand-l` | Primary CTA, links, accents |
| `secondary_color` | `--secondary-h`, `--secondary-s`, `--secondary-l` | Secondary buttons, highlights |
| `accent_color` | `--accent-h`, `--accent-s`, `--accent-l` | Tertiary accents |
| `background_color` | `--background-h`, `--background-s`, `--background-l` | Page background |
| `text_color` | `--text-h`, `--text-s`, `--text-l` | Main text color |
| `surface_color` | `--surface-h`, `--surface-s`, `--surface-l` | Card/panel backgrounds |
| `heading_font` | `--font-heading` | Display/heading typeface |
| `body_font` | `--font-body` | Body text typeface |

### Step 2.3: Extract Typography

Audit your wireframe's typography:

```
TYPOGRAPHY AUDIT
================
Headings:    font-family: "Playfair Display", serif
             sizes: 48px (h1), 36px (h2), 24px (h3), 20px (h4)
             weight: 400-700
             line-height: 1.1-1.2

Body:        font-family: "Lato", sans-serif
             size: 16px (base), 14px (small), 18px (large)
             weight: 400, 500
             line-height: 1.6-1.7

Accent:      font-family: "Crimson Text", serif (optional, for quotes/callouts)
```

### Step 2.4: Extract Spacing & Breakpoints

Note any custom breakpoints or spacing patterns:

```
SPACING AUDIT
=============
Section padding: 4rem (mobile) → 6rem (tablet) → 8rem (desktop)
Container max-width: 1280px
Card gap: 1.5rem (mobile) → 2rem (desktop)
Custom breakpoint: 970px (iPad landscape)
```

---

## 4. Phase 3: Tailwind Configuration

### Step 3.1: Create tailwind.config.js

```javascript
// themes/theme_b/tailwind/tailwind.config.js

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Theme templates
    '../templates/**/*.html',
    // Core templates (for block base classes)
    '../../../core/sum_core/templates/**/*.html',
    // Wireframe reference (preserves all classes used in design)
    '../../../docs/dev/design/wireframes/your-theme/compiled/*.html',
  ],

  theme: {
    extend: {
      // ======================
      // COLORS
      // ======================
      colors: {
        // Semantic colors that read from CSS variables (with fallbacks)
        // These allow SiteSettings to override at runtime

        primary: 'hsl(var(--brand-h, 16) var(--brand-s, 46%) var(--brand-l, 43%) / <alpha-value>)',
        secondary: 'hsl(var(--secondary-h, 148) var(--secondary-s, 13%) var(--secondary-l, 38%) / <alpha-value>)',
        accent: 'hsl(var(--accent-h, 16) var(--accent-s, 46%) var(--accent-l, 43%) / <alpha-value>)',

        // Theme-specific named palette (your wireframe's colors)
        // Use descriptive names that make sense for YOUR theme
        sage: {
          black: 'hsl(var(--text-h, 146) var(--text-s, 29%) var(--text-l, 14%) / <alpha-value>)',
          linen: 'hsl(var(--background-h, 40) var(--background-s, 33%) var(--background-l, 95%) / <alpha-value>)',
          oat: 'hsl(var(--surface-h, 40) var(--surface-s, 22%) var(--surface-l, 86%) / <alpha-value>)',
          moss: 'hsl(var(--secondary-h, 148) var(--secondary-s, 13%) var(--secondary-l, 38%) / <alpha-value>)',
          terra: 'hsl(var(--brand-h, 16) var(--brand-s, 46%) var(--brand-l, 43%) / <alpha-value>)',
          stone: 'rgb(var(--color-sage-stone, 143 141 136) / <alpha-value>)',
        },
      },

      // ======================
      // FONTS
      // ======================
      fontFamily: {
        display: ['var(--font-heading, "Playfair Display")', 'Georgia', 'serif'],
        body: ['var(--font-body, "Lato")', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        accent: ['var(--font-heading, "Crimson Text")', 'Georgia', 'serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'monospace'],
      },

      // ======================
      // BREAKPOINTS
      // ======================
      screens: {
        'ipad': '970px',      // iPad landscape
        'desktop': '1200px',  // Header nav switch point
        // Default TW: sm(640), md(768), lg(1024), xl(1280), 2xl(1536)
      },

      // ======================
      // ANIMATIONS
      // ======================
      transitionTimingFunction: {
        'expo-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'smooth': 'cubic-bezier(0.25, 1, 0.5, 1)',
      },

      // ======================
      // TYPOGRAPHY (Prose)
      // ======================
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-body': 'rgb(26 47 35 / 0.9)',
            '--tw-prose-headings': 'rgb(26 47 35)',
            '--tw-prose-links': 'hsl(var(--brand-h, 16) var(--brand-s, 46%) var(--brand-l, 43%))',
            '--tw-prose-bold': 'rgb(26 47 35)',
            '--tw-prose-quotes': 'rgb(26 47 35 / 0.9)',
            maxWidth: 'none',
          },
        },
      },
    },
  },

  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],

  // Safelist classes that are generated dynamically
  safelist: [
    'hero--gradient-primary',
    'hero--gradient-secondary',
    'hero--gradient-accent',
  ],
};
```

### Step 3.2: Understanding the Variable Pattern

The magic of SiteSettings integration is the HSL variable pattern:

```css
/* SiteSettings injects this via {% branding_css %}: */
:root {
  --brand-h: 16;      /* Hue (0-360) */
  --brand-s: 46%;     /* Saturation */
  --brand-l: 43%;     /* Lightness */
}

/* Tailwind config consumes it with fallbacks: */
primary: 'hsl(var(--brand-h, 16) var(--brand-s, 46%) var(--brand-l, 43%) / <alpha-value>)'
                         ↑ fallback if no SiteSettings configured
```

This means:
- Theme works standalone with sensible defaults
- SiteSettings overrides apply without CSS rebuild
- `<alpha-value>` enables opacity utilities (`bg-primary/50`)

---

## 5. Phase 4: Base Template & Branding Integration

### Step 4.1: Create base.html

```html
{# themes/theme_b/templates/theme/base.html #}
{% load static wagtailcore_tags wagtailimages_tags %}
{% load branding_tags analytics_tags meta_tags schema_tags %}

<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  {# Analytics (GTM head snippet) #}
  {% analytics_head %}

  {# SEO Meta Tags #}
  {% render_meta page %}
  {% render_og page %}
  {% render_schema page %}

  {# Get SiteSettings for branding #}
  {% get_site_settings as site_settings %}

  {# Favicon #}
  {% if site_settings.favicon %}
    {% image site_settings.favicon fill-32x32 as favicon_rendition %}
    <link rel="icon" href="{{ favicon_rendition.url }}" />
  {% endif %}

  {# ============================================ #}
  {# FONT LOADING ORDER (Critical!)              #}
  {# ============================================ #}

  {# 1. Default theme fonts (fallback) #}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Lato:wght@300;400;500;700&display=swap" rel="stylesheet" />

  {# 2. Client branding fonts (override) - loads AFTER defaults #}
  {% branding_fonts %}

  {# ============================================ #}
  {# CSS LOADING ORDER (Critical!)               #}
  {# ============================================ #}

  {# 1. Theme CSS (contains CSS variable defaults) #}
  <link rel="stylesheet" href="{% static 'theme_b/css/main.css' %}" />

  {# 2. Branding CSS variables (override) - MUST load AFTER main.css #}
  {% branding_css %}

  <title>{% block title %}{{ page.seo_title|default:page.title }}{% endblock %} | {{ site_settings.company_name|default:"Site Name" }}</title>
</head>

<body id="body" class="antialiased font-body text-sage-black bg-sage-linen selection:bg-primary selection:text-white">

  {# Skip link for accessibility #}
  <a href="#main" class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-primary focus:text-white focus:px-4 focus:py-2 focus:rounded">
    Skip to main content
  </a>

  {# Analytics body (GTM noscript) #}
  {% analytics_body %}

  {# Header - pass has_hero for transparent-at-top behavior #}
  {% include "theme/includes/header.html" with has_hero=page.has_hero_block %}

  {# Main Content #}
  <main id="main">
    {% block content %}{% endblock %}
  </main>

  {# Footer #}
  {% include "theme/includes/footer.html" %}

  {# Mobile Sticky CTA #}
  {% include "theme/includes/sticky_cta.html" %}

  {# JavaScript #}
  <script src="{% static 'sum_core/js/event_tracking.js' %}" defer></script>
  <script src="{% static 'sum_core/js/main.js' %}"></script>
  <script src="{% static 'sum_core/js/navigation.js' %}"></script>
  <script src="{% static 'theme_b/js/main.js' %}"></script>
</body>
</html>
```

### Step 4.2: Understanding Load Order

**Why order matters:**

1. **Fonts:** Default theme fonts load first, then `{% branding_fonts %}` adds client fonts. CSS `var(--font-heading)` picks up the client override.

2. **CSS:** `main.css` contains `:root` variable defaults. `{% branding_css %}` injects client overrides AFTER, so they win in the cascade.

```css
/* main.css sets defaults */
:root {
  --brand-h: 16;  /* Terra cotta default */
}

/* {% branding_css %} injects AFTER */
:root {
  --brand-h: 210;  /* Client's blue - WINS */
}
```

---

## 6. Phase 5: Component Classes (input.css)

### Step 5.1: Create input.css Structure

```css
/* themes/theme_b/static/theme_b/css/input.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ============================================
   SECTION 1: CSS VARIABLE DEFAULTS
   These are your theme's default colors.
   SiteSettings overrides these at runtime.
   ============================================ */

:root {
  /* RGB format for Tailwind's color-mix */
  --color-sage-black: 26 47 35;      /* #1A2F23 */
  --color-sage-linen: 247 245 241;   /* #F7F5F1 */
  --color-sage-oat: 227 222 212;     /* #E3DED4 */
  --color-sage-moss: 85 111 97;      /* #556F61 */
  --color-sage-terra: 160 86 59;     /* #A0563B */
  --color-sage-stone: 143 141 136;   /* #8F8D88 */

  /* HSL defaults (overridden by branding_css) */
  --brand-h: 16;
  --brand-s: 46%;
  --brand-l: 43%;

  --secondary-h: 148;
  --secondary-s: 13%;
  --secondary-l: 38%;
}

/* ============================================
   SECTION 2: BASE LAYER
   Global resets and default styling
   ============================================ */

@layer base {
  body {
    @apply bg-sage-linen text-sage-black;
  }

  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
  }
  ::-webkit-scrollbar-track {
    @apply bg-sage-linen;
  }
  ::-webkit-scrollbar-thumb {
    @apply bg-sage-oat rounded-full;
  }

  /* Focus indicators for accessibility */
  :focus-visible {
    @apply outline-none ring-2 ring-primary ring-offset-2;
  }

  /* Form validation states */
  input:invalid:not(:placeholder-shown),
  textarea:invalid:not(:placeholder-shown) {
    @apply border-red-500 bg-red-50;
  }
}

/* ============================================
   SECTION 3: COMPONENTS LAYER
   Semantic, reusable component classes
   ============================================ */

@layer components {

  /* ---------------------
     BUTTONS
     --------------------- */

  .btn {
    @apply inline-flex items-center justify-center gap-2;
    @apply px-6 py-3 rounded-full;
    @apply font-medium text-sm tracking-wide;
    @apply transition-all duration-300 ease-smooth;
    @apply focus-visible:ring-2 focus-visible:ring-offset-2;
  }

  .btn-primary {
    @apply btn;
    @apply bg-primary text-white;
    @apply hover:brightness-110 hover:shadow-lg hover:shadow-primary/25;
    @apply focus-visible:ring-primary;
  }

  .btn-secondary {
    @apply btn;
    @apply bg-secondary text-white;
    @apply hover:brightness-110;
    @apply focus-visible:ring-secondary;
  }

  .btn-outline {
    @apply btn;
    @apply bg-transparent border-2 border-sage-black text-sage-black;
    @apply hover:bg-sage-black hover:text-sage-linen;
    @apply focus-visible:ring-sage-black;
  }

  .btn-outline-inverse {
    @apply btn;
    @apply bg-transparent border-2 border-white/30 text-white;
    @apply hover:bg-white hover:text-sage-black;
    @apply focus-visible:ring-white;
  }

  .btn--link {
    @apply inline-flex items-center gap-2;
    @apply text-primary font-medium;
    @apply transition-colors duration-200;
    @apply hover:text-primary/80;
  }

  .btn--link svg {
    @apply w-4 h-4 transition-transform duration-200;
  }

  .btn--link:hover svg {
    @apply translate-x-1;
  }

  /* ---------------------
     SECTION LAYOUT
     --------------------- */

  .section {
    @apply py-16 md:py-24 lg:py-32;
  }

  .section--hero {
    @apply py-24 md:py-32 lg:py-48;
  }

  .section__header {
    @apply max-w-3xl mx-auto text-center mb-12 md:mb-16;
  }

  .section__heading {
    @apply font-display text-3xl md:text-4xl lg:text-5xl;
    @apply leading-tight mb-4;
  }

  .section__intro {
    @apply text-lg text-sage-black/70 leading-relaxed;
  }

  /* ---------------------
     HERO VARIANTS
     --------------------- */

  .hero--gradient {
    @apply relative overflow-hidden;
  }

  .hero--gradient-primary {
    background: radial-gradient(
      ellipse 80% 50% at 50% -20%,
      hsl(var(--brand-h) var(--brand-s) var(--brand-l) / 0.15),
      transparent
    );
  }

  .hero--gradient-secondary {
    background: radial-gradient(
      ellipse 80% 50% at 50% -20%,
      hsl(var(--secondary-h) var(--secondary-s) var(--secondary-l) / 0.15),
      transparent
    );
  }

  .hero--gradient-accent {
    background: radial-gradient(
      ellipse 80% 50% at 50% -20%,
      hsl(var(--accent-h) var(--accent-s) var(--accent-l) / 0.15),
      transparent
    );
  }

  /* ---------------------
     CARDS
     --------------------- */

  .card {
    @apply bg-white rounded-2xl overflow-hidden;
    @apply transition-all duration-300 ease-smooth;
  }

  .card:hover {
    @apply shadow-xl shadow-sage-black/5;
    @apply -translate-y-1;
  }

  .card__body {
    @apply p-6 md:p-8;
  }

  /* ---------------------
     REVEAL ANIMATIONS
     --------------------- */

  .reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
  }

  .reveal.active {
    opacity: 1;
    transform: translateY(0);
  }

  .delay-100 { transition-delay: 100ms; }
  .delay-200 { transition-delay: 200ms; }
  .delay-300 { transition-delay: 300ms; }
  .delay-400 { transition-delay: 400ms; }
  .delay-500 { transition-delay: 500ms; }

  /* ---------------------
     NAVIGATION
     --------------------- */

  .nav-link {
    @apply text-sm font-medium;
    @apply transition-colors duration-200;
    @apply hover:text-primary;
  }

  #main-header.scrolled {
    @apply bg-white/95 backdrop-blur-md shadow-sm;
  }

  /* ---------------------
     FOOTER
     --------------------- */

  .footer {
    @apply bg-sage-black text-sage-linen;
  }

  .footer__link {
    @apply text-sage-linen/70 hover:text-sage-linen;
    @apply transition-colors duration-200;
  }

  .footer__social-link {
    @apply w-10 h-10 rounded-full;
    @apply flex items-center justify-center;
    @apply bg-white/10 text-white;
    @apply transition-all duration-200;
    @apply hover:bg-primary hover:scale-110;
  }
}

/* ============================================
   SECTION 4: UTILITIES LAYER
   ============================================ */

@layer utilities {
  .sr-only {
    @apply absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0;
    clip: rect(0, 0, 0, 0);
  }

  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }

  .no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
}

/* ============================================
   REDUCED MOTION
   ============================================ */

@media (prefers-reduced-motion: reduce) {
  .reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }

  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Step 5.2: Button Naming Convention

Buttons follow a consistent pattern across SUM Platform:

| Class | Use Case | Appearance |
|-------|----------|------------|
| `.btn-primary` | Main CTA, form submits | Filled with brand color |
| `.btn-secondary` | Secondary actions | Filled with secondary color |
| `.btn-outline` | Tertiary actions (light bg) | Transparent with border |
| `.btn-outline-inverse` | Actions on dark/image bg | White border, white text |
| `.btn--link` | Inline text links with arrow | Text only, animated arrow |

---

## 7. Phase 6: Block Template Conversion

### Step 6.1: Understanding Block Template Resolution

Wagtail looks for block templates in this order:
1. `themes/theme_b/templates/sum_core/blocks/{block_name}.html` (theme override)
2. `core/sum_core/templates/sum_core/blocks/{block_name}.html` (core default)

**Always override in your theme** - this is how you apply your styling.

### Step 6.2: Converting a Wireframe Section to a Block Template

**Example: Converting a hero section from wireframe HTML**

**Before (wireframe HTML):**
```html
<section class="py-32 md:py-48 bg-gradient-to-b from-amber-50 to-transparent">
  <div class="max-w-7xl mx-auto px-6 text-center">
    <span class="inline-block px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm mb-8">
      Trusted by 500+ homeowners
    </span>
    <h1 class="text-5xl md:text-6xl lg:text-7xl font-serif mb-6">
      Transform Your <span class="text-amber-700">Outdoor Space</span>
    </h1>
    <p class="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
      Premium landscaping services that bring your vision to life.
    </p>
    <div class="flex flex-wrap justify-center gap-4">
      <a href="/contact" class="px-8 py-4 bg-amber-700 text-white rounded-full">
        Get Free Quote
      </a>
      <a href="/portfolio" class="px-8 py-4 border-2 border-gray-800 rounded-full">
        View Our Work
      </a>
    </div>
  </div>
</section>
```

**After (block template):**
```html
{# themes/theme_b/templates/sum_core/blocks/hero_gradient.html #}
{% load wagtailcore_tags %}

<section class="section--hero hero hero--gradient hero--gradient-{{ self.gradient_style|default:'primary' }}">
  <div class="max-w-7xl mx-auto px-6 text-center">

    {# Status Badge (optional) #}
    {% if self.status %}
      <span class="reveal inline-block px-4 py-2 bg-secondary/10 text-secondary rounded-full text-sm font-medium mb-8">
        {{ self.status }}
      </span>
    {% endif %}

    {# Headline #}
    <h1 class="reveal delay-100 font-display text-5xl md:text-6xl lg:text-7xl leading-tight mb-6">
      {{ self.headline|richtext }}
    </h1>

    {# Subheadline (optional) #}
    {% if self.subheadline %}
      <p class="reveal delay-200 text-xl text-sage-black/70 max-w-2xl mx-auto mb-10">
        {{ self.subheadline }}
      </p>
    {% endif %}

    {# CTAs #}
    {% if self.ctas %}
      <div class="reveal delay-300 flex flex-wrap justify-center gap-4">
        {% for cta in self.ctas %}
          <a href="{{ cta.value.link }}"
             class="btn {% if cta.value.style == 'primary' %}btn-primary{% elif cta.value.style == 'secondary' %}btn-secondary{% else %}btn-outline{% endif %}">
            {{ cta.value.label }}
            {% if cta.value.style == 'link' %}
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            {% endif %}
          </a>
        {% endfor %}
      </div>
    {% endif %}

  </div>
</section>
```

### Step 6.3: Key Conversion Patterns

| Wireframe Pattern | Theme Pattern |
|-------------------|---------------|
| Hardcoded colors (`bg-amber-700`) | Semantic colors (`bg-primary`) |
| Hardcoded text (`Trusted by 500+`) | Block field (`{{ self.status }}`) |
| Static content | Conditional rendering (`{% if self.field %}`) |
| No animations | Reveal classes (`.reveal.delay-100`) |
| Inline styles | Component classes (`.btn-primary`) |
| Fixed structure | Loop over block children (`{% for cta in self.ctas %}`) |

### Step 6.4: Common Block Templates to Create

Create these in `themes/theme_b/templates/sum_core/blocks/`:

| Block | Template | Key Features |
|-------|----------|--------------|
| Hero Gradient | `hero_gradient.html` | Gradient bg, status badge, CTAs |
| Hero Image | `hero_image.html` | Background image, overlay |
| Service Cards | `service_cards.html` | Grid, icons, hover effects |
| Stats | `stats.html` | Counter animation, grid |
| Testimonials | `testimonials.html` | Carousel or grid |
| Portfolio | `portfolio.html` | Filterable grid, lightbox |
| FAQ | `faq.html` | Accordion |
| Contact Form | `contact_form.html` | Form validation, submit |
| Gallery | `gallery.html` | Masonry or grid |
| CTA Banner | `cta_banner.html` | Full-width, prominent |

---

## 8. Phase 7: Navigation & Footer

### Step 7.1: Header Template

The header uses the `{% header_nav %}` template tag which provides:

```python
{
  'menu_items': [...],        # Nested menu with is_active states
  'show_phone': bool,
  'phone_number': str,
  'phone_href': str,          # tel: URI
  'header_cta': {
    'enabled': bool,
    'text': str,
    'href': str
  }
}
```

**Create header.html:**
```html
{# themes/theme_b/templates/theme/includes/header.html #}
{% load static navigation_tags %}
{% header_nav as nav %}

<header id="main-header"
        class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
        {% if has_hero %}data-transparent-at-top="true"{% endif %}>

  <div class="max-w-7xl mx-auto px-6">
    <div class="flex items-center justify-between h-20">

      {# Logo #}
      <a href="/" class="flex-shrink-0">
        {% get_site_settings as site_settings %}
        {% if site_settings.header_logo %}
          {% image site_settings.header_logo height-40 as logo %}
          <img src="{{ logo.url }}" alt="{{ site_settings.company_name }}" class="h-10" />
        {% else %}
          <span class="font-display text-xl font-bold">{{ site_settings.company_name }}</span>
        {% endif %}
      </a>

      {# Desktop Navigation #}
      <nav class="hidden desktop:flex items-center gap-8">
        {% for item in nav.menu_items %}
          <a href="{{ item.href }}"
             class="nav-link {% if item.is_active %}text-primary{% endif %}">
            {{ item.label }}
          </a>
        {% endfor %}
      </nav>

      {# CTA & Mobile Toggle #}
      <div class="flex items-center gap-4">
        {% if nav.header_cta.enabled %}
          <a href="{{ nav.header_cta.href }}" class="hidden md:inline-flex btn btn-primary">
            {{ nav.header_cta.text }}
          </a>
        {% endif %}

        <button id="mobile-menu-toggle"
                class="desktop:hidden p-2"
                aria-label="Toggle menu"
                aria-expanded="false">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

    </div>
  </div>

  {# Mobile Menu Panel #}
  <div id="mobile-menu" class="hidden desktop:hidden">
    {# Mobile menu content #}
  </div>

</header>
```

### Step 7.2: Footer Template

The footer uses `{% footer_nav %}`:

```python
{
  'tagline': str,
  'link_sections': [...],     # Title + links
  'social': { 'facebook': url, 'instagram': url, ... },
  'business': { 'company_name', 'phone_number', 'email', 'address' },
  'copyright': { 'raw': str, 'rendered': str }
}
```

**Create footer.html:**
```html
{# themes/theme_b/templates/theme/includes/footer.html #}
{% load static navigation_tags branding_tags %}
{% footer_nav as footer %}
{% get_site_settings as site_settings %}

<footer class="footer py-16 md:py-24">
  <div class="max-w-7xl mx-auto px-6">

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">

      {# Brand Column #}
      <div class="lg:col-span-1">
        {% if site_settings.footer_logo %}
          {% image site_settings.footer_logo height-48 as logo %}
          <img src="{{ logo.url }}" alt="{{ site_settings.company_name }}" class="h-12 mb-6" />
        {% else %}
          <span class="font-display text-2xl font-bold block mb-6">
            {{ site_settings.company_name }}
          </span>
        {% endif %}

        {% if footer.tagline %}
          <p class="text-sage-linen/70 mb-6">{{ footer.tagline }}</p>
        {% endif %}

        {# Social Links #}
        <div class="flex gap-3">
          {% if footer.social.facebook %}
            <a href="{{ footer.social.facebook }}" class="footer__social-link" aria-label="Facebook">
              <svg class="w-5 h-5"><!-- Facebook icon --></svg>
            </a>
          {% endif %}
          {# ... other social icons ... #}
        </div>
      </div>

      {# Link Sections #}
      {% for section in footer.link_sections %}
        <div>
          <h3 class="font-display text-lg font-semibold mb-4">{{ section.title }}</h3>
          <ul class="space-y-3">
            {% for link in section.links %}
              <li>
                <a href="{{ link.href }}" class="footer__link">{{ link.label }}</a>
              </li>
            {% endfor %}
          </ul>
        </div>
      {% endfor %}

    </div>

    {# Copyright #}
    <div class="border-t border-white/10 mt-12 pt-8 text-center text-sage-linen/50 text-sm">
      {{ footer.copyright.rendered }}
    </div>

  </div>
</footer>
```

### Step 7.3: Sticky CTA Template

```html
{# themes/theme_b/templates/theme/includes/sticky_cta.html #}
{% load navigation_tags %}
{% sticky_cta as cta %}

{% if cta.enabled %}
<div class="sticky-cta fixed bottom-4 right-4 z-40 flex items-center gap-2 md:hidden">

  {% if cta.phone_enabled %}
    <a href="{{ cta.phone_href }}"
       class="w-14 h-14 rounded-full bg-secondary text-white flex items-center justify-center shadow-lg"
       aria-label="Call us">
      <svg class="w-6 h-6"><!-- Phone icon --></svg>
    </a>
  {% endif %}

  {% if cta.button_enabled %}
    <a href="{{ cta.button_href }}"
       class="px-6 py-3 rounded-full bg-primary text-white font-medium shadow-lg">
      {{ cta.button_text }}
    </a>
  {% endif %}

</div>
{% endif %}
```

---

## 9. Phase 8: JavaScript Interactions

### Step 9.1: Create main.js

```javascript
// themes/theme_b/static/theme_b/js/main.js

/**
 * Theme B JavaScript
 *
 * Features:
 * - Header scroll effect
 * - Mobile menu
 * - Reveal animations
 * - FAQ accordion
 */

(function() {
  'use strict';

  // ============================================
  // HEADER SCROLL EFFECT
  // ============================================

  function initHeaderScroll() {
    const header = document.getElementById('main-header');
    if (!header) return;

    const isTransparentAtTop = header.dataset.transparentAtTop === 'true';

    function updateHeader() {
      const scrolled = window.scrollY > 50;
      header.classList.toggle('scrolled', scrolled);

      if (isTransparentAtTop) {
        header.classList.toggle('bg-transparent', !scrolled);
      }
    }

    window.addEventListener('scroll', updateHeader, { passive: true });
    updateHeader();
  }

  // ============================================
  // MOBILE MENU
  // ============================================

  function initMobileMenu() {
    const toggle = document.getElementById('mobile-menu-toggle');
    const menu = document.getElementById('mobile-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', () => {
      const isOpen = menu.classList.toggle('hidden');
      toggle.setAttribute('aria-expanded', !isOpen);
      document.body.classList.toggle('overflow-hidden', !isOpen);
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !menu.classList.contains('hidden')) {
        menu.classList.add('hidden');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('overflow-hidden');
      }
    });
  }

  // ============================================
  // REVEAL ANIMATIONS
  // ============================================

  function initRevealAnimations() {
    const reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    // Respect reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      reveals.forEach(el => el.classList.add('active'));
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    reveals.forEach(el => observer.observe(el));
  }

  // ============================================
  // FAQ ACCORDION
  // ============================================

  function initFaqAccordion() {
    const faqItems = document.querySelectorAll('[data-faq-item]');

    faqItems.forEach(item => {
      const button = item.querySelector('[data-faq-trigger]');
      const content = item.querySelector('[data-faq-content]');

      if (!button || !content) return;

      button.addEventListener('click', () => {
        const isOpen = button.getAttribute('aria-expanded') === 'true';

        // Close all others
        faqItems.forEach(other => {
          if (other !== item) {
            other.querySelector('[data-faq-trigger]')?.setAttribute('aria-expanded', 'false');
            other.querySelector('[data-faq-content]')?.style.setProperty('max-height', '0');
          }
        });

        // Toggle current
        button.setAttribute('aria-expanded', !isOpen);
        content.style.maxHeight = isOpen ? '0' : `${content.scrollHeight}px`;
      });
    });
  }

  // ============================================
  // INITIALIZE
  // ============================================

  document.addEventListener('DOMContentLoaded', () => {
    try { initHeaderScroll(); } catch (e) { console.error('Header scroll init failed:', e); }
    try { initMobileMenu(); } catch (e) { console.error('Mobile menu init failed:', e); }
    try { initRevealAnimations(); } catch (e) { console.error('Reveal animations init failed:', e); }
    try { initFaqAccordion(); } catch (e) { console.error('FAQ accordion init failed:', e); }
  });

})();
```

### Step 9.2: JavaScript Best Practices

1. **Error boundaries:** Wrap each feature in try/catch
2. **Passive listeners:** Use `{ passive: true }` for scroll events
3. **Reduced motion:** Check `prefers-reduced-motion` media query
4. **ARIA attributes:** Maintain accessibility state
5. **Keyboard support:** Handle Escape, Tab navigation
6. **Data attributes:** Use `data-*` for JS hooks, not classes

---

## 10. Phase 9: Build, Test & Polish

### Step 10.1: Build CSS

```bash
cd themes/theme_b/tailwind

# Development (with watch)
npm run dev

# Production build
npm run build

# Update fingerprint for cache busting
cd ..
python build_fingerprint.py
```

### Step 10.2: Package.json Scripts

Ensure your `package.json` has:

```json
{
  "scripts": {
    "dev": "npx tailwindcss -i ../static/theme_b/css/input.css -o ../static/theme_b/css/main.css --watch",
    "build": "npx tailwindcss -i ../static/theme_b/css/input.css -o ../static/theme_b/css/main.css --minify"
  }
}
```

### Step 10.3: Testing Checklist

**Visual:**
- [ ] Test with default colors (no SiteSettings configured)
- [ ] Test with SiteSettings color overrides
- [ ] Test with custom fonts
- [ ] Test all breakpoints (mobile, tablet, desktop)
- [ ] Test dark images with light text overlays
- [ ] Test long content (overflow handling)

**Functional:**
- [ ] Navigation links work
- [ ] Mobile menu opens/closes
- [ ] Header scroll effect works
- [ ] Reveal animations trigger
- [ ] FAQ accordion works
- [ ] Form validation works
- [ ] Skip link focuses main content

**Accessibility:**
- [ ] Keyboard navigation
- [ ] Screen reader testing
- [ ] Color contrast (4.5:1 minimum)
- [ ] Focus indicators visible
- [ ] ARIA labels present

**Performance:**
- [ ] CSS under 150KB (ideally under 100KB)
- [ ] No layout shift on load
- [ ] Images lazy loaded
- [ ] Fonts display swap

### Step 10.4: Final File Checklist

```
themes/theme_b/
├── theme.json                          ✓ Manifest
├── README.md                           ✓ Theme documentation
├── build_fingerprint.py                ✓ Cache busting
├── tailwind/
│   ├── package.json                    ✓ npm config
│   ├── npm-shrinkwrap.json             ✓ Locked deps
│   ├── tailwind.config.js              ✓ Theme config
│   └── postcss.config.js               ✓ PostCSS config
├── static/theme_b/
│   ├── css/
│   │   ├── input.css                   ✓ Tailwind source
│   │   ├── main.css                    ✓ Compiled output
│   │   └── .build_fingerprint          ✓ Cache hash
│   └── js/
│       └── main.js                     ✓ Theme JS
└── templates/
    ├── theme/
    │   ├── base.html                   ✓ Master template
    │   ├── home_page.html              ✓ Homepage
    │   ├── standard_page.html          ✓ Generic pages
    │   └── includes/
    │       ├── header.html             ✓ Navigation
    │       ├── footer.html             ✓ Footer
    │       └── sticky_cta.html         ✓ Mobile CTA
    └── sum_core/blocks/
        ├── hero_gradient.html          ✓ Hero blocks
        ├── hero_image.html             ✓
        ├── service_cards.html          ✓ Services
        ├── stats.html                  ✓ Stats strip
        ├── testimonials.html           ✓ Testimonials
        ├── portfolio.html              ✓ Portfolio grid
        ├── faq.html                    ✓ FAQ accordion
        ├── contact_form.html           ✓ Contact form
        ├── gallery.html                ✓ Image gallery
        └── cta_banner.html             ✓ CTA sections
```

---

## 12. Quick Reference

### Template Tags Cheat Sheet

```django
{# Load branding tags #}
{% load branding_tags %}

{# Get SiteSettings object #}
{% get_site_settings as site_settings %}

{# Inject CSS variables (in <head>, AFTER main.css) #}
{% branding_css %}

{# Inject Google Fonts (in <head>) #}
{% branding_fonts %}

{# Load navigation tags #}
{% load navigation_tags %}

{# Get header navigation #}
{% header_nav as nav %}

{# Get footer navigation #}
{% footer_nav as footer %}

{# Get sticky CTA config #}
{% sticky_cta as cta %}
```

### SiteSettings Fields Quick Reference

| Field | Access | Type |
|-------|--------|------|
| `primary_color` | `site_settings.primary_color` | Hex string |
| `secondary_color` | `site_settings.secondary_color` | Hex string |
| `heading_font` | `site_settings.heading_font` | Font name |
| `body_font` | `site_settings.body_font` | Font name |
| `company_name` | `site_settings.company_name` | String |
| `header_logo` | `site_settings.header_logo` | Wagtail Image |
| `footer_logo` | `site_settings.footer_logo` | Wagtail Image |
| `favicon` | `site_settings.favicon` | Wagtail Image |
| `phone_number` | `site_settings.phone_number` | String |
| `email` | `site_settings.email` | String |

### CSS Variable Quick Reference

```css
/* Brand colors (HSL components) */
--brand-h, --brand-s, --brand-l
--secondary-h, --secondary-s, --secondary-l
--accent-h, --accent-s, --accent-l

/* Semantic colors */
--background-h, --background-s, --background-l
--text-h, --text-s, --text-l
--surface-h, --surface-s, --surface-l

/* Typography */
--font-heading
--font-body
```

### Common Tailwind Classes

```css
/* Layout */
.max-w-7xl .mx-auto .px-6
.grid .grid-cols-1 .md:grid-cols-2 .lg:grid-cols-3 .gap-8

/* Typography */
.font-display .font-body
.text-sage-black .text-sage-black/70
.text-xl .md:text-2xl .lg:text-3xl

/* Colors (semantic) */
.bg-primary .text-primary
.bg-secondary .text-secondary
.bg-sage-linen .bg-sage-oat .bg-sage-black

/* Interactive */
.btn .btn-primary .btn-outline
.transition-all .duration-300 .ease-smooth

/* Animation */
.reveal .delay-100 .delay-200 .delay-300
```

---

## 11. Phase 10: Cookie Banner & Legal Page Templates (v0.6+)

### Cookie Banner Override

The cookie banner is included via `sum_core/includes/cookie_banner.html`. Themes can override styling but **must preserve the DOM contract** for the JS to function:

**Required DOM Elements:**

```html
{# Theme override: templates/sum_core/includes/cookie_banner.html #}
{% load branding_tags wagtailcore_tags %}
{% get_site_settings as site_settings %}

{% if site_settings.cookie_banner_enabled %}
  {# Container: MUST have .cookie-banner class #}
  <aside class="cookie-banner" aria-label="Cookie preferences" style="display: none;" aria-hidden="true">

    {# Content area - style as needed #}
    <div class="cookie-banner__content">
      <p>Your cookie message here...</p>
      {% if site_settings.privacy_policy_page %}
        <a href="{% pageurl site_settings.privacy_policy_page %}">Privacy Policy</a>
      {% endif %}
    </div>

    {# Buttons: MUST have data-cookie-consent attributes #}
    <div class="cookie-banner__actions">
      <button type="button" data-cookie-consent="accept">Accept</button>
      <button type="button" data-cookie-consent="reject">Reject</button>
    </div>

    {# Status: MUST have .cookie-banner__status and aria-live #}
    <p class="cookie-banner__status" aria-live="polite"></p>

  </aside>
{% endif %}
```

**Contract Checklist:**

| Element | Selector | Required |
|---------|----------|----------|
| Container | `.cookie-banner` | Yes |
| Accept button | `[data-cookie-consent="accept"]` | Yes |
| Reject button | `[data-cookie-consent="reject"]` | Yes |
| Status message | `.cookie-banner__status` with `aria-live="polite"` | Yes |
| Initial visibility | `style="display: none;"` | Yes |
| ARIA hidden | `aria-hidden="true"` | Yes |

**Footer "Manage Cookies" Link:**

The footer should include a link to re-open the banner:

```html
{% if site_settings.cookie_banner_enabled %}
  <a href="#" data-cookie-consent="manage">Manage cookies</a>
{% endif %}
```

### Legal Page Template

Legal pages use the `theme/legal_page.html` template. This is theme-owned and must render the `LegalPage` model fields.

**Template Structure:**

```html
{# themes/your_theme/templates/theme/legal_page.html #}
{% extends "theme/base.html" %}
{% load wagtailcore_tags %}

{% block content %}
  {# Hero/Header Section #}
  <section class="legal-header">
    <h1>{{ page.title }}</h1>
    {% if page.search_description %}
      <p>{{ page.search_description }}</p>
    {% endif %}
    {% if page.last_updated %}
      <time datetime="{{ page.last_updated|date:'Y-m-d' }}">
        Last updated: {{ page.last_updated|date:"F Y" }}
      </time>
    {% endif %}
    <button onclick="window.print()">Print Document</button>
  </section>

  {# Table of Contents (generated from sections) #}
  {% if page.sections %}
    <nav aria-label="Table of Contents">
      {% for section in page.sections %}
        <a href="#{{ section.value.anchor|slugify }}">
          {{ section.value.heading }}
        </a>
      {% endfor %}
    </nav>

    {# Section Content #}
    {% for section in page.sections %}
      <article id="{{ section.value.anchor|slugify }}" class="scroll-mt-24">
        <h2>{{ section.value.heading }}</h2>
        <div class="prose">
          {{ section.value.body|richtext }}
        </div>
      </article>
    {% endfor %}
  {% endif %}
{% endblock %}
```

**Legal Page Contract:**

| Field | Access | Purpose |
|-------|--------|---------|
| `page.title` | String | Page heading |
| `page.search_description` | String | Intro text |
| `page.last_updated` | Date | Last updated date |
| `page.sections` | StreamField | LegalSectionBlock list |
| `section.value.anchor` | String | Section ID for linking |
| `section.value.heading` | String | Section heading |
| `section.value.body` | RichText | Section content |

**Accessibility Requirements:**

- Section IDs must use `{{ section.value.anchor|slugify }}`
- ToC links must match section IDs
- Add `.scroll-mt-*` class for fixed header offset
- Include print button functionality
- Desktop: Sticky sidebar ToC recommended
- Mobile: Collapsible dropdown ToC recommended

**See Theme A Reference:**

Study `themes/theme_a/templates/theme/legal_page.html` for a complete implementation including:
- Breadcrumb navigation
- Desktop sticky sidebar ToC
- Mobile collapsible ToC with JS toggle
- Print-friendly styling
- Proper ARIA attributes

---

## Need Help?

- **Block fields reference:** See `docs/dev/design/blocks-reference.md`
- **CSS architecture:** See `docs/dev/design/css-architecture-and-tokens.md`
- **Design philosophy:** See `docs/dev/design/design_system.md`
- **Wiring inventory:** See `docs/dev/WIRING-INVENTORY.md`
- **Example theme:** Study `themes/theme_a/` as reference

---

*This guide is maintained alongside the SUM Platform codebase. Last updated: December 2024.*
