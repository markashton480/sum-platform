# SUM Platform Theme System - Comprehensive Repo Audit

**Date**: 2025-12-19  
**Investigator**: Claude (Opus 4.5)  
**Purpose**: Re-anchor the project after M6 theme migration. Provide a complete situational awareness baseline for planning a dedicated milestone to properly refit the theme system.

---

## Executive Summary

**Status: The theme system works, but the codebase is carrying legacy weight.**

The Tailwind migration (Theme A / Sage & Stone) is **functionally complete**:
- ✅ CLI copies themes correctly
- ✅ Template resolution works per spec
- ✅ Theme A has 20 Tailwind-styled block templates
- ✅ Compiled CSS is 68KB with all utilities

**However**, the codebase now carries two complete styling systems:
1. **Legacy CSS Token System** (M1/M2 era) - 25 CSS files, fully functional, used by core fallback templates
2. **Tailwind Theme System** (M6/Theme A) - Complete and working in `themes/theme_a/`

This isn't broken, but it's inefficient. A new milestone could:
- Either migrate core fallbacks to minimal/unstyled templates
- Or deprecate/remove the legacy CSS system entirely

---

## 1. What's Where - Directory Map

### Theme A (Tailwind) - The New System

```
core/sum_core/themes/theme_a/
├── theme.json                           # Theme manifest
├── package.json                         # NPM deps (tailwind, typography)
├── tailwind.config.js                   # Content paths + sage palette
├── postcss.config.js
├── templates/
│   ├── theme/                           # Page layouts
│   │   ├── base.html                    # Tailwind base template
│   │   ├── home_page.html
│   │   ├── standard_page.html
│   │   ├── service_page.html
│   │   ├── service_index_page.html
│   │   └── includes/
│   │       ├── header.html
│   │       ├── footer.html
│   │       └── sticky_cta.html
│   └── sum_core/blocks/                 # ✅ BLOCK OVERRIDES (20 files)
│       ├── hero_gradient.html           # Tailwind classes
│       ├── hero_image.html
│       ├── service_cards.html
│       ├── testimonials.html
│       ├── stats.html
│       ├── faq.html
│       ├── gallery.html
│       ├── portfolio.html
│       ├── process_steps.html
│       ├── trust_strip_logos.html
│       ├── contact_form.html
│       ├── quote_request_form.html
│       ├── rich_text.html
│       ├── content_richtext.html
│       ├── content_image.html
│       ├── content_quote.html
│       ├── content_buttons.html
│       ├── content_editorial_header.html
│       ├── content_spacer.html
│       └── content_divider.html
└── static/theme_a/
    ├── css/
    │   ├── input.css                    # Tailwind source
    │   └── main.css                     # Compiled (68KB)
    └── js/
        └── main.js
```

### Legacy CSS Token System (M1/M2 Era)

```
core/sum_core/static/sum_core/css/
├── main.css                             # Entry point (imports all)
├── tokens.css                           # HSL-based design tokens
├── reset.css                            # CSS reset
├── typography.css                       # Font stacks, scale
├── layout.css                           # Container, grid
├── utilities.css                        # Spacing, colors, display
└── components.*.css                     # 17 component files:
    ├── components.buttons.css
    ├── components.cards.css
    ├── components.comparison.css
    ├── components.content.css
    ├── components.faq.css
    ├── components.features.css
    ├── components.footer.css
    ├── components.forms.css
    ├── components.gallery.css
    ├── components.header.css
    ├── components.hero.css
    ├── components.mobile-fab.css
    ├── components.portfolio.css
    ├── components.process.css
    ├── components.services.css
    ├── components.stats.css
    ├── components.sticky-cta.css
    ├── components.testimonials.css
    └── components.trust-strip.css
```

### Core Fallback Templates (Still Use Legacy CSS)

