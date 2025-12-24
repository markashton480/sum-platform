# BLOG.007: Form Submission Handler Enhancement

**Phase:** 2 - Forms Rendering + Submission  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 11h  
**Dependencies:** BLOG.004, BLOG.006

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-007-submission-handler
```

## Objective

Extend the existing form submission handler at `POST /forms/submit/` to process dynamic forms, validate against FormDefinition, store submissions in the Lead model, and trigger spam protection checks.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:254-274`
- Existing Submission Handler: `core/sum_core/forms/views.py`
- Lead Model: `core/sum_core/leads/models.py`
- Rate Limiting: `docs/dev/RATE-LIMIT.md`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **File:** `core/sum_core/forms/views.py` (enhance existing)

### Submission Handler Logic

Extend existing `submit_form` view to handle both static and dynamic forms:

```python
def submit_form(request):
    """
    Handle form submissions for both static and dynamic forms.
    
    Dynamic forms are identified by 'form_definition_id' in POST data.
    Static forms continue to work as before (backwards compatible).
    """
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Check if this is a dynamic form submission
    form_def_id = request.POST.get('form_definition_id')
    
    if form_def_id:
        return _handle_dynamic_form_submission(request, form_def_id)
    else:
        return _handle_static_form_submission(request)  # Existing logic


def _handle_dynamic_form_submission(request, form_def_id):
    """Process dynamic form submission."""
    
    # 1. Load FormDefinition
    # 2. Validate spam protection (honeypot, timing, rate limit)
    # 3. Generate Django form class
    # 4. Validate form data
    # 5. Save to Lead model
    # 6. Trigger async tasks (notifications, webhooks)
    # 7. Return response
    pass
```

### Spam Protection Integration

Implement checks (reuse existing infrastructure where possible):

1. **Honeypot Field Check**
   - Field name: `website` (common bot target)
   - Should be empty (bots fill it)
   - Fail silently if filled (don't reveal it's a honeypot)

2. **Timing Validation**
   - Field name: `form_timestamp`
   - Minimum time between page load and submission (e.g., 3 seconds)
   - Too fast = likely bot

3. **Rate Limiting**
   - Reuse existing per-IP rate limiting (see `docs/dev/RATE-LIMIT.md`)
   - Apply to dynamic form submissions
   - Return 429 if exceeded

### Lead Model Integration

Store in existing Lead model (**no schema changes**):

```python
from sum_core.leads.models import Lead

lead = Lead.objects.create(
    form_type=form_definition.slug,  # Existing field
    form_data=cleaned_data,  # Existing JSONField
    
    # Preserve existing attribution fields
    source_url=request.META.get('HTTP_REFERER', ''),
    landing_page=request.path,
    utm_source=request.GET.get('utm_source', ''),
    utm_medium=request.GET.get('utm_medium', ''),
    utm_campaign=request.GET.get('utm_campaign', ''),
    ip_address=get_client_ip(request),
)
```

### Response Handling

Return JSON response:
```json
{
  "success": true,
  "message": "Thank you for your submission!",
  "redirect_url": "/thank-you/"  // Optional, from DynamicFormBlock
}
```

Or error response:
```json
{
  "success": false,
  "errors": {
    "email": ["Enter a valid email address."],
    "phone": ["This field is required."]
  }
}
```

## Implementation Tasks

- [ ] Review existing `submit_form` view in `core/sum_core/forms/views.py`
- [ ] Add dynamic form detection logic (check for `form_definition_id`)
- [ ] Implement `_handle_dynamic_form_submission()`:
  - Load FormDefinition by ID
  - Check if form is active
  - Generate form class using DynamicFormGenerator
  - Instantiate with POST data
  - Validate form
- [ ] Implement spam protection checks:
  - Honeypot field validation
  - Timing validation (min 3 seconds)
  - Rate limiting (reuse existing)
- [ ] Integrate with Lead model (no schema changes)
- [ ] Trigger async tasks (will be implemented in BLOG.008)
- [ ] Return appropriate JSON responses
- [ ] Handle file uploads (save to media, store reference in form_data)
- [ ] Write comprehensive integration tests in `tests/forms/test_form_submission.py`:
  - Successful dynamic form submission
  - Form validation errors
  - Honeypot detection
  - Timing validation
  - Rate limiting
  - Lead created with correct data
  - Attribution fields preserved
  - File upload handling
  - Inactive form rejection

## Acceptance Criteria

- [ ] Dynamic forms submit successfully
- [ ] Form validation works (required fields, email format, etc.)
- [ ] Spam protection catches bots (honeypot, timing)
- [ ] Rate limiting prevents abuse
- [ ] Leads created with form_type = FormDefinition.slug
- [ ] Attribution data preserved (UTM, referrer, IP)
- [ ] File uploads handled correctly
- [ ] Inactive forms rejected with error
- [ ] JSON responses correct format
- [ ] Backwards compatible with static forms
- [ ] Integration tests pass with ≥80% coverage
- [ ] `make lint` passes

## Testing Commands

```bash
# Run integration tests
pytest tests/forms/test_form_submission.py -v

# Check coverage
pytest tests/forms/test_form_submission.py --cov=core/sum_core/forms/views --cov-report=term-missing

# Manual testing with curl
curl -X POST http://localhost:8000/forms/submit/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "form_definition_id=1&email=test@example.com&name=Test&website=&form_timestamp=$(date +%s)"

# Test in browser
# 1. Create FormDefinition
# 2. Add DynamicFormBlock to page
# 3. Fill and submit form
# 4. Verify Lead created in admin

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(forms): enhance submission handler for dynamic forms

- Extend POST /forms/submit/ to handle dynamic forms
- Add FormDefinition loading and validation
- Integrate DynamicFormGenerator for runtime validation
- Implement honeypot and timing spam protection
- Store submissions in Lead model (no schema changes)
- Preserve attribution data (UTM, referrer, IP)
- Handle file uploads
- Add comprehensive integration tests
- Maintain backwards compatibility with static forms

Refs: BLOG.007"

git push origin feature/BLOG-007-submission-handler

gh pr create \
  --base develop \
  --title "feat(forms): Submission handler for dynamic forms" \
  --body "Implements BLOG.007 - Process dynamic form submissions.

## Changes
- Extended submission handler to support dynamic forms
- FormDefinition loading and active status check
- Runtime form generation and validation
- Spam protection: honeypot, timing, rate limiting
- Lead model integration (existing schema)
- Attribution preservation
- File upload handling
- Comprehensive integration tests

## Testing
- ✅ Dynamic form submissions work
- ✅ Validation enforced
- ✅ Spam protection active
- ✅ Leads created correctly
- ✅ File uploads handled
- ✅ Static forms still work (backwards compatible)
- ✅ Lint checks pass

## Related
- Depends on: BLOG.004, BLOG.006
- Enables: BLOG.008 (notifications/webhooks)
- Critical path task"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Address all feedback, test thoroughly
```

## Notes for AI Agents

- **Critical path** task - completes the core form submission flow
- Do NOT modify Lead model schema - use existing fields
- Reuse existing rate limiting infrastructure from `docs/dev/RATE-LIMIT.md`
- Honeypot field should fail silently (don't reveal to bots)
- Timing validation prevents automated submissions
- File uploads should integrate with existing media handling
- Ensure backwards compatibility - static forms must continue working
- Test with various FormDefinition configurations
- Consider edge cases: missing fields, invalid FormDefinition ID, inactive forms
