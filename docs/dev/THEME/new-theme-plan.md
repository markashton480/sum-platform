# Theme A Complete Implementation Plan

## Executive Summary

**Current State:** Theme A block templates have been migrated to Tailwind and match wireframe styling. Infrastructure is complete. Header/footer/navigation are done. Most blocks have tests.

**Target State:** Theme A perfectly recreates the wireframe across all page types (homepage, about, services, portfolio, blog, terms). All blocks match wireframe structure. Branding is data-driven, not hardcoded.

**Remaining Gap:** 4 blocks don't exist (TeamMemberBlock, TimelineBlock, ServiceDetailBlock, PageHeaderBlock). Blog/Portfolio page types don't exist. QuoteRequestFormBlock needs checklist verification.

**Timeline:** ~1 week remaining for new blocks + page types.

---

## Progress Audit (Updated: 2024-12-23)

### ✅ COMPLETED

**Category A - Fix Existing Block Templates (13/13 DONE)**
- [x] HeroImageBlock - template matches wireframe
- [x] HeroGradientBlock - template matches wireframe  
- [x] PortfolioBlock - template + horizontal scroll mobile
- [x] ContactFormBlock - split layout, floating labels
- [x] FAQBlock - accordion with proper styling
- [x] ServiceCardsBlock - grid with featured card layout
- [x] StatsBlock - 4-column grid with proper spacing
- [x] TrustStripLogosBlock - text OR image logos (THEME-020)
- [x] TestimonialsBlock - dark theme, horizontal scroll (THEME-019)
- [x] EditorialHeaderBlock - page header styling (THEME-021)
- [x] RichTextContentBlock - prose typography (THEME-022)
- [x] QuoteBlock - pull quote styling (THEME-023)
- [x] ImageBlock - caption styling (THEME-024/029)

**Category B - Create New Blocks (2/6 DONE)**
- [x] ManifestoBlock - exists in content.py + theme_a template
- [x] FeaturedCaseStudyBlock - exists in gallery.py + theme_a template

**Category D - Site-Wide Components (4/4 DONE)**
- [x] Header/Navigation - mega menu, mobile drill-down
- [x] Footer - multi-column layout with social
- [x] Alert Banner - dismissible with local storage
- [x] Mobile Menu - slide-in drill-down system

**Category E - Infrastructure (5/5 DONE)**
- [x] Fast Iteration Setup - test_project resolves to themes/theme_a
- [x] Add Missing Fields - PortfolioItemBlock has constraint/material/outcome
- [x] Add established_year - SiteSettings has this field
- [x] Strip Hardcoded Branding - only 2 cosmetic comments remain in base.html
- [x] Management Commands - (verify status)

### ❌ REMAINING WORK

**Category B - Create New Blocks (4 remaining)**
- [ ] TeamMemberBlock - team member grid (photo, name, role, bio)
- [ ] TimelineBlock - history timeline with dates
- [ ] ServiceDetailBlock - service detail section (repeating pattern)
- [ ] PageHeaderBlock - simple interior page header with breadcrumbs

**Category C - Create New Page Types (3 remaining)**
- [ ] BlogIndexPage - blog listing page
- [ ] BlogPostPage - individual blog articles
- [ ] PortfolioIndexPage - dedicated portfolio page (if needed)

**Other**
- [ ] QuoteRequestFormBlock - verify template matches wireframe (template exists but not in checklist)

---

## Original Plan (Reference)

---

---

## Part 1: Current State Analysis (HISTORICAL - see Progress Audit above)

### What Exists in sum_core (from blocks-reference.md)

**Hero Blocks:**
- HeroImageBlock ✅ (exists, needs template fix)
- HeroGradientBlock ✅ (exists, needs template fix)

**Section Blocks:**
- ServiceCardsBlock ✅ (exists, needs template fix)
- TestimonialsBlock ✅ (exists, needs template fix)
- GalleryBlock ✅ (exists, needs template review)
- PortfolioBlock ✅ (exists, needs fields + template)
- TrustStripLogosBlock ✅ (exists, needs template fix)
- StatsBlock ✅ (exists, needs template review)
- ProcessStepsBlock ✅ (exists, needs template review)
- FAQBlock ✅ (exists, needs template review)

**Content Blocks:**
- EditorialHeaderBlock ✅ (exists, needs template fix)
- RichTextContentBlock ✅ (exists, needs template review)
- QuoteBlock ✅ (exists, needs template review)
- ImageBlock ✅ (exists, needs template review)
- ButtonGroupBlock ✅ (exists, needs template review)
- SpacerBlock ✅ (exists, probably fine)
- DividerBlock ✅ (exists, probably fine)