```
core/sum_core/templates/
├── theme/                               # Fallback page templates
│   ├── base.html                        # Loads sum_core/css/main.css
│   ├── home_page.html
│   ├── standard_page.html
│   ├── service_page.html
│   ├── service_index_page.html
│   └── includes/
│       ├── header.html
│       ├── footer.html
│       └── sticky_cta.html
└── sum_core/blocks/                     # 21 fallback block templates
    ├── hero_gradient.html               # Uses legacy CSS classes
    ├── hero_image.html
    ├── service_cards.html
    ├── testimonials.html
    ├── stats.html
    ├── faq.html
    ├── gallery.html
    ├── portfolio.html
    ├── process_steps.html
    ├── trust_strip.html                 # ⚠️ Missing from Theme A
    ├── trust_strip_logos.html
    ├── contact_form.html
    ├── quote_request_form.html
    ├── rich_text.html
    ├── content_richtext.html
    ├── content_image.html
    ├── content_quote.html
    ├── content_buttons.html
    ├── content_editorial_header.html
    ├── content_spacer.html
    └── content_divider.html
```

---

## 2. What's Been Done - Work History

### M1: CSS Token System (Complete, Now Legacy)

**Task Tickets**: M1-001 through M1-007

Built the HSL-based design token system:
- Defined spacing scale (xs through 3xl)
- Color system with `--brand-h/s/l` for client overrides
- Typography scale with `--fs-*` custom properties
- Shadow, radius, easing tokens

**Documentation**: `docs/dev/design/css-architecture-and-tokens.md`

### M2: Block Infrastructure (Complete, Now Legacy)

**Task Tickets**: M2-001 through M2-012

Built all StreamField blocks consuming the token system:
- Hero blocks (image, gradient)
- Service cards, testimonials, stats
- Process steps, FAQ, gallery, portfolio
- Content blocks (richtext, image, quote, buttons)
- Form blocks (contact, quote request)
- Trust strip, divider, spacer

**All templates written for CSS token system classes.**

### M6: Theme A Migration (Complete)

**Task Tickets**: M6-A-001 through M6-A-003, plus CMs

Created Theme A (Sage & Stone):
- Translated static wireframe to Django templates
- Built Tailwind config with `sage-*` color palette
- Created 20 block template overrides
- Fixed content paths in tailwind.config.js
- Added @tailwindcss/typography plugin
- Rebuilt CSS to 68KB

**Key Documentation**:
- `docs/dev/master-docs/THEME-ARCHITECTURE-SPECv1.md`
- `docs/dev/THEME/UNFUCK-THEME-MISSION.md` ← Comprehensive task list
- `docs/dev/THEME/BLOCK-MIGRATION-CHECKLIST.md`
- `docs/dev/THEME/PRE-SUM-INIT-CHECKLIST.md`

### Corrective Missions

The M6 work spawned several CMs due to the complexity of the migration:

- **CM-M6-01 through CM-M6-05**: Various fixes during theme work
- **CM-M6-A-004**: Follow-up corrections

The final state is documented in `UNFUCK-THEME-MISSION.md` as **✅ COMPLETED**.

---

## 3. What's Looking Weird

### 3.1 Dual Styling Systems (Not Broken, Just Wasteful)

The project now has two complete CSS systems:

| System | Location | Size | Used By |
|--------|----------|------|---------|
| Legacy CSS Tokens | `sum_core/static/sum_core/css/` | ~25 files | Core fallback templates |
| Tailwind (Theme A) | `themes/theme_a/static/theme_a/css/` | 68KB compiled | Theme A templates |

**Impact**: If all clients use Theme A, the legacy CSS is dead weight. But removing it would break core fallback rendering.

### 3.2 Missing Theme A Template

**File**: `trust_strip.html`

Core has 21 block templates, Theme A has 20. The `trust_strip.html` template exists in core but not in Theme A.

**Quick Fix**: Copy and convert `trust_strip.html` to Tailwind.

### 3.3 Hardcoded Sage & Stone Branding

Theme A templates contain Sage & Stone demo content:
- Font families: Playfair Display, Lato, Crimson Text
- Color palette: `sage-black`, `sage-linen`, `sage-moss`, `sage-terra`
- "Est. YYYY" pattern in header (referencing non-existent `established_year` field)

**Impact**: Theme A is really "Sage & Stone Theme" not a generic "Theme A". Other themes (B, C, D) would need their own branding.

### 3.4 Non-Existent Model Field Referenced

In [theme/includes/header.html](core/sum_core/themes/theme_a/templates/theme/includes/header.html):

