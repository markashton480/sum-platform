# BLOG.010: BlogPostPage Model

**Phase:** 3 - Blog Models + Templates  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 10h  
**Dependencies:** BLOG.003, BLOG.005

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-010-blog-post-page
```

## Objective

Create the `BlogPostPage` Wagtail page model for individual blog articles. This model **must** include DynamicFormBlock in its StreamField to enable CTA placement within posts (critical constraint).

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:360-389`
- Wagtail Page Models: https://docs.wagtail.org/en/stable/topics/pages.html
- StreamField: https://docs.wagtail.org/en/stable/topics/streamfield.html
- Existing Pages: `core/sum_core/pages/`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **File:** `core/sum_core/pages/blog.py` (add to existing file)

### Model Definition

```python
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel
from django.db import models
from wagtail import blocks as wagtail_blocks

from sum_core.blocks import ALL_BLOCKS  # Includes DynamicFormBlock
from sum_core.seo.mixins import SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin


class BlogPostPage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """
    Individual blog post/article.
    
    URL: /blog/<slug>/
    Template: blog_post_page.html
    """
    
    # Core content
    category = models.ForeignKey(
        'pages.Category',
        on_delete=models.PROTECT,  # Don't delete categories with posts
        related_name='blog_posts',
        help_text="Blog post category"
    )
    published_date = models.DateTimeField(
        help_text="Date this post was published"
    )
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Featured image displayed at top of post"
    )
    excerpt = models.TextField(
        blank=True,
        max_length=500,
        help_text="Short excerpt for listings (auto-generated if blank)"
    )
    body = StreamField(
        ALL_BLOCKS,  # MUST include DynamicFormBlock for CTAs
        blank=False,
        use_json_field=True,
        help_text="Article content with optional form CTAs"
    )
    author_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Author name (optional - no multi-author system)"
    )
    reading_time = models.IntegerField(
        editable=False,
        default=1,
        help_text="Estimated reading time in minutes (auto-calculated)"
    )
    
    # Panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('category'),
        FieldPanel('published_date'),
        FieldPanel('featured_image'),
        FieldPanel('excerpt'),
        FieldPanel('author_name'),
        FieldPanel('body'),
    ]
    
    # Page type constraints
    parent_page_types = ['pages.BlogIndexPage']
    subpage_types = []  # Blog posts have no children
    
    def save(self, *args, **kwargs):
        """Auto-calculate reading time before saving."""
        self.reading_time = self.calculate_reading_time()
        super().save(*args, **kwargs)
    
    def calculate_reading_time(self):
        """
        Calculate reading time based on word count.
        
        Assumes 200 words per minute average reading speed.
        Minimum 1 minute.
        """
        word_count = 0
        
        # Extract text from StreamField blocks
        for block in self.body:
            if hasattr(block.value, '__str__'):
                # Simple word count from string representation
                word_count += len(str(block.value).split())
        
        # Calculate minutes (minimum 1)
        minutes = max(1, round(word_count / 200))
        return minutes
    
    def get_excerpt(self):
        """
        Return excerpt if provided, otherwise generate from body.
        
        Strips HTML and truncates to ~150 characters.
        """
        if self.excerpt:
            return self.excerpt
        
        # Generate from first text block
        for block in self.body:
            if block.block_type in ['paragraph', 'text', 'rich_text']:
                text = str(block.value)
                # Strip HTML tags (simple approach)
                import re
                text = re.sub(r'<[^>]+>', '', text)
                # Truncate to 150 chars
                if len(text) > 150:
                    return text[:147] + '...'
                return text
        
        return ''
    
    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
```

### Admin Panel Organization

Organize panels for better UX:

```python
from wagtail.admin.panels import MultiFieldPanel, TabbedInterface, ObjectList

# Override edit_handler for custom tab layout
edit_handler = TabbedInterface([
    ObjectList(content_panels, heading='Content'),
    ObjectList(Page.promote_panels + [
        MultiFieldPanel(
            [FieldPanel('reading_time', read_only=True)],
            heading='Metadata'
        )
    ], heading='Promote'),
    ObjectList(Page.settings_panels, heading='Settings'),
    # SEO tab from mixins
])
```

## Implementation Tasks

