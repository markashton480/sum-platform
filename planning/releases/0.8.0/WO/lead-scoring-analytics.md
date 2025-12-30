# Work Order: Lead Scoring/Analytics Dashboard

> **Parent:** [VD v0.8.0](../VD.md)
> **Branch:** `feature/lead-analytics`
> **Priority:** P0

---

## Overview

### Goal

Deliver lead scoring functionality and an analytics dashboard for lead management insights. This transforms lead management from basic status tracking to data-driven prioritization and reporting.

### Context

Lead Management v1 (delivered in v0.7.0) provides status management, notes, and assignment. However, teams need a way to prioritize leads based on engagement and data quality, and to understand conversion patterns through analytics.

### Dependency

This work order builds on Lead Management v1 from v0.7.0. The Lead model, status pipeline, notes, and assignment must be in place.

---

## Acceptance Criteria

### Must Have

- [ ] Leads receive calculated scores (0-100)
- [ ] Score displayed in lead list and detail views
- [ ] Score updates when lead data changes
- [ ] Dashboard displays key metrics
- [ ] Conversion rate visible (New -> Converted)
- [ ] Leads filterable by score range
- [ ] Leads sortable by score

### Should Have

- [ ] Score breakdown visible (what contributed to score)
- [ ] Time-series chart for lead volume
- [ ] Lead source distribution chart
- [ ] Average time to conversion metric
- [ ] Export dashboard data

### Could Have

- [ ] Custom scoring rules
- [ ] Score history tracking
- [ ] Automated score-based assignment

---

## Technical Approach

### Lead Scoring Algorithm (v1)

Simple, transparent scoring based on data completeness and engagement signals:

```python
# sum_core/leads/scoring.py

def calculate_lead_score(lead) -> int:
    """Calculate lead score from 0-100."""
    score = 0

    # Data completeness (max 40 points)
    if lead.email:
        score += 10
    if lead.name and len(lead.name) > 2:
        score += 10
    if lead.phone:
        score += 10
    if lead.company:
        score += 10

    # Form data richness (max 30 points)
    form_data = lead.form_data or {}
    if len(form_data) >= 5:
        score += 30
    elif len(form_data) >= 3:
        score += 20
    elif len(form_data) >= 1:
        score += 10

    # Engagement signals (max 30 points)
    if lead.notes.exists():
        score += 10
    if lead.status in ['contacted', 'qualified']:
        score += 10
    if lead.assigned_to:
        score += 10

    return min(score, 100)
```

### Score Model Integration

Add score field to Lead model:

```python
# In Lead model
score = models.IntegerField(default=0, db_index=True)
score_updated_at = models.DateTimeField(null=True)

def update_score(self):
    from .scoring import calculate_lead_score
    self.score = calculate_lead_score(self)
    self.score_updated_at = timezone.now()
    self.save(update_fields=['score', 'score_updated_at'])
```

### Dashboard Metrics

Key metrics for the dashboard:

| Metric | Calculation |
| ------ | ----------- |
| Total Leads | Count all leads |
| Leads This Week | Leads created in last 7 days |
| Conversion Rate | (Converted / Total) * 100 |
| Avg Score | Mean of all lead scores |
| Avg Time to Conversion | Mean days from created to converted |
| Lead Source Distribution | Group by source field |
| Status Distribution | Group by status |

### Dashboard View

```python
# sum_core/leads/views.py

@staff_member_required
def lead_analytics_dashboard(request):
    leads = Lead.objects.all()

    metrics = {
        'total_leads': leads.count(),
        'leads_this_week': leads.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'conversion_rate': calculate_conversion_rate(leads),
        'avg_score': leads.aggregate(avg=Avg('score'))['avg'] or 0,
        'status_distribution': leads.values('status').annotate(count=Count('id')),
        'source_distribution': leads.values('source').annotate(count=Count('id')),
    }

    return render(request, 'sum_core/leads/dashboard.html', {'metrics': metrics})
```

---

## File Changes

### New Files

| File | Purpose |
| ---- | ------- |
| `sum_core/leads/scoring.py` | Scoring algorithm |
| `sum_core/leads/analytics.py` | Analytics calculations |
| `sum_core/leads/views.py` | Dashboard view (new or extend) |
| `sum_core/templates/sum_core/leads/dashboard.html` | Dashboard template |
| `sum_core/templates/sum_core/leads/includes/score_badge.html` | Score display component |
| `tests/leads/test_scoring.py` | Scoring tests |
| `tests/leads/test_analytics.py` | Analytics tests |

### Modified Files

| File | Changes |
| ---- | ------- |
| `sum_core/leads/models.py` | Add score field, update_score method |
| `sum_core/leads/admin.py` | Display score, add filtering |
| `sum_core/urls.py` | Add dashboard URL |

---

## Tasks

### TASK-001: Design Lead Scoring Algorithm

**Estimate:** 2-3 hours
**Risk:** Medium

Design and document the scoring algorithm with clear, transparent rules.

**Acceptance Criteria:**
- [ ] Algorithm documented with point breakdown
- [ ] Scoring factors identified (data completeness, engagement)
- [ ] Maximum score is 100
- [ ] Algorithm is deterministic (same inputs = same score)
- [ ] Edge cases considered (empty lead, maximum data)

**Technical Notes:**
- Keep algorithm simple and explainable
- Document in code and user-facing docs
- Consider future extensibility but don't over-engineer

**Branch:** `feature/lead-analytics/001-scoring-algorithm`

---

### TASK-002: Add Score Field to Lead Model

