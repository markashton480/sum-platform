# Task

**Title:** `WO-CI-003: Document Lead.form_data structure`

---

## Parent

**Work Order:** #462 (WO: CI & Documentation Enhancements)
**Tracking Issue:** #475
**Related Issue:** #186

---

## Branch

| Branch | Target |
|--------|--------|
| `chore/ci-docs-improvements/003-form-data-docs` | `chore/ci-docs-improvements` |

```bash
git checkout chore/ci-docs-improvements
git pull origin chore/ci-docs-improvements
git checkout -b chore/ci-docs-improvements/003-form-data-docs
git push -u origin chore/ci-docs-improvements/003-form-data-docs
```

---

## Deliverable

This task will deliver:

- Documentation of Lead.form_data JSON structure
- Examples of form_data contents
- Guidance on accessing and using form_data
- Integration with developer handbook

---

## Boundaries

### Do

- Document the `Lead.form_data` JSONField structure
- Provide examples of typical form_data contents
- Explain how form submissions populate form_data
- Document best practices for accessing form_data
- Add to HANDBOOK.md or create dedicated doc
- Include code examples

### Do NOT

- ❌ Do not modify the Lead model
- ❌ Do not change form handling code
- ❌ Do not add new form_data fields
- ❌ Do not modify database schema

---

## Acceptance Criteria

- [ ] Lead.form_data structure documented
- [ ] Example form_data JSON provided
- [ ] Usage examples with code snippets
- [ ] Common patterns documented
- [ ] Integrated into developer documentation
- [ ] Documentation builds without errors

---

## Test Commands

```bash
make lint
make test

# Build docs if applicable
# mkdocs build
```

---

## Files Expected to Change

```
docs/
└── dev/
    └── HANDBOOK.md             # Modified: add form_data section

# OR
docs/
└── api/
    └── lead-form-data.md       # New: dedicated doc
```

---

## Dependencies

**Depends On:**
- [ ] None — can run in parallel with other tasks

**Blocks:**
- WO-CI-004: Update developer handbook

---

## Risk

**Level:** Low

**Why:**
- Documentation only, no code changes
- Easy to update if needed

---

## Labels

- [ ] `type:task`
- [ ] `component:docs`
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
docs(leads): document Lead.form_data structure and usage

- Add form_data JSON structure documentation
- Include example form data contents
- Provide usage patterns and code examples
- Add to developer handbook

Closes #186
```

---

## Documentation Template

The following content should be added to `docs/api/lead-form-data.md`:

### Lead.form_data Structure

The `Lead.form_data` field is a JSONField that stores the raw form submission data.

#### Structure

Example JSON structure:
```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "555-0123",
  "message": "I'm interested in your services...",
  "source_page": "/contact/",
  "submitted_at": "2025-01-15T10:30:00Z",
  "form_id": "contact-form-main"
}
```

#### Common Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Submitter's name |
| `email` | string | Submitter's email address |
| `phone` | string | Phone number (optional) |
| `message` | string | Free-text message content |
| `source_page` | string | URL path of the form page |
| `submitted_at` | ISO datetime | Submission timestamp |
| `form_id` | string | Identifier of the form used |

#### Accessing form_data

```python
from sum_core.leads.models import Lead

# Get a lead
lead = Lead.objects.get(id=123)

# Access form_data fields
name = lead.form_data.get('name', '')
email = lead.form_data.get('email', '')

# Check for optional fields
phone = lead.form_data.get('phone')
if phone:
    # Handle phone number
    pass
```

#### Best Practices

1. Always use `.get()` with defaults for optional fields
2. Validate field types before processing
3. Don't assume all fields exist in every submission
4. Store additional metadata in form_data, not as model fields