- [ ] Update `core/sum_core/pages/blog.py` to add BlogPostPage
- [ ] Import required modules and mixins
- [ ] Inherit from SEO mixins
- [ ] Define all model fields (category, published_date, featured_image, etc.)
- [ ] Configure body StreamField with ALL_BLOCKS (includes DynamicFormBlock)
- [ ] Set parent_page_types = ['pages.BlogIndexPage']
- [ ] Implement `save()` method with reading time calculation
- [ ] Implement `calculate_reading_time()` method (200 WPM)
- [ ] Implement `get_excerpt()` method with fallback logic
- [ ] Configure content_panels
- [ ] Optionally configure custom edit_handler with tabs
- [ ] Update `core/sum_core/pages/__init__.py` to export BlogPostPage
- [ ] Create migration: `python manage.py makemigrations sum_core`
- [ ] Write unit tests in `tests/pages/test_blog_post_page.py`:
  - BlogPostPage creation
  - Reading time calculation (various word counts)
  - Excerpt fallback logic
  - Category relationship
  - Featured image handling (nullable)
  - Parent page constraints
  - StreamField includes DynamicFormBlock
  - Auto-save reading time

## Acceptance Criteria

- [ ] BlogPostPage can be created as child of BlogIndexPage only
- [ ] All fields editable in admin
- [ ] body StreamField includes DynamicFormBlock option
- [ ] Reading time auto-calculates on save
- [ ] Excerpt fallback generates from body if blank
- [ ] Category required (protects from deletion)
- [ ] Featured image optional
- [ ] Author name optional
- [ ] SEO fields available
- [ ] Migration runs cleanly
- [ ] Unit tests pass with ≥80% coverage
- [ ] `make lint` passes

## Testing Commands

```bash
# Run unit tests
pytest tests/pages/test_blog_post_page.py -v

# Check coverage
pytest tests/pages/test_blog_post_page.py --cov=core/sum_core/pages/blog --cov-report=term-missing

# Interactive testing
python core/sum_core/test_project/manage.py runserver
# Create BlogIndexPage
# Create BlogPostPage as child
# Add DynamicFormBlock to body
# Verify reading time calculates
# Test excerpt generation

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(blog): add BlogPostPage model with dynamic forms support

- Create BlogPostPage Wagtail page type
- Include DynamicFormBlock in body StreamField (critical for CTAs)
- Auto-calculate reading time (200 WPM)
- Auto-generate excerpt from body if not provided
- Support category, featured image, author
- Integrate with SEO mixins
- Configure parent page constraints
- Add comprehensive unit tests and migration

Refs: BLOG.010"

git push origin feature/BLOG-010-blog-post-page

gh pr create \
  --base develop \
  --title "feat(blog): BlogPostPage model with dynamic forms support" \
  --body "Implements BLOG.010 - Blog article page type with CTA support.

## Changes
- BlogPostPage Wagtail page model
- StreamField with DynamicFormBlock for CTAs (**critical constraint**)
- Auto-calculated reading time (200 WPM)
- Auto-generated excerpt fallback
- Category, featured image, author support
- SEO mixin integration
- Parent page constraints
- Unit tests and migration

## Testing
- ✅ Page creation works
- ✅ DynamicFormBlock available in body
- ✅ Reading time calculates correctly
- ✅ Excerpt generation works
- ✅ Category relationship enforced
- ✅ Constraints enforced
- ✅ Lint checks pass

## Related
- Depends on: BLOG.003 (DynamicFormBlock), BLOG.005 (Category)
- Blocks on: BLOG.013 (BlogPostPage template)
- **Critical path** - enables blog with form CTAs"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Thoroughly test DynamicFormBlock integration
```

## Notes for AI Agents

- **Critical path** task - BlogPostPage MUST support DynamicFormBlock
- This is the key integration point for "Blog uses dynamic forms for CTAs"
- Reading time calculation should handle all StreamField block types
- Excerpt generation is a fallback - prefer manual excerpts
- Category uses PROTECT to prevent accidental deletion
- Featured image is optional (nullable)
- No multi-author system - simple author_name string field
- Consider adding JSON-LD structured data for articles (in template, not model)
- Template will be created in BLOG.013 - model only for now
