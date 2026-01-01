# Theme A CSS & Layout Audit Report

**Date**: 2026-01-01
**Auditor**: Claude (Opus 4.5)
**Scope**: Theme A (Sage & Stone) - CSS, Layout, Responsive, Accessibility
**Reference**: Issue #292, Issue #463
**Live Site**: https://sage-and-stone.lintel.site
**Wireframe**: `docs/dev/design/wireframes/sage-and-stone/compiled/`

---

## Executive Summary

This audit reviews all Theme A CSS and layout issues to provide a comprehensive fix plan. Issues are categorized by severity (P0-Critical, P1-High, P2-Medium, P3-Low) and type (Layout, Accessibility, Responsive, Typography, Missing Features).

**Total Issues Found**: 28

| Severity | Count | Description |
|----------|-------|-------------|
| P0 - Critical | 3 | Accessibility violations, broken functionality |
| P1 - High | 10 | Block violations, missing blocks, major UX issues |
| P2 - Medium | 9 | Visual discrepancies, template mismatches |
| P3 - Low | 6 | Minor polish, nice-to-haves |

**Key Categories**:
- Block Usage Violations: 4 issues (blocks used incorrectly vs wireframe)
- Missing Wagtail Blocks: 3 issues (blocks/templates not created)
- CSS/Layout Issues: 22 issues (styling, accessibility, responsive)

---

## Block Usage Violations

The live site uses blocks in ways that **do not match the wireframe**. This creates visual inconsistency and content duplication.

### Wireframe Home Page Block Structure

The wireframe (`index.html`) defines this exact block sequence:

| Order | Section | Block Type | Count |
|-------|---------|------------|-------|
| 1 | Hero | HeroImageBlock | 1 |
| 2 | Operational Proof Strip | StatsBlock | 1 |
| 3 | Manifesto | ManifestoBlock | 1 |
| 4 | Services | ServiceCardsBlock | 1 |
| 5 | Provenance | ProvenancePlateBlock (missing) | 1 |
| 6 | Portfolio | PortfolioBlock | 1 |
| 7 | Featured Story | FeaturedCaseStudyBlock | 1 |
| 8 | FAQ | FAQBlock | 1 |
| 9 | Contact | ContactFormBlock | 1 |

### Violation #1: StatsBlock Used Multiple Times (P1)

**Wireframe**: ONE stats strip ("Operational Proof Strip") with 4 items:
- Capacity: 12 Commissions/Year
- Timeline: 12-16 Week Build
- Origin: Workshop: Herefordshire
- Promise: Lifetime Joinery Guarantee

**Live Site**: Appears to have TWO stats sections:
1. Stats strip after hero (correct)
2. "247 Kitchens completed" social proof (NOT in wireframe)

**Issue**: StatsBlock being used twice when wireframe only has one.

**Fix**: Remove the second stats block OR convert to a different block type that matches wireframe intent.

---

### Violation #2: TestimonialsBlock on Home Page (P1)

**Wireframe**: NO dedicated testimonials block on home page. The only quote appears INSIDE the Featured Case Study section ("Sage & Stone didn't just build a kitchen...").

**Live Site**: Appears to have a separate "Testimonial" section with "Sarah M."

**Issue**: TestimonialsBlock being used on home page when wireframe doesn't include it. The wireframe integrates testimonial content into the FeaturedCaseStudyBlock.

**Fix**: Remove TestimonialsBlock from home page. Testimonial-style quote should be part of FeaturedCaseStudyBlock only.

---

### Violation #3: FeaturedCaseStudyBlock Template Mismatch (P1)

**Wireframe Structure** (`index.html` lines 593-651):
```
- Quote icon (SVG)
- Large blockquote: "Sage & Stone didn't just build a kitchen..."
- Challenge section (border-left, terra accent)
- Outcome section (border-left, terra accent)
- Client attribution: "Eleanor & James, Haslemere, UK"
- "View Full Case Study" CTA
```