```django
Est. {{ site_settings.established_year|default:"2025" }}
```

**Problem**: `SiteSettings` has no `established_year` field. Always shows "Est. 2025".

**Fix Options**:
1. Add `established_year` to `SiteSettings`
2. Remove the "Est." line from header (it's demo branding)

### 3.5 Block Python Meta Still Uses Core Paths

All block classes in `core/sum_core/blocks/*.py` have:

```python
class Meta:
    template = "sum_core/blocks/hero_gradient.html"
```

**This is actually fine** because Django template resolution finds Theme A's override first (via `theme/active/templates/sum_core/blocks/`). But it's confusing when reading the code.

---

## 4. Legacy CSS Token System Status

### Is It Still Active?

**Yes, for core fallback templates.**

The core fallback `base.html` at `core/sum_core/templates/theme/base.html` loads:

```html
<link rel="stylesheet" href="{% static 'sum_core/css/main.css' %}">
```

**If a client doesn't use a theme**, or if Theme A's template resolution fails, the site falls back to:
1. Core page templates (which load legacy CSS)
2. Core block templates (which use legacy CSS classes)

### Token System Architecture

Defined in `docs/dev/design/css-architecture-and-tokens.md`:

```css
/* From tokens.css */
:root {
    --brand-h: 211;
    --brand-s: 25%;
    --brand-l: 35%;
    
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    --spacing-3xl: 4rem;
    
    /* Typography scale */
    --fs-xs: clamp(0.75rem, 2vw, 0.875rem);
    --fs-sm: clamp(0.875rem, 2vw, 1rem);
    --fs-md: clamp(1rem, 2vw, 1.125rem);
    /* ... etc */
}
```

**Client Overrides**: The `{% branding_css %}` template tag injects custom values for `--brand-h/s/l` from `SiteSettings`.

### Should We Remove It?

**Options**:

1. **Keep as fallback** (current state): Safe, but wasteful if Theme A is always used.

2. **Convert core fallbacks to unstyled**: Make `sum_core/templates/sum_core/blocks/` minimal semantic HTML. Clients MUST use a theme.

3. **Remove entirely**: Delete legacy CSS, keep only themed rendering. Risky if anyone depends on core fallback styling.

**Recommendation**: Keep for now, revisit when you have themes B/C/D and can be confident all clients will use a theme.

---

## 5. Block Conversion Status

### Blocks With Theme A Overrides (20/21)

| Block | Core Template | Theme A Template | Status |
|-------|---------------|------------------|--------|
| HeroGradientBlock | ✅ | ✅ | Converted |
| HeroImageBlock | ✅ | ✅ | Converted |
| ServiceCardsBlock | ✅ | ✅ | Converted |
| TestimonialsBlock | ✅ | ✅ | Converted |
| StatsBlock | ✅ | ✅ | Converted |
| FAQBlock | ✅ | ✅ | Converted |
| GalleryBlock | ✅ | ✅ | Converted |
| PortfolioBlock | ✅ | ✅ | Converted |
| ProcessStepsBlock | ✅ | ✅ | Converted |
| TrustStripLogosBlock | ✅ | ✅ | Converted |
| ContactFormBlock | ✅ | ✅ | Converted |
| QuoteRequestFormBlock | ✅ | ✅ | Converted |
| RichTextBlock | ✅ | ✅ | Converted |
| ContentRichTextBlock | ✅ | ✅ | Converted |
| ContentImageBlock | ✅ | ✅ | Converted |
| ContentQuoteBlock | ✅ | ✅ | Converted |
| ContentButtonsBlock | ✅ | ✅ | Converted |
| ContentEditorialHeaderBlock | ✅ | ✅ | Converted |
| ContentSpacerBlock | ✅ | ✅ | Converted |
| ContentDividerBlock | ✅ | ✅ | Converted |
| **TrustStripBlock** | ✅ | ❌ | **MISSING** |

### Blocks Without Templates (May Be Deprecated)

Per `BLOCK-MIGRATION-CHECKLIST.md`, these are referenced in code but have no templates:
- `button.html`
- `hero.html` (generic - we use hero_gradient/hero_image)
- `features_list.html`
- `comparison.html`

**Action**: Verify if these blocks are actually used. If not, consider removing them.

---

## 6. Related Documentation

### Architecture & Specs

| Document | Location | Purpose |
|----------|----------|---------|
| THEME-ARCHITECTURE-SPECv1 | `docs/dev/master-docs/` | The contract for theme system |
| CSS Architecture | `docs/dev/design/css-architecture-and-tokens.md` | Legacy token system design |
| Design System | `docs/dev/design/design_system.md` | Visual design decisions |

### Theme Work Tracking

| Document | Location | Purpose |
|----------|----------|---------|
| UNFUCK-THEME-MISSION | `docs/dev/THEME/` | Complete task list (marked DONE) |
| BLOCK-MIGRATION-CHECKLIST | `docs/dev/THEME/` | Block-by-block status |
| PRE-SUM-INIT-CHECKLIST | `docs/dev/THEME/` | Verification before CLI usage |
| FUCKED-THEME | `docs/dev/reports/` | Original diagnosis report |

### Milestone Documentation

| Milestone | Location | Relevance |
|-----------|----------|-----------|
| M1 | `docs/dev/M1/` | CSS token system (now legacy) |
| M2 | `docs/dev/M2/` | Block infrastructure |
| M6 | `docs/dev/M6/` | VPS deployment (unrelated to themes!) |
| M6-A | `docs/dev/M6/M6-A-*` | Theme A work tickets |

---

## 7. Recommendations for Next Milestone

### 7.1 Quick Fixes (Can Do Immediately)

1. **Create `trust_strip.html` for Theme A**
   - Copy core version, convert to Tailwind
   - Location: `themes/theme_a/templates/sum_core/blocks/trust_strip.html`

2. **Fix `established_year` issue**
   - Either add field to `SiteSettings` (with migration)
   - Or remove the "Est. YYYY" line from Theme A header

3. **Rename Theme A properly**
   - Current: "theme_a" with "Sage & Stone" branding baked in
   - Consider: "sage_stone" as the slug, or strip demo branding to make it generic

### 7.2 Milestone Work (Requires Planning)

**Option A: Keep Dual Systems**
- Accept that core fallbacks exist for safety
- Focus on creating themes B, C, D
- Legacy CSS becomes "emergency fallback only"

**Option B: Migrate Core to Minimal HTML**
- Rewrite core block templates as semantic HTML only (no styling)
- Core becomes "unstyled fallback" that forces theme usage
- Remove legacy CSS after confirming no clients depend on it

**Option C: Create Theme Base Class**
- Extract common patterns from Theme A
- Create base components that themes inherit
- Reduces duplication across future themes

### 7.3 Suggested Milestone Structure

If creating a dedicated milestone (e.g., M7 or M-THEME):

| Task | Type | Priority | Est. Time |
|------|------|----------|-----------|
| Add `trust_strip.html` to Theme A | Bug fix | HIGH | 30m |
| Fix/remove `established_year` | Bug fix | HIGH | 15m |
| Audit unused blocks | Cleanup | MEDIUM | 1h |
| Document Theme A customization | Docs | MEDIUM | 2h |
| Create Theme B skeleton | Feature | LOW | 4h |
| Create theme base class | Refactor | LOW | 4h |
| Deprecate legacy CSS (decision) | Planning | LOW | 1h |

---

## 8. Summary

**The theme system is working.** Theme A is complete with 20 block templates, proper Tailwind config, and 68KB compiled CSS. The CLI copies themes correctly, template resolution works per spec.

**The legacy CSS token system is still present** and functional as a fallback. It's not actively broken, but it's dead weight if all clients use Theme A.

**Minor gaps remain**:
- Missing `trust_strip.html` in Theme A
- `established_year` field doesn't exist but is referenced
- Some blocks may be deprecated (no templates)

**The M1+M2 approach with Tailwind** is essentially what Theme A already is - you just need to:
1. Recognize Theme A as "complete but demo-branded"
2. Decide whether to genericize it or accept it as "Sage & Stone specific"
3. Plan for themes B, C, D if needed

The cognitive load is high because you have two styling systems, but they're not fighting each other - they're just redundant.
