# Sage & Stone Site Seeder — Work Order

## Overview

**Objective:** Create management command(s) to programmatically generate the Sage & Stone bespoke kitchen website as a fully functioning Wagtail site, based on the wireframes in `docs/dev/design/wireframes/sage-and-stone/`.

**Target Usage:**
```bash
# Future CLI v2 integration
sum init sage-and-stone --theme theme_a --seed-site

# Current: Management command approach
python manage.py seed_sage_stone [--clear] [--images-only] [--content-only]
```

**Branch:** `feature/sage-stone-seeder` → `release/2.0.0`

**Dependencies:**
- Theme A must be complete and applied
- sum_core blocks and page types available
- PIL/Pillow for placeholder image generation

---

## Scope

### In Scope
1. Management command `seed_sage_stone` that creates:
   - All 7 page types from wireframe
   - Complete StreamField content with copy from wireframes
   - Navigation structure (header mega menu, footer)
   - Site settings and branding configuration
   - Blog categories
   - Placeholder images matching wireframe dimensions

2. Content fidelity to wireframe:
   - All copy text extracted and used
   - Block structure matching visual layout
   - Navigation hierarchy preserved

3. Idempotent operation:
   - Safe to re-run (get_or_create patterns)
   - `--clear` flag for full reset
   - Atomic transactions

### Out of Scope
- Theme CSS/template modifications
- Form submission handling (forms use existing infrastructure)
- Real image assets (use generated placeholders)
- CLI v2 integration (Phase 2)
- Multi-site support

---

## Architecture Decision

### Single vs. Multiple Commands

**Decision: Single unified command with modular internal structure**

Rationale:
- Sage & Stone is a complete site demonstration, not component library
- Dependencies between content (e.g., blog categories → blog posts)
- Simpler user experience: one command, one site
- Internal modularity allows selective execution via flags

### Command Structure

```python
# seed_sage_stone.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            self.setup_site()           # Subtask 1
            self.create_images()        # Subtask 2
            self.create_branding()      # Subtask 3
            self.create_navigation()    # Subtask 4
            self.create_pages()         # Subtask 5
            self.create_blog_content()  # Subtask 6
            self.finalize()             # Subtask 7
```

---

## Page Type Mapping

| Wireframe Page | sum_core Model | Notes |
|----------------|----------------|-------|
| Home | `HomePage` (client) | Custom model in `home/models.py` |
| About | `StandardPage` | Uses core StreamField blocks |
| Services | `StandardPage` | Complex layout via blocks |
| Portfolio | `StandardPage` | PortfolioBlock with items |
| Blog List | `BlogIndexPage` | Core model, needs Categories |
| Blog Article | `BlogPostPage` | Multiple articles needed |
| Terms of Supply | `LegalPage` | Core model with sections |

---

## Block Mapping Summary

| Wireframe Section | sum_core Block | Gap? |
|-------------------|----------------|------|
| Hero (image overlay) | `HeroImageBlock` | ✅ |
| Hero (gradient) | `HeroGradientBlock` | ✅ |
| Operational Proof Strip | `StatsBlock` | ✅ |
| Manifesto | `ManifestoBlock` | ✅ |
| Services Grid | `ServiceCardsBlock` | ✅ |
| Provenance Signature | `FeaturedCaseStudyBlock` + custom | ⚠️ Modal needs consideration |
| Portfolio Grid | `PortfolioBlock` | ✅ |
| Featured Case Study | `FeaturedCaseStudyBlock` | ✅ |
| FAQ Accordion | `FAQBlock` | ✅ |
| Contact Form | `ContactFormBlock` | ✅ |
| Team Grid | `TeamMemberBlock` | ✅ |
| Process Timeline | `ProcessStepsBlock` / `TimelineBlock` | ✅ |
| Trust Badges | `TrustStripBlock` (logos) | ✅ |
| Testimonials | `TestimonialsBlock` | ✅ |
| Gallery | `GalleryBlock` | ✅ |
| Legal Sections | `LegalSectionBlock` | ✅ |
| Editorial Header | `EditorialHeaderBlock` | ✅ |
| Rich Text | `RichTextContentBlock` | ✅ |
| Quote | `QuoteBlock` / `SocialProofQuoteBlock` | ✅ |
| Buttons | `ButtonGroupBlock` | ✅ |
| Lead Magnet (email signup) | Custom or `ContactFormBlock` | ⚠️ Simplified |

---

## Difficult / Fiddly Bits

### 1. Provenance Brass Plate (High Complexity)
**Wireframe:** Interactive brass plate modal showing maker info, GPS coordinates, completion date.

**Challenge:** No direct block equivalent. This is a presentation feature.

**Resolution:** Use `FeaturedCaseStudyBlock` with appropriate content. The brass plate visual effect is a theme/CSS concern, not content. Seed the data; theme handles presentation.

### 2. Mega Menu Navigation
**Wireframe:** 3-level nested navigation with featured image.

**Challenge:** HeaderNavigation `menu_items` supports nested `SubmenuItemBlock` → `SubSubmenuItemBlock`.

