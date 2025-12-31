# Task

**Title:** `WO-SS-002: Fix footer duplication bug`

---

## Parent

**Work Order:** WO: Sage & Stone Deployment Review (v0.6.1)

---

## Branch

| Branch | Target |
|--------|--------|
| `fix/sage-stone-review/002-footer-fix` | `fix/sage-stone-review` |

```bash
git checkout fix/sage-stone-review
git pull origin fix/sage-stone-review
git checkout -b fix/sage-stone-review/002-footer-fix
git push -u origin fix/sage-stone-review/002-footer-fix
```

---

## Deliverable

This task will deliver:

- Fix for footer duplication bug
- Single "Studio" section in footer
- Updated theme template or CMS configuration guidance
- No visual regressions

---

## Background

### Issue Description

The footer displays two identical "Studio" sections. This occurs because:
1. The CMS-configured footer navigation menu includes a "Studio" section
2. The theme template hardcodes a "Studio" section
3. Both render, causing duplication

### Root Cause Analysis

From diagnosis report (commit eac7efa):
- Both the CMS setting and template include "Studio" content
- They appear side-by-side or stacked in the footer
- This creates visual redundancy and confusion

---

## Boundaries

### Do

- Fix the footer duplication by ONE of these approaches:
  - **Option A (Recommended):** Remove hardcoded Studio section from theme template, let CMS control it
  - **Option B:** Keep hardcoded section, document that CMS should NOT include Studio
- Ensure footer displays correctly with single Studio section
- Test on staging environment
- Document the chosen approach

### Do NOT

- ❌ Do not change footer layout/styling beyond the duplication fix
- ❌ Do not add new footer functionality
- ❌ Do not modify other theme components
- ❌ Do not change CMS navigation structure (unless Option A requires removal)

---

## Acceptance Criteria

- [ ] Footer displays single "Studio" section
- [ ] No visual regressions in footer
- [ ] Footer works correctly on all breakpoints
- [ ] Chosen approach documented
- [ ] Staging site verified
- [ ] `make lint && make test` passes

---

## Test Commands

```bash
make lint
make test

# Visual verification on staging
# https://sage-and-stone.lintel.site
```

---

## Files Expected to Change

```
# Option A (modify template):
themes/theme_a/templates/theme_a/includes/footer.html    # Modified

# Option B (document CMS config):
docs/themes/theme-a-configuration.md                      # New/Modified
```

---

## Dependencies

**Depends On:**
- [ ] WO-SS-001: Complete staging site review

**Blocks:**
- Nothing specific

---

## Risk

**Level:** Low-Medium

**Why:**
- Template changes could affect other clients
- Need to verify across different CMS configurations

**Mitigation:**
- Test thoroughly on staging
- Document the approach clearly
- Consider backward compatibility

---

## Labels

- [ ] `type:task`
- [ ] `type:bug`
- [ ] `component:themes`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied
- [ ] Parent Work Order updated

---

## Commit Message

```
fix(themes): resolve footer duplication in Theme A

- Remove hardcoded Studio section from footer template
- Footer content now controlled entirely by CMS navigation
- Document theme footer configuration requirements

Closes #TBD
```

---

## Implementation Notes

### Option A: Remove Hardcoded Section

If the footer template has something like:

```html
<!-- Before -->
<footer>
  {% include "theme_a/includes/footer_nav.html" %}

  <!-- Hardcoded Studio section -->
  <div class="studio-section">
    <h3>Studio</h3>
    <p>Contact info...</p>
  </div>
</footer>
```

Remove the hardcoded section:

```html
<!-- After -->
<footer>
  {% include "theme_a/includes/footer_nav.html" %}
  <!-- Studio section now managed via CMS footer navigation -->
</footer>
```

### Option B: Document CMS Configuration

Add documentation noting:
- Theme A footer includes a hardcoded Studio section
- CMS Footer Navigation should NOT include a "Studio" item
- If different contact info needed, modify the template
