# THEME-018: Theme A — ContactFormBlock template (split layout + floating labels)

## Branch

- [ ] Checkout/create: `theme/theme-018-contact-form-block`
- [ ] Verify: `git branch --show-current`

## Context

`ContactFormBlock` is a Phase 1 homepage priority block in `new-theme-plan.md` and is used across the site (homepage + contact page + service pages per showroom wiring). We need Theme A’s override to match the Sage & Stone wireframe while preserving SUM Core’s form submission contract (endpoint, hidden fields, anti-spam, success handling).
Reference the “frame, not the paint” approach in `THEME-GUIDE.md`: structure and component classes first; branding comes from CSS variables / SiteSettings.

## Objective

Implement `themes/theme_a/templates/sum_core/blocks/contact_form.html` to match the wireframe’s split layout:

- Left column: section header content (eyebrow/heading/intro), designed to be sticky on desktop.
- Right column: the contact form with accessible floating-label inputs and a primary submit button.
- Mobile: stacked layout with sane spacing.
  Preserve all core-required form mechanics (action, CSRF, hidden inputs, honeypot/timing token if present).

## Key Files

- `themes/theme_a/templates/sum_core/blocks/contact_form.html` – Theme override to implement (main deliverable)
- `core/sum_core/templates/sum_core/blocks/contact_form.html` – Reference for form contract (field names, hidden inputs, data attrs)
- `themes/theme_a/static/theme_a/css/input.css` – Only touch if you need new component utilities (prefer not to)
- `themes/theme_a/static/theme_a/css/main.css` – Tailwind compiled output (update only if required)
- `themes/theme_a/build_fingerprint` – Update only if `main.css` changes
- `tests/themes/test_theme_a_contact_form_rendering.py` – New/updated theme contract test for this block
- Wireframe reference: `docs/dev/design/wireframes/sage-and-stone/compiled/index.html` (contact section) and `compiled/contact.html` if present

## Acceptance Criteria

- [ ] Theme A `ContactFormBlock` renders with split layout and matches wireframe closely (spacing/typography/CTA treatment)
- [ ] Desktop behavior: left header column is sticky (or functionally equivalent) without breaking smaller breakpoints
- [ ] Form keeps SUM Core contract:
  - [ ] posts to the correct endpoint (likely `/forms/submit/`)
  - [ ] includes CSRF token
  - [ ] includes any required hidden inputs (`form_type`, etc.) exactly as core expects
  - [ ] does not rename/remove core field names or anti-spam fields
- [ ] Uses semantic classes + existing component classes (`.btn`, `.btn-primary`, etc.); no hardcoded “Sage & Stone” content
- [ ] Accessibility baseline:
  - [ ] every input has a label (floating label is still a real `<label for="">`)
  - [ ] clear focus states
  - [ ] errors don’t rely on color alone (if template renders errors)
- [ ] Tests pass per `test-strategy-post-mvp-v1.md`
- [ ] No regressions in existing functionality

## Steps

1. Branch verification
   - [ ] Checkout/create branch and verify current branch name
2. Inspect the core block template contract
   - [ ] Open `core/sum_core/templates/sum_core/blocks/contact_form.html`
   - [ ] Identify:
     - action URL
     - required hidden inputs (e.g. `form_type`, timing token, honeypot)
     - expected field names and any `data-*` hooks used by JS
3. Implement Theme A override template
   - [ ] Create/update: `themes/theme_a/templates/sum_core/blocks/contact_form.html`
   - [ ] Start by copying the wireframe HTML structure/classes for the contact section (then “bind” content):
     - `eyebrow`, `heading`, `intro` from block fields
     - `submit_label` and `success_message` from block fields (with defaults respected)
   - [ ] Use component classes:
     - submit button uses `.btn-primary`
     - avoid inventing one-off button styles
   - [ ] Floating labels:
     - use CSS/Tailwind `peer` pattern or an existing input pattern in Theme A
     - ensure labels remain clickable/associated to inputs
   - [ ] Sticky header:
     - implement with `lg:sticky lg:top-*` (or the project’s established breakpoint guidance)
4. Keep file churn tight
   - [ ] Do NOT touch unrelated files.
   - [ ] Only rebuild `main.css` if new classes are introduced that are not already present in the compiled output.
     - If you run a build, commit CSS/fingerprint only if there is an actual diff.
5. Add/extend theme rendering tests
   - [ ] Add `tests/themes/test_theme_a_contact_form_rendering.py`
   - [ ] Test should assert the presence of the critical contract elements:
     - form action is correct
     - CSRF token present (or at least `{% csrf_token %}` rendered in template render context)
     - required hidden inputs are present (especially `form_type="contact"` if core uses it)
   - [ ] Also assert a couple of key structural hooks/classes (e.g., section wrapper and submit button class) to prevent regressions.

## Testing Requirements

- [ ] Unit/integration tests as required by strategy
- [ ] Run: `make test`
- [ ] Run targeted: `pytest -q tests/themes/test_theme_a_contact_form_rendering.py`
- [ ] Expected: all green locally; no snapshot of failing unrelated suites

## Documentation Updates

Update if changes affect:

- [ ] `blocks-reference.md` (only if block fields/contract changed — not expected)
- [ ] `page-types-reference.md` (not expected)
- [ ] `WIRING-INVENTORY.md` (only if form wiring/endpoint expectations change — not expected)

## Deliverables

- [ ] Create `THEME-018_followup.md` (same directory as this ticket) containing:
  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push

- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-018): theme_a ContactFormBlock template`
  - **Must include both** `THEME-018.md` AND `THEME-018_followup.md`
- [ ] Push: `git push origin theme/theme-018-contact-form-block`

## Verification

- [ ] `git status --porcelain` → empty or documented untracked only

---
