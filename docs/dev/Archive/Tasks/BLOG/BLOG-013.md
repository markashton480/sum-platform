# BLOG.013: Admin UI Enhancements

**Phase:** 4 - Integration + Polish  
**Priority:** P2  
**Estimated Hours:** 7h  
**Dependencies:** BLOG.001, BLOG.010

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-013-admin-enhancements
```

## Objective

Polish the Wagtail admin experience for FormDefinition and Blog pages: add preview buttons, usage reports, submission counts, reading time display, and improved list filtering.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:485-501`
- Wagtail Admin Customization: https://docs.wagtail.org/en/stable/extending/admin_views.html
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Enhancement 1: FormDefinition Admin

**Location:** `core/sum_core/forms/models.py` and `core/sum_core/forms/wagtail_hooks.py`

#### Preview Button
Add custom action to preview form in modal:
```python
# In wagtail_hooks.py
from wagtail.admin.panels import FieldPanel
from django.urls import path, reverse

class FormDefinitionViewSet(SnippetViewSet):
    # Add preview action
    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        return urls + [
            path('<int:pk>/preview/', self.preview_view, name='preview'),
        ]
    
    def preview_view(self, request, pk):
        form_def = self.get_object()
        # Render form in admin modal
        return render(request, 'sum_core/admin/form_preview.html', {
            'form_definition': form_def,
        })
```

#### Usage Report
Add method to find pages using this form:
```python
class FormDefinition(models.Model):
    # ... existing fields ...
    
    def get_usage_pages(self):
        """Find all pages that embed this form."""
        from wagtail.models import Page
        pages = []
        
        # Search StreamFields for DynamicFormBlock references
        for page_model in [StandardPage, ServicePage, BlogPostPage]:
            for page in page_model.objects.all():
                if hasattr(page, 'body'):
                    for block in page.body:
                        if block.block_type == 'dynamic_form' and block.value.get('form_definition') == self:
                            pages.append(page)
                            break
        
        return pages
    
    @property
    def usage_count(self):
        """Number of pages using this form."""
        return len(self.get_usage_pages())
```

#### Submission Count
Add property for submission count:
```python
class FormDefinition(models.Model):
    # ... existing fields ...
    
    @property
    def submission_count(self):
        """Count of submissions for this form."""
        from sum_core.leads.models import Lead
        return Lead.objects.filter(form_type=self.slug).count()
```

Update admin list display:
```python
class FormDefinitionAdmin(ModelAdmin):
    model = FormDefinition
    list_display = ['name', 'slug', 'is_active', 'submission_count', 'usage_count', 'created_at']
    list_filter = ['is_active', 'site', 'created_at']
    search_fields = ['name', 'slug']
```

### Enhancement 2: Blog Admin

**Location:** `core/sum_core/pages/blog.py`

#### Category Filtering
Add to BlogPostPage admin:
```python
# In Wagtail admin, add to modeladmin if using
class BlogPostPageAdmin:
    list_filter = ['category', 'published_date', 'live']
    list_display = ['title', 'category', 'published_date', 'reading_time', 'live']
```

#### Reading Time Display
Add to admin panels (read-only):
```python
class BlogPostPage(Page):
    # ... existing fields ...
    
    content_panels = Page.content_panels + [
        # ... other panels ...
        FieldPanel('reading_time', read_only=True),  # Show in admin
    ]
```

#### Featured Image Preview
Use custom panel or thumbnail in list:
```python
from wagtail.admin.panels import FieldPanel

class BlogPostPage(Page):
    # ... existing fields ...
    
    content_panels = Page.content_panels + [
        FieldPanel('featured_image', widget=AdminImageChooser),  # Shows preview
        # ... other panels ...
    ]
```

### Enhancement 3: Lead Admin

**Location:** `core/sum_core/leads/admin.py`

Add FormDefinition filtering:
```python
class LeadAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'form_type', 'email', 'source_url']
    list_filter = ['form_type', 'created_at']
    search_fields = ['form_data']  # JSON field search
    
    def email(self, obj):
        """Extract email from form_data for display."""
        return obj.form_data.get('email', 'N/A')
```

Add form-specific field display:
```python
# In lead detail view template
<h3>Form Data</h3>
<dl>
    {% for key, value in lead.form_data.items %}
    <dt><strong>{{ key|title }}</strong></dt>
    <dd>{{ value }}</dd>
    {% endfor %}
</dl>
```

