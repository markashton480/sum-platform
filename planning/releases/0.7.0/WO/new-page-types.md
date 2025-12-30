# WO: New Page Types (v0.7.0)

## Metadata

- **Version:** v0.7.0
- **Component:** pages
- **Priority:** P1 (If Time Permits)
- **Branch:** `feature/page-types`
- **Parent VD:** #TBD
- **Issue:** #TBD

---

## Description

Add purpose-built page types to reduce StandardPage overuse. The current approach of fitting everything into StandardPage isn't working well - editors need structured, opinionated page types with appropriate defaults and constraints. This work order adds AboutPage and LandingPage as minimum viable additions, with ContactPage and FAQPage if cheap to add.

**Why this matters:**
- StandardPage is too generic for structured content
- Editors waste time configuring common patterns
- Purpose-built pages enable better seeding and demos
- Required for Theme B/C to have meaningful test content

**Priority Note:** This is P1 (optional) - only proceed if P0 items are complete or on track.

---

## Acceptance Criteria

- [ ] AboutPage type with team, mission, timeline structure
- [ ] LandingPage type with conversion-focused blocks
- [ ] Both page types available in Wagtail admin
- [ ] Theme A templates for both page types
- [ ] Theme B templates (if Theme B exists)
- [ ] Seeder can generate example pages
- [ ] ContactPage and FAQPage (stretch, if cheap)

---

## Deliverables

1. **AboutPage**
   - Pre-configured sections: Mission, Team, Values, History
   - TeamMemberBlock for staff profiles
   - TimelineBlock for company milestones
   - StatsBlock for achievements

2. **LandingPage**
   - Hero section (required)
   - Benefits/features section
   - Social proof/testimonials
   - Single CTA focus (conversion-optimized)

3. **ContactPage (Stretch)**
   - Contact form integration
   - Location/map support
   - Business hours display
   - Social media links

4. **FAQPage (Stretch)**
   - FAQ item blocks (Q&A pairs)
   - Category grouping
   - Accordion UI support

5. **Theme Templates**
   - Templates for each page type in each theme

---

## Technical Approach

### Page Model Pattern

All new page types should inherit from existing mixins:

```python
from wagtail.models import Page
from sum_core.pages.mixins import SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin

class AboutPage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    # Use restricted StreamField, not full PageStreamBlock
    body = StreamField([
        ('mission', MissionBlock()),
        ('team', TeamSectionBlock()),
        ('timeline', TimelineBlock()),
        ('stats', StatsBlock()),
        ('rich_text', RichTextBlock()),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    template = 'sum_core/pages/about_page.html'
```

### Block Definitions

New supporting blocks should be created in `core/sum_core/blocks/`:

- `TeamMemberBlock` - photo, name, title, bio
- `TeamSectionBlock` - heading + list of TeamMemberBlock
- `TimelineItemBlock` - year, title, description
- `TimelineBlock` - list of TimelineItemBlock
- `StatsItemBlock` - number, label, description
- `StatsBlock` - list of StatsItemBlock

---

## Boundaries

### Do

- Create AboutPage and LandingPage (minimum)
- Create necessary supporting blocks
- Add templates for Theme A (and Theme B if exists)
- Add seeder support for new page types
- Keep page types focused and opinionated
- ContactPage/FAQPage only if genuinely cheap

### Do NOT

- Create partial or placeholder page types
- Add more than 4 page types total
- Over-engineer with too many options
- Change StandardPage behavior
- Add page types not usable without theme templates

---

## Subtasks

### TASK-001: Create Supporting Blocks

**Description:**
Create the new blocks needed for AboutPage and LandingPage: TeamMemberBlock, TeamSectionBlock, TimelineBlock, StatsBlock, etc.

**Acceptance Criteria:**
- [ ] TeamMemberBlock with photo, name, title, bio
- [ ] TeamSectionBlock wrapping multiple team members
- [ ] TimelineItemBlock and TimelineBlock
- [ ] StatsItemBlock and StatsBlock
- [ ] All blocks render in admin preview

**Boundaries:**
- Do: Keep blocks simple and focused
- Do: Use existing block patterns
- Do NOT: Add overly complex options
- Do NOT: Create one-off blocks

**Branch:** `feature/page-types/001-supporting-blocks`

---

### TASK-002: Create AboutPage Model

**Description:**
Create AboutPage model with structured sections for team, mission, timeline, and stats using the supporting blocks.

**Acceptance Criteria:**
- [ ] AboutPage model with restricted StreamField
- [ ] Migration created and tested
- [ ] Page type appears in Wagtail admin
- [ ] Parent/child page type rules configured
- [ ] SEO and OpenGraph fields included

**Boundaries:**
- Do: Use existing mixins
- Do: Restrict StreamField to relevant blocks
- Do NOT: Allow full PageStreamBlock
- Do NOT: Add custom admin features

**Branch:** `feature/page-types/002-about-page-model`

---

### TASK-003: Create LandingPage Model

**Description:**
Create LandingPage model optimized for conversion with hero, benefits, testimonials, and focused CTA.