**Resolution:** ✅ Fully supported. Create full hierarchy:
```
Kitchens (top)
├── Collections
│   ├── The Heritage
│   ├── The Modernist
│   └── The Utility
├── Fitted Joinery
│   ├── Larder Cupboards
│   ├── Island Units
│   └── ...
└── Featured (The Cotswold Barn)
```

### 3. Blog Category Filtering
**Wireframe:** Filter tabs (All, Commission Stories, Material Science, The Workshop)

**Challenge:** Categories are snippets that must exist before blog posts.

**Resolution:** Create `Category` snippets first, then reference in `BlogPostPage.category`. BlogIndexPage template handles filtering via query params.

### 4. Alert Banner
**Wireframe:** "Waitlist open for Autumn 2026 Commissions" dismissible banner.

**Challenge:** No explicit block for site-wide alerts.

**Resolution:** Two options:
- **Option A:** Add to SiteSettings (new field, out of scope)
- **Option B:** Hardcoded in theme header template (theme concern)
- **Recommendation:** Skip for seed, document as theme enhancement

### 5. Mobile 3-Level Drill-Down Menu
**Wireframe:** Complex mobile navigation with back buttons.

**Challenge:** This is entirely a theme/JS concern.

**Resolution:** Same navigation data powers both desktop mega menu and mobile drill-down. Theme handles presentation logic.

### 6. Sticky Table of Contents (Blog Article, Terms)
**Wireframe:** Sidebar ToC that scrolls with content.

**Challenge:** `TableOfContentsBlock` exists but is manual. Auto-generation from headings is a theme/JS feature.

**Resolution:** Seed `TableOfContentsBlock` with correct anchor IDs. Theme JS can enhance with scroll-spy.

### 7. Newsletter Signup (Blog Sidebar)
**Wireframe:** "The Ledger" email subscription form.

**Challenge:** No dedicated newsletter block.

**Resolution:** Use `ContactFormBlock` with modified labels, or document as future enhancement. Lead capture still works.

### 8. Image Placeholders
**Wireframe:** References 20+ images from Unsplash.

**Challenge:** Cannot bundle copyrighted images.

**Resolution:** Generate colored placeholder images with PIL:
- Match aspect ratios from wireframe
- Use brand colors (sage-black, sage-moss, etc.)
- Include text labels ("Hero Image", "Team Photo 1", etc.)

---

## Subtask Breakdown

| # | Subtask | Description | Est. Complexity |
|---|---------|-------------|-----------------|
| 1 | Site & Root Setup | Create Site, set root, configure basics | Low |
| 2 | Image Generation | PIL-based placeholder images | Medium |
| 3 | Branding Configuration | SiteSettings with colors, fonts, info | Low |
| 4 | Navigation Structure | Header mega menu + footer | Medium |
| 5 | Core Pages | Home, About, Services, Portfolio | High |
| 6 | Blog Content | Categories + Index + 7 Articles | Medium |
| 7 | Legal Pages | Terms of Supply with sections | Low |

---

## Success Criteria

1. **Functional Site:** Running `seed_sage_stone` produces a navigable, styled website
2. **Content Fidelity:** All wireframe copy present and correctly placed
3. **Navigation Complete:** All menu items clickable, linking to correct pages
4. **Visual Match:** Site structure matches wireframe layout (theme handles styling)
5. **Idempotent:** Can re-run without errors or duplicates
6. **Documented:** Clear instructions for customization

---

## Testing Strategy

1. **Unit Tests:** Each content creation function in isolation
2. **Integration Test:** Full seed → site structure verification
3. **Manual QA:** Visual comparison with wireframe
4. **Regression:** Ensure existing `seed_showroom` still works

---

## File Deliverables

```
core/sum_core/
└── test_project/
    └── home/
        └── management/
            └── commands/
                └── seed_sage_stone.py

# Or if packaged in boilerplate:
cli/sum_cli/boilerplate/project_name/home/management/commands/
└── seed_sage_stone.py
```

---

## Related Documents

- [Content Mapping](./content-mapping.md) — Detailed wireframe → block mapping
- [Subtask 1: Site Setup](./subtask-001-site-setup.md)
- [Subtask 2: Image Generation](./subtask-002-image-generation.md)
- [Subtask 3: Branding](./subtask-003-branding.md)
- [Subtask 4: Navigation](./subtask-004-navigation.md)
- [Subtask 5: Core Pages](./subtask-005-core-pages.md)
- [Subtask 6: Blog Content](./subtask-006-blog-content.md)
- [Subtask 7: Legal Pages](./subtask-007-legal-pages.md)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Block type mismatch | High | Content mapping review before implementation |
| Theme not supporting all blocks | Medium | Theme A audit for block template coverage |
| Image generation performance | Low | Lazy generation, caching |
| Complex navigation breaking | Medium | Thorough testing of menu hierarchy |

---

## Timeline Estimate

**Phase 1 (Core):** Subtasks 1-5 — Functional site with main pages
**Phase 2 (Content):** Subtasks 6-7 — Blog and legal content
**Phase 3 (Polish):** Testing, documentation, edge cases

---

## Approval

- [ ] Architecture reviewed
- [ ] Content mapping validated
- [ ] Theme compatibility confirmed
- [ ] Ready for implementation
