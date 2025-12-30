# WO: Internal Linking & CTAs (v0.7.0)

## Metadata

- **Version:** v0.7.0
- **Component:** blocks
- **Priority:** P0 (Must Land)
- **Branch:** `feature/internal-linking`
- **Parent VD:** #TBD
- **Issue:** #TBD

---

## Description

Fix internal linking across all blocks and add a dedicated CTABlock for consistent call-to-action patterns. The UniversalLinkBlock exists and supports internal pages, but it's not used consistently across all blocks. This work order audits all link usages, fixes blocks using raw URLBlock, and adds a purpose-built CTABlock.

**Why this matters:**
- Internal linking was reported missing from CTAs in the Sage & Stone review
- ServiceCardItemBlock uses URLBlock instead of UniversalLinkBlock
- Editors need page chooser in all link contexts
- CTAs are used throughout but lack a consistent block pattern
- This is platform correctness that underpins themes and pages

---

## Acceptance Criteria

- [ ] All blocks that accept links use UniversalLinkBlock
- [ ] Page chooser appears in all link contexts in Wagtail admin
- [ ] Internal links render correctly in all theme templates
- [ ] CTABlock available with primary/secondary button support
- [ ] CTABlock renders consistently across themes
- [ ] No regression in existing link functionality
- [ ] Link validation shows warnings for missing targets

---

## Deliverables

1. **UniversalLinkBlock Audit & Fixes**
   - Inventory all blocks with link fields
   - Fix blocks using URLBlock to use UniversalLinkBlock
   - Update templates to use link.href consistently

2. **CTABlock Implementation**
   - Primary and secondary button support
   - Both use UniversalLinkBlock
   - Style variants (inline, card, banner)
   - Analytics attributes support

3. **Template Updates**
   - Ensure all themes render UniversalLinkBlock correctly
   - Add CTABlock templates for all themes
   - Handle all link types (page, url, email, phone, anchor)

4. **Link Validation**
   - Admin hints showing link type
   - Warnings for broken internal links (deleted pages)

---

## Technical Approach

### Current State Analysis

From the codebase review:

```python
# core/sum_core/blocks/links.py - UniversalLinkBlock EXISTS and supports:
LINK_TYPE_CHOICES = [
    ("page", "Page"),      # Internal page linking
    ("url", "External URL"),
    ("email", "Email"),
    ("phone", "Phone"),
    ("anchor", "Anchor"),
]
```

**Problem:** `ServiceCardItemBlock` and potentially other blocks use `URLBlock` instead:

```python
# core/sum_core/blocks/services.py (BROKEN)
link_url = URLBlock()  # Should be UniversalLinkBlock!
```

### Fix Strategy

1. **Audit** all blocks in `core/sum_core/blocks/`
2. **Replace** `URLBlock` with `UniversalLinkBlock` where appropriate
3. **Update** templates to use `link.href` and `link.attrs_str`
4. **Test** page chooser appears in admin
5. **Test** links render correctly in all themes

### CTABlock Design

```python
class CTABlock(StructBlock):
    heading = CharBlock(required=False)
    description = RichTextBlock(required=False)
    primary_button = StructBlock([
        ('text', CharBlock()),
        ('link', UniversalLinkBlock()),
    ])
    secondary_button = StructBlock([
        ('text', CharBlock(required=False)),
        ('link', UniversalLinkBlock(required=False)),
    ], required=False)
    style = ChoiceBlock(choices=[
        ('inline', 'Inline'),
        ('card', 'Card'),
        ('banner', 'Banner'),
    ], default='inline')

    class Meta:
        icon = 'pick'
        label = 'Call to Action'
```

---

## Boundaries

### Do

- Audit all blocks for link field usage
- Replace URLBlock with UniversalLinkBlock where links should support pages
- Add CTABlock to PageStreamBlock
- Update all theme templates for consistent link rendering
- Add validation for broken internal links
- Write comprehensive tests

### Do NOT

- Change UniversalLinkBlock's core behavior
- Add link analytics tracking (defer)
- Add A/B testing for CTAs (defer)
- Change existing link appearance in themes
- Remove URLBlock entirely (still valid for URL-only contexts)

---

## Subtasks

### TASK-001: Audit All Link Usages

**Description:**
Create comprehensive inventory of all blocks that use link fields. Identify which use URLBlock, PageChooserBlock, or UniversalLinkBlock. Document which need fixing.

**Acceptance Criteria:**
- [ ] List of all blocks with link-type fields
- [ ] Classification: URLBlock / PageChooserBlock / UniversalLinkBlock
- [ ] List of blocks that need migration to UniversalLinkBlock
- [ ] Documentation in planning directory

**Boundaries:**
- Do: Check all files in `core/sum_core/blocks/`
- Do: Check navigation blocks
- Do NOT: Make changes yet (audit only)
- Do NOT: Include third-party blocks

**Branch:** `feature/internal-linking/001-link-audit`

---

### TASK-002: Fix ServiceCardItemBlock

**Description:**
Update ServiceCardItemBlock to use UniversalLinkBlock instead of URLBlock. Update service card templates in all themes.

**Acceptance Criteria:**
- [ ] ServiceCardItemBlock uses UniversalLinkBlock
- [ ] Migration created if needed
- [ ] Theme A service card template updated
- [ ] Page chooser appears in admin
- [ ] Internal links render correctly

**Boundaries:**
- Do: Fix both ServiceCardItemBlock and ServiceCardsBlock
- Do: Update all theme templates
- Do NOT: Change service card visual design
- Do NOT: Add new service card features