**Acceptance Criteria:**
- [ ] LandingPage model with conversion-focused structure
- [ ] Hero section (required)
- [ ] Benefits/features section
- [ ] Testimonials section
- [ ] CTA section (uses CTABlock if available)
- [ ] Migration created and tested

**Boundaries:**
- Do: Keep conversion-focused
- Do: Use existing blocks where possible
- Do NOT: Add A/B testing fields
- Do NOT: Add analytics integration

**Branch:** `feature/page-types/003-landing-page-model`

---

### TASK-004: AboutPage Theme Templates

**Description:**
Create AboutPage templates for Theme A (and Theme B if it exists).

**Acceptance Criteria:**
- [ ] Theme A about_page.html template
- [ ] Team section template partial
- [ ] Timeline template partial
- [ ] Stats template partial
- [ ] Theme B template (if Theme B exists)

**Boundaries:**
- Do: Follow theme design patterns
- Do: Make sections visually distinct
- Do NOT: Add JavaScript interactions
- Do NOT: Create Theme-specific page features

**Branch:** `feature/page-types/004-about-templates`

---

### TASK-005: LandingPage Theme Templates

**Description:**
Create LandingPage templates for Theme A (and Theme B if it exists).

**Acceptance Criteria:**
- [ ] Theme A landing_page.html template
- [ ] Hero rendering optimized for conversion
- [ ] Benefits section template
- [ ] Testimonials section template
- [ ] Theme B template (if exists)

**Boundaries:**
- Do: Optimize for conversion (clear visual hierarchy)
- Do: Make CTA prominent
- Do NOT: Add tracking pixels in template
- Do NOT: Add popup/modal behavior

**Branch:** `feature/page-types/005-landing-templates`

---

### TASK-006: Page Type Seeder Support

**Description:**
Add seeder profiles/data for generating example AboutPage and LandingPage content.

**Acceptance Criteria:**
- [ ] Seeder creates sample AboutPage with team, timeline, stats
- [ ] Seeder creates sample LandingPage with full content
- [ ] Both themes supported if Theme B exists
- [ ] Demo content is compelling/realistic

**Boundaries:**
- Do: Create realistic demo content
- Do: Test with both themes
- Do NOT: Create minimal/placeholder content
- Do NOT: Duplicate content across themes

**Branch:** `feature/page-types/006-seeder-support`

---

### TASK-007: ContactPage (Stretch)

**Description:**
If time permits, create ContactPage with form, location, hours, and social links.

**Acceptance Criteria:**
- [ ] ContactPage model with structured sections
- [ ] Contact form using DynamicFormBlock
- [ ] Location section
- [ ] Business hours display
- [ ] Theme templates

**Boundaries:**
- Do: Only attempt if TASK-001 through 006 complete
- Do: Keep scope minimal
- Do NOT: Add Google Maps integration
- Do NOT: Add complex form routing

**Branch:** `feature/page-types/007-contact-page` (stretch)

---

### TASK-008: FAQPage (Stretch)

**Description:**
If time permits, create FAQPage with Q&A structure and accordion UI.

**Acceptance Criteria:**
- [ ] FAQPage model with FAQ sections
- [ ] FAQItemBlock (question + answer)
- [ ] Category/grouping support
- [ ] Accordion UI in templates
- [ ] Schema.org FAQ markup

**Boundaries:**
- Do: Only attempt if other tasks complete
- Do: Add schema markup for SEO
- Do NOT: Add complex categorization
- Do NOT: Add search within FAQs

**Branch:** `feature/page-types/008-faq-page` (stretch)

---

## Merge Order

1. TASK-001 (Supporting Blocks) - foundational
2. TASK-002 (AboutPage Model) - depends on 001
3. TASK-003 (LandingPage Model) - depends on 001, can parallel with 002
4. TASK-004 (About Templates) - depends on 002
5. TASK-005 (Landing Templates) - depends on 003
6. TASK-006 (Seeder) - depends on 002-005
7. TASK-007 (ContactPage) - stretch, only if 001-006 done
8. TASK-008 (FAQPage) - stretch, only if 001-006 done

---

## Estimated Effort

| Task | Estimate | Risk |
| ---- | -------- | ---- |
| TASK-001 | 3-4 hours | Low |
| TASK-002 | 2-3 hours | Low |
| TASK-003 | 2-3 hours | Low |
| TASK-004 | 3-4 hours | Medium |
| TASK-005 | 3-4 hours | Medium |
| TASK-006 | 2-3 hours | Low |
| TASK-007 | 4-5 hours | Medium (stretch) |
| TASK-008 | 4-5 hours | Medium (stretch) |

**Total (minimum):** 15-21 hours
**Total (with stretch):** 23-31 hours

---

## Dependencies

- WO1 (Multi-theme) should be in progress for Theme B templates
- WO3 (CTABlock) should be available for LandingPage CTA section

---

## Notes

- This is P1 - don't delay P0 work for this
- AboutPage and LandingPage are the minimum viable set
- ContactPage and FAQPage are nice-to-have stretch goals
- Focus on making the core pages excellent before adding more
- Supporting blocks may be reusable in StandardPage too