**Current Template** (`featured_case_study.html`):
```
- Stats card overlay (stats_label, stats_value)
- Eyebrow text
- Heading (richtext)
- Intro (richtext)
- Points list (ordered list)
- CTA link
```

**Missing Elements**:
- Large blockquote quote
- Challenge/Outcome structure with border-left styling
- Quote icon SVG
- Client name with location (cite element)

**Current Template Has Elements NOT in Wireframe**:
- Stats card overlay
- Points list (ordered list)

**Fix**: Redesign FeaturedCaseStudyBlock to match wireframe. Add:
- `quote` (TextBlock)
- `challenge` (TextBlock)
- `outcome` (TextBlock)
- `client_name` (CharBlock)
- `client_location` (CharBlock)

---

### Violation #4: SocialProofQuoteBlock Placement (P2)

**Wireframe**: No standalone quote block on home page.

**Current Template**: `content_social_proof_quote.html` renders a prominent quote with author/company/logo.

**Issue**: If this block is used on home page, it duplicates content that should be in FeaturedCaseStudyBlock.

**Fix**: Reserve SocialProofQuoteBlock for inner pages only (Services, About).

---

### Block Placement Rules (Derived from Wireframe)

| Block | Home Page | Services | About | Portfolio |
|-------|-----------|----------|-------|-----------|
| HeroImageBlock | ✅ 1x | ✅ 1x | ✅ 1x | ✅ 1x |
| StatsBlock | ✅ 1x | ✅ 1x | ❌ | ❌ |
| ManifestoBlock | ✅ 1x | ❌ | ❌ | ❌ |
| ServiceCardsBlock | ✅ 1x | ✅ detailed | ❌ | ❌ |
| ProvenancePlateBlock | ✅ 1x | ❌ | ❌ | ❌ |
| PortfolioBlock | ✅ 1x | ❌ | ❌ | ✅ full list |
| FeaturedCaseStudyBlock | ✅ 1x | ❌ | ❌ | ❌ |
| TestimonialsBlock | ❌ | ❌ | ❌ | ❌ |
| FAQBlock | ✅ 1x | ✅ 1x | ❌ | ❌ |
| ContactFormBlock | ✅ 1x | ✅ 1x | ✅ 1x | ❌ |
| SocialProofQuoteBlock | ❌ | ✅ | ✅ | ❌ |
| ProcessStepsBlock | ❌ | ✅ 1x | ❌ | ❌ |
| TeamMembersBlock | ❌ | ❌ | ✅ 1x | ❌ |

---

## Missing Wagtail Blocks

The following wireframe sections have no corresponding core block definitions or theme templates:

### Block #1: Provenance Block (P1 - High)

**Wireframe Location**: `index.html` lines 465-524 (`id="provenance"`)
**Description**: "The Provenance Plate" - A signature experience section showing:
- Interactive brass plate graphic with maker info
- GPS coordinates of timber source
- Completion date
- Modal popup with detailed artifact dossier

**Current State**:
- No core block definition exists
- No theme template exists
- Wireframe uses inline HTML with hardcoded demo data

**Required Implementation**:
1. Create `ProvenancePlateBlock` in `core/sum_core/blocks/`
2. Fields needed:
   - `eyebrow` (CharBlock)
   - `heading` (CharBlock)
   - `intro` (RichTextBlock)
   - `maker_name` (CharBlock)
   - `source_location` (CharBlock)
   - `source_coordinates` (CharBlock)
   - `completion_date` (DateBlock)
   - `modal_details` (StructBlock with additional fields)
3. Create theme template at `themes/theme_a/templates/sum_core/blocks/provenance_plate.html`

**Priority**: P1 (Signature differentiator for Sage & Stone brand)

---

### Block #2: Feature Comparison Block (P2 - Medium)

**Wireframe Implication**: Referenced in core blocks (`ComparisonBlock`) but no theme template.

**Current State**:
- Core block exists: `ComparisonBlock` in `core/sum_core/blocks/content.py`
- Theme template missing: No `comparison.html` in Theme A templates

