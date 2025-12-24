# THEME-035: ProcessStepsBlock template rewrite + theme test

## Branch
- [ ] Checkout/create: `theme/THEME-035-process-steps-block`
- [ ] Verify: `git branch --show-current`

## Context
ProcessStepsBlock (`process`) is a high-visibility section block used near the top
of `/services/` in the seeded showroom. We are in the “rewrite existing blocks”
phase (no new page types or navigation). The goal is to align with Theme A’s
section layout patterns, including sticky desktop headers.

Asset guardrail: avoid touching generated theme CSS artifacts
(`themes/theme_a/static/theme_a/css/main.css` and
`themes/theme_a/static/theme_a/css/.build_fingerprint`) for template-only tickets
unless CI requires a rebuild. If needed, rebuild once at branch tip.

## Objective
Override the core template for ProcessStepsBlock by implementing Theme A’s
version at `themes/theme_a/templates/sum_core/blocks/process_steps.html`, and
add theme tests to verify override resolution.

## Key Files
- `themes/theme_a/templates/sum_core/blocks/process_steps.html`
- `core/sum_core/templates/sum_core/blocks/process_steps.html` (reference only)
- `docs/dev/blocks-reference.md`
- `docs/dev/THEME-GUIDE.md`
- `tests/themes/test_theme_block_contracts.py`
- `tests/themes/test_theme_a_rendering.py`
- `tests/themes/test_theme_a_process_steps_rendering.py`

## Acceptance Criteria
- [ ] Theme A provides `themes/theme_a/templates/sum_core/blocks/process_steps.html`
- [ ] Template renders all fields correctly:
  - [ ] eyebrow (optional)
  - [ ] heading (required richtext)
  - [ ] intro (optional richtext)
  - [ ] steps list (min 3) with number/title/description
  - [ ] auto-number when `step.number` is missing
- [ ] Desktop layout includes sticky header behavior (header column sticks)
- [ ] Mobile layout is clean and readable (no sticky behavior)
- [ ] Theme tests verify template override resolution
- [ ] Tests pass per `test-strategy-post-mvp-v1.md`
- [ ] No unnecessary diffs to generated CSS artifacts

## Steps
1. Branch verification
   - [ ] Checkout/create `theme/THEME-035-process-steps-block`
   - [ ] Verify branch: `git branch --show-current`

2. Implement Theme A override
   - [ ] Create/update `themes/theme_a/templates/sum_core/blocks/process_steps.html`
   - [ ] Use `{% load wagtailcore_tags %}` and render rich text with `|richtext`
   - [ ] Implement two-column section layout on desktop:
     - [ ] Left column: sticky section header
     - [ ] Right column: steps list
   - [ ] Steps rendering requirements:
     - [ ] Number badge uses `step.number` or `forloop.counter`
     - [ ] Title prominent; description optional (render via `|richtext`)
   - [ ] Keep markup semantic and accessible

3. Update tests
   - [ ] Add `sum_core/blocks/process_steps.html` to required theme block templates
   - [ ] Assert template override resolution via `get_template`
   - [ ] Add focused rendering assertions for the Theme A template

4. Run tests
   - [ ] `pytest tests/themes/ -v`
   - [ ] `make test`

## Documentation Updates
Update only if block contracts changed (not expected):
- [ ] `blocks-reference.md`
- [ ] `page-types-reference.md`
- [ ] `WIRING-INVENTORY.md`

## Deliverables
- [ ] Create `THEME-035_followup.md` with:
  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push
- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-035): rewrite ProcessStepsBlock template + theme contract test`
  - Must include both `THEME-035.md` and `THEME-035_followup.md`
- [ ] Push: `git push origin theme/THEME-035-process-steps-block`
- [ ] Open PR - monitor until green
- [ ] Resolve any open conversations

## Verification
- [ ] `git status --porcelain` → empty or documented untracked only
