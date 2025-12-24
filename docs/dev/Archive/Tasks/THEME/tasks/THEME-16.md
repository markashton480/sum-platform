# THEME-016: ServiceCardsBlock theme_a template rewrite (featured card layout)

## Branch

- [ ] Checkout/create: `feat/theme-016-service-cards`
- [ ] Verify: `git branch --show-current`

## Context

Now that post-MVP tests are back to green, we can resume Phase 1 homepage block work. The Theme A plan explicitly calls out **ServiceCardsBlock** as a homepage priority and expects the **“3 cards, 1 featured/large”** layout from the compiled Sage & Stone wireframe (homepage section around lines ~403–484).

Block contract (fields + child fields) is defined in `blocks-reference.md` and must not change as part of this ticket.

## Objective

Implement a Theme A override for `ServiceCardsBlock` that:

- matches the wireframe’s **featured card** composition,
- supports the existing block fields (eyebrow/heading/intro/cards/layout_style),
- uses the theme’s Tailwind/token universe (no hardcoded hex),
- preserves accessibility + graceful fallbacks (icon vs image, missing links, etc.).

## Key Files

- `themes/theme_a/templates/sum_core/blocks/service_cards.html` – **create/replace** Theme A override for the block template (main deliverable)
- `docs/dev/design/wireframes/sage-and-stone/compiled/index.html` – copy the **services grid** markup pattern (source of truth for layout/classes)
- `core/sum_core/blocks/` (where `ServiceCardsBlock` is defined) – verify field names and any constraints; use `rg "class ServiceCardsBlock"` to locate exact module
- `tests/themes/test_theme_a_service_cards_rendering.py` – add theme contract tests similar in spirit to StatsBlock’s theme rendering test (THEME-015) (path/name can follow existing `tests/themes/` conventions)

## Acceptance Criteria

- [ ] Theme A renders `ServiceCardsBlock` using `themes/theme_a/templates/sum_core/blocks/service_cards.html` (confirmed via template origin inspection or theme test harness).
- [ ] Visual layout matches wireframe intent: **one featured/large card + remaining smaller cards** on desktop; sensible mobile behavior (horizontal scroll or stacked per reference).
- [ ] Uses block contract exactly:

  - `eyebrow` optional
  - `heading` RichText (italic/bold features) and renders with correct typography
  - `intro` optional
  - `cards` list (min 1, max 12)
  - `layout_style` (`default`/`tight`) affects spacing variant

- [ ] Card rendering rules:

  - [ ] If `image` exists, render image (preferred); else render `icon` (emoji/short text); else render a neutral fallback marker.
  - [ ] If `link_url` exists, card (or CTA) is clickable; if not, render non-clickable card without broken anchors.
  - [ ] `link_label` defaults to “Learn more” when missing.

- [ ] No hardcoded brand strings or hex colors.
- [ ] Tests pass per post-MVP strategy:

  - [ ] targeted theme test(s) for ServiceCardsBlock added
  - [ ] full suite remains green (`make test`)

## Steps

1. **Branch verification**

   - Create/checkout branch and confirm it.

2. **Pull the canonical markup from the compiled wireframe**

   - Open: `docs/dev/design/wireframes/sage-and-stone/compiled/index.html`
   - Extract the _Services grid_ section (the one mapped to ServiceCardsBlock in the plan).
   - Treat this markup as “golden” for class names + structure.

3. **Implement Theme A template override**

   - Create/replace: `themes/theme_a/templates/sum_core/blocks/service_cards.html`
   - Implement section structure:

     - header area using `eyebrow`, `heading`, `intro`
     - cards area matching the wireframe grid/scroll behavior

   - **Featured card rule (important):**

     - Implement “featured” as the **first item** in `cards` (index 0) unless the wireframe clearly implies another deterministic rule.
     - Featured card gets the “large” grid span styling on desktop.
     - Document this in a brief comment inside the template (and in the followup report) so future us can decide whether to add an explicit “featured” boolean field later.

4. **Implement card partial logic cleanly**

   - Within the template (or via an include if a pattern exists in Theme A), render each card with:

     - media (image preferred, else icon)
     - title
     - description (`|richtext` if RichTextBlock output)
     - CTA link label when `link_url` exists

   - Avoid duplicating button styling: prefer Theme A’s established button/link pattern (as introduced during THEME-014 button standardisation).

5. **Add theme rendering tests**

   - Add `tests/themes/test_theme_a_service_cards_rendering.py` that asserts:

     - template resolves to Theme A override
     - featured rule is applied (first card has the “featured” wrapper/classes or structural marker)
     - link label default works
     - image-vs-icon fallback does not error and renders expected element(s)

   - Keep assertions resilient (structure/classes/origin), not brittle full HTML snapshots.

6. **Manual sanity check via showroom (fast iteration)**

   - Seed and view:

     - `python manage.py seed_showroom --clear --hostname localhost --port 8000`

   - Confirm on the homepage `/` that ServiceCardsBlock looks correct at mobile/tablet/desktop widths.

## Testing Requirements

- [ ] Run: `pytest tests/themes/test_theme_a_service_cards_rendering.py -q`
- [ ] Run: `make test`
- [ ] Expected: all green, no deletions/side effects to `themes/` (guardrails remain)

## Documentation Updates

Update if changes affect:

- [ ] `WIRING-INVENTORY.md` (not expected; wiring unchanged)
- [ ] `blocks-reference.md` (only if you discover contract mismatch; do **not** change fields in this ticket)
- [ ] `page-types-reference.md` (not expected)
- Optional (recommended): add 2–3 lines to `themes/theme_a/README.md` documenting the “first card is featured” behavior.

## Deliverables

- [ ] Create `THEME-016_followup.md` (same directory as this ticket) containing:

  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push

- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-016): implement theme_a ServiceCardsBlock template`

  - **Must include both** `THEME-016.md` AND `THEME-016_followup.md`

- [ ] Push: `git push origin feat/theme-016-service-cards`

## Verification

- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent

### Criteria Selection

- **Model:** Gemini Pro
- **Thinking:** Standard
- **Rationale:** This is Tailwind/UI-heavy and benefits from closely matching the compiled wireframe markup while safely binding Wagtail block fields.
