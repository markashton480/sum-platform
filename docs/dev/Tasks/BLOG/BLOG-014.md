# BLOG.014: Performance Optimization

**Phase:** 4 - Integration + Polish  
**Priority:** P1  
**Estimated Hours:** 8h  
**Dependencies:** BLOG.009, BLOG.011

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-014-performance-optimization
```

## Objective

Optimize blog listing and dynamic forms for performance. Target: Lighthouse score ≥90 across all metrics, form submission latency <500ms p95, CSS bundle ≤100kb compressed.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:503-523`
- Django Query Optimization: https://docs.djangoproject.com/en/stable/topics/db/optimization/
- Wagtail Performance: https://docs.wagtail.org/en/stable/advanced_topics/performance.html
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Optimization 1: Blog Listing Performance

**Location:** `core/sum_core/pages/blog.py`

Optimize queries with select_related and prefetch_related:

```python
class BlogIndexPage(Page):
    # ... existing code ...
    
    def get_posts(self):
        """Get all live blog posts with optimized queries."""
        return (
            BlogPostPage.objects.live()
            .descendant_of(self)
            .select_related('category')  # Avoid N+1 on category
            .prefetch_related('featured_image')  # Optimize image fetching
            .order_by('-published_date')
        )
```

Add caching for category counts (optional):

```python
from django.core.cache import cache

def get_context(self, request, *args, **kwargs):
    context = super().get_context(request, *args, **kwargs)
    
    # ... existing pagination code ...
    
    # Cache category list (changes infrequently)
    categories = cache.get('blog_categories')
    if categories is None:
        categories = Category.objects.all()
        cache.set('blog_categories', categories, 3600)  # 1 hour
    
    context['categories'] = categories
    return context
```

### Optimization 2: Dynamic Form Performance

**Location:** `core/sum_core/forms/dynamic.py`

Cache generated form classes:

```python
from django.core.cache import cache

class DynamicFormGenerator:
    def __init__(self, form_definition):
        self.form_definition = form_definition
        self._cache_key = f'form_class_{form_definition.id}_{form_definition.updated_at.timestamp()}'
    
    def generate_form_class(self):
        """Generate Django Form class with caching."""
        # Check cache first
        FormClass = cache.get(self._cache_key)
        if FormClass is not None:
            return FormClass
        
        # Generate form class
        FormClass = self._do_generate_form_class()
        
        # Cache for 1 hour (or until FormDefinition updated)
        cache.set(self._cache_key, FormClass, 3600)
        
        return FormClass
    
    def _do_generate_form_class(self):
        """Actual form class generation logic."""
        # ... existing generation code ...
```

Cache FormDefinition instances:

```python
# In form submission handler (views.py)
def _handle_dynamic_form_submission(request, form_def_id):
    cache_key = f'form_def_{form_def_id}'
    form_def = cache.get(cache_key)
    
    if form_def is None:
        form_def = FormDefinition.objects.select_related('site').get(id=form_def_id)
        cache.set(cache_key, form_def, 1800)  # 30 minutes
    
    # ... rest of submission logic ...
```

### Optimization 3: Template Optimization

**Location:** `themes/theme_a/templates/sum_core/pages/`

Minimize template includes and optimize image loading:

```django
{# In blog_index_page.html #}
{% load wagtailcore_tags wagtailimages_tags %}

{# Use optimized image renditions #}
{% for post in posts %}
    {% image post.featured_image fill-600x400 format-webp as card_img %}
    <img 
        src="{{ card_img.url }}" 
        alt="{{ post.title }}"
        loading="lazy"  {# Lazy load images #}
        class="w-full h-48 object-cover"
    />
{% endfor %}
```

Lazy load images below the fold:

```django
{# Add loading="lazy" to all images except first 3 #}
{% for post in posts %}
    {% if forloop.counter > 3 %}
        {% image post.featured_image fill-600x400 as card_img %}
        <img src="{{ card_img.url }}" loading="lazy" alt="{{ post.title }}" />
    {% else %}
        {% image post.featured_image fill-600x400 as card_img %}
        <img src="{{ card_img.url }}" alt="{{ post.title }}" />
    {% endif %}
{% endfor %}
```

### Optimization 4: Lighthouse Audit and Fixes

Run Lighthouse and address issues:

1. **Performance**
   - Optimize images (WebP format, appropriate sizes)
   - Minimize CSS/JS
   - Lazy load below-fold content
   - Use CDN for static assets (if available)

2. **Accessibility**
   - Add ARIA labels
   - Ensure color contrast
   - Keyboard navigation

