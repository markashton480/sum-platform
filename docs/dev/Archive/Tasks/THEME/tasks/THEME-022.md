# THEME-022: Rewrite Theme A RichTextContentBlock template (prose typography)

## Branch
- [ ] Checkout/create: `theme/theme-022-richtext-content-block`
- [ ] Verify: `git branch --show-current`

## Context
We’re staying on the “rewrite existing blocks” track. In Phase 2 (Content Blocks), the next high-impact block after page headers is RichTextContentBlock: it powers long-form page content (terms, about sections, blog article body) and is explicitly called out in Category A as “Prose typography configuration”. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

This ticket is designed to run cleanly in parallel with THEME-021 in a second worktree:
- THEME-021 touches `content_editorial_header.html`
- THEME-022 touches `content_richtext.html`
No overlap expected.

## Objective
Create/replace Theme A’s override for `RichTextContentBlock` to match the Sage & Stone editorial prose feel:
- readable line length, spacing rhythm, and heading styles
- consistent list styling
- block alignment option (`left` / `center`) supported
- no hardcoded colors (use semantic/token classes)
- covered by a focused theme rendering test.

## Key Files
- `themes/theme_a/templates/sum_core/blocks/content_richtext.html` – **Theme A override** (main deliverable) :contentReference[oaicite:4]{index=4}
- `core/sum_core/templates/sum_core/blocks/content_richtext.html` – reference for baseline semantics (core fallback)
- `docs/dev/design/wireframes/sage-and-stone/compiled/terms.html` – reference for long-form legal prose styling :contentReference[oaicite:5]{index=5}
- `docs/dev/design/wireframes/sage-and-stone/compiled/blog_article.html` – reference for article body typography :contentReference[oaicite:6]{index=6}
- `docs/dev/blocks-reference.md` – field contract: `align`, `body`, template path :contentReference[oaicite:7]{index=7}
- `tests/themes/test_theme_a_richtext_content_rendering.py` – add new theme rendering test (name can vary but keep it unique)

## Acceptance Criteria
- [ ] Theme A override exists at `themes/theme_a/templates/sum_core/blocks/content_richtext.html` :contentReference[oaicite:8]{index=8}
- [ ] Field contract respected (no schema change):
  - [ ] `self.body` renders via `{{ self.body|richtext }}`
  - [ ] `self.align` (`left/center`) changes layout appropriately :contentReference[oaicite:9]{index=9}
- [ ] Typography matches wireframe intent:
  - [ ] sensible max-width for long-form prose
  - [ ] heading hierarchy looks intentional
  - [ ] lists, links, blockquotes (if produced by richtext) look “designed”
- [ ] Uses semantic/token classes only (no hex, no “Sage & Stone” hardcoded)
- [ ] Adds a theme rendering test that asserts:
  - template origin resolves to Theme A override
  - `align=center` results in expected wrapper classes
  - richtext markup is present (e.g. `<h2>`, `<ul>`, `<a>`)
- [ ] `make test` stays green per `test-strategy-post-mvp-v1.md` :contentReference[oaicite:10]{index=10}
- [ ] Minimal diff scope (no rebuilds/sync tooling unless strictly required)

## Steps
1. Branch verification
   - [ ] Checkout/create `theme/theme-022-richtext-content-block`
   - [ ] Confirm: `git branch --show-current`

2. Pull canonical markup cues from wireframes
   - [ ] Inspect `compiled/terms.html` and `compiled/blog_article.html` for body/prose classes, spacing, link styling, headings. :contentReference[oaicite:11]{index=11}

3. Implement Theme A override template
   - [ ] Create/update `themes/theme_a/templates/sum_core/blocks/content_richtext.html`
   - [ ] Render structure:
     - outer section wrapper with consistent vertical spacing
     - inner container with max width (likely narrower than `max-w-7xl`; use wireframe guidance)
     - prose wrapper (`prose` / `prose-lg` style approach if Theme A already uses it; otherwise emulate with Tailwind typography utilities)
   - [ ] Alignment mapping:
     - `left`: standard container alignment
     - `center`: `mx-auto` plus `text-center` for headings where appropriate (don’t force all body text centered unless wireframe indicates)
   - [ ] Render body:
     - `{{ self.body|richtext }}` inside the prose wrapper
   - [ ] Keep “frame not paint”:
     - rely on typography + spacing + semantic text classes
     - avoid hardcoding colors; links should pick up theme link styling

4. Tests
   - [ ] Add `tests/themes/test_theme_a_richtext_content_rendering.py`
   - [ ] Assertions:
     - template origin is Theme A override
     - presence of richtext-produced tags
     - alignment toggles expected wrapper classes

5. Run tests
   - [ ] `pytest -q tests/themes/test_theme_a_richtext_content_rendering.py`
   - [ ] `make test`

## Testing Requirements
- [ ] Run: `pytest -q tests/themes/test_theme_a_richtext_content_rendering.py`
- [ ] Run: `make test`
- [ ] Expected: all green

## Documentation Updates
Update if changes affect:
- [ ] `blocks-reference.md` (not expected—template rewrite only) :contentReference[oaicite:12]{index=12}
- [ ] `WIRING-INVENTORY.md` (not expected)
- [ ] `page-types-reference.md` (not expected) :contentReference[oaicite:13]{index=13}

## Deliverables
- [ ] Create `THEME-022_followup.md` (same directory as this ticket) containing:
  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push
- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-022): rewrite Theme A RichTextContentBlock template`
  - **Must include both** `THEME-022.md` AND `THEME-022_followup.md`
- [ ] Push: `git push origin theme/theme-022-richtext-content-block`

## Verification
- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent
### Criteria Selection
- **Model:** GPT-5.2 Codex
- **Thinking:** Standard
- **Rationale:** Pure template + test work, but typography is easy to subtly regress. We want careful binding and minimal churn.
