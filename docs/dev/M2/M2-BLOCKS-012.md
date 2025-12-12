**Task ID**: **BLOCKS-012** (M2 Stabilisation)

**Title**: Stabilise homepage rendering tests + patch missing token(s)

**Goal**: Eliminate flaky 404s in homepage rendering integration tests and resolve the known missing CSS token reference so Milestone 3 starts on a stable, predictable base.

**Workstream**: 3 — StreamField Blocks

**Milestone**: 2 — StreamField Blocks

**Inputs Required**:

* PRD Section(s): Testing/quality expectations for platform (tests must pass in CI).
* Tech Spec Section(s): N/A (use existing project patterns)
* Design References: `docs/dev/design/css-architecture-and-tokens.md`, `docs/dev/design/design-implementation.md` (token-only rules)
* Dependencies: Milestone 2 blocks implemented + current test suite exists (already true).

**Files/Modules to Touch**:

* `tests/templates/test_homepage_rendering.py` – remove the batch-run 404 flake by making page creation/routing deterministic (likely publish/live + site-root handling)
* (If present) `tests/templates/test_homepage_renders_gallery_block` or gallery rendering test file – same fix strategy as above
* `core/sum_core/static/sum_core/css/tokens.css` – define `--duration-default` (or refactor gallery to use an existing duration token)
* `core/sum_core/static/sum_core/css/components.gallery.css` – ensure it references a defined duration token
* (Optional cleanup scope) `core/sum_core/static/sum_core/css/components.{hero,faq,process,trust-strip,testimonials}.css` – replace the specific hardcoded spacing/weight values called out in the audit with `var(--space-*)` / `var(--font-*)`
* (Optional) `core/sum_core/branding/templatetags/branding_tags.py` – rename ambiguous `l` variable to something explicit if still present

**Implementation Steps**:

1. Reproduce the failure reliably by running the whole template test folder in one go (and ideally with `-n auto` once) to confirm the “fails in batch” behaviour.
2. Make the homepage rendering tests deterministic:

   * Ensure the created HomePage is **live/published** if the test uses HTTP routing (`client.get(home.url)`), and
   * Ensure the page sits under the correct Site root and the request resolves against the correct Site.
   * Prefer a shared helper/fixture so future rendering tests don’t reintroduce the same mistake.
3. Patch CSS token issue:

   * Add `--duration-default` to `tokens.css` *or* switch gallery CSS to a duration token that already exists.
4. Optional but recommended: apply the audit’s token cleanup list (only the named offenders) so the CSS stays teachable for agents.
5. Run `make lint` and `make test` to confirm the suite is green and stable.

**Design Guidelines**
Follow the token-only styling rules and the workflow docs when touching CSS: component CSS must use tokens (spacing/colour/typography roles), and changes should not reintroduce hardcoded values outside `tokens.css`.

**Acceptance Criteria**:

* [ ] The homepage rendering tests no longer return 404 in batch runs (re-run the whole suite at least twice; ideally once with `pytest -n auto`).
* [ ] `--duration-default` is no longer undefined (either defined in `tokens.css` or removed as a dependency by refactoring gallery CSS).
* [ ] `make lint` and `make test` pass.
* [ ] If optional cleanup is done: the specific hardcoded values cited in the audit are converted to tokens without changing visual intent.