**Branch:** `feature/internal-linking/002-fix-service-cards`

---

### TASK-003: Fix Other Identified Blocks

**Description:**
Based on TASK-001 audit, fix all other blocks identified as using URLBlock where UniversalLinkBlock is appropriate.

**Acceptance Criteria:**
- [ ] All identified blocks fixed
- [ ] Templates updated for each fixed block
- [ ] Page chooser works in all contexts
- [ ] Tests pass for all updated blocks

**Boundaries:**
- Do: Fix all blocks from audit
- Do: Update corresponding templates
- Do NOT: Change blocks that legitimately need URL-only
- Do NOT: Change block behavior beyond link type

**Branch:** `feature/internal-linking/003-fix-other-blocks`

---

### TASK-004: Create CTABlock

**Description:**
Create dedicated CTABlock with primary/secondary buttons, style variants, and proper UniversalLinkBlock usage.

**Acceptance Criteria:**
- [ ] CTABlock created with structure from technical approach
- [ ] Primary button required, secondary optional
- [ ] Style variants: inline, card, banner
- [ ] Both buttons use UniversalLinkBlock
- [ ] Block registered in PageStreamBlock

**Boundaries:**
- Do: Create flexible, reusable CTA pattern
- Do: Support common CTA patterns
- Do NOT: Add animation or JS behavior
- Do NOT: Add A/B testing fields

**Branch:** `feature/internal-linking/004-cta-block`

---

### TASK-005: CTABlock Theme Templates

**Description:**
Create CTABlock templates for all themes (Theme A, Theme B if exists). Ensure consistent rendering across style variants.

**Acceptance Criteria:**
- [ ] Theme A CTABlock template
- [ ] All style variants render correctly
- [ ] Responsive design for all variants
- [ ] Theme B template (if Theme B exists)
- [ ] Consistent button styling with theme

**Boundaries:**
- Do: Follow theme design patterns
- Do: Make all variants accessible
- Do NOT: Add theme-specific CTA features
- Do NOT: Change existing button styles

**Branch:** `feature/internal-linking/005-cta-templates`

---

### TASK-006: Link Rendering Consistency

**Description:**
Ensure all themes render UniversalLinkBlock consistently. Handle all link types (page, url, email, phone, anchor) correctly.

**Acceptance Criteria:**
- [ ] Page links render with correct href
- [ ] External URLs render with target="_blank" if configured
- [ ] Email links render as mailto:
- [ ] Phone links render as tel:
- [ ] Anchor links render as #anchor
- [ ] All themes handle all types

**Boundaries:**
- Do: Test all link types in all themes
- Do: Fix any rendering inconsistencies
- Do NOT: Add new link types
- Do NOT: Change link opening behavior

**Branch:** `feature/internal-linking/006-link-rendering`

---

### TASK-007: Link Validation in Admin

**Description:**
Add validation hints in Wagtail admin showing link type and warnings for potentially broken links (deleted/unpublished pages).

**Acceptance Criteria:**
- [ ] Link type indicator in admin panels
- [ ] Warning shown for links to unpublished pages
- [ ] Warning shown for links to deleted pages (if detectable)
- [ ] Validation doesn't block saving (warnings only)

**Boundaries:**
- Do: Add helpful hints and warnings
- Do: Use Wagtail's validation patterns
- Do NOT: Block page saving for link issues
- Do NOT: Add link repair functionality

**Branch:** `feature/internal-linking/007-link-validation`

---

### TASK-008: Comprehensive Link Tests

**Description:**
Add comprehensive tests for all link functionality including block rendering, template output, and admin behavior.

**Acceptance Criteria:**
- [ ] Tests for each link type rendering
- [ ] Tests for CTABlock rendering
- [ ] Tests for fixed blocks (service cards, etc.)
- [ ] Tests for link validation
- [ ] All tests pass in CI

**Boundaries:**
- Do: Cover all link scenarios
- Do: Test both block output and template rendering
- Do NOT: Test visual appearance
- Do NOT: Add browser/E2E tests

**Branch:** `feature/internal-linking/008-link-tests`

---

## Merge Order

1. TASK-001 (Audit) - foundational, informs other tasks
2. TASK-002 (Service Cards) - highest priority fix
3. TASK-003 (Other Blocks) - depends on audit
4. TASK-004 (CTABlock) - can parallel with 002/003
5. TASK-005 (CTA Templates) - depends on 004
6. TASK-006 (Link Rendering) - depends on 002/003
7. TASK-007 (Validation) - depends on link fixes
8. TASK-008 (Tests) - can start early, finalize after all fixes

---

## Estimated Effort

| Task | Estimate | Risk |
| ---- | -------- | ---- |
| TASK-001 | 1-2 hours | Low |
| TASK-002 | 2-3 hours | Low |
| TASK-003 | 2-4 hours | Medium (depends on audit) |
| TASK-004 | 2-3 hours | Low |
| TASK-005 | 2-3 hours | Low |
| TASK-006 | 2-3 hours | Medium |
| TASK-007 | 2-3 hours | Medium |
| TASK-008 | 2-3 hours | Low |

**Total:** 15-24 hours

---

## Testing Requirements

- Unit tests for each block type
- Template rendering tests for all link types
- Admin UI tests for page chooser functionality
- Integration tests for link validation
- Cross-theme tests for CTABlock

---

## Notes

- This is platform correctness work - it should "just work" for editors
- CTABlock should become the preferred way to add calls to action
- Link validation is about helping editors, not blocking them
- Changes to UniversalLinkBlock should be minimal (it's already correct)
- Focus is on blocks that DON'T use it properly
