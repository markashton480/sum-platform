# BLOG.001: FormDefinition Model & Admin Setup

**Phase:** 1 - Dynamic Forms Foundation  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 7.5h  
**Dependencies:** None

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-001-formdefinition-model
```

## Objective

Create the `FormDefinition` Wagtail Snippet model that serves as the foundation for the dynamic forms system. This model allows content editors to define reusable forms that can be embedded anywhere via `DynamicFormBlock`.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:86-123`
- Wagtail Snippets Documentation: https://docs.wagtail.org/en/stable/topics/snippets.html
- Existing Forms: `core/sum_core/forms/models.py`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **File:** `core/sum_core/forms/models.py`

### Model Fields

Create `FormDefinition` model with:
- `site` (ForeignKey to wagtailcore.Site) - multi-site support
- `name` (CharField, max_length=255) - admin reference name
- `slug` (SlugField, max_length=100, unique per site) - unique identifier
- `fields` (StreamField) - form field definitions (will be populated in BLOG.002)
- `success_message` (TextField, default="Thank you for your submission!")
- `is_active` (BooleanField, default=True) - soft delete support
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

### Submission Settings (Embedded in FormDefinition)

Add notification/webhook settings:
- `email_notification_enabled` (BooleanField, default=True)
- `notification_emails` (TextField, blank=True) - comma-separated
- `auto_reply_enabled` (BooleanField, default=False)
- `auto_reply_subject` (CharField, max_length=255, blank=True)
- `auto_reply_body` (TextField, blank=True)
- `webhook_enabled` (BooleanField, default=False)
- `webhook_url` (URLField, blank=True)

### Admin Configuration

Register snippet with:
- List display: name, slug, is_active, created_at
- List filters: is_active, site
- Search fields: name, slug
- Fieldset panels organized into sections:
  - **Basic Settings:** name, slug
  - **Form Fields:** fields (StreamField - will show "Coming soon" placeholder until BLOG.002)
  - **Submission Settings:** success_message
  - **Notifications:** email settings
  - **Webhooks:** webhook settings
  - **Status:** is_active

## Implementation Tasks

- [ ] Import required Wagtail/Django modules
- [ ] Create `FormDefinition` model class decorated with `@register_snippet`
- [ ] Add all model fields with appropriate validators and help text
- [ ] Implement `__str__()` method returning name
- [ ] Add Meta class with `unique_together = [('site', 'slug')]`
- [ ] Configure `panels` for Wagtail admin with MultiFieldPanel grouping
- [ ] Create migration: `python manage.py makemigrations sum_core`
- [ ] Write unit tests in `tests/forms/test_form_definition.py`:
  - Model creation and validation
  - Unique slug per site constraint
  - Active/inactive toggle
  - Email validation for notification_emails
  - Webhook URL validation

## Acceptance Criteria

- [ ] `FormDefinition` model exists and can be created via Django ORM
- [ ] Model appears in Wagtail admin under "Snippets"
- [ ] Slug uniqueness enforced per site
- [ ] Migration runs cleanly on fresh database
- [ ] All unit tests pass with ≥80% coverage
- [ ] `make lint` passes (ruff, mypy, black, isort)
- [ ] No breaking changes to existing form functionality

## Testing Commands

```bash
# Run unit tests
pytest tests/forms/test_form_definition.py -v

# Check coverage
pytest tests/forms/test_form_definition.py --cov=core/sum_core/forms/models --cov-report=term-missing

# Run linting
make lint

# Test migration
python core/sum_core/test_project/manage.py migrate --check
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(forms): add FormDefinition model and admin setup

- Create FormDefinition Wagtail Snippet
- Add site-scoped form configuration
- Include notification/webhook settings
- Register in admin with filtering
- Add migration and unit tests

Refs: BLOG.001"

git push origin feature/BLOG-001-formdefinition-model

# Create PR
gh pr create \
  --base develop \
  --title "feat(forms): FormDefinition model and admin setup" \
  --body "Implements BLOG.001 - Foundation model for dynamic forms system.

## Changes
- FormDefinition Wagtail Snippet with site scoping
- Email notification and webhook configuration fields
- Admin registration with search and filtering
- Unit tests and migration

## Testing
- ✅ Unit tests pass
- ✅ Migration runs cleanly
- ✅ Lint checks pass

## Related
- Part of Blog v1 + Dynamic Forms v1 implementation
- Blocks on: BLOG.002 (Field Type Blocks)"
```

**Monitor CI checks:**
```bash
# Watch PR status
gh pr status

# View checks
gh pr checks

# If checks fail, view logs and fix issues
gh pr checks --watch
```

**Resolve review comments:**
- Address all review feedback
- Push fixes to same branch
- Respond to comments on GitHub
- Request re-review when ready
- Ensure all conversations resolved before merge

## Notes for AI Agents

- This is a **critical path** task - blocks BLOG.002 and BLOG.003
- Do NOT modify existing Lead model - all form data goes in existing JSONField
- StreamField blocks will be defined in BLOG.002 - use placeholder for now
- Follow existing SUM Platform patterns in `core/sum_core/` codebase
- Reference existing snippet implementations for guidance