**Required Implementation**:
1. Create `themes/theme_a/templates/sum_core/blocks/comparison.html`
2. Style to match Sage & Stone aesthetic

**Priority**: P2 (Core block exists but theme template missing)

---

### Block Coverage Analysis

| Core Block | Theme Template | Status |
|------------|---------------|--------|
| `HeroImageBlock` | `hero_image.html` | ✅ Present |
| `HeroGradientBlock` | `hero_gradient.html` | ✅ Present |
| `ManifestoBlock` | `manifesto.html` | ✅ Present |
| `ServiceCardsBlock` | `service_cards.html` | ✅ Present |
| `ServiceDetailBlock` | `service_detail.html` | ✅ Present |
| `PortfolioBlock` | `portfolio.html` | ✅ Present |
| `FeaturedCaseStudyBlock` | `featured_case_study.html` | ✅ Present |
| `TestimonialsBlock` | `testimonials.html` | ✅ Present |
| `FAQBlock` | `faq.html` | ✅ Present |
| `ProcessStepsBlock` | `process_steps.html` | ✅ Present |
| `StatsBlock` | `stats.html` | ✅ Present |
| `ContactFormBlock` | `contact_form.html` | ✅ Present |
| `DynamicFormBlock` | `dynamic_form_block.html` | ✅ Present |
| `GalleryBlock` | `gallery.html` | ✅ Present |
| `TimelineBlock` | `timeline.html` | ✅ Present |
| `TrustStripBlock` | `trust_strip_logos.html` | ✅ Present |
| `QuoteBlock` | `content_quote.html` | ✅ Present |
| `SocialProofQuoteBlock` | `content_social_proof_quote.html` | ✅ Present |
| `RichTextContentBlock` | `content_richtext.html` | ✅ Present |
| `ImageBlock` | `content_image.html` | ✅ Present |
| `ButtonGroupBlock` | `content_buttons.html` | ✅ Present |
| `SpacerBlock` | `content_spacer.html` | ✅ Present |
| `DividerBlock` | `content_divider.html` | ✅ Present |
| `PageHeaderBlock` | `page_header.html` | ✅ Present |
| `EditorialHeaderBlock` | `content_editorial_header.html` | ✅ Present |
| `TableOfContentsBlock` | `table_of_contents.html` | ✅ Present |
| `LegalSectionBlock` | `legal_section.html` | ✅ Present |
| `ComparisonBlock` | ❌ Missing | ⚠️ Need template |
| `FeaturesListBlock` | ❌ Missing | ⚠️ Need template |
| N/A (Provenance) | N/A | ❌ Block + template needed |

---

## P0 - Critical Issues (Must Fix Before Production)

### Issue #1: Form Input Placeholder Contrast Insufficient (WCAG Violation)

**Type**: Accessibility
**File**: `themes/theme_a/templates/sum_core/blocks/contact_form.html`
**Description**: Form input floating labels use `text-sage-linen/40` and `text-sage-linen/50` which fails WCAG 2.1 contrast requirements against the dark `bg-sage-black` background.

**Current Classes**:
```html
class="... text-sage-linen/40 ..."
class="... peer-placeholder-shown:text-sage-linen/50 ..."
```

**Contrast Check**:
- Background: `#1A2F23` (sage-black)
- Label color at 40% opacity: Fails 4.5:1 minimum
- Label color at 50% opacity: Fails 4.5:1 minimum

**Fix**: Increase opacity to 60% or higher:
```html
class="... text-sage-linen/60 ..."
class="... peer-placeholder-shown:text-sage-linen/70 ..."
```

**Severity**: P0 (WCAG compliance)

---

### Issue #2: Form Action URL Hardcoded

**Type**: Layout/Functionality
**File**: `themes/theme_a/templates/sum_core/blocks/contact_form.html`
**Line**: 27

**Current**:
```html
<form action="/forms/submit/" method="post" ...>
```

