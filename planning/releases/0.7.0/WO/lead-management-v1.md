# WO: Lead Management v1 (v0.7.0)

## Metadata

- **Version:** v0.7.0
- **Component:** leads
- **Priority:** P0 (Must Land)
- **Branch:** `feature/leads-v1`
- **Parent VD:** #TBD
- **Issue:** #TBD

---

## Description

Deliver the first production-ready lead management feature set as specified in POST-MVP_BIG-PLAN. This transforms leads from a simple data capture into an operational CRM-lite system. Editors will be able to manage lead pipeline, add notes, assign leads to team members, and efficiently filter/search leads.

**Why this matters:**
- Currently leads display status with no way to update it
- Operations teams need workflow to process leads
- Notes and history are essential for team collaboration
- Assignment enables workload distribution
- This is explicitly required per POST-MVP_BIG-PLAN

---

## Acceptance Criteria

- [ ] Lead status can be updated through intuitive Wagtail admin UI
- [ ] Leads can have timestamped notes added by users
- [ ] Leads can be assigned to registered users
- [ ] Activity history shows all changes to a lead
- [ ] Filtering by status, assignment, date range works
- [ ] Search across lead fields (name, email, company) works
- [ ] Bulk status updates functional for multiple leads
- [ ] No regression in lead submission or storage

---

## Deliverables

1. **Lead Model Enhancements**
   - `assigned_to` ForeignKey to User
   - Activity history tracking

2. **LeadNote Model**
   - Note content, author, timestamp
   - Related to Lead via ForeignKey

3. **Admin UI Improvements**
   - Status update inline in list view
   - Notes panel in detail view
   - Activity timeline view
   - Assignment dropdown
   - Enhanced filters

4. **Bulk Actions**
   - Bulk status change
   - Bulk assignment

5. **Lead Source Taxonomy (P1 stretch)**
   - Simple taxonomy for lead sources
   - Filtering by source

---

## Technical Approach

### Model Changes

