# THEME-023: Rewrite Theme A QuoteBlock template (pull quote styling)

## Branch
- [x] Checkout/create: `theme/theme-023-quote-block`
- [x] Verify: `git branch --show-current`

## Context
We’re continuing Phase 2 “Editorial/Content Templates” in `new-theme-plan.md`, specifically the **QuoteBlock template (pull quotes)** item. :contentReference[oaicite:2]{index=2}  
QuoteBlock already exists and has a defined contract and template path (`sum_core/blocks/content_quote.html`). :contentReference[oaicite:3]{index=3}

This ticket is designed to be safe for parallel worktrees:
- THEME-021: `content_editorial_header.html`
- THEME-022: `content_richtext.html`
- THEME-023: `content_quote.html` (this ticket)
No expected overlap.

Follow `THEME-GUIDE.md` “frame not paint” conversion patterns: semantic colors, conditional rendering, reveal classes used correctly. :contentReference[oaicite:4]{index=4}

## Objective
Create/replace Theme A’s override for QuoteBlock to match the Sage & Stone editorial pull-quote feel:
- strong typographic quote mark / treatment
- optional author + role in a caption style
- reveal animation class hooks (progressive enhancement)
- no hardcoded hex colors or S&S strings
- add a focused Theme A rendering test.

## Key Files
- `themes/theme_a/templates/sum_core/blocks/content_quote.html` – **Theme A override** (create/replace) :contentReference[oaicite:5]{index=5}
- `core/sum_core/templates/sum_core/blocks/content_quote.html` – core fallback for reference (don’t change core in this ticket)
- `docs/dev/blocks-reference.md` – field contract (quote/author/role) + template path :contentReference[oaicite:6]{index=6}
- `tests/themes/test_theme_a_quote_rendering.py` – **new** test file (unique to avoid conflicts)
- `test-strategy-post-mvp-v1.md` – testing expectations / suite discipline :contentReference[oaicite:7]{index=7}

## Acceptance Criteria
- [x] Theme override exists at `themes/theme_a/templates/sum_core/blocks/content_quote.html`. :contentReference[oaicite:8]{index=8}
- [ ] Field contract respected (no schema changes):
  - [x] `quote` rendered (required)
  - [x] `author` renders only if provided
  - [x] `role` renders only if provided :contentReference[oaicite:9]{index=9}
- [ ] Output is semantic + accessible:
  - [x] uses `<figure><blockquote>…</blockquote><figcaption>…</figcaption></figure>` (or equivalent)
  - [x] author/role are plain text (no unsafe HTML)
- [ ] Styling matches Theme A editorial aesthetic:
  - [x] visually distinct from body prose (spacing, border/marker, typography hierarchy)
  - [x] uses semantic/token utilities (no hex, no inline styles)
- [ ] Reveal hooks:
  - [x] includes Theme A’s established `reveal` class pattern (but remains visible by default per progressive enhancement guidance)
- [ ] Tests:
  - [x] New theme rendering test asserts template origin is Theme A override and verifies conditional author/role rendering.
  - [x] `make test` stays green per `test-strategy-post-mvp-v1.md`. :contentReference[oaicite:10]{index=10}
- [x] Diff remains tight (no unrelated file churn; do not run sync tooling).

## Steps
1. Branch verification
   - [x] Checkout/create `theme/theme-023-quote-block`
   - [x] Confirm `git branch --show-current`

2. Inspect contract + current behavior
   - [x] Review QuoteBlock in `docs/dev/blocks-reference.md` (fields + template path). :contentReference[oaicite:11]{index=11}
   - [x] Open core template `core/sum_core/templates/sum_core/blocks/content_quote.html` to understand current structure and any existing CSS hooks.

3. Implement Theme A override template
   - [x] Create/update `themes/theme_a/templates/sum_core/blocks/content_quote.html`.
   - [x] Use semantic structure:
     - wrapper section spacing consistent with other page-content blocks
     - `<blockquote>` for the quote text (use `|linebreaksbr` if quote content may include line breaks)
     - optional `<figcaption>` that prints `author` and `role` with sensible separators (e.g. “— Name, Role” only when present)
   - [x] Apply Theme A typography:
     - strong quote styling (e.g. accent font/italic, border/marker)
     - keep colors semantic (e.g. `text-sage-black/80` is OK if it’s already part of Theme A tokens; no hex)
   - [x] Add `reveal` class hooks on the correct elements (quote, caption) following established Theme A patterns. :contentReference[oaicite:12]{index=12}

4. Add tests
   - [x] Create `tests/themes/test_theme_a_quote_rendering.py`.
   - [x] Assertions:
     - template origin resolves to Theme A override (`themes/theme_a/.../content_quote.html`)
     - quote text appears
     - author/role absent when empty, present when provided
     - (optional) reveal class exists in output to guard regression

5. Run tests
   - [x] `pytest -q tests/themes/test_theme_a_quote_rendering.py`
   - [x] `make test`

## Testing Requirements
- [x] Run: `pytest -q tests/themes/test_theme_a_quote_rendering.py`
- [x] Run: `make test`
- [x] Expected: all green

## Documentation Updates
Update if changes affect:
- [ ] `blocks-reference.md` (only if you discover a contract mismatch — not expected) :contentReference[oaicite:13]{index=13}
- [ ] `WIRING-INVENTORY.md` (only if template resolution changes — should not)
- [ ] `page-types-reference.md` (not expected)

## Deliverables
- [x] Create `THEME-023_followup.md` (same directory as this ticket) containing:
  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push
- [ ] Stage: `git add -A`
- [ ] Commit: `feat(THEME-023): rewrite Theme A QuoteBlock template`
  - **Must include both** `THEME-023.md` AND `THEME-023_followup.md`
- [ ] Push: `git push origin theme/theme-023-quote-block`

## Verification
- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent
### Criteria Selection
- **Model:** GPT-5.2 Codex
- **Thinking:** Standard
- **Rationale:** Tight, UI-heavy template rewrite with conditional rendering + test coverage; needs careful minimal-diff execution.