**Problem**: Hardcoded URL will break if URL patterns change or if site is mounted at a subpath.

**Fix**: Use Django template tag:
```html
<form action="{% url 'sum_core:form_submit' %}" method="post" ...>
```

**Severity**: P0 (Potential broken functionality)

---

### Issue #3: Hero Parallax Effect Not Activating

**Type**: Layout/Functionality
**File**: `themes/theme_a/templates/sum_core/blocks/hero_image.html`
**Related**: `themes/theme_a/static/theme_a/js/main.js` (lines 387-399)

**Description**: The JavaScript parallax effect looks for an element with `id="hero-image"`:
```javascript
const heroImage = document.getElementById('hero-image');
if (heroImage) {
    window.addEventListener('scroll', () => {
        const scrollPosition = window.pageYOffset;
        if (scrollPosition < 1200) {
            heroImage.style.transform = `translateY(${scrollPosition * 0.4}px)`;
        }
    }, { passive: true });
}
```

**Problem**: The `hero_image.html` template does NOT include `id="hero-image"` on the img element.

**Current** (line 9):
```html
<img src="{{ hero_img.url }}"
     alt="{{ self.image_alt }}"
     class="w-full h-[120%] object-cover object-center -translate-y-10" />
```

**Wireframe has**:
```html
<img id="hero-image" src="images/euBmypOZUZA.jpg" ...>
```

**Fix**: Add the ID:
```html
<img id="hero-image" src="{{ hero_img.url }}"
     alt="{{ self.image_alt }}"
     class="w-full h-[120%] object-cover object-center -translate-y-10" />
```

**Severity**: P0 (Core feature not working)

---

## P1 - High Priority Issues

### Issue #4: Mega Menu Missing Wireframe 3-Column Layout

**Type**: Layout
**File**: `themes/theme_a/templates/theme/includes/header.html`
**Lines**: 63-81

**Description**: Wireframe shows a rich 3-column mega menu layout:
- Column 1: Main categories (3 spans)
- Column 2: Sub-categories in 2 columns (5 spans)
- Column 3: Featured image with CTA (4 spans)

**Current Implementation**: Simple single-column grid with basic links.

**Wireframe Reference** (`index.html` lines 138-183):
```html
<div class="bg-sage-linen shadow-2xl border-t border-sage-black/10 mx-6 grid grid-cols-12 overflow-hidden rounded-sm">
    <!-- Col 1: Main Categories -->
    <div class="col-span-3 bg-sage-oat/30 p-8 border-r border-sage-black/5">
        ...
    </div>
    <!-- Col 2: Sub & Sub-Sub Categories -->
    <div class="col-span-5 p-8">
        ...
    </div>
    <!-- Col 3: Visual Feature -->
    <div class="col-span-4 relative bg-sage-black overflow-hidden group/image">
        ...
    </div>
</div>
```

**Fix**: Update mega menu template to match wireframe structure with configurable featured image.

**Severity**: P1 (Major UX gap)

---

### Issue #5: Mobile Menu Missing Focus Trap

**Type**: Accessibility
**File**: `themes/theme_a/static/theme_a/js/main.js`
**Lines**: 182-303 (Mobile Menu System section)

**Description**: When mobile menu is open, keyboard tab navigation can escape to background page content. WCAG requires focus trap for modal overlays.

**Current**: `openMenu()` function (lines 230-241) does not implement focus trap.

**Required Implementation**:
1. Query focusable elements within `#mobile-menu`
2. Get first and last focusable elements
3. On Tab from last element: focus first element
4. On Shift+Tab from first element: focus last element
5. Cleanup listeners on `closeMenu()`

**Severity**: P1 (WCAG 2.1 requirement for modal dialogs)

---

### Issue #6: Print Styles Missing

**Type**: Layout
**File**: `themes/theme_a/static/theme_a/css/input.css`

**Description**: No `@media print` styles defined. Legal pages and content should print cleanly without interactive elements.

