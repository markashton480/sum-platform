# WO: Multi-theme Validation (v0.7.0)

## Metadata

- **Version:** v0.7.0
- **Component:** themes
- **Priority:** P0 (Must Land)
- **Branch:** `feature/multi-theme`
- **Parent VD:** #363
- **Issue:** #364

---

## Description

Prove the SUM Platform architecture genuinely supports multiple themes by implementing Theme B (minimum requirement) and Theme C (stretch goal if low friction). This work order establishes theme contracts, ensures the seeder supports theme selection, and documents the theme system for future theme authors.

**Why this matters:**
- Multi-theme is a core platform promise that hasn't been validated beyond Theme A
- Theme contracts prevent regression and enable third-party theme development
- Demonstrates platform flexibility for different client aesthetics

---

## Acceptance Criteria

- [ ] Theme B is fully implemented and passes all template contract tests
- [ ] Theme B seeder profile generates a complete, functional site
- [ ] Theme contract is documented in `docs/dev/THEME-GUIDE.md`
- [ ] Theme selection mechanism exists (seeder flag or config)
- [ ] No regressions in Theme A functionality
- [ ] Theme C implemented (stretch goal - only if low friction)

---

## Deliverables

1. **Theme B Implementation** (`themes/theme_b/`)
   - All required templates matching theme contract
   - Static assets (CSS, JS, images)
   - Block template overrides where needed

2. **Theme Contract Documentation**
   - Required templates list
   - Block rendering expectations
   - Static asset conventions
   - Testing requirements

3. **Seeder Theme Support**
   - `--theme` flag for `seed_showroom` command
   - Theme B seeder profile
   - Theme selection in scaffolded projects

4. **Theme C (Stretch)**
   - Only if adding is low friction
   - Same requirements as Theme B

---

## Technical Approach

### Theme B Strategy

1. **Identify minimal theme requirements** from Theme A analysis
2. **Create theme skeleton** with required directory structure
3. **Implement base templates** (base.html, page templates)
4. **Implement block templates** for all core blocks
5. **Add static assets** (Tailwind config, custom CSS)
6. **Create seeder profile** for Theme B content
7. **Validate with contract tests**

### Theme Contract Extraction

1. **Audit Theme A** to identify all templates and conventions
2. **Document required templates** with expected context variables
3. **Document block template interface** (what blocks pass to templates)
4. **Create contract test suite** that validates any theme

---

## Boundaries

### Do

- Create Theme B as a distinct visual style (not a copy of Theme A)
- Document theme contracts clearly for future theme authors
- Ensure seeder can generate sites with any implemented theme
- Add tests for theme contract compliance
- Keep Theme B scope minimal but complete

### Do NOT

- Create partial/incomplete themes
- Change Theme A while implementing Theme B
- Add new blocks solely for Theme B (use existing blocks)
- Over-engineer the theme selection mechanism
- Add theme switching runtime capability (compile-time selection is fine)

---

## Subtasks

### TASK-001: Audit Theme A and Extract Contract

**Description:**
Analyze Theme A to extract the implicit theme contract. Document all required templates, expected context variables, block template interfaces, and static asset conventions.

**Acceptance Criteria:**
- [ ] List of all templates in Theme A with their purposes
- [ ] Context variables documented for each template
- [ ] Block template interface documented
- [ ] Static asset conventions documented
- [ ] Draft theme contract in `docs/dev/THEME-GUIDE.md`

**Boundaries:**
- Do: Document what exists in Theme A
- Do: Identify which templates are required vs optional
- Do NOT: Change Theme A
- Do NOT: Add new requirements not present in Theme A

**Branch:** `feature/multi-theme/001-theme-contract-audit`

---

### TASK-002: Create Theme B Skeleton

**Description:**
Set up the Theme B directory structure with all required files based on the theme contract. This is the foundation before implementing specific templates.

**Acceptance Criteria:**
- [ ] `themes/theme_b/` directory structure matches contract
- [ ] `templates/` directory with required subdirectories
- [ ] `static/` directory with CSS/JS placeholders
- [ ] Tailwind config for Theme B
- [ ] Theme manifest/config if needed

**Boundaries:**
- Do: Create complete directory structure
- Do: Set up Tailwind with different design tokens
- Do NOT: Implement template content yet
- Do NOT: Copy Theme A templates directly

**Branch:** `feature/multi-theme/002-theme-b-skeleton`

---

### TASK-003: Implement Theme B Base Templates

**Description:**
Implement the base templates for Theme B including base.html, header, footer, and navigation components with a distinct visual style.

**Acceptance Criteria:**
- [ ] `base.html` with Theme B styling
- [ ] Header component with navigation
- [ ] Footer component
- [ ] Navigation rendering (including mega menu)
- [ ] Meta tags and SEO structure

**Boundaries:**
- Do: Create visually distinct design from Theme A
- Do: Use same context variables as Theme A (contract compliance)
- Do: Ensure responsive design
- Do NOT: Change core template tag behavior
- Do NOT: Add Theme B-specific context requirements

