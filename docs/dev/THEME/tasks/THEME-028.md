100% — **DividerBlock on its own is “why did we open a PR for this?” territory.** Let’s switch to **micro-batch tickets** for the tiny Page Content utility blocks.

The clean bundling here is:

* **SpacerBlock** (`sum_core/blocks/content_spacer.html`) 
* **DividerBlock** (`sum_core/blocks/content_divider.html`) 

Same “Page Content” group, both extremely small, and both benefit from one shared “contract test” pass.

Below is a replacement ticket that **supersedes the standalone divider ticket** and bundles both.

---

# THEME-028: SpacerBlock + DividerBlock bundle (Theme A)

## Branch

* [ ] Checkout/create: `theme/theme-028-spacer-divider-bundle`
* [ ] Verify: `git branch --show-current`

## Context

We’re continuing **rewrite existing blocks** work. Spacer + Divider are small “utility” blocks in Page Content and should be shipped together to avoid PR churn. Both have clearly defined field contracts in `blocks-reference.md`. 

We also now treat theme CSS + fingerprint as “regenerate, don’t merge”: if CI requires these artifacts, regenerate them **after rebasing onto `origin/develop`** and commit them last.

## Objective

Implement Theme A overrides for:

1. `SpacerBlock` – vertical rhythm control
2. `DividerBlock` – horizontal separator with style variants

…and add a single focused theme test file covering both blocks.

## Key Files

* `themes/theme_a/templates/sum_core/blocks/content_spacer.html` – Theme A override for SpacerBlock 
* `themes/theme_a/templates/sum_core/blocks/content_divider.html` – Theme A override for DividerBlock 
* `docs/dev/blocks-reference.md` – contract for `spacer.size` + mapping and `divider.style` variants 
* `tests/themes/test_theme_a_spacer_divider_rendering.py` – new bundled test (unique name, avoids collisions)

## Acceptance Criteria

* [ ] Theme override exists for SpacerBlock at `themes/theme_a/templates/sum_core/blocks/content_spacer.html`. 
* [ ] SpacerBlock supports `size` variants exactly:

  * [ ] `small/medium/large/xlarge` with mapping as documented (24/40/64/96 px equivalents). 
* [ ] Theme override exists for DividerBlock at `themes/theme_a/templates/sum_core/blocks/content_divider.html`. 
* [ ] DividerBlock supports `style` variants exactly:

  * [ ] `muted/strong/accent` (default muted). 
* [ ] Output is semantic:

  * [ ] Spacer renders a simple empty div (or section) with spacing class only
  * [ ] Divider uses `<hr>` (preferred) or equivalent with `role="separator"`
* [ ] No hardcoded hex colors; use theme tokens/semantic utilities.
* [ ] Bundled test added and passing:

  * [ ] renders spacer with each size and asserts expected class/marker exists
  * [ ] renders divider with each style and asserts expected class/marker exists
* [ ] `make test` passes per test strategy.
* [ ] If theme CSS artifacts are required by CI, they are regenerated **post-rebase** and committed as the final commit on the branch.

## Steps

1. **Preflight (required)**

   * [ ] Run your Codex slash command preflight (or `make preflight`) to ensure branch is current.

2. **Implement SpacerBlock override**

   * [ ] Create/update: `themes/theme_a/templates/sum_core/blocks/content_spacer.html`
   * [ ] Implement a simple mapping from `self.size` → spacing classes.

     * Must match the documented size mapping. 
   * [ ] Keep markup minimal and predictable for tests.

3. **Implement DividerBlock override**

   * [ ] Create/update: `themes/theme_a/templates/sum_core/blocks/content_divider.html`
   * [ ] Use `<hr>` with classes mapped from `self.style` (`muted/strong/accent`). 
   * [ ] Use semantic color utilities (e.g. border opacity / token colors), no hex.

4. **Add bundled theme test**

   * [ ] Create `tests/themes/test_theme_a_spacer_divider_rendering.py`
   * [ ] Assertions:

     * template origin resolves to Theme A overrides
     * each spacer size produces the expected wrapper class/marker
     * each divider style produces the expected class/marker

5. **Rebase + regenerate artifacts only if required**

   * [ ] `git fetch origin && git rebase origin/develop`
   * [ ] If CI requires `main.css` + `.build_fingerprint`, regenerate now (post-rebase) and commit them last.

6. **Run tests**

   * [ ] `pytest -q tests/themes/test_theme_a_spacer_divider_rendering.py`
   * [ ] `make test`

## Testing Requirements

* [ ] Run: `pytest -q tests/themes/test_theme_a_spacer_divider_rendering.py`
* [ ] Run: `make test`
* [ ] Expected: all green

## Documentation Updates

* [ ] None expected (contract already defined in `blocks-reference.md`) 

## Deliverables

* [ ] Create `THEME-028_followup.md` (same directory as this ticket) containing:

  * Summary of changes
  * Files modified/created
  * Test results
  * Decisions made / blockers hit

## Commit & Push

* [ ] Stage: `git add -A`
* [ ] Commit: `feat(THEME-028): theme a spacer + divider block templates`

  * **Must include both** `THEME-028.md` AND `THEME-028_followup.md`
* [ ] Push: `git push origin theme/theme-028-spacer-divider-bundle`

## Verification

* [ ] `git status --porcelain` → empty or documented untracked only

---

### Going-forward batching rule (so tickets stay sane)

**Bundle 2–4 micro blocks per ticket** when they’re:

* single-template, no JS, no models/migrations
* same block group (e.g. Page Content utilities)
* one combined test file is enough

If you want, I’ll also rewrite the next queue so we alternate: **one “real” block** (Image/ButtonGroup/SocialProof) + **one micro-bundle** (Spacer/Divider/etc.) to keep momentum high without PR spam.
