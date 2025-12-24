Below are the next **two parallel-safe tickets** (no overlap with each other’s templates/tests), and **both explicitly forbid committing** the generated CSS artifacts (`main.css` + `.build_fingerprint`) to avoid the worktree conflict drama.

---

# THEME-024: Theme A – ImageBlock template rewrite (captioned images)

## Branch

* [ ] Checkout/create: `theme/theme-024-image-block`
* [ ] Verify: `git branch --show-current`

## Context

Phase 2 (Content Blocks), Day 1–2 includes **ImageBlock** next: captioned images used throughout editorial pages (blog article, terms) and interior content. 
Block contract: `ImageBlock` → template `sum_core/blocks/content_image.html`, with reveal behavior and `full_width` option. 

**Parallel safety / worktree rule:** This ticket must **not** modify or commit:

* `themes/theme_a/static/theme_a/css/main.css`
* `themes/theme_a/static/theme_a/css/.build_fingerprint`

## Objective

Create/replace Theme A’s override for `ImageBlock` to match Sage & Stone editorial image + caption styling:

* proper `<figure>` semantics
* optional caption
* `full_width` layout variant
* reveal hooks (progressive enhancement)
* add focused theme rendering tests

## Key Files

* `themes/theme_a/templates/sum_core/blocks/content_image.html` – create/replace Theme A override 
* `docs/dev/blocks-reference.md` – confirm fields and expectations (image, alt_text, caption, full_width) 
* `docs/dev/design/wireframes/sage-and-stone/compiled/blog_article.html` – reference: in-article images with captions 
* `tests/themes/test_theme_a_image_block_rendering.py` – new test file

## Acceptance Criteria

* [ ] Theme override exists at `themes/theme_a/templates/sum_core/blocks/content_image.html` 
* [ ] Renders a semantic structure:

  * [ ] `<figure>` wrapping image and caption
  * [ ] image uses required `alt_text`
  * [ ] `<figcaption>` only renders when `caption` is present
* [ ] Supports `full_width`:

  * [ ] when `full_width=True`, image uses a wider/bleed layout relative to normal prose container
  * [ ] when `full_width=False`, image respects editorial content width
* [ ] Reveal animation hooks present but **content visible by default** (progressive enhancement)
* [ ] **No changes committed** to:

  * [ ] `themes/theme_a/static/theme_a/css/main.css`
  * [ ] `themes/theme_a/static/theme_a/css/.build_fingerprint`
* [ ] Tests added and passing
* [ ] Tests pass per `test-strategy-post-mvp-v1.md`
* [ ] No regressions in existing functionality

## Steps

1. Branch verification

   * [ ] Checkout/create `theme/theme-024-image-block`
   * [ ] Confirm branch name

2. Implement Theme A override

   * [ ] Create/update: `themes/theme_a/templates/sum_core/blocks/content_image.html`
   * [ ] Use Wagtail image rendering (`{% image self.image ... %}`), and pass `alt=self.alt_text`
   * [ ] Layout suggestion:

     * outer wrapper sets vertical rhythm consistent with other content blocks
     * inner wrapper toggles width based on `self.full_width`
   * [ ] Caption:

     * only render when `self.caption` is truthy
     * style as editorial caption (smaller, muted, aligned to image)

3. Reveal hooks (no JS changes)

   * [ ] Apply existing Theme A reveal class conventions to the figure/image/caption

4. Tests

   * [ ] Add: `tests/themes/test_theme_a_image_block_rendering.py`
   * [ ] Assertions:

     * template origin resolves to Theme A override
     * `alt_text` shows up in rendered `<img ... alt="...">`
     * caption included/excluded correctly
     * `full_width` toggles expected wrapper class(es)

5. **Prevent CSS artifact conflicts**

   * [ ] Before committing, ensure these are clean:

     * `themes/theme_a/static/theme_a/css/main.css`
     * `themes/theme_a/static/theme_a/css/.build_fingerprint`
   * [ ] If changed locally, revert:

     * `git restore themes/theme_a/static/theme_a/css/main.css themes/theme_a/static/theme_a/css/.build_fingerprint`

## Testing Requirements

* [ ] Run: `pytest -q tests/themes/test_theme_a_image_block_rendering.py`
* [ ] Run: `make test`
* [ ] Expected: all green

## Documentation Updates

Update if changes affect:

* [ ] `blocks-reference.md` (only if contract mismatch found) 
* [ ] `page-types-reference.md` (not expected)
* [ ] `WIRING-INVENTORY.md` (not expected)

## Deliverables

* [ ] Create `THEME-024_followup.md` (same directory as this ticket) containing:

  * Summary of changes
  * Files modified/created
  * Test results
  * Decisions made / blockers hit
  * Doc updates made (if any)

## Commit & Push

* [ ] Stage: `git add -A`
* [ ] Commit: `feat(THEME-024): rewrite Theme A ImageBlock template`

  * **Must include both** `THEME-024.md` AND `THEME-024_followup.md`
* [ ] Push: `git push origin theme/theme-024-image-block`

## Verification

* [ ] `git status --porcelain` → empty or documented untracked only

## Recommended Agent

**Criteria:** Standard feature (template rewrite + focused tests)
**Selection Model:** GPT-5.1 Codex Max
**Thinking:** Standard
**Rationale:** UI-focused template work with conditional rendering; keep diffs tight and tests crisp.

---