**Required**:
```css
@media print {
  #main-header,
  footer,
  .sticky-cta,
  #banner-wrapper,
  .reveal,
  #mobile-menu {
    display: none !important;
  }

  body {
    background: white !important;
    color: black !important;
  }

  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 0.8em;
    color: #666;
  }
}
```

**Severity**: P1 (Legal page usability)

---

### Issue #7: Color Variable Format Inconsistency

**Type**: Layout/CSS
**File**: `themes/theme_a/tailwind/tailwind.config.js`
**Lines**: 38-52

**Description**: Some colors use HSL format (dynamic branding support), others use RGB format. This creates maintenance confusion and limits branding override capability.

**HSL Format (correct)**:
```javascript
'black': 'hsl(var(--text-h, 146) var(--text-s, 29%) var(--text-l, 14%) / <alpha-value>)',
'linen': 'hsl(var(--background-h, 40) var(--background-s, 27%) var(--background-l, 96%) / <alpha-value>)',
```

**RGB Format (needs migration)**:
```javascript
'stone': 'rgb(var(--color-sage-stone, 143 141 136) / <alpha-value>)',
'darkmoss': 'rgb(var(--color-sage-darkmoss, 74 99 80) / <alpha-value>)',
'label': 'rgb(var(--color-sage-label, 74 93 80) / <alpha-value>)',
'meta': 'rgb(var(--color-sage-meta, 90 110 95) / <alpha-value>)',
'footer-primary': 'rgb(var(--color-sage-footer-primary, 209 217 212) / <alpha-value>)',
'footer-secondary': 'rgb(var(--color-sage-footer-secondary, 163 176 168) / <alpha-value>)',
```

**Fix**: Migrate all colors to HSL format with branding override variables.

**Severity**: P1 (Branding system consistency)

---

### Issue #8: Missing Responsive Image Handling

**Type**: Responsive
**File**: `themes/theme_a/templates/sum_core/blocks/hero_image.html`
**Line**: 8

**Description**: Hero image uses `original` rendition without responsive sizing.

**Current**:
```django
{% image self.image original as hero_img %}
```

**Problem**: Large images loaded on mobile, impacting performance.

**Fix**: Use Wagtail's responsive image features:
```django
{% image self.image fill-1920x1080 as hero_desktop %}
{% image self.image fill-768x600 as hero_tablet %}
{% image self.image fill-480x400 as hero_mobile %}
<picture>
  <source media="(min-width: 1200px)" srcset="{{ hero_desktop.url }}">
  <source media="(min-width: 768px)" srcset="{{ hero_tablet.url }}">
  <img src="{{ hero_mobile.url }}" alt="{{ self.image_alt }}" class="...">
</picture>
```

**Severity**: P1 (Performance)

---

## P2 - Medium Priority Issues

### Issue #9: Established Year Field Missing

**Type**: Layout/Data
**File**: `themes/theme_a/templates/theme/includes/header.html`
**Related**: FUCKED-THEME.md report

**Description**: Template references `site_settings.established_year` which doesn't exist in `SiteSettings` model.

**Current**:
```django
Est. {{ site_settings.established_year|default:"2025" }}
```

**Options**:
1. Add `established_year` field to `SiteSettings` model
2. Remove "Est. YYYY" display (Sage & Stone specific branding)

**Severity**: P2 (Non-functional display)

---

### Issue #10: Portfolio Card Hover States Desktop-Only

**Type**: Responsive
**File**: `themes/theme_a/static/theme_a/css/input.css`
**Lines**: 157-164

**Description**: Correctly uses `@media (hover: hover) and (pointer: fine)` for portfolio card hover. However, there's no alternative interaction state for touch devices.

**Current**: Desktop users get zoom effect, touch users get nothing.

**Suggestion**: Add `:active` states for touch interaction feedback.

**Severity**: P2

---

### Issue #11: Sticky CTA Z-Index Layering

**Type**: Layout
**File**: `themes/theme_a/static/theme_a/css/input.css`
**Line**: 430