**Form Blocks:**
- ContactFormBlock ✅ (exists, needs template fix)
- QuoteRequestFormBlock ✅ (exists, needs template fix)

### What's Missing (from wireframe analysis)

**Blocks that don't exist:**
- ManifestoBlock ❌ (centered prose sections)
- FeaturedCaseStudyBlock ❌ (split layout with stats)
- TeamMemberBlock ❌ (about page team grid)
- TimelineBlock ❌ (about page history)
- ServiceDetailBlock ❌ (services page detailed sections)
- PageHeaderBlock ❌ (interior page headers with breadcrumbs)

**Page types that don't exist:**
- BlogIndexPage ❌ (blog list page)
- BlogPostPage ❌ (individual blog articles)

**Site-wide components that need attention:**
- Header/Navigation (complex mega menu)
- Footer (multi-column with social)
- Alert banner (dismissible)
- Mobile menu (drill-down system)

---

## Part 2: Wireframe Inventory & Block Mapping

### 1. index.html (Homepage)

**Components in wireframe:**

| Component | Lines | Maps to Block | Status |
|-----------|-------|---------------|--------|
| Hero (full screen, image bg) | 317-353 | HeroImageBlock | EXISTS - needs template |
| Stats strip (4 metrics) | 356-377 | StatsBlock | EXISTS - needs template |
| Manifesto section (centered prose) | 380-400 | ❌ ManifestoBlock | DOESN'T EXIST |
| Services grid (3 cards, 1 large) | 403-484 | ServiceCardsBlock | EXISTS - needs template |
| Provenance feature (split layout) | 485-524 | ❌ FeaturedCaseStudyBlock | DOESN'T EXIST |
| Portfolio cards (3-col, horiz scroll mobile) | 527-591 | PortfolioBlock | EXISTS - needs fields + template |
| Featured case study (split layout) | 594-624 | ❌ FeaturedCaseStudyBlock | DOESN'T EXIST |
| FAQ (accordion) | 650-735 | FAQBlock | EXISTS - needs template |
| Contact form (split layout) | 738-814 | ContactFormBlock | EXISTS - needs template |

### 2. about.html (About Page)

**Components in wireframe:**

| Component | Lines | Maps to Block | Status |
|-----------|-------|---------------|--------|
| Page header (simple, centered) | ~300 | ❌ PageHeaderBlock | DOESN'T EXIST |
| Intro section (large text) | ~320 | RichTextContentBlock | EXISTS - needs template |
| Image + text (alternating) | ~350-450 | Multiple ImageBlock + RichText | EXISTS - needs coordination |
| Team members grid | ~500 | ❌ TeamMemberBlock | DOESN'T EXIST |
| Timeline/history | ~550 | ❌ TimelineBlock | DOESN'T EXIST |

### 3. services.html (Services Page)

**Components in wireframe:**

| Component | Lines | Maps to Block | Status |
|-----------|-------|---------------|--------|
| Hero (gradient, no image) | ~300 | HeroGradientBlock | EXISTS - needs template |
| Service detail sections (repeating) | ~350-600 | ❌ ServiceDetailBlock | DOESN'T EXIST |
| Trust strip / accreditations | 629-652 | TrustStripLogosBlock | EXISTS - needs template |
| FAQ | ~655-800 | FAQBlock | EXISTS - needs template |
| Contact CTA | ~800+ | ContactFormBlock or CTA | EXISTS - needs template |

### 4. portfolio.html (Portfolio Page)

**Components in wireframe:**

| Component | Lines | Maps to Block | Status |
|-----------|-------|---------------|--------|
| Page header | ~300 | ❌ PageHeaderBlock | DOESN'T EXIST |
| Filter navigation | ~320 | Custom or blocks? | TBD |
| Portfolio grid (larger, more items) | ~350+ | PortfolioBlock | EXISTS - needs fields + template |
| Pagination | ~bottom | Built-in Wagtail | EXISTS |

### 5. blog_list.html (Blog Index)

**Components in wireframe:**

| Component | Lines | Maps to Block | Status |
|-----------|-------|---------------|--------|
| Page header | ~300 | ❌ PageHeaderBlock | DOESN'T EXIST |
| Blog post cards (list) | ~350+ | Needs BlogIndexPage | DOESN'T EXIST |
| Pagination | ~bottom | Built-in Wagtail | EXISTS |