3. **Best Practices**
   - HTTPS everywhere
   - No console errors
   - Modern image formats

4. **SEO**
   - Meta tags present (via SEO mixins)
   - Semantic HTML
   - Proper heading hierarchy

## Implementation Tasks

- [ ] Add `select_related('category')` to BlogIndexPage.get_posts()
- [ ] Add `prefetch_related('featured_image')` to get_posts()
- [ ] Implement category caching (optional, 1 hour TTL)
- [ ] Add form class caching to DynamicFormGenerator
- [ ] Add FormDefinition caching in submission handler
- [ ] Add `loading="lazy"` to below-fold images
- [ ] Convert images to WebP format (via Wagtail renditions)
- [ ] Minimize template includes where possible
- [ ] Run Lighthouse audit on blog index page
- [ ] Run Lighthouse audit on blog post page
- [ ] Address Lighthouse recommendations
- [ ] Measure form submission latency (target <500ms p95)
- [ ] Check CSS bundle size (target ≤100kb compressed)
- [ ] Write performance tests in `tests/performance/` (optional):
  - Query count for blog listing
  - Form generation time
  - Caching effectiveness

## Acceptance Criteria

- [ ] Blog listing uses select_related/prefetch_related
- [ ] No N+1 query issues on blog pages
- [ ] Form classes cached and reused
- [ ] FormDefinitions cached in submission handler
- [ ] Images lazy load below the fold
- [ ] WebP format used for images
- [ ] Lighthouse score ≥90 (Performance, Accessibility, Best Practices, SEO)
- [ ] Form submission latency <500ms p95
- [ ] CSS bundle ≤100kb compressed
- [ ] No console errors on blog pages
- [ ] All optimizations maintain functionality
- [ ] `make lint` passes

## Testing Commands

```bash
# Run Lighthouse audit
lighthouse http://localhost:8000/blog/ --view
lighthouse http://localhost:8000/blog/sample-post/ --view

# Check query counts (Django Debug Toolbar or)
python core/sum_core/test_project/manage.py shell
>>> from django.test.utils import override_settings
>>> from django.db import connection
>>> from django.test.client import Client
>>> client = Client()
>>> with override_settings(DEBUG=True):
...     response = client.get('/blog/')
...     print(len(connection.queries), 'queries')

# Measure form submission time
curl -w "@curl-format.txt" -X POST http://localhost:8000/forms/submit/ \
  -d "form_definition_id=1&email=test@example.com&name=Test"

# Check CSS bundle size
ls -lh themes/theme_a/static/css/dist/ | grep .css

# Run linting
make lint

# Load testing (optional)
ab -n 100 -c 10 http://localhost:8000/blog/
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "perf: optimize blog and forms performance

- Add select_related/prefetch_related to blog queries
- Cache FormDefinition instances and generated form classes
- Lazy load below-fold images
- Use WebP format for image renditions
- Minimize template includes
- Address Lighthouse audit recommendations
- Achieve Lighthouse score ≥90 across all metrics
- Form submission latency <500ms p95

Refs: BLOG.014"

git push origin feature/BLOG-014-performance-optimization

gh pr create \
  --base develop \
  --title "perf: Blog and forms performance optimization" \
  --body "Implements BLOG.014 - Performance optimization.

## Changes
- Query optimization with select_related/prefetch_related
- Form class and FormDefinition caching
- Image lazy loading
- WebP image format
- Lighthouse audit fixes
- CSS/JS minimization

## Metrics
- ✅ Lighthouse score ≥90 (all metrics)
- ✅ Form submission <500ms p95
- ✅ CSS bundle ≤100kb compressed
- ✅ No N+1 queries
- ✅ Images optimized

## Testing
- ✅ Lighthouse audits pass
- ✅ Query counts optimized
- ✅ Load testing successful
- ✅ Functionality maintained
- ✅ Lint checks pass

## Related
- Depends on: BLOG.009, BLOG.011
- Critical for production readiness"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Run Lighthouse, verify metrics, address feedback
```

## Notes for AI Agents

- **Critical** for production - performance directly impacts user experience
- Start with Lighthouse audit to identify specific issues
- Django Debug Toolbar helpful for identifying N+1 queries
- Cache invalidation key: include `updated_at` timestamp in cache key
- Be careful with caching - ensure cache invalidates on form edits
- WebP format provides significant size savings with minimal quality loss
- Lazy loading images below fold dramatically improves initial load time
- Test with realistic data volumes (50+ blog posts, complex forms)
- Consider query optimization before adding caching (premature optimization)
- Measure before and after to validate improvements