**Estimate:** 1-2 hours
**Risk:** Low

Add score field and related fields to the Lead model.

**Acceptance Criteria:**
- [ ] Score field added (IntegerField, 0-100)
- [ ] score_updated_at timestamp field added
- [ ] Migration created and tested
- [ ] Default score is 0
- [ ] Score field is indexed for filtering

**Technical Notes:**
- Use db_index=True for score field
- Consider data migration for existing leads

**Branch:** `feature/lead-analytics/002-score-field`

---

### TASK-003: Implement Score Calculation

**Estimate:** 2-3 hours
**Risk:** Medium

Implement the scoring function and automatic updates.

**Acceptance Criteria:**
- [ ] calculate_lead_score function implemented
- [ ] Score calculation matches documented algorithm
- [ ] update_score method on Lead model
- [ ] Score updates on save (via signal or override)
- [ ] Bulk recalculation command available

**Technical Notes:**
- Use post_save signal or override save method
- Create management command for bulk recalculation
- Consider performance for bulk operations

**Branch:** `feature/lead-analytics/003-score-calculation`

---

### TASK-004: Display Score in Lead Admin

**Estimate:** 2-3 hours
**Risk:** Low

Add score display to lead list and detail views in admin.

**Acceptance Criteria:**
- [ ] Score column in lead list view
- [ ] Score displayed in lead detail view
- [ ] Score breakdown visible (what contributed)
- [ ] Visual indicator (color coding by range)
- [ ] Score sortable in list view

**Technical Notes:**
- Use ModelAdmin list_display
- Create score badge template include
- Color coding: red (<30), yellow (30-60), green (>60)

**Branch:** `feature/lead-analytics/004-admin-score-display`

---

### TASK-005: Create Analytics Dashboard View

**Estimate:** 3-4 hours
**Risk:** Medium

Create the analytics dashboard page with key metrics.

**Acceptance Criteria:**
- [ ] Dashboard view created
- [ ] Staff-only access enforced
- [ ] Key metrics calculated and displayed
- [ ] Dashboard URL accessible from admin
- [ ] Basic layout and structure

**Technical Notes:**
- Use @staff_member_required decorator
- Create dedicated template
- Consider caching for expensive calculations

**Branch:** `feature/lead-analytics/005-dashboard-view`

---

### TASK-006: Dashboard Metrics and Charts

**Estimate:** 3-5 hours
**Risk:** Medium

Add metrics display and visualization charts to dashboard.

**Acceptance Criteria:**
- [ ] Total leads, weekly leads displayed
- [ ] Conversion rate calculated and displayed
- [ ] Average score displayed
- [ ] Status distribution visualization
- [ ] Source distribution visualization
- [ ] Time-series chart for lead volume (last 30 days)

**Technical Notes:**
- Use Chart.js for visualizations
- Keep charts simple and readable
- Consider server-side rendering for static charts

**Branch:** `feature/lead-analytics/006-metrics-charts`

---

### TASK-007: Score-based Filtering

**Estimate:** 1-2 hours
**Risk:** Low

Add ability to filter leads by score range.

**Acceptance Criteria:**
- [ ] Filter by score range in admin
- [ ] Quick filters (High: 70+, Medium: 30-69, Low: <30)
- [ ] Filter works with existing filters
- [ ] Sort by score works

**Technical Notes:**
- Use SimpleListFilter for score ranges
- Add to existing filter configuration

**Branch:** `feature/lead-analytics/007-score-filtering`

---

### TASK-008: Analytics Tests

**Estimate:** 2-4 hours
**Risk:** Low

Write comprehensive tests for scoring and analytics.

**Acceptance Criteria:**
- [ ] Test score calculation for various inputs
- [ ] Test edge cases (empty lead, full lead)
- [ ] Test score updates on save
- [ ] Test analytics calculations
- [ ] Test dashboard view access control
- [ ] Test filtering by score

**Technical Notes:**
- Create factory for leads with various data
- Test both unit and integration levels

**Branch:** `feature/lead-analytics/008-tests`

---

## Execution Order

```
001 (Algorithm Design)
    |
    v
002 (Score Field)
    |
    v
003 (Score Calculation)
    |
    +---> 004 (Admin Display)
    |         |
    |         v
    v     007 (Filtering)
005 (Dashboard View)
    |
    v
006 (Metrics & Charts)
    |
    v
008 (Tests)
```

### Parallelization

- TASK-004 (Admin Display) and TASK-005 (Dashboard) can proceed in parallel after TASK-003
- TASK-007 (Filtering) can parallel with TASK-006

---

## Testing Requirements

### Unit Tests

- Score calculation with various inputs
- Analytics metric calculations
- Edge cases and boundary conditions

### Integration Tests

- Score updates when lead saved
- Dashboard renders with real data
- Filtering returns correct results

### Manual Testing

- Visual check of score display
- Chart rendering verification
- Performance with many leads

---

## Definition of Done

- [ ] All 8 tasks completed and merged
- [ ] All acceptance criteria met
- [ ] Tests passing (`make test`)
- [ ] Linting passing (`make lint`)
- [ ] Scores calculate correctly
- [ ] Dashboard displays metrics
- [ ] Filtering by score works
- [ ] PR merged to `release/0.8.0`

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Algorithm debates delay implementation | Medium | Medium | Document simple v1, iterate later |
| Dashboard performance with many leads | Low | Medium | Add caching, limit date ranges |
| Score calculation overhead | Low | Low | Async update, batch recalculation |
| Chart library adds complexity | Low | Low | Keep charts simple, vanilla Chart.js |

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
