# BLOG.009: BlogIndexPage Model and Listing Logic

**Phase:** 3 - Blog Models + Templates  
**Priority:** P1  
**Estimated Hours:** 9h  
**Dependencies:** BLOG.005

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-009-blog-index-page
```

## Objective

Create the `BlogIndexPage` Wagtail page model that lists blog posts with pagination and category filtering. This is the main blog landing page (e.g., `/blog/`).

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:332-358`
- Wagtail Page Models: https://docs.wagtail.org/en/stable/topics/pages.html
- Pagination: https://docs.djangoproject.com/en/stable/topics/pagination/
- Existing Pages: `core/sum_core/pages/`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **File:** `core/sum_core/pages/blog.py` (add to existing file with Category)

### Model Definition

```python
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models


class BlogIndexPage(Page):
    """
    Blog listing page - displays all blog posts with pagination and filtering.
    
    URL: /blog/
    Template: blog_index_page.html
    """
    
    intro = RichTextField(
        blank=True,
        help_text="Optional intro text displayed above post listing"
    )
    posts_per_page = models.IntegerField(
        default=10,
        help_text="Number of posts to display per page"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('posts_per_page'),
    ]
    
    # Page type constraints
    max_count = 1  # Only one blog index per site
    parent_page_types = ['pages.HomePage']  # Or root
    subpage_types = ['pages.BlogPostPage']
    
    def get_posts(self):
        """Get all live blog posts ordered by published date (newest first)."""
        return BlogPostPage.objects.live().descendant_of(self).order_by('-published_date')
    
    def get_posts_by_category(self, category):
        """Get blog posts filtered by category."""
        return self.get_posts().filter(category=category)
    
    def get_context(self, request, *args, **kwargs):
        """Add pagination and category filtering to template context."""
        context = super().get_context(request, *args, **kwargs)
        
        # Get all posts or filter by category
        posts = self.get_posts()
        category_slug = request.GET.get('category')
        selected_category = None
        
        if category_slug:
            try:
                selected_category = Category.objects.get(slug=category_slug)
                posts = self.get_posts_by_category(selected_category)
            except Category.DoesNotExist:
                pass  # Ignore invalid category, show all posts
        
        # Pagination
        page_num = request.GET.get('page', 1)
        paginator = Paginator(posts, self.posts_per_page)
        
        try:
            paginated_posts = paginator.page(page_num)
        except PageNotAnInteger:
            paginated_posts = paginator.page(1)
        except EmptyPage:
            paginated_posts = paginator.page(paginator.num_pages)
        
        # Add to context
        context['posts'] = paginated_posts
        context['categories'] = Category.objects.all()
        context['selected_category'] = selected_category
        
        return context
```

### SEO Integration

Inherit from existing SEO mixins:
```python
from sum_core.seo.mixins import SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin

class BlogIndexPage(
    SeoFieldsMixin,
    OpenGraphMixin,
    BreadcrumbMixin,
    Page
):
    # ... rest of model
```

### Admin Configuration

Configure admin panels with appropriate grouping:
- **Content Tab:** title, intro, posts_per_page
- **SEO Tab:** Inherited from SEO mixins

## Implementation Tasks

- [ ] Update `core/sum_core/pages/blog.py` to add BlogIndexPage
- [ ] Import required modules (Page, RichTextField, Paginator, etc.)
- [ ] Inherit from existing SEO mixins
- [ ] Define model fields (intro, posts_per_page)
- [ ] Configure content_panels
- [ ] Set parent_page_types and subpage_types constraints
- [ ] Set max_count = 1 (single blog index per site)
- [ ] Implement `get_posts()` method
- [ ] Implement `get_posts_by_category(category)` method
- [ ] Implement `get_context()` with pagination and filtering
- [ ] Update `core/sum_core/pages/__init__.py` to export BlogIndexPage
- [ ] Create migration: `python manage.py makemigrations sum_core`
- [ ] Write unit tests in `tests/pages/test_blog_index_page.py`:
  - BlogIndexPage creation
  - get_posts() returns correct posts
  - get_posts_by_category() filters correctly
  - Pagination works
  - Category filtering via query param
  - Invalid category handled gracefully
  - Empty page edge cases
  - Parent/subpage constraints enforced

## Acceptance Criteria

- [ ] BlogIndexPage can be created in Wagtail admin
- [ ] Only one BlogIndexPage allowed per site
- [ ] Only BlogPostPage allowed as child
- [ ] get_posts() returns live posts ordered by date
- [ ] Pagination works correctly
- [ ] Category filtering via `?category=slug` works
- [ ] Invalid category gracefully shows all posts
- [ ] Empty and out-of-range page numbers handled
- [ ] SEO fields available in admin
- [ ] Migration runs cleanly
- [ ] Unit tests pass with ≥80% coverage
- [ ] `make lint` passes

## Testing Commands

```bash
# Run unit tests
pytest tests/pages/test_blog_index_page.py -v

# Check coverage
pytest tests/pages/test_blog_index_page.py --cov=core/sum_core/pages/blog --cov-report=term-missing

# Interactive testing
python core/sum_core/test_project/manage.py runserver
# Create BlogIndexPage at /blog/
# Verify pagination and filtering work (once BlogPostPage exists)

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(blog): add BlogIndexPage model with pagination

- Create BlogIndexPage Wagtail page type
- Implement pagination (configurable posts per page)
- Support category filtering via query parameter
- Integrate with existing SEO mixins
- Configure parent/child page constraints
- Add comprehensive unit tests and migration

Refs: BLOG.009"

git push origin feature/BLOG-009-blog-index-page

gh pr create \
  --base develop \
  --title "feat(blog): BlogIndexPage model with pagination" \
  --body "Implements BLOG.009 - Blog listing page with filtering.

## Changes
- BlogIndexPage Wagtail page model
- Pagination with configurable posts per page
- Category filtering via query param
- get_posts() and get_posts_by_category() methods
- SEO mixin integration
- Parent/child page constraints
- Unit tests and migration

## Testing
- ✅ Page creation works
- ✅ Pagination functions correctly
- ✅ Category filtering works
- ✅ Edge cases handled (invalid category, empty pages)
- ✅ Constraints enforced
- ✅ Lint checks pass

## Related
- Depends on: BLOG.005
- Blocks on: BLOG.012 (BlogIndexPage template)
- Works with: BLOG.011 (BlogPostPage)"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Address feedback, resolve conversations
```

## Notes for AI Agents

- BlogIndexPage should be **simple** - listing logic only
- Ensure `descendant_of(self)` used to get children (Wagtail pattern)
- Pagination should handle all edge cases (invalid page, empty, out of range)
- Category filtering is optional - default shows all posts
- Query param approach (`?category=slug`) is simpler than path-based routing
- SEO mixins should already exist - reuse them
- Template will be created in BLOG.012 - model only for now
- Consider adding category post counts to context (optional enhancement)
