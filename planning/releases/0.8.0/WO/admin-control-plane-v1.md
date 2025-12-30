# Work Order: Admin Control Plane v1

> **Parent:** [VD v0.8.0](../VD.md)
> **Branch:** `feature/admin-control-plane`
> **Priority:** P0

---

## Overview

### Goal

Add feature toggles and granular site settings for admin control over platform capabilities. This allows operators to enable/disable major features per site and fine-tune typography and spacing without code changes.

### Context

Currently, all SUM features are always enabled. Operators cannot disable features they don't need (e.g., blog for a simple landing page site). Additionally, typography and spacing are theme-controlled with no admin-level override. This work order introduces a control plane for feature management and design fine-tuning.

---

## Acceptance Criteria

### Must Have

- [ ] Feature toggle fields added to SiteSettings
- [ ] Blog feature can be enabled/disabled
- [ ] Leads feature can be enabled/disabled
- [ ] Jobs feature toggle (placeholder for future use)
- [ ] Disabled features hidden from navigation
- [ ] Disabled features return 404 on direct access
- [ ] Settings persist and apply site-wide

### Should Have

- [ ] Typography weight controls (light, normal, bold)
- [ ] Typography spacing controls (tight, normal, loose)
- [ ] Controls apply to rendered output
- [ ] Preview of typography changes
- [ ] Feature status displayed in admin header

### Could Have

- [ ] Per-page feature overrides
- [ ] Scheduled feature activation
- [ ] Feature usage analytics

---

## Technical Approach

### SiteSettings Extension

Add feature toggles to the existing SiteSettings model:

```python
# sum_core/settings/models.py

class SiteSettings(BaseSetting):
    # Existing fields...

    # Feature Toggles
    enable_blog = models.BooleanField(
        default=True,
        help_text="Enable blog functionality (index, posts, search)"
    )
    enable_leads = models.BooleanField(
        default=True,
        help_text="Enable lead capture forms and management"
    )
    enable_jobs = models.BooleanField(
        default=False,
        help_text="Enable job listings (future feature)"
    )

    # Typography Controls
    heading_weight = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light (300)'),
            ('normal', 'Normal (400)'),
            ('medium', 'Medium (500)'),
            ('semibold', 'Semi-Bold (600)'),
            ('bold', 'Bold (700)'),
        ],
        default='bold',
    )
    body_weight = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light (300)'),
            ('normal', 'Normal (400)'),
            ('medium', 'Medium (500)'),
        ],
        default='normal',
    )
    line_height = models.CharField(
        max_length=20,
        choices=[
            ('tight', 'Tight (1.25)'),
            ('normal', 'Normal (1.5)'),
            ('relaxed', 'Relaxed (1.75)'),
            ('loose', 'Loose (2.0)'),
        ],
        default='normal',
    )
    letter_spacing = models.CharField(
        max_length=20,
        choices=[
            ('tight', 'Tight (-0.025em)'),
            ('normal', 'Normal (0)'),
            ('wide', 'Wide (0.025em)'),
        ],
        default='normal',
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('enable_blog'),
            FieldPanel('enable_leads'),
            FieldPanel('enable_jobs'),
        ], heading="Feature Toggles"),
        MultiFieldPanel([
            FieldPanel('heading_weight'),
            FieldPanel('body_weight'),
            FieldPanel('line_height'),
            FieldPanel('letter_spacing'),
        ], heading="Typography Controls"),
        # Existing panels...
    ]
```

### Feature Toggle Context Processor

```python
# sum_core/context_processors.py

def feature_toggles(request):
    from .settings.models import SiteSettings
    site = getattr(request, 'site', None)
    if site:
        settings = SiteSettings.for_site(site)
        return {
            'features': {
                'blog': settings.enable_blog,
                'leads': settings.enable_leads,
                'jobs': settings.enable_jobs,
            }
        }
    return {'features': {}}
```

### Navigation Filtering

Update navigation templates to respect feature toggles:

```html
{% if features.blog %}
<a href="/blog/">Blog</a>
{% endif %}
```

### URL Protection

Create decorator for feature-gated views:

```python
# sum_core/decorators.py

from functools import wraps
from django.http import Http404

def requires_feature(feature_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            settings = SiteSettings.for_request(request)
            if not getattr(settings, f'enable_{feature_name}', False):
                raise Http404(f"{feature_name} feature is disabled")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Typography CSS Variables

Generate CSS variables from settings:

```python
# sum_core/templatetags/typography_tags.py

@register.simple_tag(takes_context=True)
def typography_css_vars(context):
    settings = context.get('site_settings')
    if not settings:
        return ''

    weight_map = {
        'light': '300', 'normal': '400', 'medium': '500',
        'semibold': '600', 'bold': '700',
    }
    line_height_map = {
        'tight': '1.25', 'normal': '1.5', 'relaxed': '1.75', 'loose': '2.0',
    }
    letter_spacing_map = {
        'tight': '-0.025em', 'normal': '0', 'wide': '0.025em',
    }

    return format_html(
        '<style>:root {{ '
        '--heading-weight: {}; '
        '--body-weight: {}; '
        '--line-height: {}; '
        '--letter-spacing: {}; '
        '}}</style>',
        weight_map.get(settings.heading_weight, '700'),
        weight_map.get(settings.body_weight, '400'),
        line_height_map.get(settings.line_height, '1.5'),
        letter_spacing_map.get(settings.letter_spacing, '0'),
    )
```

---

## File Changes

### New Files

| File | Purpose |
| ---- | ------- |
| `sum_core/decorators.py` | Feature gate decorator |
| `sum_core/templatetags/typography_tags.py` | Typography CSS generation |
| `tests/settings/test_feature_toggles.py` | Toggle tests |
| `tests/settings/test_typography.py` | Typography tests |

### Modified Files

| File | Changes |
| ---- | ------- |
| `sum_core/settings/models.py` | Add toggle and typography fields |
| `sum_core/context_processors.py` | Add feature toggles context |
| `themes/*/templates/base.html` | Include typography CSS vars |
| `themes/*/templates/includes/navigation.html` | Respect feature toggles |
| `sum_core/pages/blog_index_page.py` | Add feature check |
| `sum_core/leads/views.py` | Add feature check |

---

## Tasks

### TASK-001: Add Feature Toggle Fields to SiteSettings

**Estimate:** 2-3 hours
**Risk:** Low

Add boolean fields for feature toggles to SiteSettings model.

**Acceptance Criteria:**
- [ ] enable_blog field added (default True)
- [ ] enable_leads field added (default True)
- [ ] enable_jobs field added (default False)
- [ ] Fields appear in Wagtail admin
- [ ] Migration created and tested
- [ ] Help text explains each toggle

**Technical Notes:**
- Use MultiFieldPanel for grouping
- Consider admin panel organization

**Branch:** `feature/admin-control-plane/001-toggle-fields`

---

### TASK-002: Implement Blog Feature Toggle

**Estimate:** 2-3 hours
**Risk:** Medium

Make blog functionality respect the enable_blog toggle.

**Acceptance Criteria:**
- [ ] Blog hidden from navigation when disabled
- [ ] Blog index page returns 404 when disabled
- [ ] Blog post pages return 404 when disabled
- [ ] Blog search returns 404 when disabled
- [ ] Admin can still access blog pages in Wagtail

**Technical Notes:**
- Use feature gate decorator on views
- Update navigation templates
- Consider robots.txt implications

**Branch:** `feature/admin-control-plane/002-blog-toggle`

---

### TASK-003: Implement Leads Feature Toggle

**Estimate:** 2-3 hours
**Risk:** Medium

Make lead capture respect the enable_leads toggle.

**Acceptance Criteria:**
- [ ] Lead forms hidden when disabled
- [ ] Form submission returns 404 when disabled
- [ ] Dynamic forms don't render when disabled
- [ ] Lead admin still accessible in Wagtail
- [ ] Existing leads preserved when disabled

**Technical Notes:**
- Gate form rendering in templates
- Gate submission endpoint
- Don't delete data when disabled

**Branch:** `feature/admin-control-plane/003-leads-toggle`

---

### TASK-004: Implement Jobs Feature Toggle (Placeholder)

**Estimate:** 1-2 hours
**Risk:** Low

Add jobs feature toggle as placeholder for future functionality.

**Acceptance Criteria:**
- [ ] enable_jobs field in SiteSettings
- [ ] Toggle appears in admin
- [ ] Default is False (disabled)
- [ ] Context processor includes jobs status
- [ ] No functional implementation needed yet

**Technical Notes:**
- This is a forward-looking placeholder
- Document that jobs feature is coming

**Branch:** `feature/admin-control-plane/004-jobs-toggle`

---

### TASK-005: Add Typography Controls

**Estimate:** 2-3 hours
**Risk:** Medium

Add typography control fields to SiteSettings.

**Acceptance Criteria:**
- [ ] Heading weight control (light to bold)
- [ ] Body weight control (light to medium)
- [ ] Line height control (tight to loose)
- [ ] Letter spacing control (tight to wide)
- [ ] Fields grouped in admin panel
- [ ] Sensible defaults set

**Technical Notes:**
- Use choice fields for controlled options
- Consider preview capability

**Branch:** `feature/admin-control-plane/005-typography-controls`

---

### TASK-006: Add Spacing Controls

**Estimate:** 2-3 hours
**Risk:** Medium

Implement CSS variable generation and theme integration for typography.

**Acceptance Criteria:**
- [ ] Template tag generates CSS variables
- [ ] Base template includes CSS variables
- [ ] Theme CSS uses CSS variables
- [ ] Changes apply site-wide
- [ ] Fallback values for missing settings

**Technical Notes:**
- Use inline style tag in head
- Ensure themes reference the variables
- Test on all themes

**Branch:** `feature/admin-control-plane/006-spacing-controls`

---

### TASK-007: Control Plane Tests

**Estimate:** 2-3 hours
**Risk:** Low

Write comprehensive tests for feature toggles and typography controls.

**Acceptance Criteria:**
- [ ] Test blog disabled hides navigation
- [ ] Test blog disabled returns 404
- [ ] Test leads disabled hides forms
- [ ] Test leads disabled rejects submissions
- [ ] Test typography CSS variable generation
- [ ] Test context processor

**Technical Notes:**
- Use Django test client
- Test both enabled and disabled states

**Branch:** `feature/admin-control-plane/007-tests`

---

## Execution Order

```
001 (Toggle Fields)
    |
    +---> 002 (Blog Toggle)
    |
    +---> 003 (Leads Toggle)
    |
    +---> 004 (Jobs Toggle)
    |
    v