**Description**: Sticky CTA uses `z-50` which may conflict with other z-50 elements (header, mobile menu).

**Current**:
```css
.sticky-cta {
  @apply fixed bottom-8 right-8 z-50 ...;
}
```

**Context**:
- Header: `z-50`
- Mobile menu: `z-[80]`
- Sticky CTA: `z-50`

**Suggestion**: Establish clear z-index scale:
- Modal overlays: 80-100
- Navigation: 50-60
- Floating elements: 40-50
- Content: 0-30

**Severity**: P2

---

### Issue #12: Form Success/Error Message Styling Incomplete

**Type**: Layout
**File**: `themes/theme_a/templates/sum_core/blocks/contact_form.html`
**Lines**: 108-109

**Description**: Form messages container exists but styling for `.form-messages--success` and `.form-messages--error` is applied via JavaScript classes that aren't defined in CSS.

**Current HTML**:
```html
<div class="form-messages" role="alert" aria-live="polite"></div>
```

**Missing CSS**: No `.form-messages--success`, `.form-messages--error`, `.form-success-msg`, `.form-error-msg` styles defined.

**Fix**: Add to `input.css`:
```css
.form-messages--success {
  @apply p-4 bg-sage-moss/20 border border-sage-moss/40 rounded-sm mt-4;
}
.form-messages--error {
  @apply p-4 bg-sage-terra/20 border border-sage-terra/40 rounded-sm mt-4;
}
.form-success-msg {
  @apply text-sage-moss font-mono text-sm uppercase tracking-widest;
}
.form-error-msg {
  @apply text-sage-terra font-mono text-sm uppercase tracking-widest;
}
```

**Severity**: P2

---

### Issue #13: Blog Typography Prose Overrides Incomplete

**Type**: Typography
**File**: `themes/theme_a/static/theme_a/css/input.css`
**Lines**: 252-277

**Description**: `.prose-sage` overrides are defined but the actual blog templates may not consistently apply them.

**Check Required**: Verify `blog_post_page.html` uses `.prose-sage` class on article content.

**Severity**: P2

---

### Issue #14: Skip Link Styling Incomplete

**Type**: Accessibility
**File**: `docs/dev/design/wireframes/sage-and-stone/compiled/index.html`
**Line**: 88-90

**Description**: Wireframe includes skip-to-main-content link:
```html
<a href="#main" class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[70] focus:bg-sage-terra focus:text-white focus:px-6 focus:py-3 focus:font-bold focus:shadow-lg focus:outline-none">
    Skip to main content
</a>
```

**Check Required**: Verify this exists in `base.html` and works correctly.

**Severity**: P2 (Accessibility)

---

### Issue #15: Missing Featured Image on Portfolio Cards

**Type**: Layout
**File**: Compare wireframe `portfolio.html` with implementation

**Description**: Wireframe portfolio cards have rich metadata display (Constraint, Material, Outcome). Current implementation may not match this structure.

**Severity**: P2

---

### Issue #16: Service Cards Grid Inconsistency

**Type**: Layout
**File**: `themes/theme_a/templates/sum_core/blocks/service_cards.html`

**Description**: Wireframe shows 2+1 grid layout for services (primary service spans 2 columns). Current implementation may not match.

**Severity**: P2

---

## P3 - Low Priority Issues

### Issue #17: Testimonial Quote Mark Styling

**Type**: Typography
**Description**: Wireframe uses custom quote mark SVG. Current implementation may use basic quotation marks.

**Severity**: P3

---

### Issue #18: Footer Social Icons Limited

**Type**: Layout
**File**: `themes/theme_a/templates/theme/includes/footer.html`

**Description**: Only Instagram icon shown. May need LinkedIn, Facebook, etc.

**Severity**: P3

---

### Issue #19: Breadcrumb Implementation Missing

**Type**: Layout
**Description**: Wireframe shows breadcrumbs on inner pages. Check if implemented.

**Severity**: P3

