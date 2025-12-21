## THEME-013 review (PortfolioBlock)

From the work report, THEME-013 looks **on-track and aligned** with the plan’s “Task 6: Fix PortfolioBlock Template” requirements (mobile horizontal scroll + fade, desktop 3-col grid, 4:3 images, hover zoom, metadata + fallback).

Green flags:

* You **confirmed the contract** in `sum_core/blocks/content.py` before templating (correct order of operations).
* Theme override was implemented in the correct canonical location under `themes/theme_a/templates/...` (no `core/sum_core/themes/...` drift).
* Added a **rendering test** plus ran the **full suite** (734 passing).
* You updated `docs/dev/blocks-reference.md` to reflect the true block contract (good hygiene, and it’s explicitly called out as modified).

Only “watch items” (not blockers):

* Rebuilding Tailwind + fingerprint every time is fine, but it’s worth keeping an eye on **lockfile churn** (if `package-lock.json` / `pnpm-lock.yaml` changes unexpectedly, it should be deliberate).
* The transcript is the usual Cursor action log (not content-rich), but the work report is specific enough to audit.

I don’t see anything that needs a corrective ticket for THEME-013 based on what’s provided.

---

## Next step

Per the homepage wireframe mapping, the next two “still needs template” blocks after Portfolio are:

* **FAQBlock** (wireframe lines 650–735)
* **ContactFormBlock** (wireframe lines 738–814) 

So the next full ticket should be **FAQBlock**.

---

# TASK TICKET: THEME-014 — Fix FAQBlock Template (Theme A)

## Context

The homepage wireframe calls for a proper accordion FAQ section (lines **650–735**) mapped to **FAQBlock**. The block exists in core, but Theme A needs the template to match the reference design.

FAQBlock contract (fields + behaviour) is defined in `docs/dev/blocks-reference.md` and must be respected. 

## Objective

Implement / update the Theme A override template for **FAQBlock** so it:

1. Matches the wireframe layout and styling intent (Theme A / Sage palette tokens).
2. Preserves the **SEO JSON-LD** behaviour (“FAQPage” structured data).
3. Is accessible and keyboard-friendly by default.
4. Respects `allow_multiple_open` behaviour.

## Non-goals

* Don’t change the block schema, StreamField registration, or migrations.
* Don’t edit historical tickets/reports/transcripts (audit trail stays immutable).
* Don’t introduce heavy JS frameworks or global behaviour that could affect other components.

## Files

### Primary implementation

* `themes/theme_a/templates/sum_core/blocks/faq.html`

### Reference (read-only unless explicitly needed)

* `core/sum_core/templates/sum_core/blocks/faq.html` (compare/borrow JSON-LD patterns, but don’t change unless there’s a proven core bug)

### Tests

* Create: `tests/themes/test_theme_a_faq_rendering.py`

## Requirements

### A) Layout + styling (Theme A)

Implement the section with the same “header pattern” we’re using elsewhere:

* Eyebrow (optional): `font-accent italic` and uses the accent token class (e.g. `text-sage-terra`)
* Heading: `font-display` and supports italics/bold from RichText
* Intro (optional): rendered below heading (prose-ish sizing, but don’t rely on `.prose` unless it’s already part of the theme conventions)

Accordion:

* Each FAQ item should be a clear “question row” with:

  * Question text prominent
  * A plus/minus or chevron indicator
  * Answer revealed with a smooth transition (progressive enhancement is fine)

### B) Accessibility baseline

* Use semantic, keyboard-friendly markup.

  * Preferred: `<details><summary>…</summary>…</details>` for each FAQ item (best baseline accessibility and no-js support).
* Ensure visible focus states on the interactive element (summary/button).
* Ensure the question is the interactive control; avoid nested interactive elements that break keyboard flow.

### C) `allow_multiple_open` behaviour

Contract: `allow_multiple_open` defaults to True. 

* If `allow_multiple_open == True`: multiple `<details>` can remain open (native behaviour).
* If `allow_multiple_open == False`: implement a **tiny, scoped** JS enhancement that closes sibling items when one opens.

Scoping requirement:

* Must support multiple FAQ blocks on one page without interference.
* Suggested approach: wrap the block in a container with a deterministic attribute (e.g. `data-faq-block`) and scope the JS to the nearest container.

### D) SEO JSON-LD must remain intact

FAQBlock is expected to generate FAQPage structured data. 

* Ensure the Theme A template outputs equivalent JSON-LD to the core template.
* If the core template currently outputs JSON-LD via a helper include/tag, reuse that same approach in the Theme A template.

### E) Branding/token compliance

* No hardcoded hex values.
* Use the theme token classes (e.g. sage palette utilities), which are already wired to branding variables via SiteSettings in this project.

## Implementation steps (agent checklist)

1. Open the core FAQ template and identify exactly how JSON-LD is generated.
2. Implement Theme A override in `themes/theme_a/templates/sum_core/blocks/faq.html`:

   * Build the section header (eyebrow/heading/intro)
   * Render items as `<details>` accordion
   * Add scoped JS only for the `allow_multiple_open=False` case
3. Add rendering tests:

   * Verify template renders eyebrow/heading/intro when present
   * Verify N FAQ items render as `<details>` (or chosen structure)
   * Verify JSON-LD script is present when items exist
   * Verify when `allow_multiple_open=False`, the template includes the hook needed for the behaviour (e.g. a `data-allow-multiple-open="false"` attribute or equivalent)
4. Run tests:

   * `source .venv/bin/activate && pytest tests/themes/test_theme_a_faq_rendering.py`
   * `source .venv/bin/activate && make test`
5. Only rebuild Tailwind + fingerprint if you introduce **new** utility classes that aren’t currently present in `themes/theme_a/static/theme_a/css/main.css`:

   * quick check: `rg "<some-new-class>" themes/theme_a/static/theme_a/css/main.css`
   * if missing: run the theme build pipeline and regenerate fingerprint.

## Manual verification (Wagtail + browser)

1. In Wagtail admin, add an **FAQ block** to the homepage with 3–6 items.
2. Test on desktop + mobile widths:

   * Accordion opens/closes correctly
   * If `allow_multiple_open=False`, opening one closes others
   * Keyboard: Tab to summary, Enter/Space toggles, focus is visible
3. View page source and confirm JSON-LD exists and contains each Q/A pair.

## Acceptance criteria

* Theme A FAQ matches wireframe intent for lines 650–735 (layout, spacing, typographic hierarchy). 
* No schema/model changes.
* JSON-LD output preserved.
* Accessible accordion behaviour.
* Test coverage added and full suite passes.

## Deliverables

* Theme A FAQ template updated
* New rendering tests added
* (Optional) Tailwind rebuild + fingerprint update if required by new classes
* Work report: `docs/dev/THEME/tasks/THEME-014_followup.md`