### 6. blog_article.html (Blog Post)

**Components in wireframe:**

| Component | Lines | Maps to Block | Status |
|-----------|-------|---------------|--------|
| Article header (meta, title, image) | ~300 | EditorialHeaderBlock | EXISTS - needs template |
| Article body (prose typography) | ~400+ | RichTextContentBlock | EXISTS - needs prose styling |
| Pull quotes | throughout | QuoteBlock | EXISTS - needs template |
| Images with captions | throughout | ImageBlock | EXISTS - needs template |
| Related posts | ~bottom | Custom or query | TBD |

### 7. terms.html (Legal Pages)

**Components in wireframe:**

| Component | Lines | Maps to Block | Status |
|-----------|-------|---------------|--------|
| Simple header | ~300 | EditorialHeaderBlock | EXISTS - needs template |
| Legal prose (long form) | ~350+ | RichTextContentBlock | EXISTS - needs template |
| Table of contents | ~320 | Custom or block? | TBD |

---

## Part 3: The Gap - What Needs to Happen

### Category A: Fix Existing Block Templates (High Priority)
These blocks exist in sum_core but templates don't match wireframe.

1. **HeroImageBlock** - Full screen, parallax effect, dual CTAs
2. **HeroGradientBlock** - Text-focused, no image version
3. **PortfolioBlock** - Horizontal scroll mobile, new metadata fields
4. **ContactFormBlock** - Split layout, floating labels
5. **FAQBlock** - Accordion with proper styling
6. **ServiceCardsBlock** - Grid with featured card layout
7. **StatsBlock** - 4-column grid with proper spacing
8. **TrustStripLogosBlock** - Text OR image logos, centered
9. **TestimonialsBlock** - Dark theme, horizontal scroll mobile
10. **EditorialHeaderBlock** - Page header styling
11. **RichTextContentBlock** - Prose typography configuration
12. **QuoteBlock** - Pull quote styling
13. **ImageBlock** - Caption styling

### Category B: Create New Blocks (Medium Priority)
These blocks don't exist, need to be created.

1. **ManifestoBlock** - Centered prose with eyebrow/heading/body/quote
2. **FeaturedCaseStudyBlock** - Split layout, floating stats, numbered list
3. **PageHeaderBlock** - Simple interior page header with breadcrumbs
4. **TeamMemberBlock** - Team member grid (photo, name, role, bio)
5. **TimelineBlock** - History timeline with dates
6. **ServiceDetailBlock** - Service detail section (repeating pattern)

### Category C: Create New Page Types (Low Priority - Post Initial)
Blog functionality isn't in MVP but wireframes exist.

1. **BlogIndexPage** - Blog listing page
2. **BlogPostPage** - Individual blog articles
3. **PortfolioIndexPage** - Dedicated portfolio page (if not using standard page)

### Category D: Site-Wide Components (Medium Priority)
Header, footer, navigation need matching.

1. **Header/Navigation** - Mega menu, mobile drill-down
2. **Footer** - Multi-column layout
3. **Alert Banner** - Dismissible banner
4. **Mobile Menu** - Slide-in drill-down system

### Category E: Infrastructure (High Priority - Do First)
Make development fast and ensure branding is data-driven.

1. **Fast Iteration Setup** - Point test_project at themes/theme_a
2. **Add Missing Fields** - PortfolioItemBlock needs constraint/material/outcome
3. **Add established_year** - SiteSettings needs this field
4. **Management Commands** - Generic demo + S&S demo
5. **Strip Hardcoded Branding** - Remove all "Sage & Stone" from templates

---

## Part 4: Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Goal:** Fast iteration works, priority blocks match wireframe.

**Day 1: Setup**
- Update test_project settings to point at themes/theme_a
- Add fields to PortfolioItemBlock (constraint/material/outcome)
- Add established_year to SiteSettings
- Create migration, run it
- Test: Edit template → refresh → see changes instantly

**Day 2-3: Priority Block Templates**
Fix templates for blocks that appear on homepage:
- HeroImageBlock template (index hero)
- StatsBlock template (stats strip)
- ServiceCardsBlock template (services grid)
- PortfolioBlock template (portfolio cards)
- ContactFormBlock template (contact form)

**Day 4-5: Create Missing Homepage Blocks**
- Create ManifestoBlock (Python + template)
- Create FeaturedCaseStudyBlock (Python + template)
- Register both in PageStreamBlock
- Test: Add both to homepage, verify rendering