---

### Issue #20: Cookie Consent Banner Missing

**Type**: Compliance
**Description**: No GDPR cookie consent implementation visible.

**Severity**: P3 (Should be P1 for EU deployment)

---

### Issue #21: Structured Data Schema Incomplete

**Type**: SEO
**Description**: FAQPage schema may be duplicated. LocalBusiness schema inconsistent (London phone, Herefordshire location).

**Severity**: P3

---

### Issue #22: Animation Duration Consistency

**Type**: Layout
**Description**: Various animations use different timing values. Consider standardizing on theme timing tokens.

**Severity**: P3

---

## Recommended Fix Order

Based on severity and dependencies:

### Phase 1: Critical Accessibility (P0)
1. **Issue #1**: Fix form placeholder contrast (quick CSS change)
2. **Issue #2**: Fix hardcoded form action URL
3. **Issue #3**: Add hero-image ID for parallax

### Phase 2: High Priority UX (P1)
4. **Issue #5**: Implement mobile menu focus trap
5. **Issue #6**: Add print styles
6. **Issue #7**: Migrate color variables to HSL
7. **Issue #4**: Enhance mega menu layout
8. **Issue #8**: Add responsive images

### Phase 3: Medium Priority Polish (P2)
9. Fix remaining P2 issues as time permits

### Phase 4: Low Priority Enhancement (P3)
10. Address P3 issues in future sprints

---

## Cross-Browser Testing Checklist

| Browser | Desktop | Tablet | Mobile | Issues Found |
|---------|---------|--------|--------|--------------|
| Chrome 120+ | TBD | TBD | TBD | |
| Firefox 120+ | TBD | TBD | TBD | |
| Safari 17+ | TBD | TBD | TBD | |
| Edge 120+ | TBD | TBD | TBD | |

---

## Related Documentation

- **Previous Audit**: `docs/dev/reports/FUCKED-THEME.md` (Block template path issue)
- **Theme Architecture**: `docs/dev/master-docs/THEME-ARCHITECTURE-SPECv1.md`
- **Wireframe Source**: `docs/dev/design/wireframes/sage-and-stone/compiled/`
- **Issue #292**: Original Theme A fixes task
- **Work Order #461**: WO: Theme A Critical Fixes

---

## Appendix A: Files Requiring Changes

| Priority | File | Changes |
|----------|------|---------|
| P0 | `themes/theme_a/templates/sum_core/blocks/contact_form.html` | Contrast, URL |
| P0 | `themes/theme_a/templates/sum_core/blocks/hero_image.html` | Add ID |
| P1 | `themes/theme_a/static/theme_a/js/main.js` | Focus trap |
| P1 | `themes/theme_a/static/theme_a/css/input.css` | Print styles, form messages |
| P1 | `themes/theme_a/tailwind/tailwind.config.js` | HSL migration |
| P1 | `themes/theme_a/templates/theme/includes/header.html` | Mega menu |
| P1 | `core/sum_core/blocks/` | Create `ProvenancePlateBlock` |
| P1 | `themes/theme_a/templates/sum_core/blocks/provenance_plate.html` | Create template |
| P2 | `themes/theme_a/templates/sum_core/blocks/comparison.html` | Create template |
| P2 | `themes/theme_a/templates/sum_core/blocks/features_list.html` | Create template |
| P2 | Multiple | Various polish |

---

## Appendix B: Missing Block Templates Summary

Core blocks that exist but lack Theme A templates:

| Block | Core Definition | Required Template |
|-------|----------------|-------------------|
| `ComparisonBlock` | `core/sum_core/blocks/content.py` | `comparison.html` |
| `FeaturesListBlock` | `core/sum_core/blocks/content.py` | `features_list.html` |

Wireframe sections that need new core blocks:

| Section | Wireframe Location | Required Block |
|---------|-------------------|----------------|
| Provenance Plate | `index.html#provenance` | `ProvenancePlateBlock` |

---

*End of audit report.*
