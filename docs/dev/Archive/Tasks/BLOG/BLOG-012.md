# BLOG.012: Form Management Features

**Phase:** 4 - Integration + Polish  
**Priority:** P1  
**Estimated Hours:** 9h  
**Dependencies:** BLOG.001

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-012-form-management
```

## Objective

Add first-class form management capabilities: clone/duplicate forms, active toggle behavior, support for multiple forms on same page, and optional versioning/archiving features.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:459-483`
- Wagtail Admin Actions: https://docs.wagtail.org/en/stable/extending/custom_admin_views.html
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Feature 1: Clone/Duplicate FormDefinition

**Location:** `core/sum_core/forms/models.py` and `core/sum_core/forms/wagtail_hooks.py`

Add clone method to FormDefinition:
```python
def clone(self):
    """
    Create a duplicate of this FormDefinition.
    
    Returns:
        New FormDefinition instance with copied fields
    """
    # Create copy
    cloned = FormDefinition(
        site=self.site,
        name=f"{self.name} (Copy)",
        slug=f"{self.slug}-copy",
        fields=self.fields.raw_data,  # Deep copy StreamField
        success_message=self.success_message,
        is_active=False,  # Start inactive for safety
        email_notification_enabled=self.email_notification_enabled,
        notification_emails=self.notification_emails,
        auto_reply_enabled=self.auto_reply_enabled,
        auto_reply_subject=self.auto_reply_subject,
        auto_reply_body=self.auto_reply_body,
        webhook_enabled=self.webhook_enabled,
        webhook_url=self.webhook_url,
    )
    
    # Ensure unique slug
    counter = 1
    original_slug = cloned.slug
    while FormDefinition.objects.filter(slug=cloned.slug, site=self.site).exists():
        cloned.slug = f"{original_slug}-{counter}"
        counter += 1
    
    cloned.save()
    return cloned
```

Add admin action in Wagtail hooks:
```python
# File: core/sum_core/forms/wagtail_hooks.py
from wagtail import hooks
from wagtail.snippets.views.snippets import SnippetViewSet
from django.urls import reverse
from django.shortcuts import redirect

@hooks.register('register_snippet_viewset')
class FormDefinitionViewSet(SnippetViewSet):
    model = FormDefinition
    
    # Add clone action
    def clone_view(self, request, pk):
        form_def = self.get_object()
        cloned = form_def.clone()
        messages.success(request, f"Form '{form_def.name}' cloned successfully.")
        return redirect(reverse('wagtailsnippets:edit', args=[
            'forms', 'formdefinition', cloned.pk
        ]))
```

### Feature 2: Active Toggle Behavior

**Location:** `core/sum_core/blocks/forms.py`

Update DynamicFormBlock to filter inactive forms:
```python
class DynamicFormBlock(blocks.StructBlock):
    form_definition = SnippetChooserBlock(
        'forms.FormDefinition',
        required=True,
        help_text="Select the form to display"
    )
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        
        # Warn if form is inactive
        if value.get('form_definition') and not value['form_definition'].is_active:
            context['form_inactive_warning'] = True
        
        return context
```

Update template to show warning:
```django
{# In dynamic_form_block.html #}
{% if form_inactive_warning %}
<div class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4" role="alert">
    <p class="font-bold">Warning</p>
    <p>This form is currently inactive and won't accept submissions.</p>
</div>
{% endif %}
```

Filter snippet chooser to show only active forms (optional):
```python
# In SnippetChooserBlock or custom chooser
def get_queryset(self):
    return FormDefinition.objects.filter(is_active=True)
```

### Feature 3: Multiple Forms on Same Page

**Location:** `themes/theme_a/templates/sum_core/blocks/dynamic_form_block.html`

Ensure unique form IDs:
```django
{# Generate unique ID based on form definition ID and block position #}
{% with form_id="form-"|add:self.form_definition.id|add:"-"|add:forloop.counter0 %}
<form id="{{ form_id }}" method="post" action="/forms/submit/">
    {# ... form fields ... #}
</form>
{% endwith %}
```

Update JavaScript to handle multiple forms:
```javascript
// In dynamic_forms.js
document.querySelectorAll('.dynamic-form-wrapper form').forEach((form) => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        // Handle submission for this specific form
        submitForm(this);
    });
});

function submitForm(formElement) {
    const formId = formElement.id;
    // AJAX submission logic specific to this form
    // ...
}
```