```python
# core/sum_core/leads/models.py

class Lead(models.Model):
    # Existing fields...
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )

class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class LeadActivity(models.Model):
    """Tracks all changes to leads for audit trail"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # status_changed, assigned, note_added, etc.
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Admin Enhancements

- Use Wagtail's `ModelAdmin` or `viewsets` for enhanced UI
- Custom panels for notes and activity
- Inline status editing
- Custom filters for date ranges, assignment

---

## Boundaries

### Do

- Add lead assignment with simple user selection
- Add timestamped notes with author tracking
- Add activity history for audit trail
- Add enhanced filtering (status, date, assignment)
- Add bulk actions for common operations
- Keep UI consistent with Wagtail patterns
- Write comprehensive tests

### Do NOT

- Add lead scoring (deferred)
- Add analytics dashboards (deferred)
- Add workflow automation (deferred)
- Add email notifications (deferred)
- Add custom user roles for leads
- Change the lead submission flow
- Add complex permission systems

---

## Subtasks

### TASK-001: Add Lead Assignment Field

**Description:**
Add `assigned_to` ForeignKey to the Lead model. Create migration. Update admin to show and allow editing assignment.

**Acceptance Criteria:**
- [ ] `assigned_to` field added to Lead model
- [ ] Migration created and tested
- [ ] Assignment visible in lead list view
- [ ] Assignment editable in lead detail view
- [ ] Assignment dropdown shows active users

**Boundaries:**
- Do: Add simple FK to User
- Do: Filter to active users in dropdown
- Do NOT: Add assignment rules or auto-assignment
- Do NOT: Add assignment notifications

**Branch:** `feature/leads-v1/001-lead-assignment`

---

### TASK-002: Create LeadNote Model

**Description:**
Create LeadNote model for timestamped notes on leads. Include author tracking and creation timestamp.

**Acceptance Criteria:**
- [ ] LeadNote model created with lead FK, author FK, content, created_at
- [ ] Migration created and tested
- [ ] Model registered appropriately
- [ ] Basic model tests pass

**Boundaries:**
- Do: Keep model simple
- Do: Track author via FK
- Do NOT: Add note editing (create-only for audit trail)
- Do NOT: Add note types or categories

**Branch:** `feature/leads-v1/002-lead-note-model`

---

### TASK-003: Create LeadActivity Model

**Description:**
Create LeadActivity model for tracking all changes to leads. This provides an audit trail of status changes, assignments, and other actions.

**Acceptance Criteria:**
- [ ] LeadActivity model with action types, old/new values, timestamps
- [ ] Migration created and tested
- [ ] Activity created on status change
- [ ] Activity created on assignment change
- [ ] Activity created on note addition

**Boundaries:**
- Do: Track status changes, assignments, notes
- Do: Store old/new values as JSON
- Do NOT: Track field-level changes for all fields
- Do NOT: Add activity for view/read events

**Branch:** `feature/leads-v1/003-lead-activity-model`

---

### TASK-004: Lead Notes Admin Panel

**Description:**
Add notes panel to lead detail view in Wagtail admin. Allow adding new notes with timestamp display.

**Acceptance Criteria:**
- [ ] Notes visible in lead detail view
- [ ] Add note form inline in detail view
- [ ] Notes display author and timestamp
- [ ] Notes ordered by most recent first
- [ ] Author auto-set to current user

**Boundaries:**
- Do: Use Wagtail panel patterns
- Do: Show all notes in timeline format
- Do NOT: Allow note editing or deletion
- Do NOT: Add rich text in notes

**Branch:** `feature/leads-v1/004-notes-admin-panel`

---

### TASK-005: Lead Activity Timeline

**Description:**
Add activity timeline panel to lead detail view showing all historical changes to the lead.

**Acceptance Criteria:**
- [ ] Activity timeline visible in lead detail
- [ ] Shows status changes with old/new values
- [ ] Shows assignment changes
- [ ] Shows note additions
- [ ] Timestamps and users displayed

**Boundaries:**
- Do: Display activities in chronological order
- Do: Format activity descriptions clearly
- Do NOT: Allow activity editing
- Do NOT: Add activity filtering in panel

**Branch:** `feature/leads-v1/005-activity-timeline`

---

### TASK-006: Enhanced Lead Filters

**Description:**
Add advanced filtering to lead list view including status, assignment, date ranges, and saved filter presets.

**Acceptance Criteria:**
- [ ] Filter by status (multi-select)
- [ ] Filter by assigned_to (including unassigned)
- [ ] Filter by date range (submitted date)
- [ ] Filter by source (if source field exists)
- [ ] Quick filters: "New this week", "My leads", "Unassigned"

**Boundaries:**
- Do: Use Wagtail's filter mechanisms
- Do: Add quick filter shortcuts
- Do NOT: Add saved filter persistence (can defer)
- Do NOT: Add complex query builder

**Branch:** `feature/leads-v1/006-enhanced-filters`

---

### TASK-007: Lead Search

**Description:**
Add search functionality across lead fields including name, email, company, and form_data content.

**Acceptance Criteria:**
- [ ] Search box in lead list view
- [ ] Search matches name, email fields
- [ ] Search matches company if present
- [ ] Search matches content in form_data JSON
- [ ] Results highlighted or indicated

**Boundaries:**
- Do: Use Django/Wagtail search capabilities
- Do: Search key form_data fields
- Do NOT: Implement full-text search engine
- Do NOT: Add fuzzy matching

**Branch:** `feature/leads-v1/007-lead-search`

---

### TASK-008: Bulk Status Updates

**Description:**
Add bulk action to change status for multiple selected leads at once.

**Acceptance Criteria:**
- [ ] Checkbox selection in lead list
- [ ] Bulk action dropdown with status options
- [ ] Confirmation before bulk update
- [ ] Activity records created for each lead
- [ ] Success message shows count updated

**Boundaries:**
- Do: Use Wagtail's bulk action patterns
- Do: Create activity records for audit
- Do NOT: Add bulk assignment (can defer)
- Do NOT: Add bulk delete

**Branch:** `feature/leads-v1/008-bulk-status`

---

### TASK-009: Inline Status Editing

**Description:**
Allow quick status updates directly from the lead list view without entering detail view.

**Acceptance Criteria:**
- [ ] Status displayed as editable in list view
- [ ] Click to change status inline
- [ ] Activity recorded on change
- [ ] Visual feedback on successful change

**Boundaries:**
- Do: Use appropriate Wagtail UI patterns
- Do: Keep it simple (dropdown or buttons)
- Do NOT: Add inline editing for other fields
- Do NOT: Break list view performance

**Branch:** `feature/leads-v1/009-inline-status`

---

### TASK-010: Lead Source Taxonomy (P1)

**Description:**
Add simple taxonomy for lead sources. Lightweight implementation - don't let it balloon.

**Acceptance Criteria:**
- [ ] LeadSource model or choices field
- [ ] Source selectable in lead admin
- [ ] Filter by source in list view
- [ ] Source visible in lead list

**Boundaries:**
- Do: Keep implementation minimal
- Do: Use simple choices or small model
- Do NOT: Add complex taxonomy hierarchy
- Do NOT: Add source analytics

**Branch:** `feature/leads-v1/010-lead-source` (P1)

---

## Merge Order

1. TASK-002 (LeadNote Model) - foundational model
2. TASK-003 (LeadActivity Model) - foundational model
3. TASK-001 (Assignment Field) - depends on activity for tracking
4. TASK-004 (Notes Panel) - depends on 002
5. TASK-005 (Activity Timeline) - depends on 003
6. TASK-006 (Enhanced Filters) - depends on 001
7. TASK-007 (Search) - can parallel with 006
8. TASK-008 (Bulk Status) - depends on 003 for activity
9. TASK-009 (Inline Status) - depends on 003 for activity
10. TASK-010 (Source Taxonomy) - P1, last if time permits

---

## Estimated Effort

| Task | Estimate | Risk |
| ---- | -------- | ---- |
| TASK-001 | 2-3 hours | Low |
| TASK-002 | 1-2 hours | Low |
| TASK-003 | 2-3 hours | Low |
| TASK-004 | 3-4 hours | Medium |
| TASK-005 | 2-3 hours | Low |
| TASK-006 | 3-4 hours | Medium |
| TASK-007 | 2-3 hours | Medium |
| TASK-008 | 2-3 hours | Low |
| TASK-009 | 2-3 hours | Medium |
| TASK-010 | 2-3 hours | Low (P1) |

**Total (without P1):** 19-28 hours
**Total (with P1):** 21-31 hours

---

## Testing Requirements

- Model tests for LeadNote, LeadActivity
- Admin tests for new panels and actions
- Integration tests for activity tracking
- Bulk action tests
- Filter and search tests
- Migration tests (forwards and backwards)

---

## Notes

- Activity tracking is essential for audit compliance
- Keep UI patterns consistent with existing Wagtail admin
- Consider "My Leads" as primary view for assigned users
- Source taxonomy should be simple - resist feature creep
- All changes must create activity records for traceability
