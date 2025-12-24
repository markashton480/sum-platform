# BLOG.008: Notifications and Webhooks

**Phase:** 2 - Forms Rendering + Submission  
**Priority:** P1  
**Estimated Hours:** 9h  
**Dependencies:** BLOG.007

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-008-notifications-webhooks
```

## Objective

Create Celery tasks for async email notifications and webhook delivery when dynamic forms are submitted. Integrate with existing notification infrastructure where possible.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:276-302`
- Celery Documentation: https://docs.celeryproject.org/
- Existing Integrations: `core/sum_core/integrations/`
- Email System: Check existing email sending in codebase
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **New File:** `core/sum_core/forms/tasks.py`

### Task 1: Admin Notification Email

```python
@shared_task(bind=True, max_retries=3)
def send_form_notification(self, lead_id, form_definition_id):
    """
    Send email notification to admin recipients when form submitted.
    
    Args:
        lead_id: ID of the created Lead instance
        form_definition_id: ID of the FormDefinition
    
    Retries: 3 attempts with exponential backoff
    """
    try:
        lead = Lead.objects.get(id=lead_id)
        form_def = FormDefinition.objects.get(id=form_definition_id)
        
        # Skip if notifications disabled
        if not form_def.email_notification_enabled:
            return
        
        # Parse recipient emails
        recipients = [
            email.strip() 
            for email in form_def.notification_emails.split(',')
            if email.strip()
        ]
        
        if not recipients:
            return
        
        # Render email templates
        subject = f"New {form_def.name} Submission"
        html_message = render_to_string(
            'sum_core/emails/form_notification.html',
            {'lead': lead, 'form_definition': form_def}
        )
        plain_message = render_to_string(
            'sum_core/emails/form_notification.txt',
            {'lead': lead, 'form_definition': form_def}
        )
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Task 2: Auto-Reply Email

```python
@shared_task(bind=True, max_retries=3)
def send_auto_reply(self, lead_id, form_definition_id):
    """
    Send auto-reply email to form submitter.
    
    Args:
        lead_id: ID of the created Lead instance
        form_definition_id: ID of the FormDefinition
    
    Retries: 3 attempts with exponential backoff
    """
    try:
        lead = Lead.objects.get(id=lead_id)
        form_def = FormDefinition.objects.get(id=form_definition_id)
        
        # Skip if auto-reply disabled
        if not form_def.auto_reply_enabled:
            return
        
        # Extract email from form_data
        submitter_email = lead.form_data.get('email')
        if not submitter_email:
            return
        
        # Use custom subject/body or defaults
        subject = form_def.auto_reply_subject or f"Thank you for contacting us"
        body = form_def.auto_reply_body or form_def.success_message
        
        # Simple interpolation (name only for security)
        name = lead.form_data.get('name', 'there')
        subject = subject.replace('{{name}}', name)
        body = body.replace('{{name}}', name)
        
        # Send email
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[submitter_email],
            fail_silently=False,
        )
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Task 3: Webhook Delivery

```python
@shared_task(bind=True, max_retries=3)
def send_webhook(self, lead_id, form_definition_id):
    """
    Send webhook with form submission data.
    
    Args:
        lead_id: ID of the created Lead instance
        form_definition_id: ID of the FormDefinition
    
    Retries: 3 attempts with exponential backoff
    """
    try:
        lead = Lead.objects.get(id=lead_id)
        form_def = FormDefinition.objects.get(id=form_definition_id)
        
        # Skip if webhook disabled
        if not form_def.webhook_enabled or not form_def.webhook_url:
            return
        
        # Build webhook payload
        payload = {
            'event': 'form.submitted',
            'timestamp': timezone.now().isoformat(),
            'form': {
                'id': form_def.id,
                'name': form_def.name,
                'slug': form_def.slug,
            },
            'submission': {
                'id': lead.id,
                'data': lead.form_data,
                'created_at': lead.created_at.isoformat(),
            },
            'attribution': {
                'source_url': lead.source_url,
                'landing_page': lead.landing_page,
                'utm_source': lead.utm_source,
                'utm_medium': lead.utm_medium,
                'utm_campaign': lead.utm_campaign,
            }
        }
        
        # Send webhook (timeout after 10 seconds)
        response = requests.post(
            form_def.webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10,
        )
        
        # Raise for 4xx/5xx status codes
        response.raise_for_status()
        
    except requests.RequestException as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Integration with Submission Handler

Update `BLOG.007` submission handler to trigger tasks:

```python
# In _handle_dynamic_form_submission after Lead is created:

from sum_core.forms.tasks import (
    send_form_notification,
    send_auto_reply,
    send_webhook,
)

# Trigger async tasks
send_form_notification.delay(lead.id, form_definition.id)
send_auto_reply.delay(lead.id, form_definition.id)
send_webhook.delay(lead.id, form_definition.id)
```

### Email Templates

Create email templates:
- `themes/theme_a/templates/sum_core/emails/form_notification.html` - Admin notification (HTML)
- `themes/theme_a/templates/sum_core/emails/form_notification.txt` - Admin notification (plain text)

## Implementation Tasks

- [ ] Create `core/sum_core/forms/tasks.py`
- [ ] Import Celery, Django mail, requests modules
- [ ] Implement `send_form_notification` task with retry logic
- [ ] Implement `send_auto_reply` task with retry logic
- [ ] Implement `send_webhook` task with retry logic
- [ ] Create email templates (HTML + plain text) for admin notifications
- [ ] Update BLOG.007 submission handler to trigger tasks
- [ ] Add task configuration to Celery settings (if needed)
- [ ] Write unit tests in `tests/forms/test_async_tasks.py`:
  - Each task executes successfully
  - Tasks respect enabled/disabled flags
  - Email content correct
  - Webhook payload structure
  - Retry logic on failures
  - Tasks skip when no recipients/URL configured
  - Use Celery eager mode for synchronous testing

## Acceptance Criteria

- [ ] Admin notification emails sent when form submitted
- [ ] Auto-reply emails sent to submitters
- [ ] Webhooks delivered to configured URLs
- [ ] Tasks respect enabled/disabled toggles in FormDefinition
- [ ] Retry logic works on transient failures
- [ ] Email templates render correctly (HTML + plain text)
- [ ] Webhook payload includes all required data
- [ ] Tasks fail gracefully if Lead/FormDefinition deleted
- [ ] Unit tests pass with ≥80% coverage (using Celery eager mode)
- [ ] `make lint` passes
- [ ] No emails/webhooks sent for disabled notifications

## Testing Commands

```bash
# Run unit tests (Celery eager mode)
pytest tests/forms/test_async_tasks.py -v

# Check coverage
pytest tests/forms/test_async_tasks.py --cov=core/sum_core/forms/tasks --cov-report=term-missing

# Test with real Celery (local dev)
# Start Celery worker
celery -A sum_core worker --loglevel=info

# Submit form in browser, check:
# - Email arrives
# - Webhook received (use webhook.site for testing)
# - Celery logs show task execution

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(forms): add notifications and webhooks for dynamic forms

- Implement Celery tasks for async processing
- Admin email notifications with HTML/plain text templates
- Auto-reply emails to submitters
- Webhook delivery with retry logic
- Exponential backoff for failed tasks
- Respect enabled/disabled toggles
- Comprehensive task tests using Celery eager mode
- Integration with submission handler

Refs: BLOG.008"

git push origin feature/BLOG-008-notifications-webhooks

gh pr create \
  --base develop \
  --title "feat(forms): Notifications and webhooks for dynamic forms" \
  --body "Implements BLOG.008 - Async notifications and webhooks.

## Changes
- Celery tasks for email notifications
- Admin notification emails (HTML + plain text)
- Auto-reply emails to submitters
- Webhook delivery with payload
- Retry logic with exponential backoff
- Email templates
- Integration with submission handler
- Comprehensive unit tests

## Testing
- ✅ Tasks execute correctly
- ✅ Emails sent and formatted properly
- ✅ Webhooks delivered
- ✅ Retry logic works
- ✅ Toggles respected
- ✅ Tests pass in eager mode
- ✅ Lint checks pass

## Related
- Depends on: BLOG.007
- Completes Phase 2 async processing"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Test with real emails/webhooks, address feedback
```

## Notes for AI Agents

- Use Celery `shared_task` decorator for flexibility
- Implement retry logic with exponential backoff (3 retries)
- Email templates should be professional and include all form data
- Webhook payload must be secure - don't include sensitive data
- Auto-reply should support basic interpolation ({{name}} only for security)
- Test with Celery eager mode (`CELERY_TASK_ALWAYS_EAGER=True`)
- Consider email validation before sending auto-reply
- Webhook timeout should be reasonable (10 seconds)
- Handle missing email gracefully in auto-reply task
