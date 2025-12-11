# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

Please carefully review the task details in @[docs/dev/M2/M2-005.md] and implement.

*Viewed [M2-005.md](file:///home/mark/workspaces/tradesite/docs/dev/M2/M2-005.md) *

### Planner Response

Now let me explore the existing codebase structure to understand the patterns and existing blocks:

*Listed directory [blocks](file:///home/mark/workspaces/tradesite/core/sum_core/blocks) *

*Viewed [gallery_design.html](file:///home/mark/workspaces/tradesite/docs/dev/design/gallery_design.html) *

*Listed directory [blocks](file:///home/mark/workspaces/tradesite/tests/blocks) *

*Listed directory [css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css) *

### Planner Response

Now let me examine the existing block patterns to understand how they're structured:

*Viewed [testimonials.py](file:///home/mark/workspaces/tradesite/core/sum_core/blocks/testimonials.py) *

*Viewed [base.py](file:///home/mark/workspaces/tradesite/core/sum_core/blocks/base.py) *

*Viewed [__init__.py](file:///home/mark/workspaces/tradesite/core/sum_core/blocks/__init__.py) *

*Viewed [test_testimonials_block.py](file:///home/mark/workspaces/tradesite/tests/blocks/test_testimonials_block.py) *

### Planner Response

Now let me look at the test_page_streamblock.py and check the test templates folder for any integration tests:

*Viewed [test_page_streamblock.py](file:///home/mark/workspaces/tradesite/tests/blocks/test_page_streamblock.py) *

*Listed directory [templates](file:///home/mark/workspaces/tradesite/tests/templates) *

*Viewed [tokens.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/tokens.css) *

*Viewed [main.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/main.css) *

### Planner Response

Let me also check the existing testimonials template and the homepage rendering test and conftest to understand these patterns:

*Viewed [testimonials.html](file:///home/mark/workspaces/tradesite/core/sum_core/templates/sum_core/blocks/testimonials.html) *

*Viewed [test_homepage_rendering.py](file:///home/mark/workspaces/tradesite/tests/templates/test_homepage_rendering.py) *

*Viewed [conftest.py](file:///home/mark/workspaces/tradesite/tests/conftest.py) *

### Planner Response

Now I have a complete understanding of the codebase patterns and requirements. Let me implement the M2-005 Gallery Block task. I'll create:

1. **`core/sum_core/blocks/gallery.py`** - The Gallery blocks
2. **`core/sum_core/templates/sum_core/blocks/gallery.html`** - The template
3. **`core/sum_core/static/sum_core/css/components.gallery.css`** - The CSS partial
4. **Update [core/sum_core/blocks/base.py](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/base.py:0:0-0:0)** - Add gallery to PageStreamBlock
5. **Update [core/sum_core/blocks/__init__.py](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/__init__.py:0:0-0:0)** - Export gallery blocks
6. **Update [core/sum_core/static/sum_core/css/main.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/main.css:0:0-0:0)** - Import gallery CSS
7. **`tests/blocks/test_gallery_block.py`** - Unit tests
8. **Update [tests/blocks/test_page_streamblock.py](cci:7://file:///home/mark/workspaces/tradesite/tests/blocks/test_page_streamblock.py:0:0-0:0)** - Add gallery assertion
9. **Add integration test for gallery rendering**

Let me create all these files:

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

### Planner Response

Now let me update the existing files to integrate the gallery block:

*Edited relevant file*

*Edited relevant file*

### Planner Response

Now let me update the [__init__.py](cci:7://file:///home/mark/workspaces/tradesite/tests/blocks/__init__.py:0:0-0:0) to export the gallery blocks:

*Edited relevant file*

*Edited relevant file*

### Planner Response

Now let me update the main.css to import the gallery component CSS:

*Edited relevant file*

### Planner Response

Now let me create the test files:

*Edited relevant file*

### Planner Response

Now let me update the test_page_streamblock.py to include the gallery assertion:

*Edited relevant file*

### Planner Response

Now let me create the integration test for gallery rendering. First, let me check if there's a way to create test images in the existing test setup:

*Searched filesystem*

*Grep searched codebase*

### Planner Response

Let me check the service cards test to understand how to create test images:

*Viewed [test_service_cards_block.py](file:///home/mark/workspaces/tradesite/tests/blocks/test_service_cards_block.py) *

### Planner Response

Now I can create a proper integration test for the gallery block. Let me add it to the homepage rendering test file:

*Edited relevant file*

### Planner Response

Now let me run the tests to verify everything works:

*User accepted the command `make test`*

*Checked command status*

### Planner Response

I need to fix a few issues. Let me check the CharBlock for max_length and fix the integration test image passing:

*Grep searched codebase*

### Planner Response

In Wagtail's CharBlock, the [max_length](cci:1://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:111:4-115:46) is a config parameter, not an attribute. Let me check how to access it properly:

*User accepted the command `python -c "from wagtail import blocks; b = blocks.CharBlock(max_length=255); print(dir(b))"`*

### Planner Response

Let me fix the tests. The issue is that CharBlock uses validators rather than a direct [max_length](cci:1://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:111:4-115:46) attribute, and the integration test needs to pass image objects rather than PKs. Let me update the tests:

*Edited relevant file*

### Planner Response

Now let me fix the integration test - the issue is that we need to pass actual image objects, not just PKs. Let me view and fix the test:

*Viewed [test_homepage_rendering.py](file:///home/mark/workspaces/tradesite/tests/templates/test_homepage_rendering.py) *

### Planner Response

Let me look at how the test_testimonials_block or other tests with images handle this:

*Grep searched codebase*

### Planner Response

Let me check how page body data with images works in other tests:

*Grep searched codebase*

### Planner Response

The issue might be that when assigning to a StreamField, we need to pass the actual Image object, not just a PK. Let me fix the integration test:

*Edited relevant file*

### Planner Response

Now let's run the tests again:

*User accepted the command `make test`*

*Checked command status*

### Planner Response

All 56 tests are passing. Now let me also run the linter to make sure everything meets the code quality standards:

*User accepted the command `make lint`*

### Planner Response

There are some linting issues with whitespace and unused imports. Let me fix the files I created/modified:

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

### Planner Response

Now let me run lint and test again:

*User accepted the command `make lint`*

### Planner Response

The lint errors I'm seeing are pre-existing issues in other files (not the gallery files). The errors are in:
- [branding_tags.py](cci:7://file:///home/mark/workspaces/tradesite/tests/branding/test_branding_tags.py:0:0-0:0) - ambiguous variable name `l` (pre-existing)
- [test_hero_blocks.py](cci:7://file:///home/mark/workspaces/tradesite/tests/blocks/test_hero_blocks.py:0:0-0:0) - unused variables (pre-existing)
- [test_service_cards_block.py](cci:7://file:///home/mark/workspaces/tradesite/tests/blocks/test_service_cards_block.py:0:0-0:0) - unused variable (pre-existing)

All my gallery-related changes are now clean. Let me verify by running lint specifically on my new files:

*User accepted the command `ruff check core/sum_core/blocks/gallery.py tests/blocks/test_gallery_block.py core/sum_core/templates/sum_core/blocks/gallery.html core/sum_core/static/sum_core/css/components.gallery.css`*

### Planner Response

Ruff is trying to parse the HTML templates as Python, which of course fails. Let me check just the Python files:

*User accepted the command `ruff check core/sum_core/blocks/gallery.py tests/blocks/test_gallery_block.py`*

### Planner Response

My new Python files pass all lint checks. Let me run the tests one more time to confirm everything is working:

*User accepted the command `make test`*

*Checked command status*

### Planner Response

All **56 tests pass**. The implementation is complete. Let me provide a summary of what was implemented:

---

## ✅ M2-005 Gallery Block Implementation Complete

I've successfully implemented the **Gallery Block** feature as specified in M2-005. Here's a summary of what was created/modified:

### New Files Created

| File | Purpose |
|------|---------|
| [core/sum_core/blocks/gallery.py](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/gallery.py:0:0-0:0) | **GalleryImageBlock** and **GalleryBlock** definitions with proper Meta, icons, labels, and constraints (1-24 images) |
| [core/sum_core/templates/sum_core/blocks/gallery.html](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/templates/sum_core/blocks/gallery.html:0:0-0:0) | Semantic HTML template using `<figure>`/`<figcaption>`, design token utility classes, lazy loading, and alt text fallback |
| [core/sum_core/static/sum_core/css/components.gallery.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/components.gallery.css:0:0-0:0) | Premium responsive gallery CSS using tokens (no hardcoded hex/fonts) with mobile carousel → 2-col tablet → 3-col desktop + editorial stagger effect |
| [tests/blocks/test_gallery_block.py](cci:7://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:0:0-0:0) | Unit tests for block structure, field requirements, constraints, and meta attributes |

### Modified Files

| File | Change |
|------|--------|
| [core/sum_core/blocks/base.py](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/base.py:0:0-0:0) | Added [GalleryBlock](cci:2://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/gallery.py:32:0-65:49) import and registered it in [PageStreamBlock](cci:2://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/base.py:24:0-61:85) under `group="Sections"` |
| [core/sum_core/blocks/__init__.py](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/__init__.py:0:0-0:0) | Exported [GalleryBlock](cci:2://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/gallery.py:32:0-65:49) and [GalleryImageBlock](cci:2://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/gallery.py:12:0-29:31) in `__all__` |
| [core/sum_core/static/sum_core/css/main.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/main.css:0:0-0:0) | Added `@import "components.gallery.css"` to the CSS bundle |
| [tests/blocks/test_page_streamblock.py](cci:7://file:///home/mark/workspaces/tradesite/tests/blocks/test_page_streamblock.py:0:0-0:0) | Added assertion for "gallery" in `PageStreamBlock.child_blocks` |
| [tests/templates/test_homepage_rendering.py](cci:7://file:///home/mark/workspaces/tradesite/tests/templates/test_homepage_rendering.py:0:0-0:0) | Added integration test verifying gallery rendering with 3 images, alt text fallback, and caption behaviour |

### Acceptance Criteria Met

✅ **Editor Experience**: Gallery block available in Wagtail admin under "Sections" group with image icon  
✅ **1-24 Images**: Enforced via ListBlock `min_num=1`, `max_num=24`  
✅ **Optional Fields**: [alt_text](cci:1://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:103:4-108:53) and [caption](cci:1://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:110:4-115:52) on each image  
✅ **Rendering**: Semantic `<section class="section gallery">` with `.gallery__grid` and `.gallery__item`  
✅ **Alt Text Fallback**: Falls back to `item.image.title` if [alt_text](cci:1://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:103:4-108:53) is blank  
✅ **Responsive Grid**: 1-col mobile → 2-col tablet → 3-col desktop  
✅ **No Hardcoded Values**: All CSS uses design tokens (`--space-*`, `--font-*`, etc.)  
✅ **Tests**: All 56 tests pass including new gallery-specific tests  

### Design Features

The gallery follows the reference design ([gallery_design.html](cci:7://file:///home/mark/workspaces/tradesite/docs/dev/design/gallery_design.html:0:0-0:0)) with:
- Premium eyebrow/heading/intro header styling
- Mobile horizontal scroll carousel with snap-scroll
- Editorial stagger effect on desktop (2nd column offset down)
- Subtle hover zoom effect on images
- Consistent use of design tokens throughout

### User Input

Can we change the card title to rich text so that we can italisise words like in the reference design? Please see @[core/sum_core/blocks/testimonials.py] @[core/sum_core/templates/sum_core/blocks/testimonials.html] for implementation guidelines 

### Planner Response

Good idea! Looking at the testimonials block, the heading uses `RichTextBlock` with `features=['bold', 'italic']` to allow styling. Let me update the gallery block with the same approach.

*Edited relevant file*

### Planner Response

Now let me update the template to use the `|richtext` filter for the heading, just like in testimonials:

*Edited relevant file*

### Planner Response

Now I need to update the CSS to style the heading content that comes from rich text (which will be wrapped in a `<p>` or other tags). Let me also update the tests to reflect the change:

*Viewed [components.testimonials.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/components.testimonials.css) *

### Planner Response

Now I need to update the gallery CSS to apply similar rich text heading support - the heading styling needs to target child elements and add italic styling. Let me update the gallery CSS:

*Edited relevant file*

### Planner Response

Now let me update the tests to reflect that the heading is now a RichTextBlock instead of a CharBlock:

*Viewed [test_gallery_block.py](file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py) *

### Planner Response

I need to update the test for the heading - it's now a RichTextBlock and is optional (like in testimonials). Let me also add a test for the richtext features:

*Edited relevant file*

### Planner Response

Now I also need to update the integration test to pass the heading as rich text format:

*Viewed [test_homepage_rendering.py](file:///home/mark/workspaces/tradesite/tests/templates/test_homepage_rendering.py) *

*Edited relevant file*

### Planner Response

Now let me also update the test assertions to check for the rich text content properly:

*Viewed [test_homepage_rendering.py](file:///home/mark/workspaces/tradesite/tests/templates/test_homepage_rendering.py) *

*Edited relevant file*

### Planner Response

Now let me run the tests to ensure everything passes:

*User accepted the command `make test`*

*Checked command status*

### Planner Response

All **56 tests pass**. Let me verify the lint status on the modified files:

*User accepted the command `ruff check core/sum_core/blocks/gallery.py tests/blocks/test_gallery_block.py tests/templates/test_homepage_rendering.py`*

### Planner Response

All checks pass. Here's a summary of the changes:

---

## ✅ Gallery Heading Updated to Rich Text

The gallery block heading now supports **bold** and *italic* formatting, allowing editors to emphasize key words like in the reference design (e.g., "A Showcase of *Precision* & Detail").

### Changes Made

| File | Change |
|------|--------|
| [core/sum_core/blocks/gallery.py](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/blocks/gallery.py:0:0-0:0) | Changed [heading](cci:1://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:47:4-54:49) from `CharBlock(required=True)` → `RichTextBlock(required=False, features=['bold', 'italic'])` |
| [core/sum_core/templates/sum_core/blocks/gallery.html](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/templates/sum_core/blocks/gallery.html:0:0-0:0) | Updated template to use `{{ self.heading|richtext }}` inside a `<div class="gallery__heading">` wrapper |
| [core/sum_core/static/sum_core/css/components.gallery.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/components.gallery.css:0:0-0:0) | Added CSS rules for `.gallery__heading > *` (font styling) and `.gallery__heading em, .gallery__heading i` (accent color for italics) |
| [tests/blocks/test_gallery_block.py](cci:7://file:///home/mark/workspaces/tradesite/tests/blocks/test_gallery_block.py:0:0-0:0) | Updated tests to verify heading is `RichTextBlock` with bold/italic features |
| [tests/templates/test_homepage_rendering.py](cci:7://file:///home/mark/workspaces/tradesite/tests/templates/test_homepage_rendering.py:0:0-0:0) | Updated integration test to use rich text heading with `<em>` tags |

### Editor Experience

In the Wagtail admin, editors can now:
1. Add a heading like: `A Showcase of **Precision** & Detail`
2. Select key words and apply *italic* formatting
3. The italic words will render with the accent color (`--accent-pop` token)

This matches the testimonials pattern and the reference [gallery_design.html](cci:7://file:///home/mark/workspaces/tradesite/docs/dev/design/gallery_design.html:0:0-0:0) design where headings like "*Precision* & Detail" have emphasized styling.

### User Input

I don't know if my human eyes are deceiving me but the headings on the sections look different to me.  My questions is: why does 'gallery heading' have its own heading styling? Surely a 'section heading' style would make more sense? Then we control the way they all look consistently. 

### Planner Response

You're absolutely right! This is a great architectural observation. Currently each section has its own heading styles (`.testimonials__heading`, `.gallery__heading`, etc.) which leads to inconsistency and duplicated code. A shared **section header pattern** would be much better.

Let me audit what we have and propose a unified approach:

*Grep searched codebase*

*Grep searched codebase*

*Viewed [layout.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/layout.css) *

### Planner Response

I can see the duplication. Let me check the utilities file and then propose a solution:

*Viewed [utilities.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/utilities.css) *

### Planner Response

You're spot on. The proper solution is to create **shared section header styles** in the layout layer that all sections can inherit, with only colour variants for light/dark themes. Let me create a unified approach:

*Edited relevant file*

### Planner Response

Now let me update the gallery template to use the shared section classes instead of component-specific ones:

*Viewed [gallery.html](file:///home/mark/workspaces/tradesite/core/sum_core/templates/sum_core/blocks/gallery.html) *

*Edited relevant file*

### Planner Response

Now let me update the testimonials template to use shared section classes:

*Viewed [testimonials.html](file:///home/mark/workspaces/tradesite/core/sum_core/templates/sum_core/blocks/testimonials.html) *

*Edited relevant file*

### Planner Response

Now let me check the services template and update it as well:

*Viewed [service_cards.html](file:///home/mark/workspaces/tradesite/core/sum_core/templates/sum_core/blocks/service_cards.html) *

*Edited relevant file*

### Planner Response

Now let me remove the duplicate header styles from the component CSS files. I'll remove them from gallery CSS first:

*Viewed [components.gallery.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/components.gallery.css) *

*Edited relevant file*

### Planner Response

Now let me remove the duplicate header styles from testimonials CSS:

*Viewed [components.testimonials.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/components.testimonials.css) *

*Edited relevant file*

### Planner Response

Now let me remove the duplicate header styles from services CSS:

*Viewed [components.services.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/components.services.css) *

*Edited relevant file*

### Planner Response

Now let me update the tests to reflect the new class names in the rendered HTML:

*Viewed [test_homepage_rendering.py](file:///home/mark/workspaces/tradesite/tests/templates/test_homepage_rendering.py) *

### Planner Response

Now let me run the tests to see if everything still passes:

*User accepted the command `make test`*

*Checked command status*

### Planner Response

All **56 tests pass**. Let me also update the CSS architecture documentation to reflect this new pattern:

*Viewed [css-architecture-and-tokens.md](file:///home/mark/workspaces/tradesite/docs/dev/design/css-architecture-and-tokens.md) *

### Planner Response

Let me add a section about the shared section header pattern to the docs:

*Edited relevant file*

### Planner Response

Now I need to update the remaining section references in the doc (5.3 Cards should be 5.4):

*Edited relevant file*

### Planner Response

Let me run the tests one final time to confirm everything works:

*User accepted the command `make test`*

*Checked command status*

### Planner Response

All **56 tests pass**. Here's a summary of the architectural refactor:

---

## ✅ Unified Section Header Pattern Implemented

You were absolutely right - having separate heading styles for each section (`.gallery__heading`, `.testimonials__heading`, `.services__heading`) leads to visual inconsistency and duplicated code. I've refactored to a **shared section header pattern**.

### What Changed

| Layer | Before | After |
|-------|--------|-------|
| **layout.css** | Only had `.section`, `.container` | Now includes shared `.section__header`, `.section__eyebrow`, `.section__heading`, `.section__intro` |
| **Templates** | Used component-specific classes (`gallery__eyebrow`, `testimonials__heading`, etc.) | Now use shared classes (`section__eyebrow`, `section__heading`, etc.) |
| **Component CSS** | Duplicated header styles in each component file | Removed duplicates - components only define their specific grid/card styles |

### Shared Classes in [layout.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/layout.css:0:0-0:0)

```css
.section__header     /* Container: max-width, margin, z-index */
.section__eyebrow    /* Pill-style label: uppercase, accent color */
.section__heading    /* Main heading with rich text support */
.section__intro      /* Lead paragraph: muted text */
```

### Dark Theme Support

For dark sections like testimonials, simply add `.section--dark` to the `<section>`:

```html
<section class="section section--dark testimonials">
  <header class="section__header">
    <!-- Automatically uses inverted colours -->
  </header>
</section>
```

### Benefits

1. **Consistency**: All section headings now look identical
2. **Single source of truth**: Change heading styles in one place ([layout.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/layout.css:0:0-0:0))
3. **Less CSS**: Removed ~120 lines of duplicated code across 3 component files
4. **Dark theme**: Built into the shared pattern, not duplicated per component
5. **Documentation**: Updated [css-architecture-and-tokens.md](cci:7://file:///home/mark/workspaces/tradesite/docs/dev/design/css-architecture-and-tokens.md:0:0-0:0) with the new pattern

### User Input

Okay that's much better, but I think I preferred the way the testimonial section headers were formatted. Can we now update all the section headers to what the testimonial header was set to?

### Planner Response

Let me check what the original testimonials header styles were before the refactor so I can apply them to the shared section header pattern:

*User accepted the command `git diff HEAD~5 -- core/sum_core/static/sum_core/css/components.testimonials.css | head -100`*

### Planner Response

Let me look at the original testimonials header that existed before my changes:

*User accepted the command `git show HEAD~6:core/sum_core/static/sum_core/css/components.testimonials.css 2>/dev/null | head -60 || echo "File not in that commit"`*

*User accepted the command `git log --oneline -10`*

*User accepted the command `git show 4d89cc2:core/sum_core/static/sum_core/css/components.testimonials.css | head -60`*

### Planner Response

Now I can see the original testimonials header formatting. The key differences from my current shared pattern are:

1. **Margin-bottom**: `var(--space-16, 4rem)` instead of `var(--space-12)`
2. **Font size**: `clamp(2rem, 5vw, 3.5rem)` instead of `clamp(var(--text-4xl), 5vw, var(--text-5xl))`

Let me update the shared section header styles in [layout.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/layout.css:0:0-0:0) to match the original testimonials formatting:

*Viewed [layout.css](file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/layout.css) *

*Edited relevant file*

### Planner Response

Now let me run the tests to make sure everything still works:

*User accepted the command `make test`*

*Checked command status*

### Planner Response

All **56 tests pass**. 

---

## ✅ Section Headers Updated to Testimonials Styling

I've updated the shared section header pattern in [layout.css](cci:7://file:///home/mark/workspaces/tradesite/core/sum_core/static/sum_core/css/layout.css:0:0-0:0) to match the original testimonials header formatting:

### Changes Applied

| Property | Before | After (Testimonials Style) |
|----------|--------|---------------------------|
| `.section__header` margin-bottom | `var(--space-12)` | `var(--space-16, 4rem)` |
| `.section__heading > *` font-size | `clamp(var(--text-4xl), 5vw, var(--text-5xl))` | `clamp(2rem, 5vw, 3.5rem)` |

### Result

Now **all section headers** (Gallery, Services, Testimonials) will have:
- **More generous spacing** between the header and content (4rem instead of 3rem)
- **Slightly smaller heading text** that scales better across breakpoints (2rem → 3.5rem instead of 2.25rem → 3rem)
- **Consistent formatting** that matches what you preferred in the testimonials section