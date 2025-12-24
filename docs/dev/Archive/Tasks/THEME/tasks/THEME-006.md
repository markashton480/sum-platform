# TASK ID: THEME-006

## Mission

Bring **ManifestoBlock** back into strict alignment with `new-theme-plan.md` Task 3 (block contract + Theme A template requirements), now that canonical theme location is repo-root `themes/`.

## Why this task exists

THEME-004 implemented Manifesto end-to-end, but it drifted from the plan’s block contract and template requirements (extra fields/CTA, requiredness drift, and template oddities). We’re correcting this via a **new ticket** to preserve the audit trail and stop compounding drift.

## Source of truth

- **Manifesto spec:** `new-theme-plan.md` → Task 3: Create ManifestoBlock (field structure + Tailwind template requirements + wireframe reference).
- **Theme location + wiring contract:** `THEME-ARCHITECTURE-SPECv1.md` §9 (repo-root themes, init copy, loader priority).
- **Canonical StreamField blockset wiring:** blocks are registered into `PageStreamBlock` (used by StandardPage/HomePage patterns) and maintained in `core/sum_core/blocks/base.py`.

## Scope

### In scope

1. Update `ManifestoBlock` Python definition to **exactly match** Task 3’s block structure and required fields.
2. Ensure Theme A template lives at **repo-root** `themes/theme_a/templates/sum_core/blocks/manifesto.html` and matches the specified Tailwind layout.
3. Keep a sane core fallback at `core/sum_core/templates/sum_core/blocks/manifesto.html` (basic markup; not theme-styled).
4. Update docs (`docs/dev/blocks-reference.md`) and tests accordingly.
5. Generate & commit the **required StreamField migration** (new migration; do not edit historical ones).

### Out of scope

- Any other block templates, header/footer, or global theme refactors.
- Any Tailwind rebuild pipeline changes unless absolutely required for the manifesto template to be picked up (it shouldn’t be, if theme globs already include `templates/sum_core/**`).

## Implementation details

### 1) Fix the block contract (Python)

**File:** `core/sum_core/blocks/content.py`

Implement **exactly**:

```python
class ManifestoBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(max_length=100, required=False)
    heading = blocks.RichTextBlock(required=True, features=["italic", "bold"])
    body = blocks.RichTextBlock(required=True, features=["bold", "italic", "link", "ol", "ul"])
    quote = blocks.TextBlock(required=False)

    class Meta:
        icon = "doc-full"
        template = "sum_core/blocks/manifesto.html"
```

**Hard requirements:**

- `heading` and `body` must be required=True.
- No CTA fields. No extra intro field. No additional “helpful” extensions — this ticket is about matching the plan.

### 2) Ensure registration is correct (PageStreamBlock)

**File:** `core/sum_core/blocks/base.py`

- Ensure `manifesto` remains registered in the canonical `PageStreamBlock` so it’s available on any page using that stream blockset.

### 3) Theme A template (the actual output contract)

**File:** `themes/theme_a/templates/sum_core/blocks/manifesto.html`

Must match `new-theme-plan.md` “Template Requirements”:

- Section: `py-24 md:py-32 bg-sage-linen`
- Container: `max-w-3xl mx-auto`
- Centered
- Eyebrow: `text-sage-terra font-accent italic text-2xl`
- Heading: `font-display text-4xl md:text-5xl`
- Body: `prose prose-lg`
- Quote (if present): border-top + `font-accent italic text-xl`

Also:

- Use `{% load wagtailcore_tags %}` and render rich text with `|richtext`.
- Make quote conditional and avoid empty spacing when absent.

### 4) Core fallback template

**File:** `core/sum_core/templates/sum_core/blocks/manifesto.html`

Keep it intentionally minimal (semantic HTML, no theme-specific Tailwind palette classes), so:

- Theme A provides the real look
- Core remains readable fallback.

### 5) Docs update

**File:** `docs/dev/blocks-reference.md`

- Update ManifestoBlock entry to reflect the corrected fields (no CTA; requiredness correct; features list correct).
  (If the repo documents “Key:” names for blocks, ensure it remains `manifesto`.)

### 6) Tests + migration

#### Tests

Update the existing tests added in THEME-004 (or add new ones) so they enforce the contract:

- **Block schema test**: Manifesto has exactly these fields, and requiredness matches plan.
- **StreamBlock registration test**: `manifesto` exists in `PageStreamBlock`.
- **Render smoke test**: rendering uses theme template resolution when theme templates are active.

(Keep tests small and focused; we’re guarding contract drift.)

#### Migration

Because `PageStreamBlock` is part of StreamField definitions on page models, changing the block schema will require a new `sum_core_pages` migration that is **only AlterField operations**. This is expected.

**Rules:**

- Create a **new** migration (next number). Do not edit existing migrations.
- Sanity-check the migration: only `AlterField` updates for StreamField definitions.

## Database / environment requirements

All migration + tests must run against Postgres (no SQLite fallback surprises). `DJANGO_DB_*` must be set correctly; Postgres is the dev parity target.

## How to verify (manual)

1. `make db-up`
2. Run harness: `python core/sum_core/test_project/manage.py runserver`
3. In Wagtail admin, add a **Manifesto** block to a page body using `PageStreamBlock`.
4. Fill eyebrow + heading + body (+ optional quote) with the wireframe content.
5. View page: should match the centered prose section (wireframe lines 380–400 per plan).

## Acceptance criteria

- ManifestoBlock matches `new-theme-plan.md` Task 3 contract exactly (fields + requiredness + features).
- Theme A template exists at `themes/theme_a/templates/sum_core/blocks/manifesto.html` and visually matches the specified layout/typography.
- Core fallback template exists and renders cleanly (unstyled fallback).
- New StreamField migration is created, committed, and contains only AlterField operations.
- Tests updated/added and passing.

## Guardrails (non-negotiable)

- Do **not** edit or “update” any historical task docs, transcripts, or followups (audit trail is immutable).
- Only create:

  - `docs/dev/THEME/tasks/THEME-006.md` (this ticket)
  - `docs/dev/THEME/tasks/THEME-006_followup.md` (work report)
  - plus the actual code/templates/tests/migration required to implement the ticket.

---
