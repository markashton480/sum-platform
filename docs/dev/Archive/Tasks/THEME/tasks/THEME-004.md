# THEME-004 Ticket Outline

## Goal

Add **ManifestoBlock** end-to-end:

* Python block definition + registration in the correct StreamField
* Theme A template for the block
* Docs + minimal tests
* Verified in harness using **Postgres**

### Non-negotiables

* DB vendor must be `postgresql` before migrations/tests.
* No unrelated migrations. If `makemigrations --check` shows extras, stop and investigate.

### Implementation steps

1. **Locate the correct StreamField**

   * Find where homepage blocks are defined (likely a HomePage streamfield or the shared `PageStreamBlock` depending on your architecture).
   * Add `ManifestoBlock` to the relevant block chooser so editors can add it.

2. **Create `ManifestoBlock`**

   * Place it in the canonical blocks module (based on THEME-003, that’s likely `core/sum_core/blocks/content.py`). 
   * Fields should match the wireframe intent:

     * heading / eyebrow (optional)
     * body/rich text (or structured bullets if the design uses them)
     * optional CTA (label + URL) if wireframe includes one
   * Keep fields optional where possible; wireframe-perfect rendering can be conditional.

3. **Theme template**

   * Add a template under `themes/theme_a/templates/...` following existing block-template conventions in Theme A.
   * Ensure the template uses the new block fields and aligns with wireframe spacing/typography.

4. **Migrations**

   * If adding the block changes StreamField definitions on a Page model, generate the correct app migration (often `sum_core_pages`).
   * Ensure it’s the *only* pending migration.

5. **Tests**

   * A small test that the block exists and is registered in the intended StreamField.
   * A template render smoke test if you already have that pattern; if not, keep it simple.

6. **Docs**

   * Update `docs/dev/blocks-reference.md` with ManifestoBlock definition and fields.
   * Add/commit `docs/dev/THEME/tasks/THEME-004.md` and later `THEME-004_followup.md`.

### Acceptance criteria

* Editors can add ManifestoBlock in the correct page type(s).
* ManifestoBlock renders in Theme A templates.
* Postgres migrations clean + tests pass.
* No pending `makemigrations --check` output.

---