**Milestone:** Homepage matches wireframe (minus header/footer).

### Phase 2: Content Blocks (Week 2)

**Goal:** Interior pages work, prose/editorial content matches wireframe.

**Day 1-2: Editorial/Content Templates**
- EditorialHeaderBlock template (page headers)
- RichTextContentBlock template (prose styling)
- QuoteBlock template (pull quotes)
- ImageBlock template (captioned images)
- ButtonGroupBlock template (CTA buttons)

**Day 3: About Page Blocks**
- Create TeamMemberBlock (grid of team members)
- Create TimelineBlock (history timeline)
- Create PageHeaderBlock (simple interior header)

**Day 4-5: Services Page Blocks**
- Create ServiceDetailBlock (detailed service sections)
- Update TrustStripLogosBlock template (text OR image)
- Update FAQBlock template (proper accordion)
- Update TestimonialsBlock template (dark theme)

**Milestone:** About and Services pages match wireframe.

### Phase 3: Navigation & Layout (Week 2-3)

**Goal:** Header, footer, navigation work across all pages.

**Day 1-2: Header & Navigation**
- Create header template for theme_a
- Implement mega menu structure
- Implement mobile drill-down menu
- Test across breakpoints

**Day 3: Footer**
- Create footer template for theme_a
- Multi-column layout with navigation
- Social icons
- Copyright/legal links

**Day 4: Alert Banner**
- Create alert banner component
- Dismissible with local storage
- Test persistence

**Day 5: Page Templates**
- Create/update page templates (home, standard, services)
- Ensure proper template inheritance
- Test: All pages have correct header/footer

**Milestone:** Full site navigation and layout complete.

### Phase 4: Blog & Portfolio (Week 3 - Optional)

**Goal:** Blog and portfolio dedicated pages work.

**Day 1-2: Blog Pages**
- Create BlogIndexPage model
- Create BlogPostPage model
- Create blog list template
- Create blog article template
- Test: Create posts, view index, view detail

**Day 3: Portfolio Page**
- Create PortfolioIndexPage (if needed)
- Create portfolio detail template
- Add filtering/categories (if needed)

**Day 4-5: Polish**
- Add related posts to blog
- Add portfolio navigation
- Add breadcrumbs to all pages
- Test all page types

**Milestone:** Blog and portfolio pages complete.

### Phase 5: Demo Content & Final Polish (Week 3)

**Goal:** Demo commands work, all branding is data-driven, everything matches wireframe.

**Day 1: Management Commands**
- Create load_theme_demo.py (generic content)
- Create load_sage_and_stone_demo.py (wireframe content)
- Test both commands, verify output

**Day 2: Branding Cleanup**
- Search all templates for "Sage & Stone" - remove
- Search for "Est. 2025" - replace with {{ site_settings.established_year }}
- Search for hardcoded colors - ensure using theme classes
- Verify all text comes from block fields or site settings

**Day 3-4: Visual QA**
- Compare every page to wireframe side-by-side
- Check responsive behavior (mobile, tablet, desktop)
- Check hover states, transitions, animations
- Check accessibility (keyboard nav, focus states, ARIA)

**Day 5: Documentation**
- Update block documentation
- Update theme documentation
- Document any wireframe deviations
- Create handoff document

**Milestone:** Complete implementation, ready for production.

---

## Part 5: Detailed Task Breakdown

### Task 1: Fast Iteration Setup

**What:** Make test_project point directly at theme_a.

**Files to Edit:**
- `core/sum_core/test_project/test_project/settings.py`

**Changes:**
- Line ~50: Change `THEME_TEMPLATES_DIR` to point at `BASE_DIR.parent.parent.parent / "themes" / "theme_a" / "templates"`
- Update TEMPLATES['DIRS'] to use THEME_TEMPLATES_DIR

**Test:**
```bash
cd core/sum_core/test_project
python manage.py runserver
# Edit any template in themes/theme_a/templates/
# Refresh browser
# See changes immediately
```

**Success Criteria:** Changes appear instantly without copying files.

---

### Task 2: Add Fields to Models

**What:** Add missing fields that wireframe needs.

**File 1:** `core/sum_core/blocks/gallery.py`
- Add to PortfolioItemBlock: constraint, material, outcome (all CharBlock, max_length=100, required=False)

**File 2:** `core/sum_core/branding/models.py`
- Add to SiteSettings: established_year (IntegerField, null=True, blank=True)

