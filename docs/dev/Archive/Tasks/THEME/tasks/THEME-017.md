# THEME-017: Theme A FAQBlock (Accordion + JSON-LD) — Sage & Stone parity

## Branch

- [ ] Checkout/create: `feat/THEME-017-faq-block-theme-a`
- [ ] Verify: `git branch --show-current`

## Context

FAQ appears on the Sage & Stone homepage and services page and must match the wireframe’s accordion styling/behavior. In core, `FAQBlock` also generates FAQPage JSON-LD for SEO and supports `allow_multiple_open`.  
We now have `THEME-GUIDE.md` as the “how to implement themes” reference, including a concrete FAQ accordion JS pattern to follow.

## Objective

Implement Theme A’s `FAQBlock` override so it:

- Matches Sage & Stone wireframe structure/styling for FAQ (index.html lines ~650–735; also used on services page).
- Preserves/continues FAQPage JSON-LD output.
- Correctly honors `allow_multiple_open` (default `True`) in accordion behavior.
- Keeps file churn tight (no “sync” side-effect changes).

## Key Files

- `themes/theme_a/templates/sum_core/blocks/faq.html` – **primary deliverable** (theme override for FAQ).
- `core/sum_core/templates/sum_core/blocks/faq.html` – reference for existing schema/semantics (do not lose JSON-LD).
- `docs/dev/design/wireframes/sage-and-stone/compiled/index.html` – copy the FAQ section markup/classes as baseline (lines ~650–735).
- `themes/theme_a/static/theme_a/js/main.js` – ensure accordion behavior exists and respects `allow_multiple_open` (adapt pattern from THEME-GUIDE).
- `tests/themes/test_theme_a_faq_rendering.py` (create) – rendering + contract tests for the theme override.

## Acceptance Criteria

- [ ] Theme override exists at `themes/theme_a/templates/sum_core/blocks/faq.html` and is loaded (theme wins).
- [ ] Renders eyebrow/heading/intro/items using block fields (no hardcoded S&S copy).
- [ ] Accordion opens/closes items; when `allow_multiple_open=False`, opening one closes others.
- [ ] FAQPage JSON-LD is still present and contains the items.
- [ ] Minimal diff scope: only files required for FAQ template + behavior + tests.
- [ ] Tests pass per `test-strategy-post-mvp-v1.md`.
- [ ] No regressions in existing functionality.

## Steps

1. **Branch safety**

   - [ ] Create/switch to `feat/THEME-017-faq-block-theme-a`
   - [ ] Confirm with `git branch --show-current`

2. **Establish baselines**

   - [ ] Open wireframe compiled homepage and isolate FAQ section (index.html ~650–735).
   - [ ] Inspect core FAQ template for JSON-LD generation + any existing accessibility semantics.

3. **Template implementation (Theme A override)**

   - [ ] Implement/update: `themes/theme_a/templates/sum_core/blocks/faq.html`
   - [ ] Follow THEME-GUIDE conversion rules: semantic colors, component classes, reveal usage where appropriate, no hardcoded hex.
   - [ ] Ensure safe, accessible markup:

     - Each item has a trigger with `aria-expanded`, and content region with `aria-hidden` or `aria-controls` linkage.
     - Generate stable-ish IDs to avoid collisions (recommend: prefix with `faq-{{ page.pk|default:'0' }}-{{ forloop.counter }}`).

   - [ ] Add a wrapper-level flag for behavior, e.g.:

     - `data-faq-allow-multiple="{{ self.allow_multiple_open|yesno:'true,false' }}"` (default should behave like True).

   - [ ] Preserve JSON-LD output (either keep the existing script block structure from core or reproduce it faithfully).

4. **Accordion behavior (JS)**

   - [ ] Check `themes/theme_a/static/theme_a/js/main.js` for existing FAQ logic.
   - [ ] If missing or incompatible, implement/adjust using THEME-GUIDE’s `data-faq-item`, `data-faq-trigger`, `data-faq-content` approach.
   - [ ] Modify the guide’s “close all others” logic to be conditional:

     - If wrapper says allow multiple = true → do NOT close others.
     - If false → close others (guide behavior).

   - [ ] Keep progressive enhancement in mind (no-JS should still show content reasonably). If you can’t preserve full accordion without JS, at least ensure content is reachable (e.g., using `<details>` fallback or default-open first item).

5. **Tests**

   - [ ] Add `tests/themes/test_theme_a_faq_rendering.py` following the existing Theme A block rendering test patterns (e.g., StatsBlock test style).
   - [ ] Assertions to include:

     - Theme template renders for FAQ block (not core).
     - FAQ content includes rendered questions/answers.
     - JSON-LD `<script type="application/ld+json">` exists and includes “FAQPage” and the questions.
     - `data-faq-allow-multiple` reflects `allow_multiple_open` values.

## Testing Requirements

- [ ] Run: `make test`
- [ ] Run focused: `pytest -q tests/themes -k faq`
- [ ] Expected: all green locally (and no surprise file churn).

## Documentation Updates

Update if changes affect:

- [ ] `blocks-reference.md` (only if block fields/behavior contract changed)
- [ ] `page-types-reference.md` (not expected)
- [ ] `WIRING-INVENTORY.md` (only if template wiring/resolution changed)

## Deliverables

- [ ] Create `THEME-017_followup.md` (same directory as this ticket) containing:

  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push

- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-017): implement Theme A FAQ accordion + JSON-LD`

  - **Must include both** `THEME-017.md` AND `THEME-017_followup.md`

- [ ] Push: `git push origin feat/THEME-017-faq-block-theme-a`

## Verification

- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent

**Model:** GPT-5.1 Codex Max
**Thinking:** Standard
**Rationale:** Mostly a contained template + small JS enhancement + tests. Moderate risk (schema + a11y + behavior flag) but doesn’t warrant heavyweight architectural reasoning.
