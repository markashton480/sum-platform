# THEME-025: Theme A – ButtonGroupBlock template rewrite (CTA button group)

## Branch

* [ ] Checkout/create: `theme/theme-025-button-group-block`
* [ ] Verify: `git branch --show-current`

## Context

Phase 2 (Content Blocks), Day 1–2 includes **ButtonGroupBlock**: reusable CTA group for interior pages and article endcaps. 
Block contract: `ButtonGroupBlock` → template `sum_core/blocks/content_buttons.html`, with alignment + list of `ContentButtonBlock` items styled `primary/secondary`. 

**Parallel safety / worktree rule:** This ticket must **not** modify or commit:

* `themes/theme_a/static/theme_a/css/main.css`
* `themes/theme_a/static/theme_a/css/.build_fingerprint`

## Objective

Create/replace Theme A’s override for `ButtonGroupBlock`:

* alignment left/center/right
* button styles primary/secondary mapped to Theme A button classes
* 1–3 buttons
* add focused theme rendering tests

## Key Files

* `themes/theme_a/templates/sum_core/blocks/content_buttons.html` – create/replace Theme A override 
* `docs/dev/blocks-reference.md` – confirm `alignment` and `buttons[*].style` contract 
* `tests/themes/test_theme_a_button_group_rendering.py` – new test file

## Acceptance Criteria

* [ ] Theme override exists at `themes/theme_a/templates/sum_core/blocks/content_buttons.html` 
* [ ] Renders 1–3 buttons from the list
* [ ] Alignment works:

  * [ ] `left` → group aligns left
  * [ ] `center` → group centers
  * [ ] `right` → group aligns right
* [ ] Button styles work:

  * [ ] `primary` uses Theme A primary button classes
  * [ ] `secondary` uses Theme A secondary/outline button classes
* [ ] Output is accessible:

  * [ ] uses `<a href="...">` with clear label
  * [ ] no empty hrefs, no unsafe HTML injection
* [ ] **No changes committed** to:

  * [ ] `themes/theme_a/static/theme_a/css/main.css`
  * [ ] `themes/theme_a/static/theme_a/css/.build_fingerprint`
* [ ] Tests added and passing
* [ ] Tests pass per `test-strategy-post-mvp-v1.md`
* [ ] No regressions in existing functionality

## Steps

1. Branch verification

   * [ ] Checkout/create `theme/theme-025-button-group-block`
   * [ ] Confirm branch name

2. Implement Theme A override

   * [ ] Create/update: `themes/theme_a/templates/sum_core/blocks/content_buttons.html`
   * [ ] Map alignment → flex justification:

     * left: `justify-start`
     * center: `justify-center`
     * right: `justify-end`
   * [ ] Map button style to Theme A button classes (use existing Theme A conventions; do not invent new global CSS)
   * [ ] Render buttons as anchors with spacing (stack on mobile if appropriate; inline row on larger screens)

3. Tests

   * [ ] Add: `tests/themes/test_theme_a_button_group_rendering.py`
   * [ ] Assertions:

     * template origin resolves to Theme A override
     * both buttons render with correct labels + hrefs
     * `primary/secondary` styles apply correct classes
     * `alignment=center` and `alignment=right` toggle wrapper class as expected

4. **Prevent CSS artifact conflicts**

   * [ ] Before committing, ensure these are clean:

     * `themes/theme_a/static/theme_a/css/main.css`
     * `themes/theme_a/static/theme_a/css/.build_fingerprint`
   * [ ] If changed locally, revert:

     * `git restore themes/theme_a/static/theme_a/css/main.css themes/theme_a/static/theme_a/css/.build_fingerprint`

## Testing Requirements

* [ ] Run: `pytest -q tests/themes/test_theme_a_button_group_rendering.py`
* [ ] Run: `make test`
* [ ] Expected: all green

## Documentation Updates

Update if changes affect:

* [ ] `blocks-reference.md` (only if contract mismatch found) 
* [ ] `page-types-reference.md` (not expected)
* [ ] `WIRING-INVENTORY.md` (not expected)

## Deliverables

* [ ] Create `THEME-025_followup.md` (same directory as this ticket) containing:

  * Summary of changes
  * Files modified/created
  * Test results
  * Decisions made / blockers hit
  * Doc updates made (if any)

## Commit & Push

* [ ] Stage: `git add -A`
* [ ] Commit: `feat(THEME-025): rewrite Theme A ButtonGroupBlock template`

  * **Must include both** `THEME-025.md` AND `THEME-025_followup.md`
* [ ] Push: `git push origin theme/theme-025-button-group-block`

## Verification

* [ ] `git status --porcelain` → empty or documented untracked only

## Recommended Agent

**Criteria:** Standard feature (template rewrite + focused tests)
**Selection Model:** GPT-5.1 Codex Max
**Thinking:** Standard
**Rationale:** Straight mapping from block contract → markup + classes; keep diffs minimal and avoid CSS artifact churn.

---