005 (Typography Controls)
    |
    v
006 (Spacing Controls / CSS Integration)
    |
    v
007 (Tests)
```

### Parallelization

- TASK-002, TASK-003, and TASK-004 can proceed in parallel after TASK-001
- TASK-005 can start after TASK-001
- TASK-006 requires TASK-005
- TASK-007 after all feature tasks

---

## Testing Requirements

### Unit Tests

- Toggle field defaults
- Context processor output
- CSS variable generation
- Feature gate decorator

### Integration Tests

- Full page load with toggles
- Navigation respects toggles
- Form behavior with leads disabled
- Typography applies to rendered pages

---

## Definition of Done

- [ ] All 7 tasks completed and merged
- [ ] All acceptance criteria met
- [ ] Tests passing (`make test`)
- [ ] Linting passing (`make lint`)
- [ ] Feature toggles work in admin
- [ ] Typography controls apply to output
- [ ] Documentation updated
- [ ] PR merged to `release/0.8.0`

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Breaking existing sites | Low | High | Defaults match current behavior |
| Typography not applied consistently | Medium | Medium | Audit theme CSS for variable usage |
| Admin confusion about toggles | Low | Low | Clear help text and documentation |
| SEO impact of disabled features | Low | Medium | Document robots.txt considerations |

---

## Sign-Off

| Role | Name | Date | Approved |
| ---- | ---- | ---- | -------- |
| Author | Claude-on-WSL | 2025-12-30 | - |
| Tech Lead | | | Pending |

---

## Revision History

| Date | Author | Changes |
| ---- | ------ | ------- |
| 2025-12-30 | Claude-on-WSL | Initial WO created |