### Feature 4: Form Versioning (Optional - P3)

**Location:** `core/sum_core/forms/models.py`

Add read-only archived state:
```python
class FormDefinition(models.Model):
    # ... existing fields ...
    
    is_archived = models.BooleanField(
        default=False,
        help_text="Archived forms are read-only and hidden from choosers"
    )
    
    def archive(self):
        """Archive this form (soft delete with audit trail)."""
        self.is_active = False
        self.is_archived = True
        self.save()
```

## Implementation Tasks

- [ ] Add `clone()` method to FormDefinition model
- [ ] Create Wagtail admin action for cloning forms
- [ ] Add slug uniqueness handling in clone method
- [ ] Update DynamicFormBlock to show warning for inactive forms
- [ ] Optionally filter snippet chooser to active forms only
- [ ] Update form template to generate unique IDs
- [ ] Update JavaScript to handle multiple form submissions
- [ ] Test multiple forms on same page (rendering and submission)
- [ ] Add archived state (optional, P3 priority)
- [ ] Create Wagtail hook for clone action button
- [ ] Write unit tests in `tests/forms/test_form_management.py`:
  - Clone form successfully
  - Cloned form has unique slug
  - Cloned form starts inactive
  - Active toggle filters forms
  - Multiple forms render unique IDs
  - Multiple forms submit independently

## Acceptance Criteria

- [ ] Can clone FormDefinition from admin
- [ ] Cloned forms have unique slugs (auto-incremented)
- [ ] Cloned forms start as inactive
- [ ] Inactive forms show warning when embedded
- [ ] Multiple forms on same page render correctly
- [ ] Multiple forms submit independently
- [ ] Form IDs unique (no collisions)
- [ ] JavaScript handles multiple forms without conflicts
- [ ] Optional: Archived forms hidden from choosers
- [ ] Unit tests pass with ≥80% coverage
- [ ] `make lint` passes

## Testing Commands

```bash
# Run unit tests
pytest tests/forms/test_form_management.py -v

# Check coverage
pytest tests/forms/test_form_management.py --cov=core/sum_core/forms --cov-report=term-missing

# Manual testing:
python core/sum_core/test_project/manage.py runserver

# Test clone:
# 1. Create FormDefinition
# 2. Click "Clone" action in admin
# 3. Verify new form created with unique slug
# 4. Verify clone is inactive

# Test multiple forms:
# 1. Create 2+ FormDefinitions
# 2. Add multiple DynamicFormBlocks to a page
# 3. Verify unique form IDs in HTML
# 4. Submit each form independently
# 5. Verify correct form data saved

# Test active toggle:
# 1. Deactivate a FormDefinition
# 2. View page with embedded form
# 3. Verify warning shows
# 4. Test submission fails gracefully

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(forms): add form management features

- Implement clone/duplicate FormDefinition
- Add unique slug generation for clones
- Show warning for inactive embedded forms
- Support multiple forms on same page with unique IDs
- Update JavaScript to handle multiple form submissions
- Add optional archived state for versioning
- Comprehensive unit tests

Refs: BLOG.012"

git push origin feature/BLOG-012-form-management

gh pr create \
  --base develop \
  --title "feat(forms): Form management features" \
  --body "Implements BLOG.012 - Advanced form management.

## Changes
- Clone/duplicate FormDefinition with unique slug
- Active toggle with embedded form warnings
- Multiple forms per page support
- Unique form ID generation
- JavaScript handling for multiple forms
- Optional archived state
- Comprehensive unit tests

## Testing
- ✅ Clone works with unique slugs
- ✅ Inactive warning displays
- ✅ Multiple forms render correctly
- ✅ Multiple forms submit independently
- ✅ No ID collisions
- ✅ Tests pass
- ✅ Lint checks pass

## Related
- Depends on: BLOG.001
- Enhances form management UX"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Test thoroughly with multiple forms scenario
```

## Notes for AI Agents

- Clone feature is critical for form iteration and testing
- Ensure slug uniqueness across site (not just globally)
- Cloned forms should start inactive to prevent accidental use
- Multiple forms must have truly unique IDs (use form_def.id + block index)
- JavaScript event listeners should be per-form, not global
- Consider adding "usage report" showing which pages use each form (future enhancement)
- Archived state is P3 priority - implement if time allows
- Test edge case: cloning an already-cloned form (double copy)
