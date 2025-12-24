# BLOG.005: Category Snippet for Blog

**Phase:** 3 - Blog Models + Templates  
**Priority:** P1  
**Estimated Hours:** 4h  
**Dependencies:** None (can run in parallel with Phase 2)

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-005-category-snippet
```

## Objective

Create the `Category` Wagtail Snippet for organizing blog posts. This is a simple, single-level taxonomy system (no hierarchical categories).

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:310-330`
- Wagtail Snippets: https://docs.wagtail.org/en/stable/topics/snippets.html
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **New File:** `core/sum_core/pages/blog.py`

### Model Definition

Create `Category` Wagtail Snippet:

```python
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Category(models.Model):
    """
    Blog post category (single-level taxonomy).
    
    Simple categorization system - no parent/child relationships.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., 'News', 'Tutorials', 'Case Studies')"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional category description for SEO"
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
    ]
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

### Admin Configuration

- List display: name, slug
- Search fields: name, description
- Ordering: alphabetical by name

## Implementation Tasks

- [ ] Create `core/sum_core/pages/blog.py`
- [ ] Import required Django and Wagtail modules
- [ ] Implement `Category` model with all fields
- [ ] Decorate with `@register_snippet`
- [ ] Configure `panels` for admin
- [ ] Add `__str__()` method
- [ ] Set Meta class with verbose_name_plural and ordering
- [ ] Update `core/sum_core/pages/__init__.py` to export `Category`
- [ ] Create migration: `python manage.py makemigrations sum_core`
- [ ] Write unit tests in `tests/pages/test_category.py`:
  - Category creation
  - Slug uniqueness
  - String representation
  - Admin registration
  - Ordering

## Acceptance Criteria

- [ ] `Category` model exists and can be created
- [ ] Appears in Wagtail admin under "Snippets"
- [ ] Slug uniqueness enforced
- [ ] Description field optional
- [ ] Categories ordered alphabetically in lists
- [ ] Migration runs cleanly
- [ ] Unit tests pass with ≥80% coverage
- [ ] `make lint` passes

## Testing Commands

```bash
# Run unit tests
pytest tests/pages/test_category.py -v

# Check coverage
pytest tests/pages/test_category.py --cov=core/sum_core/pages/blog --cov-report=term-missing

# Interactive test
python core/sum_core/test_project/manage.py runserver
# Navigate to /admin/snippets/pages/category/
# Create test categories

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(blog): add Category snippet for blog organization

- Create Category Wagtail Snippet
- Single-level taxonomy (no hierarchy)
- Unique slug constraint
- Optional description for SEO
- Admin registration with ordering
- Add migration and unit tests

Refs: BLOG.005"

git push origin feature/BLOG-005-category-snippet

gh pr create \
  --base develop \
  --title "feat(blog): Category snippet for blog organization" \
  --body "Implements BLOG.005 - Category snippet for blog posts.

## Changes
- Category Wagtail Snippet with name, slug, description
- Unique slug enforcement
- Alphabetical ordering
- Admin registration
- Unit tests and migration

## Testing
- ✅ Category CRUD works in admin
- ✅ Slug uniqueness enforced
- ✅ Ordering alphabetical
- ✅ Lint checks pass

## Related
- Part of Blog v1 implementation
- Used by: BLOG.010 (BlogIndexPage), BLOG.011 (BlogPostPage)"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Address feedback, resolve conversations
```

## Notes for AI Agents

- This is a standalone task that can run in parallel with Phase 2 forms work
- Keep categories simple - no parent/child, no icons, no colors
- Description field is for SEO/metadata only (may not display in UI)
- Consider adding sample categories in migration (optional)
- This blocks BlogPostPage model creation (BLOG.011)
