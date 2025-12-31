# Sage & Stone CSS Audit Report

**WO-THEME-001** | Audit Date: 2025-12-31
**Wireframes Source:** `docs/dev/design/wireframes/sage-and-stone/compiled/`
**Live Site:** https://sage-and-stone.lintel.site

---

## Executive Summary

This audit compares the static HTML/CSS wireframes against the live Wagtail-powered site to identify CSS discrepancies, missing Wagtail blocks, and implementation gaps that need resolution before theme completion.

---

## 1. Design Token Discrepancies

### 1.1 Color Palette

**Wireframe Tailwind Config:**
```javascript
colors: {
    sage: {
        black: '#1A2F23',    // Obsidian Green
        moss: '#6B8F71',     // Moss
        terra: '#A0563B',    // Burnished Terra
        oat: '#EDE8E0',      // Oat
        linen: '#F7F5F1',    // Linen
        darkmoss: '#4A6350',
        // Contrast-Safe Tokens
        'label': '#4A5D50',
        'meta': '#5A6E5F',
        'footer-primary': '#D1D9D4',
        'footer-secondary': '#A3B0A8',
    }
}
```

**Live Site Observation:** Uses CSS custom properties with HSL values instead of hex. Need to verify exact color matching.

| Token | Wireframe (Hex) | Status | Action Required |
|-------|-----------------|--------|-----------------|
| sage-black | #1A2F23 | VERIFY | Convert to HSL variable |
| sage-moss | #6B8F71 | VERIFY | Convert to HSL variable |
| sage-terra | #A0563B | VERIFY | Convert to HSL variable |
| sage-oat | #EDE8E0 | VERIFY | Convert to HSL variable |
| sage-linen | #F7F5F1 | VERIFY | Convert to HSL variable |
| sage-darkmoss | #4A6350 | VERIFY | Convert to HSL variable |
| sage-label | #4A5D50 | VERIFY | Accessibility contrast token |
| sage-meta | #5A6E5F | VERIFY | Accessibility contrast token |
| sage-footer-primary | #D1D9D4 | VERIFY | Footer text token |
| sage-footer-secondary | #A3B0A8 | VERIFY | Footer text token |

### 1.2 Typography

**Wireframe Fonts:**
- Display: `Playfair Display` (serif) - headings
- Body: `Lato` (sans-serif) - paragraphs
- Accent: `Crimson Text` (serif) - blog prose

**Live Site:** Typography appears to match. Verify Google Fonts integration.

### 1.3 Custom Breakpoints

**Wireframe Config:**
```javascript
screens: {
    ipad: '970px',
    desktop: '1200px',
}
```

**Issue:** Standard Tailwind breakpoints (sm, md, lg, xl) may not match wireframe intent. The wireframe uses custom `ipad:` and `desktop:` prefixes for responsive classes.

**Action Required:** Ensure Wagtail theme includes custom breakpoint configuration or migrate to standard breakpoints consistently.

---

## 2. Critical CSS Component Gaps

### 2.1 Alert Banner (Grid Animation)

**Wireframe Implementation:**
```css
.banner-grid-wrapper {
    display: grid;
    grid-template-rows: 1fr;
    transition: grid-template-rows 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.banner-grid-wrapper.closed {
    grid-template-rows: 0fr;
}
.banner-inner {
    overflow: hidden;
}
```

**Status:** REQUIRES VERIFICATION
**Priority:** HIGH
**Notes:** This CSS Grid technique enables smooth height animation without JavaScript height calculations. Must verify the banner dismiss functionality animates correctly on live site.

### 2.2 Mega Menu System

**Wireframe Implementation:**
```css
.mega-panel {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-10px);
    width: 100vw;
    max-width: 80rem;
    opacity: 0;
    pointer-events: none;
    transition: opacity 200ms ease-out, transform 200ms cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 100;
    padding-top: 1.5rem; /* THE BRIDGE */
}
.mega-panel[data-open="true"] {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
    pointer-events: auto;
}
```

**Critical Feature:** The `padding-top: 1.5rem` creates an invisible "bridge" that prevents the menu from closing when moving cursor from trigger to panel.

**Status:** REQUIRES VERIFICATION
**Priority:** CRITICAL
**Notes:**
- Desktop: 12-column mega menu with featured image
- Live site shows simpler dropdown structure
- Verify hover bridge pattern is implemented

### 2.3 Mobile Navigation (3-Level Drill-Down)

**Wireframe Features:**
- Full-screen overlay with `translate-x-full` slide animation
- 3 sliding panels (300vw total width)
- CSS variable `--menu-x` controls transform
- Safe area insets for notched devices
- Touch-optimized targets (min 44px)

