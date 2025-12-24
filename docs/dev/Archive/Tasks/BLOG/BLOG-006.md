# BLOG.006: Form Templates and Rendering

**Phase:** 2 - Forms Rendering + Submission  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 14h  
**Dependencies:** BLOG.003, BLOG.004

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-006-form-templates
```

## Objective

Create the complete template and frontend implementation for rendering dynamic forms. This includes three presentation styles (inline, modal, sidebar), Tailwind styling, and JavaScript for interactions.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:226-252`
- Wagtail Templates: https://docs.wagtail.org/en/stable/topics/writing_templates.html
- Existing Forms: `themes/theme_a/templates/sum_core/forms/`
- Existing Form Styling: Check existing contact forms for patterns
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **Main Template:** `themes/theme_a/templates/sum_core/blocks/dynamic_form_block.html`
- **Supporting Files:** `themes/theme_a/static/js/` and `themes/theme_a/static/css/` as needed

### Template Structure

Replace placeholder template created in BLOG.003 with full implementation:

```django
{% load wagtailcore_tags %}

{# Generate Django form from FormDefinition #}
{% with form_class=self.form_definition|generate_dynamic_form %}
    {% with form=form_class %}
        
        <div class="dynamic-form-wrapper" data-presentation="{{ self.presentation_style }}">
            
            {% if self.presentation_style == 'inline' %}
                {% include 'sum_core/forms/_dynamic_form_inline.html' %}
            {% elif self.presentation_style == 'modal' %}
                {% include 'sum_core/forms/_dynamic_form_modal.html' %}
            {% elif self.presentation_style == 'sidebar' %}
                {% include 'sum_core/forms/_dynamic_form_sidebar.html' %}
            {% endif %}
            
        </div>
        
    {% endwith %}
{% endwith %}
```

### Presentation Variants

Create three sub-templates:

1. **_dynamic_form_inline.html**
   - Renders form directly in page flow
   - Standard form layout with labels above fields
   - Submit button at bottom

2. **_dynamic_form_modal.html**
   - CTA button triggers modal overlay
   - Modal contains form
   - Close button and click-outside-to-close
   - Form centered in viewport

3. **_dynamic_form_sidebar.html**
   - Fixed position sidebar (right side)
   - Slide-in animation
   - Close button
   - Form contained in sidebar panel

### Form Rendering Components

Create shared form rendering template:
- **File:** `themes/theme_a/templates/sum_core/forms/_dynamic_form_fields.html`

Include:
- CSRF token
- Honeypot field (hidden, for spam detection)
- Timing token (bot detection - timestamp in hidden field)
- Loop through form fields and render each
- Handle layout blocks (SectionHeadingBlock, HelpTextBlock)
- Error message display
- Success message area

### Tailwind Styling

Style forms to match existing SUM Platform form patterns:
- Field containers with consistent spacing
- Label styling (bold, margin-bottom)
- Input field styling (border, padding, focus states)
- Error state styling (red border, error message)
- Loading/submitting state (disabled state, spinner)
- Button styling (primary CTA style)
- Responsive design (mobile-friendly)

Reference existing form styles in theme_a.

### JavaScript Interactions

Create `themes/theme_a/static/js/dynamic_forms.js`:

```javascript
// Modal functionality
// - Open modal on CTA button click
// - Close modal on close button or outside click
// - Prevent body scroll when modal open

// Sidebar functionality
// - Slide sidebar in/out
// - Close on button click
// - Persist state in session storage (optional)

// Form submission
// - AJAX submission with fetch API
// - Show loading state during submission
// - Display success message or errors
// - Clear form on success
// - Fallback to standard POST if AJAX fails

// Timing token
// - Set hidden field value on page load (timestamp)
// - Used for bot detection in backend
```

### Template Tag (if needed)

Create custom template tag/filter if needed:
- **File:** `core/sum_core/templatetags/form_tags.py`
- **Filter:** `generate_dynamic_form` - calls DynamicFormGenerator
- Takes FormDefinition, returns form instance

## Implementation Tasks

- [ ] Create custom template tag `generate_dynamic_form` in `core/sum_core/templatetags/form_tags.py`
- [ ] Update main `dynamic_form_block.html` template
- [ ] Create `_dynamic_form_inline.html`
- [ ] Create `_dynamic_form_modal.html`
- [ ] Create `_dynamic_form_sidebar.html`
- [ ] Create `_dynamic_form_fields.html` (shared rendering)
- [ ] Add honeypot and timing fields to form
- [ ] Style all variants with Tailwind CSS
- [ ] Create `dynamic_forms.js` with all interactions
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Add loading/submitting states
- [ ] Handle form validation errors display
- [ ] Test with all field types from BLOG.002
- [ ] Verify accessibility (keyboard navigation, ARIA labels)

## Acceptance Criteria

- [ ] All three presentation styles render correctly
- [ ] Forms display all field types properly
- [ ] Tailwind styling matches existing form aesthetic
- [ ] Modal opens/closes correctly
- [ ] Sidebar slides in/out smoothly
- [ ] JavaScript works without errors
- [ ] Form submission shows loading state
- [ ] Success/error messages display
- [ ] Honeypot and timing fields present (hidden)
- [ ] Responsive on all screen sizes
- [ ] Keyboard accessible
- [ ] Works with FormDefinitions containing all block types
- [ ] `make lint` passes

## Testing Commands

```bash
# Start development server
python core/sum_core/test_project/manage.py runserver

# Create test FormDefinition with all field types
# Create test page with DynamicFormBlock (all 3 presentation styles)
# Test in browser:
# - Inline rendering
# - Modal open/close
# - Sidebar slide in/out
# - All field types display
# - Responsive design
# - Form submission (will fail gracefully until BLOG.007)

# Check for JS errors in browser console

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(forms): add dynamic form templates and rendering

- Implement three presentation styles (inline, modal, sidebar)
- Create shared form field rendering template
- Add Tailwind CSS styling matching platform aesthetic
- Implement JavaScript for modal/sidebar interactions
- Add honeypot and timing fields for spam protection
- Support all field types from FormFieldBlocks
- Responsive and accessible design
- Template tag for form generation

Refs: BLOG.006"

git push origin feature/BLOG-006-form-templates

gh pr create \
  --base develop \
  --title "feat(forms): Dynamic form templates and rendering" \
  --body "Implements BLOG.006 - Complete frontend for dynamic forms.

## Changes
- Three presentation variants: inline, modal, sidebar
- Shared form field rendering template
- Tailwind styling for all form elements
- JavaScript for modal/sidebar interactions
- AJAX form submission (graceful degradation)
- Honeypot and timing fields
- Responsive and accessible
- Template tag for form generation

## Testing
- ✅ All presentation styles work
- ✅ All field types render correctly
- ✅ Modal and sidebar interactions smooth
- ✅ Responsive design verified
- ✅ Keyboard accessible
- ✅ No JS errors
- ✅ Lint checks pass

## Related
- Depends on: BLOG.003, BLOG.004
- Blocks on: BLOG.007 (submission handler integration)"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Test thoroughly in browser, address all feedback
```

## Notes for AI Agents

- **Critical path** task - required for end-to-end form functionality
- Follow existing form styling patterns exactly (check existing ContactFormBlock templates)
- Ensure AJAX submission has proper fallback to standard POST
- Modal must handle scroll locking (prevent body scroll when open)
- Sidebar should be fixed position but not overlap main content on mobile
- Honeypot field should be truly hidden (not just display:none - bots can detect that)
- Timing token: set value to current timestamp on page load via JS
- Test with screen reader if possible for accessibility
- Consider dark mode if theme supports it
