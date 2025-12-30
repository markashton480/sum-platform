# Work Order: Blog Search v1

> **Parent:** [VD v0.8.0](../VD.md)
> **Branch:** `feature/blog-search`
> **Priority:** P0

---

## Overview

### Goal

Deliver wireframe-parity blog search functionality using Wagtail's built-in search backend. This provides users with the ability to search blog content without requiring external search infrastructure.

### Context

The blog system introduced in v0.6.0 lacks search functionality. Users must browse or use external search engines to find blog content. This work order adds a focused blog search feature that matches the wireframe specifications.

**CRITICAL SCOPE CONSTRAINT:** This is **Blog Search v1**, NOT "Search Foundation". The name is intentionally focused to prevent scope creep into site-wide search, analytics, or external backends.

---

## Acceptance Criteria

### Must Have

- [ ] Search input component renders where wireframe specifies
- [ ] Search queries blog posts by title and body content
- [ ] Search results page displays matching posts
- [ ] Results include post title, excerpt, date, and category
- [ ] Pagination works on results page (10 results per page default)
- [ ] No-results state displays helpful message
- [ ] Search works on all themes (Theme A, Theme B)
- [ ] Search respects published status (no draft posts in results)

### Should Have

- [ ] Search highlights matching terms in results
- [ ] Search is case-insensitive
- [ ] Empty query shows appropriate message
- [ ] Search input has accessible label and placeholder

### Must NOT Have (Explicit Non-Goals)

- Global/site-wide page search
- Service page, Standard page, or other page type search
- Relevance tuning, synonyms, or fuzzy matching
- External search backends (Algolia, Elasticsearch, Meilisearch)
- Query logging or search analytics
- Search suggestions or autocomplete
- Saved searches or search history

---

## Technical Approach

### Backend: Wagtail Search (DB-backed)

Use Wagtail's built-in search backend with PostgreSQL full-text search:

```python
# In BlogPostPage model
search_fields = Page.search_fields + [
    index.SearchField('title', boost=2),
    index.SearchField('body'),
    index.SearchField('excerpt'),
    index.FilterField('category'),
    index.FilterField('first_published_at'),
]
```

### Search View

```python
# sum_core/search/views.py
def blog_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        results = BlogPostPage.objects.live().search(query)
    else:
        results = BlogPostPage.objects.none()

    paginator = Paginator(results, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'sum_core/search/blog_search_results.html', {
        'query': query,
        'results': page,
    })
```

### URL Configuration

```python
# sum_core/urls.py
urlpatterns = [
    path('blog/search/', views.blog_search, name='blog_search'),
]
```

### Template Structure

```
themes/<theme>/templates/sum_core/search/
├── blog_search_results.html
├── includes/
│   ├── search_input.html
│   ├── search_result_item.html
│   └── no_results.html
```

---

## Wireframe Parity

### Search Input Placement

The search input appears in the blog index page header area, per wireframe specification. It uses a form that submits to the blog search URL.

### Results Page Layout

- Header with search query displayed
- Result count (e.g., "12 results for 'kitchen design'")
- Result cards matching blog card styling
- Pagination at bottom

### No Results State

- Friendly message: "No blog posts found for '[query]'"
- Suggestions: "Try different keywords" or "Browse all posts"
- Link back to blog index

---

## File Changes

### New Files

| File | Purpose |
| ---- | ------- |
| `sum_core/search/__init__.py` | Search module init |
| `sum_core/search/views.py` | Blog search view |
| `sum_core/search/urls.py` | Search URL patterns |
| `themes/theme_a/templates/sum_core/search/blog_search_results.html` | Theme A results template |
| `themes/theme_a/templates/sum_core/search/includes/search_input.html` | Theme A search input |
| `themes/theme_a/templates/sum_core/search/includes/no_results.html` | Theme A no results |
| `themes/theme_b/templates/sum_core/search/...` | Theme B equivalents |
| `tests/search/test_blog_search.py` | Search tests |

### Modified Files

| File | Changes |
| ---- | ------- |
| `sum_core/pages/blog_post_page.py` | Add search_fields if missing |
| `sum_core/urls.py` | Include search URLs |
| `themes/*/templates/sum_core/pages/blog_index_page.html` | Add search input |

---

## Tasks

### TASK-001: Configure Wagtail Search for BlogPostPage

**Estimate:** 2-3 hours
**Risk:** Low

Add search field configuration to BlogPostPage model for Wagtail's search backend.

**Acceptance Criteria:**
- [ ] BlogPostPage has search_fields defined
- [ ] Title field boosted for relevance
- [ ] Body content searchable
- [ ] Category as filter field
- [ ] Existing tests pass

**Technical Notes:**
- Use `index.SearchField` for text content
- Use `index.FilterField` for structured data
- Ensure migrations are created if needed

**Branch:** `feature/blog-search/001-wagtail-search-config`

---

### TASK-002: Create Search Input Component

