# Work Order: Sage & Stone Site Seeder (v0.6.0)

---

## Parent

**Version Declaration:** (v0.6.0)

**Version Context:**
- **Platform/Core Version:** v0.6.0 (sum-platform, sum-core)
- **CLI Tool Version:** v2.0.0 (sum-cli)
- **Relationship:** CLI v2.0.0 is being developed AS PART OF platform v0.6.0 release
- **Related Work:** See #210 (CLI v2 Work Order) and #190 (CLI v2 subtasks)

---

## Branch

| Branch                     | Target          |
| -------------------------- | --------------- |
| `feature/sage-stone-seeder` | `release/0.6.0` |

```bash
git checkout release/0.6.0
git checkout -b feature/sage-stone-seeder
git push -u origin feature/sage-stone-seeder
```

---

## Objective

- [ ] Create management command `seed_sage_stone` that programmatically generates complete Sage & Stone site
- [ ] Implement all 7 page types from wireframes with full StreamField content
- [ ] Configure navigation (header mega menu + footer), branding, and site settings
- [ ] Generate placeholder images matching wireframe dimensions using PIL
- [ ] Ensure idempotent operation with proper Wagtail page handling
- [ ] Integrate with CLI v2.0.0 tooling (`sum init sage-and-stone --theme theme_a --seed-site`)

---

## Scope

### In Scope
1. Management command `seed_sage_stone` that creates:
   - All 7 page types from wireframe (Home, About, Services, Portfolio, Blog, Blog Posts, Legal)
   - Complete StreamField content with copy from wireframes
   - Navigation structure (header mega menu, footer)
   - Site settings and branding configuration
   - Blog categories and 7 sample articles
   - Placeholder images matching wireframe dimensions

2. Content fidelity to wireframe:
   - All copy text extracted and used
   - Block structure matching visual layout
   - Navigation hierarchy preserved

3. Idempotent operation:
   - Wagtail page creation uses parent+slug lookups with explicit updates
   - Simple models use get_or_create patterns
   - `--clear` flag for full reset when significant structure changes needed
   - Image generation outside transaction (see Architecture Decision)
   - DB operations in atomic block where appropriate

4. CLI v2.0.0 integration:
   - Command callable via `sum init sage-and-stone --seed-site` (CLI v2 tooling)
   - Coordinate with CLI v2 subtasks (#210, #190) for integration points
   - Works both as standalone management command and CLI-invoked seeder
   - Complements existing `seed_showroom` command

### Out of Scope
- Theme CSS/template modifications (theme concern)
- Form submission handling (uses existing infrastructure)
- Real image assets (use generated placeholders)
- Multi-site support (single site demo)
- Alert banner functionality (theme enhancement)

---

## Subtasks

| #   | Subtask                   | Description                          | Branch                                     | Status |
| --- | ------------------------- | ------------------------------------ | ------------------------------------------ | ------ |
| 1   | Site & Root Setup         | Site object, root page configuration | `feature/sage-stone-seeder/001-site-setup` | 🔲     |
| 2   | Image Generation          | PIL-based placeholder images         | `feature/sage-stone-seeder/002-images`     | 🔲     |
| 3   | Branding Configuration    | SiteSettings with colors, fonts      | `feature/sage-stone-seeder/003-branding`   | 🔲     |
| 4   | Navigation Structure      | Header mega menu + footer            | `feature/sage-stone-seeder/004-navigation` | 🔲     |
| 5   | Core Pages                | Home, About, Services, Portfolio     | `feature/sage-stone-seeder/005-pages`      | 🔲     |
| 6   | Blog Content              | Categories, index, 7 articles        | `feature/sage-stone-seeder/006-blog`       | 🔲     |
| 7   | Legal Pages               | Terms of Supply with sections        | `feature/sage-stone-seeder/007-legal`      | 🔲     |
| 8   | Tests & Documentation     | TDD test suite and usage docs        | `feature/sage-stone-seeder/008-tests-docs` | 🔲     |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Merge Plan

### Order

1. **Subtask 1** — Site & Root Setup establishes base site structure
2. **Subtask 2** — Image Generation creates assets (independent, can be parallel)
3. **Subtask 3** — Branding Configuration depends on site existing
4. **Subtask 4** — Navigation Structure depends on site + pages for linking
5. **Subtask 5** — Core Pages creates main page hierarchy
6. **Subtask 6** — Blog Content depends on categories and site structure
7. **Subtask 7** — Legal Pages (independent, can be parallel with 5-6)
8. **Subtask 8** — Tests & Documentation (TDD throughout, final integration tests)

### Hot Files

| File                                            | Owner      | Notes                                      |
| ----------------------------------------------- | ---------- | ------------------------------------------ |
| `seed_sage_stone.py`                            | All tasks  | Single command file, coordinate changes    |
| `boilerplate/home/management/commands/`         | Subtask 1  | Command location, create directory first   |
| Generated images in `media/`                    | Subtask 2  | Coordinate with pages that reference them  |

---

## Affected Paths

```
cli/sum_cli/boilerplate/project_name/home/management/commands/
└── seed_sage_stone.py

test_project/home/management/commands/
└── seed_sage_stone.py  # For integration testing

# Generated content (runtime)
media/original_images/SS_*.png
```

---

## Verification

### After Each Task Merge

```bash
git checkout feature/sage-stone-seeder
git pull origin feature/sage-stone-seeder
source .venv/bin/activate
make lint && make test
```

### Before Feature PR

```bash
git fetch origin
git rebase origin/release/0.6.0
source .venv/bin/activate
make lint && make test

# Manual verification
python manage.py seed_sage_stone
python manage.py runserver
# Visit site and verify content matches wireframes
```

---

## Risk

**Level:** Medium

**Factors:**
- Complex Wagtail page tree management with revisions
- Large StreamField content creation (potential for data structure errors)
- Image generation performance with 20+ placeholder images
- Idempotency challenges with tree-structured data
- Dependency on Theme A being complete and correct

**Mitigation:**
- Use parent+slug lookups for proper tree handling (documented in Architecture)
- Image generation outside transaction to prevent orphaned files
- Thorough testing with `--clear` flag between runs
- Content mapping review before implementation (documented separately)
- Comprehensive integration tests for full seed → verify workflow
- Reference existing `seed_showroom` patterns where applicable

---

## Labels

- [ ] `type:work-order`
- [ ] `component:cli`
- [ ] `risk:medium`
- [ ] Milestone: `v0.6.0`

---

## Definition of Done

- [ ] All 8 subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] Integration test verifies full site creation
- [ ] Manual QA confirms content matches wireframes
- [ ] `seed_sage_stone --clear` works without errors
- [ ] Documentation updated with usage instructions
- [ ] Feature branch merged to `release/0.6.0` (PR approved)
- [ ] No regressions to existing `seed_showroom` command

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
        # Image generation OUTSIDE transaction to avoid orphaned files on rollback
        self.create_images()        # Subtask 2

        # Database operations in transaction
        with transaction.atomic():
            self.setup_site()           # Subtask 1
            self.create_branding()      # Subtask 3
            self.create_navigation()    # Subtask 4
            self.create_pages()         # Subtask 5
            self.create_blog_content()  # Subtask 6
            self.finalize()             # Subtask 7