### Enhancement 4: Form Preview Template

**Location:** `themes/theme_a/templates/sum_core/admin/form_preview.html`

```django
{% extends "wagtailadmin/base.html" %}
{% load wagtailcore_tags %}

{% block content %}
<div class="nice-padding">
    <h1>Preview: {{ form_definition.name }}</h1>
    
    <div class="help-block">
        <p>This is a preview of how the form will appear to users.</p>
    </div>
    
    <div class="form-preview" style="max-width: 600px; margin: 2rem 0; padding: 2rem; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;">
        {# Render the form using DynamicFormGenerator #}
        {% with form=form_definition|generate_dynamic_form %}
            {{ form.as_p }}
        {% endwith %}
    </div>
    
    <a href="{% url 'wagtailsnippets:edit' 'forms' 'formdefinition' form_definition.pk %}" class="button">
        Back to Edit
    </a>
</div>
{% endblock %}
```

## Implementation Tasks

- [ ] Add `get_usage_pages()` method to FormDefinition
- [ ] Add `usage_count` property to FormDefinition
- [ ] Add `submission_count` property to FormDefinition
- [ ] Update FormDefinition admin list display
- [ ] Create preview view and URL route
- [ ] Create form_preview.html template
- [ ] Add preview button to FormDefinition admin
- [ ] Update BlogPostPage admin with category filter
- [ ] Make reading_time read-only in BlogPostPage admin
- [ ] Enhance featured image display in admin
- [ ] Update Lead admin with form_type filtering
- [ ] Add email extraction to Lead admin list
- [ ] Create form-specific display in Lead detail view
- [ ] Write tests for admin enhancements (if applicable)

## Acceptance Criteria

- [ ] FormDefinition admin shows submission count
- [ ] FormDefinition admin shows usage count
- [ ] Preview button renders form in modal
- [ ] Usage report shows which pages use form
- [ ] BlogPostPage admin filterable by category
- [ ] Reading time displays (read-only) in admin
- [ ] Featured image preview shows in admin
- [ ] Lead admin filterable by form_type
- [ ] Lead detail shows formatted form data
- [ ] All admin enhancements work smoothly
- [ ] `make lint` passes

## Testing Commands

```bash
# Manual testing required (admin UI)
python core/sum_core/test_project/manage.py runserver

# Test FormDefinition admin:
# 1. Create FormDefinition
# 2. Submit test form
# 3. Embed in pages
# 4. Check admin list shows counts
# 5. Click preview button
# 6. View usage report

# Test Blog admin:
# 1. Create BlogPostPages
# 2. Filter by category
# 3. Check reading time displays
# 4. Upload featured image, check preview

# Test Lead admin:
# 1. Submit dynamic forms
# 2. Filter by form_type
# 3. View lead detail
# 4. Verify form data displays properly

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(admin): enhance Wagtail admin for forms and blog

- Add FormDefinition preview button and modal
- Show submission and usage counts in FormDefinition list
- Add usage report to find pages using forms
- Enhance BlogPostPage admin with category filtering
- Display reading time (read-only) in admin
- Improve featured image preview
- Add form_type filtering to Lead admin
- Enhanced form data display in Lead detail
- Admin UX improvements

Refs: BLOG.013"

git push origin feature/BLOG-013-admin-enhancements

gh pr create \
  --base develop \
  --title "feat(admin): Admin UI enhancements for forms and blog" \
  --body "Implements BLOG.013 - Polish admin experience.

## Changes
- FormDefinition preview in modal
- Submission and usage counts
- Usage report (pages using form)
- Blog category filtering
- Reading time display
- Lead admin improvements
- Form data visualization

## Testing
- ✅ Preview button works
- ✅ Counts display correctly
- ✅ Usage report accurate
- ✅ Blog filtering works
- ✅ Lead admin enhanced
- ✅ All admin features functional

## Related
- Depends on: BLOG.001, BLOG.010
- Enhances content editor UX"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Test all admin features thoroughly
```

## Notes for AI Agents

- Admin enhancements are P2 priority - nice to have, not critical path
- Preview modal should be simple - full rendering happens on frontend
- Usage report helps content editors understand form dependencies
- Submission count aids in form performance analysis
- Consider caching usage_count if performance becomes an issue
- Lead admin email extraction makes list view more useful
- Form data display should handle all field types gracefully
- These enhancements significantly improve editor experience