**Estimate:** 2-3 hours
**Risk:** Low

Create the search input component template that will be included in the blog index page.

**Acceptance Criteria:**
- [ ] Search input template created for Theme A
- [ ] Search input template created for Theme B
- [ ] Form submits to blog search URL
- [ ] Input has accessible label (visually hidden if needed)
- [ ] Placeholder text matches wireframe
- [ ] Input preserves query on results page

**Technical Notes:**
- Use include template pattern
- Ensure CSRF token included
- Consider search icon/button styling

**Branch:** `feature/blog-search/002-search-input`

---

### TASK-003: Create Blog Search Results Page

**Estimate:** 3-4 hours
**Risk:** Medium

Create the search results page view and template.

**Acceptance Criteria:**
- [ ] View handles query parameter
- [ ] View returns paginated results
- [ ] Template displays result count
- [ ] Template displays search query
- [ ] Result items show title, excerpt, date, category
- [ ] Results link to blog post pages
- [ ] Works on Theme A and Theme B

**Technical Notes:**
- Create view in `sum_core/search/views.py`
- Use Django Paginator
- Handle empty query gracefully

**Branch:** `feature/blog-search/003-results-page`

---

### TASK-004: Implement No-Results State

**Estimate:** 1-2 hours
**Risk:** Low

Create the no-results state display for when search returns zero matches.

**Acceptance Criteria:**
- [ ] No-results message displays when query has no matches
- [ ] Message includes the search query
- [ ] Helpful suggestions displayed
- [ ] Link to browse all posts
- [ ] Styled appropriately for each theme

**Technical Notes:**
- Use include template for no-results content
- Keep messaging friendly and actionable

**Branch:** `feature/blog-search/004-no-results`

---

### TASK-005: Add Results Pagination

**Estimate:** 2-3 hours
**Risk:** Low

Implement pagination for search results.

**Acceptance Criteria:**
- [ ] Results paginate at 10 per page
- [ ] Pagination controls display
- [ ] Page numbers show current and nearby pages
- [ ] Next/Previous navigation works
- [ ] Query preserved across pages
- [ ] Pagination styled for each theme

**Technical Notes:**
- Reuse existing pagination patterns from blog index
- Ensure query string preserved in pagination links

**Branch:** `feature/blog-search/005-pagination`

---

### TASK-006: Theme Templates for Search

**Estimate:** 2-4 hours
**Risk:** Medium

Ensure all search templates are properly themed for Theme A and Theme B.

**Acceptance Criteria:**
- [ ] Theme A search templates complete
- [ ] Theme B search templates complete
- [ ] Search input styling matches theme
- [ ] Results cards match blog card styling
- [ ] Pagination matches theme patterns
- [ ] Responsive design works

**Technical Notes:**
- Follow existing theme patterns
- Use theme-specific CSS classes
- Test on mobile viewports

**Branch:** `feature/blog-search/006-theme-templates`

---

### TASK-007: Blog Search Tests

**Estimate:** 2-3 hours
**Risk:** Low

Write comprehensive tests for blog search functionality.

**Acceptance Criteria:**
- [ ] Test search returns matching posts
- [ ] Test search excludes draft posts
- [ ] Test search pagination
- [ ] Test empty query handling
- [ ] Test no-results case
- [ ] Test case-insensitivity
- [ ] Integration test for full flow

**Technical Notes:**
- Create test fixtures with blog posts
- Use Django test client for view tests
- Consider pytest parametrize for edge cases

**Branch:** `feature/blog-search/007-tests`

---

## Execution Order

```
001 (Search Config)
    |
    v
002 (Search Input) ----+
    |                  |
    v                  |
003 (Results Page) <---+
    |
    +---> 004 (No Results)
    |
    v
005 (Pagination)
    |
    v
006 (Theme Templates)
    |
    v
007 (Tests)
```

### Parallelization

- TASK-002 and TASK-003 can start after TASK-001
- TASK-004 can parallel with TASK-005 after TASK-003
- TASK-006 after core functionality complete
- TASK-007 after all feature tasks

---

## Testing Requirements

### Unit Tests

- Search field configuration
- Query parsing and sanitization
- Pagination logic

### Integration Tests

- Full search flow (input -> results -> pagination)
- Draft posts excluded
- Published posts included

### Theme Tests

- Search renders correctly on Theme A
- Search renders correctly on Theme B
- Responsive layouts work

---

## Definition of Done

- [ ] All 7 tasks completed and merged
- [ ] All acceptance criteria met
- [ ] Tests passing (`make test`)
- [ ] Linting passing (`make lint`)
- [ ] Search works on Theme A and Theme B
- [ ] No-results state implemented
- [ ] Pagination working
- [ ] PR merged to `release/0.8.0`

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Scope creep to site-wide search | High | High | Explicit non-goals, PR review |
| Performance with large post count | Low | Medium | Pagination limits results |
| Search relevance issues | Low | Low | DB-backed search is "good enough" for v1 |

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