```

### Idempotency Strategy

**Wagtail Pages:**
Wagtail's tree structure and revision system require special handling:

```python
# Don't use simple get_or_create - it doesn't account for parent/tree position
# BAD: HomePage.objects.get_or_create(slug="home")

# GOOD: Look up by parent + slug, update if exists
try:
    home_page = root.get_children().type(HomePage).get(slug="home")
    # Update fields if needed
    home_page.title = "Updated Title"
    home_page.save_revision().publish()
except HomePage.DoesNotExist:
    home_page = HomePage(...)
    root.add_child(instance=home_page)
    home_page.save_revision().publish()
```

**Simple Models:**
Settings, navigation, snippets can use standard get_or_create:
```python
site_settings, created = SiteSettings.objects.get_or_create(
    site=site,
    defaults={...}
)
if not created:
    # Update fields
    site_settings.primary_color = "#..."
    site_settings.save()
```

**When to Use `--clear`:**
- Significant page hierarchy changes (reordering, parent changes)
- Testing from clean slate
- Structure changes that can't be handled by update logic

### Command Location Decision

**Decision: Boilerplate placement (not core)**

Rationale:
- This seeder is site-specific (Sage & Stone demo), not reusable core functionality
- Similar to `seed_showroom`, it's a demonstration/starter content tool
- Core should contain only reusable, site-agnostic components
- Clients can customize or remove this command as needed

**Primary Location:**
```
cli/sum_cli/boilerplate/project_name/home/management/commands/
└── seed_sage_stone.py
```

**Testing Support:**
```
test_project/home/management/commands/
└── seed_sage_stone.py  # Symlink or copy for integration tests
```

**Core Helpers (if needed):**
If common image generation or seeding utilities emerge across multiple seeders, extract to:
```
core/sum_core/utils/
└── seeding.py  # Reusable helpers only
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

## Success Criteria

1. **Functional Site:** Running `seed_sage_stone` produces a navigable, styled website
2. **Content Fidelity:** All wireframe copy present and correctly placed
3. **Navigation Complete:** All menu items clickable, linking to correct pages
4. **Visual Match:** Site structure matches wireframe layout (theme handles styling)
5. **Idempotent:** Can re-run without errors or duplicates (with proper update logic)
6. **Documented:** Clear usage instructions and customization guidance

---

## Testing Strategy

1. **Unit Tests:** Each content creation function in isolation
2. **Integration Test:** Full seed → site structure verification
3. **Manual QA:** Visual comparison with wireframe
4. **Regression:** Ensure existing `seed_showroom` still works
5. **Idempotency Test:** Run twice, verify single site exists with updated content
6. **Clear Flag Test:** Run with `--clear`, verify clean slate rebuild

---

## Target Usage

```bash
# Primary: CLI v2.0.0 integration (part of platform v0.6.0)
sum init sage-and-stone --theme theme_a --seed-site

# Alternative: Direct management command
python manage.py seed_sage_stone [--clear] [--images-only] [--content-only]
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
- [Subtask 8: Tests & Documentation](./subtask-008-tests-docs.md)

---

## Dependencies

- Theme A must be complete and applied
- sum_core blocks and page types available
- PIL/Pillow for placeholder image generation
- Database migrated with all sum_core models
- CLI v2.0.0 tooling for integration (coordinate with #210, #190)
  - `sum init` command with `--seed-site` flag
  - Seeder orchestration framework from CLI v2 subtasks
