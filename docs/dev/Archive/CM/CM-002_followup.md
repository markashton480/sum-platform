# Incident Report: LeadAnalyticsPanel AttributeError

**Date**: 2025-12-15
**Related Spec**: CM-002

## Incident Description

The Wagtail admin dashboard (`/admin/`) crashed with an HTTP 500 error after the deployment of the Lead Analytics panel.

**Error Signature**:

```text
AttributeError: 'LeadAnalyticsPanel' object has no attribute 'media'
Location: wagtail.admin.views.home.HomeView
```

## Root Cause

Wagtail's `HomeView` iterates over all registered dashboard panels and aggregates their media definitions (CSS/JS) using `media += panel.media`.

The `LeadAnalyticsPanel` class (defined in `core/sum_core/analytics/wagtail_hooks.py`) implemented the `render()` method but failed to define the `media` property. Unlike some Wagtail components, dashboard panels do not strictly enforce this at registration time, but fail at runtime when the dashboard is rendered.

## Resolution

The missing `media` property was added to `LeadAnalyticsPanel`. It returns an empty `django.forms.Media` instance, satisfying the interface contract.

```python
from django.forms import Media

class LeadAnalyticsPanel:
    # ...
    @property
    def media(self):
        return Media()
    # ...
```

## Verification

- **Static Analysis**: `mypy` and `ruff` checks passed.
- **Manual Verification**: Confirmed that `/admin/` loads successfully and the panel renders.

## Prevention (CM-002)

To prevent regression, a test case will be added (as defined in [CM-002](./CM-002.md)) to enforce that all registered homepage panels adhere to the required interface, specifically the presence of a `media` attribute.
