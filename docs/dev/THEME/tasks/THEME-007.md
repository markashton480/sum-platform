#TASK-ID: THEME-007
#TITLE: Create FeaturedCaseStudyBlock (Python + templates + wiring + tests) per `new-theme-plan.md` Task 4

## Mission

Implement **FeaturedCaseStudyBlock** exactly as specified in `new-theme-plan.md` Task 4 (block contract + Theme A template behaviour), register it in `PageStreamBlock`, and add the usual migration/tests/docs so we don’t regress.

## Source of truth

- **Block contract + template requirements:** `new-theme-plan.md` → “Task 4: Create FeaturedCaseStudyBlock”
- **Theme locations & template resolution order (v0.6+):** `WIRING-INVENTORY.md` “Theme Wiring (v0.6+)”
- **Canonical StreamBlock registration location:** `core/sum_core/blocks/base.py` (PageStreamBlock)

---

## Scope

### In scope

1. Add **FeaturedCaseStudyBlock** to `core/sum_core/blocks/gallery.py` (per plan).
2. Register it in `PageStreamBlock` (group **Sections**).
3. Add Theme A template at: `themes/theme_a/templates/sum_core/blocks/featured_case_study.html`.
4. Add core fallback template at: `core/sum_core/templates/sum_core/blocks/featured_case_study.html` (minimal, semantic, not Theme A palette-heavy).
5. Update docs: `docs/dev/blocks-reference.md` to include the new block entry.
6. Generate and commit the **required StreamField migration** (new migration; AlterField-only).
7. Add/extend tests to enforce contract + registration + theme rendering behaviour.

### Out of scope

- Any other homepage template fixes (Hero/Stats/ServiceCards/etc).
- Changes to Tailwind build pipeline.

---

## Implementation details

### 1) Block definition (must match the plan verbatim)

**File:** `core/sum_core/blocks/gallery.py`

Implement exactly:

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
        icon = "doc-full"
        template = "sum_core/blocks/featured_case_study.html"
```

**Rules:**

- Don’t add extra fields (no “helpful extensions”). The plan is the contract.
- CTA render logic should be: show CTA only if **both** `cta_text` and `cta_url` are present (avoid half-CTAs).
- Stats card should render only if at least one of `stats_label` / `stats_value` is present (avoid empty floating box).

### 2) Export + registration

You must make the block available to consumers consistently:

- Add appropriate import/export in `core/sum_core/blocks/__init__.py` (and `__all__` list), matching existing patterns.
- Update `core/sum_core/blocks/base.py` to import the block and register it in `PageStreamBlock`:

```python
featured_case_study = FeaturedCaseStudyBlock(group="Sections")
```

(Exact key name: `featured_case_study`.)

This ensures StandardPage/HomePage (client-owned) can use it via PageStreamBlock.

### 3) Theme A template (this is what the wireframe expects)

**File:** `themes/theme_a/templates/sum_core/blocks/featured_case_study.html`

Must implement these requirements from the plan:

- Grid: `lg:grid-cols-2 gap-16`
- Left: `aspect-[4/5]` image with floating stats card (`absolute top-8 right-8`)
- Stats card: `bg-sage-terra text-white p-6`
- Hover overlay: `bg-black/40` overlay with “Inspect Artifact” text
- Right: content with numbered list (1. 2. 3.)
- CTA: `border-b-2 border-sage-terra`

**Template guidance (non-negotiable behaviour):**

- Use `{% load wagtailcore_tags wagtailimages_tags %}`.
- Render rich text with `|richtext`.
- Use a `group` wrapper around the image so the overlay appears on hover (`group-hover`).
- Enforce `alt` = `self.image_alt` (required field exists for accessibility).
- Ensure the overlay text is present in markup and visible on hover.

### 4) Core fallback template

**File:** `core/sum_core/templates/sum_core/blocks/featured_case_study.html`

Keep it minimal and semantic (container/grid, image, content). Avoid Theme A palette tokens; it’s a fallback only.

### 5) Migration (expected)

Adding a new block to `PageStreamBlock` will alter StreamField definitions for page models that reference it. Create a new `sum_core_pages` migration (next number after current). Follow the established pattern from earlier tasks: AlterField-only, then `makemigrations --check` clean.

**Rules:**

- Do **not** edit existing migrations.
- Ensure migration contains **only** `AlterField` operations related to StreamFields.

### 6) Tests (guardrails against drift)

Add tests consistent with the existing suite patterns used for Manifesto:

- `tests/blocks/test_content_blocks.py` (or appropriate blocks test module):

  - Assert `FeaturedCaseStudyBlock` fields exist exactly as per contract (especially requiredness of `heading`, `image`, `image_alt`).

- `tests/blocks/test_page_streamblock.py`:

  - Assert `featured_case_study` is present on `PageStreamBlock`.

- `tests/pages/test_home_page.py` (or equivalent):

  - Render a page with a `featured_case_study` block and assert key theme-template markers exist (e.g. `aspect-[4/5]`, `bg-black/40`, `border-sage-terra`).
  - Use the existing approach where tests install theme templates into `theme/active` during pytest for determinism (same rationale as earlier work).

### 7) Docs update

Update `docs/dev/blocks-reference.md` with a new entry:

- **Key:** `featured_case_study`
- **Template:** `sum_core/blocks/featured_case_study.html`
- Field table exactly matching the plan’s field list + requiredness.

(Optional but good): update `page-types-reference.md` block list if it’s meant to be a live list of PageStreamBlock capabilities (only if you’ve been keeping it current).

---

## Manual verification steps

1. Run DB (Postgres) and migrate:

   - `make db-up`
   - `cd core && python manage.py migrate`

2. Run harness:

   - `python core/sum_core/test_project/manage.py runserver`

3. In Wagtail admin:

   - Add **Featured Case Study** to HomePage/StandardPage body
   - Fill all fields (including points list with 3 items, stats label/value)

4. View page:

   - Confirm split layout
   - Confirm stats card floats at top-right of image
   - Confirm hover overlay appears with “Inspect Artifact”
   - Confirm numbered list displays as 1/2/3
   - Confirm CTA has the bottom border styling (only when both CTA fields set)

---

## Acceptance criteria

- FeaturedCaseStudyBlock exists in `core/sum_core/blocks/gallery.py` with **exact** field contract from `new-theme-plan.md`.
- Block is registered as `featured_case_study` in `PageStreamBlock` (group **Sections**).
- Theme A template exists at the canonical theme path and matches the specified layout + hover + stats behaviour.
- Core fallback template exists and renders without Theme A assumptions.
- New `sum_core_pages` migration created and contains AlterField-only updates.
- Tests updated/added and passing.

---

## Guardrails (audit trail + process)

- Do **not** modify any historical task docs, transcripts, or followups.
- Only create:

  - `docs/dev/THEME/tasks/THEME-007.md` (this ticket)
  - `docs/dev/THEME/tasks/THEME-007_followup.md` (work report)
  - plus the code/templates/tests/migration needed for the implementation.