**Migration:**
```bash
cd core/
python manage.py makemigrations branding
python manage.py migrate
```

**Test:**
- Open Wagtail admin
- Settings → Site Settings → See established_year field
- Edit page with portfolio → Add item → See new metadata fields

**Success Criteria:** New fields appear in admin, save successfully.

---

### Task 3: Create ManifestoBlock

**What:** New block for centered prose sections (wireframe line 380-400).

**File:** `core/sum_core/blocks/content.py`

**Block Structure:**
```python
class ManifestoBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(max_length=100, required=False)
    heading = blocks.RichTextBlock(required=True, features=['italic', 'bold'])
    body = blocks.RichTextBlock(required=True, features=['bold', 'italic', 'link', 'ol', 'ul'])
    quote = blocks.TextBlock(required=False)
    
    class Meta:
        icon = 'doc-full'
        template = 'sum_core/blocks/manifesto.html'
```

**Template:** `themes/theme_a/templates/sum_core/blocks/manifesto.html`

**Template Requirements:**
- Section: py-24 md:py-32 bg-sage-linen
- Max-width: max-w-3xl mx-auto
- Text-align: center
- Eyebrow: text-sage-terra font-accent italic text-2xl
- Heading: font-display text-4xl md:text-5xl
- Body: prose prose-lg
- Quote (if present): border-t, font-accent italic text-xl

**Register:** Add to PageStreamBlock in models.py

**Test:**
- Add ManifestoBlock to page
- Fill fields with wireframe content
- View page
- Should match index.html lines 380-400

**Success Criteria:** Matches wireframe visually.

---

### Task 4: Create FeaturedCaseStudyBlock

**What:** Split layout with image + content (wireframe lines 594-624).

**File:** `core/sum_core/blocks/gallery.py`

**Block Structure:**
```python
class FeaturedCaseStudyBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(max_length=100, required=False)
    heading = blocks.RichTextBlock(required=True)
    intro = blocks.RichTextBlock(required=False)
    points = blocks.ListBlock(blocks.TextBlock(max_length=500), required=False)
    cta_text = blocks.CharBlock(max_length=50, required=False)
    cta_url = blocks.URLBlock(required=False)
    image = ImageChooserBlock(required=True)
    image_alt = blocks.CharBlock(max_length=255, required=True)
    stats_label = blocks.CharBlock(max_length=50, required=False)
    stats_value = blocks.CharBlock(max_length=100, required=False)
    
    class Meta:
        icon = 'doc-full'
        template = 'sum_core/blocks/featured_case_study.html'
```

**Template:** `themes/theme_a/templates/sum_core/blocks/featured_case_study.html`

**Template Requirements:**
- Grid: lg:grid-cols-2 gap-16
- Left: aspect-[4/5] image with floating stats card (absolute top-8 right-8)
- Stats card: bg-sage-terra text-white p-6
- Hover: bg-black/40 overlay with "Inspect Artifact" text
- Right: content with numbered list (1. 2. 3.)
- CTA: border-b-2 border-sage-terra

**Register:** Add to PageStreamBlock

**Test:**
- Add to page with all fields filled
- View page
- Hover image (see overlay)
- Should match wireframe

**Success Criteria:** Split layout works, stats float, hover overlay appears.

---

### Task 5: Fix HeroImageBlock Template

**What:** Make hero match wireframe lines 317-353.

**File:** `themes/theme_a/templates/sum_core/blocks/hero_image.html`

**Requirements:**
- Full screen: h-screen min-h-[700px]
- Background: absolute inset-0, image at 120% height with -translate-y-10
- Overlay: bg-black/60 (or based on block.overlay_opacity)
- Content: relative z-10, text-center, max-w-5xl, mt-20
- Status text: font-accent text-sage-oat text-xl italic
- Headline: font-display text-5xl md:text-7xl lg:text-8xl text-sage-linen
- Subheadline: text-sage-linen max-w-lg mx-auto text-base md:text-lg
- CTAs: flex flex-col sm:flex-row gap-6
- Primary CTA: bg-sage-terra text-white px-12 py-5 uppercase
- Secondary CTA: border border-sage-linen/30 with arrow icon

**Test:**
- Add HeroImageBlock to page
- Fill: status, headline, subheadline, 2 CTAs, background image
- View page
- Should be full screen, centered, two styled buttons
- Compare to wireframe visually

**Success Criteria:** Matches wireframe lines 317-353 exactly.