**Wireframe Classes:**
```css
.menu-level {
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Status:** REQUIRES VERIFICATION
**Priority:** HIGH
**Notes:** Live site shows collapsible accordion-style mobile menu. Verify if drill-down navigation is implemented or replaced.

### 2.4 Accordion/FAQ System

**Wireframe Implementation:**
```css
.accordion-grid-wrapper {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.accordion-grid-wrapper.open {
    grid-template-rows: 1fr;
}
.accordion-inner {
    overflow: hidden !important;
    min-height: 0 !important;
    visibility: hidden;
    transition: visibility 0.5s;
}
.accordion-grid-wrapper.open .accordion-inner {
    visibility: visible;
}
```

**Status:** REQUIRES VERIFICATION
**Priority:** MEDIUM
**Notes:** CSS Grid height animation for smooth accordion expansion. Used on Terms page for TOC sections.

### 2.5 Reveal Animation System

**Wireframe Implementation:**
```css
.reveal {
    opacity: 0;
    transform: translateY(30px) scale(0.98);
    transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1),
                transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal.active {
    opacity: 1;
    transform: translateY(0) scale(1);
}
```

**Status:** REQUIRES VERIFICATION
**Priority:** MEDIUM
**Notes:** IntersectionObserver-based reveal animation. Verify JS implementation.

---

## 3. Accessibility CSS Requirements

### 3.1 Focus Indicators

**Wireframe Implementation:**
```css
a:focus-visible, button:focus-visible, input:focus-visible,
textarea:focus-visible, select:focus-visible {
    outline: 3px solid #A0563B;
    outline-offset: 2px;
    border-color: #A0563B;
}

button:focus-visible, a:focus-visible {
    outline: 2px solid #A0563B;
    outline-offset: 4px;
    border-radius: 2px;
}
```

**Status:** CRITICAL - MUST VERIFY
**Priority:** CRITICAL
**Notes:** WCAG 2.1 AA compliance requires visible focus indicators.

### 3.2 Invalid Input States

**Wireframe Implementation:**
```css
input[aria-invalid="true"], textarea[aria-invalid="true"],
select[aria-invalid="true"] {
    border-color: #A0563B;
    border-width: 2px;
    background-color: #fff5f5;
}
```

**Status:** REQUIRES VERIFICATION
**Priority:** HIGH

### 3.3 Skip Link

**Wireframe Implementation:**
```html
<a href="#main" class="sr-only focus:not-sr-only focus:absolute
   focus:top-4 focus:left-4 focus:z-[70] focus:bg-sage-terra
   focus:text-white focus:px-6 focus:py-3 focus:font-bold
   focus:shadow-lg focus:outline-none">
    Skip to main content
</a>
```

**Status:** REQUIRES VERIFICATION
**Priority:** HIGH

### 3.4 Screen Reader Only Class

**Wireframe Implementation:**
```css
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
```

**Status:** REQUIRES VERIFICATION
**Priority:** MEDIUM

### 3.5 Reduced Motion Support

**Wireframe Implementation:**
```css
@media (prefers-reduced-motion: reduce) {
    .reveal {
        transition: none;
        opacity: 1;
        transform: none;
    }
    .img-zoom-container img {
        transition: none;
    }
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
```

**Status:** CRITICAL - MUST VERIFY
**Priority:** CRITICAL
**Notes:** WCAG 2.1 AA compliance for users with vestibular disorders.

---

## 4. Desktop-Only Hover Effects

**Wireframe Implementation:**
```css
@media (hover: hover) and (pointer: fine) {
    .img-zoom-container img {
        transition: transform 0.8s cubic-bezier(0.25, 1, 0.5, 1);
    }
    .group:hover .img-zoom-container img {
        transform: scale(1.05);
    }
}
```

**Status:** REQUIRES VERIFICATION
**Priority:** MEDIUM
**Notes:** Prevents "sticky hover" on touch devices.

---

## 5. Missing Wagtail Blocks Inventory

Based on wireframe analysis, the following block types are required:

### 5.1 Navigation Blocks

| Block Name | Description | Status |
|------------|-------------|--------|
| `AlertBannerBlock` | Dismissible announcement banner | VERIFY |
| `MegaMenuBlock` | Desktop navigation mega menu | VERIFY |
| `MobileMenuBlock` | 3-level drill-down mobile nav | VERIFY |

### 5.2 Content Blocks

| Block Name | Description | Wireframe Page | Status |
|------------|-------------|----------------|--------|
| `HeroBlock` | Full-width hero with parallax | index.html | VERIFY |
| `ProvenanceModalBlock` | Material provenance overlay | index.html | VERIFY |
| `TeamGridBlock` | Team member cards | about.html | VERIFY |
| `FounderLetterBlock` | Letter from founder section | about.html | VERIFY |
| `ProcessPhaseBlock` | 5-phase process timeline | services.html | VERIFY |
| `ServiceCardBlock` | Service description cards | services.html | VERIFY |
| `PortfolioGridBlock` | Filterable portfolio grid | portfolio.html | VERIFY |
| `PortfolioFilterBlock` | Category filter buttons | portfolio.html | VERIFY |
| `BlogCardBlock` | Blog post preview cards | blog_list.html | VERIFY |
| `BlogCategoryFilterBlock` | Blog category tabs | blog_list.html | VERIFY |
| `ArticleSidebarBlock` | TOC + newsletter signup | blog_article.html | VERIFY |
| `RelatedArticlesBlock` | "Read Next" section | blog_article.html | VERIFY |
| `LegalTOCBlock` | Sticky table of contents | terms.html | VERIFY |
| `PlainEnglishCalloutBlock` | Simplified legal explanation | terms.html | VERIFY |
| `AccordionBlock` | FAQ/expandable sections | terms.html | VERIFY |

### 5.3 Footer Blocks

| Block Name | Description | Status |
|------------|-------------|--------|
| `FooterBlock` | 4-column footer grid | VERIFY |
| `SocialLinksBlock` | Social media icons | VERIFY |
| `ContactInfoBlock` | Address, phone, email | VERIFY |

---

## 6. Page-Specific CSS Issues

### 6.1 Homepage (index.html)

| Issue | Description | Priority |
|-------|-------------|----------|
| Hero parallax | `attachment-fixed` class with `will-change: transform` | HIGH |
| Provenance modal | Full-screen overlay with backdrop blur | MEDIUM |
| Contact form | CTA section styling | MEDIUM |

### 6.2 About Page (about.html)

| Issue | Description | Priority |
|-------|-------------|----------|
| Team grid | Responsive card layout | MEDIUM |
| Standards section | Grid with icons | LOW |

### 6.3 Services Page (services.html)

| Issue | Description | Priority |
|-------|-------------|----------|
| Process timeline | 5-phase horizontal/vertical layout | HIGH |
| Cleanliness pledge | Quote/callout styling | LOW |

### 6.4 Portfolio Page (portfolio.html)

| Issue | Description | Priority |
|-------|-------------|----------|
| Filter buttons | Active state styling | HIGH |
| Portfolio grid | Masonry or grid layout | HIGH |
| Featured project | Full-width hero treatment | MEDIUM |

### 6.5 Blog List (blog_list.html)

| Issue | Description | Priority |
|-------|-------------|----------|
| Category filter | Active tab styling | MEDIUM |
| Card grid | Image aspect ratios | MEDIUM |
| Read time badge | Metadata styling | LOW |

### 6.6 Blog Article (blog_article.html)

| Issue | Description | Priority |
|-------|-------------|----------|
| Prose typography | Tailwind prose overrides | HIGH |
| Sidebar TOC | Scroll-spy highlighting | MEDIUM |
| Newsletter form | Inline form styling | MEDIUM |

### 6.7 Terms Page (terms.html)

| Issue | Description | Priority |
|-------|-------------|----------|
| Mobile TOC toggle | Rotation animation | HIGH |
| Sticky sidebar | Desktop fixed positioning | HIGH |
| Print styles | `@media print` support | LOW |
| Plain English boxes | Callout styling | MEDIUM |

---

## 7. Recommended Actions

### Critical (Must Fix)

1. **Verify focus indicators** - WCAG 2.1 AA compliance
2. **Verify reduced motion support** - WCAG 2.1 AA compliance
3. **Verify mega menu hover bridge** - UX critical for desktop navigation
4. **Verify skip link implementation** - Accessibility requirement

### High Priority

5. **Audit color token implementation** - Ensure exact color matching
6. **Verify mobile drill-down navigation** - Core mobile UX
7. **Verify alert banner animation** - Grid animation technique
8. **Test portfolio filter functionality** - User interaction
9. **Verify process timeline layout** - Services page layout

### Medium Priority

10. **Verify accordion animations** - Terms page interactions
11. **Verify reveal animations** - Scroll-based effects
12. **Test desktop-only hover states** - Image zoom effects
13. **Verify prose typography** - Blog article styling

### Low Priority

14. **Verify print stylesheet** - Terms page print support
15. **Verify scrollbar hiding** - `.no-scrollbar` utility

---

## 8. Testing Checklist

### Accessibility Testing

- [ ] Keyboard navigation through all interactive elements
- [ ] Focus visible on all focusable elements
- [ ] Skip link visible on Tab key press
- [ ] Reduced motion respects system preference
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] Touch targets minimum 44x44px

### Responsive Testing

- [ ] Mobile: < 970px (ipad breakpoint)
- [ ] Tablet: 970px - 1199px
- [ ] Desktop: >= 1200px

### Browser Testing

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] iOS Safari
- [ ] Chrome Android

---

## 9. Appendix: CSS File Inventory

### Wireframe CSS Files

| File | Purpose | Size |
|------|---------|------|
| `static/style.css` | Custom CSS (animations, mega menu, accordion) | ~163 lines |
| Tailwind CDN | Utility classes | External |
| Google Fonts | Typography | External |

### Required Theme CSS

Based on wireframes, the theme should include:

1. **Base/Reset** - Normalize/reset styles
2. **Design Tokens** - CSS custom properties for colors, spacing, typography
3. **Components** - Block-specific styles
4. **Utilities** - Custom utility classes (.sr-only, .no-scrollbar, .reveal)
5. **Animations** - Keyframes and transitions
6. **Responsive** - Breakpoint-specific overrides
7. **Print** - Print media query styles
8. **Accessibility** - Focus, reduced motion, high contrast

---

*Report generated: 2025-12-31*
*Next review: After theme implementation updates*