**Branch:** `feature/multi-theme/003-theme-b-base-templates`

---

### TASK-004: Implement Theme B Page Templates

**Description:**
Implement page type templates for Theme B including StandardPage, BlogIndexPage, BlogPostPage, ServiceIndexPage, ServicePage, and LegalPage.

**Acceptance Criteria:**
- [ ] StandardPage template functional
- [ ] BlogIndexPage template with listing
- [ ] BlogPostPage template with full content
- [ ] ServiceIndexPage template
- [ ] ServicePage template
- [ ] LegalPage template with TOC

**Boundaries:**
- Do: Match Theme A page template interfaces
- Do: Create distinct visual design
- Do NOT: Change page model behavior
- Do NOT: Add page types not in core

**Branch:** `feature/multi-theme/004-theme-b-page-templates`

---

### TASK-005: Implement Theme B Block Templates

**Description:**
Implement block templates for all core blocks in Theme B. Each block must render correctly with the Theme B visual style.

**Acceptance Criteria:**
- [ ] All content blocks render correctly
- [ ] All navigation blocks render correctly
- [ ] All form blocks render correctly
- [ ] All service blocks render correctly
- [ ] CTA/link blocks render correctly

**Boundaries:**
- Do: Implement all blocks from theme contract
- Do: Test each block type renders
- Do NOT: Skip blocks or leave placeholders
- Do NOT: Change block Python code

**Branch:** `feature/multi-theme/005-theme-b-block-templates`

---

### TASK-006: Create Theme B Seeder Profile

**Description:**
Create a seeder profile for Theme B that generates a complete demonstration site. Update `seed_showroom` to support theme selection.

**Acceptance Criteria:**
- [ ] Theme B seeder profile in `test_project/showroom/profiles/`
- [ ] `seed_showroom --theme theme_b` works
- [ ] Generated site is complete and functional
- [ ] All page types represented
- [ ] Images and content appropriate for Theme B style

**Boundaries:**
- Do: Create compelling demo content for Theme B
- Do: Ensure seeder is idempotent
- Do NOT: Break existing Theme A seeder
- Do NOT: Create incomplete demo site

**Branch:** `feature/multi-theme/006-theme-b-seeder`

---

### TASK-007: Theme Contract Tests

**Description:**
Create automated tests that validate theme contract compliance. These tests should work for any theme, not just Theme A or B.

**Acceptance Criteria:**
- [ ] Test suite validates required templates exist
- [ ] Test suite validates template renders without error
- [ ] Test suite validates block templates render
- [ ] Theme A passes all tests
- [ ] Theme B passes all tests

**Boundaries:**
- Do: Create reusable contract validation
- Do: Test both themes
- Do NOT: Create Theme-specific tests
- Do NOT: Test visual appearance (just functional)

**Branch:** `feature/multi-theme/007-theme-contract-tests`

---

### TASK-008: Theme C Implementation (Stretch)

**Description:**
If Theme B is complete with remaining capacity, implement Theme C following the same process. Only attempt if low friction.

**Acceptance Criteria:**
- [ ] Theme C fully implemented (if attempted)
- [ ] Theme C passes contract tests
- [ ] Theme C seeder profile works
- [ ] OR: Explicitly deferred with rationale

**Boundaries:**
- Do: Only attempt if Theme B is complete
- Do: Follow same process as Theme B
- Do NOT: Delay release for Theme C
- Do NOT: Create partial Theme C

**Branch:** `feature/multi-theme/008-theme-c` (if attempted)

---

## Merge Order

1. TASK-001 (Contract Audit) - foundational
2. TASK-002 (Skeleton) - depends on 001
3. TASK-003 (Base Templates) - depends on 002
4. TASK-004 (Page Templates) - depends on 003
5. TASK-005 (Block Templates) - can parallel with 004
6. TASK-006 (Seeder) - depends on 004, 005
7. TASK-007 (Contract Tests) - depends on 001, can validate 003-006
8. TASK-008 (Theme C) - only after 001-007 complete

---

## Estimated Effort

| Task | Estimate | Risk |
| ---- | -------- | ---- |
| TASK-001 | 2-3 hours | Low |
| TASK-002 | 1-2 hours | Low |
| TASK-003 | 4-6 hours | Medium |
| TASK-004 | 4-6 hours | Medium |
| TASK-005 | 6-8 hours | Medium |
| TASK-006 | 2-3 hours | Low |
| TASK-007 | 2-3 hours | Low |
| TASK-008 | 8-12 hours | High (stretch) |

**Total (without Theme C):** 21-31 hours
**Total (with Theme C):** 29-43 hours

---

## Notes

- Theme B should have a noticeably different aesthetic to prove theme flexibility
- Consider a minimal/clean theme vs Theme A's more elaborate design
- Theme contract is the most important long-term deliverable
- Theme C is explicitly a stretch goal - don't compromise Theme B for it
