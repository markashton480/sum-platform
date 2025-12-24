# THEME-030: Bundle – ButtonGroupBlock + SocialProofQuoteBlock (Theme A)

## Branch
- [ ] Checkout/create: `theme/theme-030-buttons-social-proof-bundle`
- [ ] Verify: `git branch --show-current`

## Context
We’re bundling two small-but-worthwhile content callout blocks into one PR to avoid micro-PR churn:
- ButtonGroupBlock (CTAs)
- SocialProofQuoteBlock (quote + attribution/logo)

Both are “rewrite existing blocks” tasks, both are template-focused, and bundling is safe because they’re adjacent in content usage and require similar review effort.

Same asset rule applies: if theme CSS/fingerprint are required for checks, regenerate them **after rebasing onto origin/develop** and commit them last.

## Objective
Implement Theme A overrides for both blocks and add one bundled test file that covers:
- alignment + style mapping for buttons
- conditional rendering for social proof quote (logo + attribution)

## Key Files
- `themes/theme_a/templates/sum_core/blocks/content_buttons.html` – Theme A override (create/replace)
- `themes/theme_a/templates/sum_core/blocks/content_social_proof_quote.html` – Theme A override (create/replace)
- Core fallback templates for both (reference only)
- `docs/dev/design/wireframes/sage-and-stone/compiled/blog_article.html` – reference for CTA groups + callouts
- `tests/themes/test_theme_a_buttons_social_proof_rendering.py` – bundled test (unique)

## Acceptance Criteria
- [ ] Preflight run at start (`/prompts:sum-preflight TICKET_ID=THEME-030` or `make preflight`)
- [ ] ButtonGroupBlock:
  - [ ] renders 1–3 buttons with correct labels + hrefs
  - [ ] alignment works (left/center/right) via wrapper classes
  - [ ] primary/secondary style maps to existing Theme A button classes (no new bespoke CSS)
- [ ] SocialProofQuoteBlock:
  - [ ] renders semantic `<figure><blockquote><figcaption>`
  - [ ] optional logo renders only if provided (no broken tag)
  - [ ] author/role/company render only if provided
  - [ ] reveal hooks included; content visible by default
- [ ] Bundled theme test added and passing
- [ ] `make test` passes
- [ ] If assets changed for CI: regenerate post-rebase, commit last

## Steps
1. Branch verification
   - [ ] Checkout/create `theme/theme-030-buttons-social-proof-bundle`
   - [ ] Verify branch: `git branch --show-current`
   - [ ] Run preflight: `/prompts:sum-preflight TICKET_ID=THEME-030` (or `make preflight`)

2. Implement ButtonGroupBlock override
   - [ ] Create/update `themes/theme_a/templates/sum_core/blocks/content_buttons.html`
   - [ ] Map alignment → `justify-start|justify-center|justify-end`
   - [ ] Map style:
     - `primary` → Theme A primary button class
     - `secondary` → Theme A secondary/outline class
   - [ ] Ensure mobile behavior is reasonable (stack or wrap)

3. Implement SocialProofQuoteBlock override
   - [ ] Create/update `themes/theme_a/templates/sum_core/blocks/content_social_proof_quote.html`
   - [ ] Use `<figure>` semantics with `<blockquote>` and `<figcaption>`
   - [ ] Render quote with `|linebreaksbr` if needed
   - [ ] Render logo via `{% image %}` if provided (alt derived from attribution/company when possible)
   - [ ] Conditional attribution lines (don’t render empty separators)

4. Add bundled tests
   - [ ] Create `tests/themes/test_theme_a_buttons_social_proof_rendering.py`
   - [ ] Assert:
     - both templates resolve to Theme A overrides (origin check)
     - alignment affects wrapper classes
     - button style classes applied
     - social proof quote conditionals behave (logo/author absent/present)

5. Rebase + regenerate assets if required
   - [ ] `git fetch origin && git rebase origin/develop`
   - [ ] If `main.css` / `.build_fingerprint` dirty and CI expects them:
     - rebuild theme CSS + regenerate fingerprint
     - commit as final commit

6. Run full checks
   - [ ] `pytest -q tests/themes/test_theme_a_buttons_social_proof_rendering.py`
   - [ ] `make test`

## Testing Requirements
- [ ] Run: `pytest -q tests/themes/test_theme_a_buttons_social_proof_rendering.py`
- [ ] Run: `make test`
- [ ] Expected: all green

## Documentation Updates
Update if changes affect:
- [ ] `blocks-reference.md` (not expected)
- [ ] `WIRING-INVENTORY.md` (not expected)
- [ ] `page-types-reference.md` (not expected)

## Deliverables
- [ ] Create `THEME-030_followup.md` with:
  - Summary
  - Files modified/created
  - Test results
  - Asset regeneration note (yes/no, when done)

## Commit & Push
- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-030): theme a buttons + social proof quote templates`
- [ ] If assets regenerated, final commit: `chore(THEME-030): regenerate theme_a css artifacts`
- [ ] Push: `git push origin theme/theme-030-buttons-social-proof-bundle`

## Verification
- [ ] `git status --porcelain` → empty or documented untracked only

## Recommended Agent
CriteriaSelectionModel: GPT-5.2 Codex  
Thinking: Standard  
Rationale: Two small templates + one bundled test; needs careful conditional rendering and low churn.