---

### Task 6: Fix PortfolioBlock Template

**What:** Horizontal scroll on mobile, new metadata.

**File:** `themes/theme_a/templates/sum_core/blocks/portfolio.html`

**Requirements:**
- Header: eyebrow (font-accent italic text-sage-terra) + heading
- Mobile: flex overflow-x-auto with gradient fade right edge
- Desktop: md:grid md:grid-cols-3
- Cards: min-w-[85vw] on mobile, aspect-[4/3] image
- Metadata: grid grid-cols-2 showing constraint/material/outcome
- Fallback to location/services if new fields empty
- Hover: image scale-105

**Test:**
- Add portfolio with 3 items
- Fill constraint/material/outcome
- View desktop: 3 columns
- View mobile: horizontal scroll with fade
- Hover: image scales

**Success Criteria:** Matches wireframe lines 527-591.

---

### Task 7-20: Continue Pattern

Each remaining task follows same structure:
- **What:** Description + wireframe reference
- **File:** Which file to edit/create
- **Requirements:** Specific implementation details
- **Test:** How to verify it works
- **Success Criteria:** What "done" looks like

[Would continue for all remaining blocks...]

---

## Part 6: Success Criteria & Acceptance

### Visual Match Checklist

For each wireframe page, verify:
- [ ] Layout matches (spacing, alignment, grid)
- [ ] Typography matches (fonts, sizes, weights)
- [ ] Colors match (using sage palette)
- [ ] Hover states work
- [ ] Mobile behavior correct
- [ ] Animations/transitions present

### Technical Checklist

- [ ] Fast iteration works (< 5 second feedback loop)
- [ ] All blocks exist and registered
- [ ] All fields exist in models
- [ ] No S&S branding hardcoded
- [ ] Branding uses SiteSettings
- [ ] Both demo commands work
- [ ] Migrations run successfully
- [ ] Test coverage adequate

### Handoff Checklist

- [ ] All 7 wireframe pages implemented
- [ ] Documentation updated
- [ ] Known issues documented
- [ ] Theme can be applied to new sites via sum init
- [ ] Client can customize via SiteSettings

---

## Part 7: Known Risks & Mitigation

### Risk 1: Scope Creep
**Risk:** Adding features not in wireframe.
**Mitigation:** Stick strictly to wireframe. Document deviations.

### Risk 2: Browser Compatibility
**Risk:** Tailwind classes don't work in older browsers.
**Mitigation:** Test in Chrome, Firefox, Safari. Document minimum versions.

### Risk 3: Performance
**Risk:** Large images, complex CSS slow page load.
**Mitigation:** Optimize images, test Lighthouse scores, set performance budgets.

### Risk 4: Accessibility Regression
**Risk:** New templates break keyboard navigation or screen readers.
**Mitigation:** Test with keyboard only, use axe DevTools, maintain ARIA labels.

### Risk 5: Responsive Breakage
**Risk:** Layout breaks at certain widths.
**Mitigation:** Test at 320px, 768px, 1024px, 1440px, 1920px widths.

---

## Part 8: Timeline & Resources

### Timeline Summary
- **Week 1:** Foundation + Homepage (40 hours)
- **Week 2:** Content Blocks + Interior Pages (40 hours)
- **Week 3:** Navigation + Blog + Polish (40 hours)
- **Total:** 120 hours / 3 weeks

### Required Resources
- **You:** Project oversight, visual QA, wireframe reference
- **AI Agents:** Implementation of templates, blocks, commands
- **Designer (optional):** Visual QA, wireframe clarification if needed

### Dependencies
- Wireframe files (✅ provided)
- blocks-reference.md (✅ provided)
- Working test_project (✅ exists)
- themes/theme_a/ directory (✅ exists per UNFUCK-PART-2)

---

## Part 9: How to Execute This Plan

### For You
1. Read this plan completely
2. Approve/modify timeline
3. Prioritize which pages to do first (homepage first is recommended)
4. Provide clarifications on any wireframe questions
5. Do visual QA after each phase

### For AI Agents
1. Work sequentially through tasks
2. Reference this plan + wireframe files + blocks-reference.md
3. Ask for clarification only if wireframe is ambiguous
4. Provide progress updates after each task
5. Run tests before marking task complete

### Daily Workflow
1. Pick next task from plan
2. Implement (code/template)
3. Test locally
4. Visual compare to wireframe
5. Mark complete or iterate
6. Move to next task

---

