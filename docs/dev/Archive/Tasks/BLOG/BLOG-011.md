# BLOG.011: Blog Templates (Theme A)

**Phase:** 3 - Blog Models + Templates  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 18h  
**Dependencies:** BLOG.009, BLOG.010

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-011-blog-templates
```

## Objective

Create complete, production-ready blog templates for theme_a, including the blog index (listing) page and individual blog post pages. Templates must match Sage & Stone UI contract and be fully responsive.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:390-450`
- Wagtail Templates: https://docs.wagtail.org/en/stable/topics/writing_templates.html
- Existing Templates: `themes/theme_a/templates/sum_core/pages/`
- Tailwind CSS: https://tailwindcss.com/
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Templates to Create

1. **blog_index_page.html** - Blog listing/archive
2. **blog_post_page.html** - Individual blog article
3. **_post_card.html** - Reusable post card component
4. **_pagination.html** - Pagination controls
5. **_category_filter.html** - Category filter UI

### Location
- **Path:** `themes/theme_a/templates/sum_core/pages/`
- **Includes:** `themes/theme_a/templates/sum_core/includes/`

### Template 1: blog_index_page.html

```django
{% extends "base.html" %}
{% load wagtailcore_tags wagtailimages_tags %}

{% block content %}
<div class="blog-index-page">
    
    {# Hero/Intro Section #}
    {% if page.intro %}
    <section class="blog-intro py-12 md:py-16">
        <div class="container mx-auto px-4">
            <h1 class="text-4xl md:text-5xl font-bold mb-4">{{ page.title }}</h1>
            <div class="prose prose-lg">
                {{ page.intro|richtext }}
            </div>
        </div>
    </section>
    {% endif %}
    
    {# Category Filter #}
    {% include 'sum_core/includes/_category_filter.html' %}
    
    {# Posts Grid #}
    <section class="blog-posts py-12">
        <div class="container mx-auto px-4">
            {% if posts %}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {% for post in posts %}
                    {% include 'sum_core/includes/_post_card.html' with post=post %}
                {% endfor %}
            </div>
            {% else %}
            <p class="text-center text-gray-600 py-12">No blog posts found.</p>
            {% endif %}
            
            {# Pagination #}
            {% if posts.has_other_pages %}
                {% include 'sum_core/includes/_pagination.html' with page_obj=posts %}
            {% endif %}
        </div>
    </section>
    
</div>
{% endblock %}
```

### Template 2: blog_post_page.html

```django
{% extends "base.html" %}
{% load wagtailcore_tags wagtailimages_tags %}

{% block content %}
<article class="blog-post-page">
    
    {# Featured Image / Hero #}
    {% if page.featured_image %}
    <div class="featured-image mb-8">
        {% image page.featured_image fill-1200x600 as hero_img %}
        <img 
            src="{{ hero_img.url }}" 
            alt="{{ page.title }}"
            class="w-full h-64 md:h-96 object-cover rounded-lg"
        />
    </div>
    {% endif %}
    
    {# Article Header #}
    <header class="article-header mb-8">
        <div class="container mx-auto px-4 max-w-4xl">
            
            {# Category Badge #}
            <a 
                href="{% pageurl page.get_parent %}?category={{ page.category.slug }}"
                class="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-4 hover:bg-primary-200 transition"
            >
                {{ page.category.name }}
            </a>
            
            {# Title #}
            <h1 class="text-4xl md:text-5xl font-bold mb-4">{{ page.title }}</h1>
            
            {# Meta #}
            <div class="flex flex-wrap items-center gap-4 text-gray-600 text-sm">
                <time datetime="{{ page.published_date|date:'c' }}">
                    {{ page.published_date|date:"F j, Y" }}
                </time>
                <span>•</span>
                <span>{{ page.reading_time }} min read</span>
                {% if page.author_name %}
                <span>•</span>
                <span>By {{ page.author_name }}</span>
                {% endif %}
            </div>
        </div>
    </header>
    
    {# Article Body (StreamField) #}
    <div class="article-body">
        <div class="container mx-auto px-4 max-w-4xl">
            <div class="prose prose-lg max-w-none">
                {% include_block page.body %}
            </div>
        </div>
    </div>
    
    {# Article Footer (optional: share buttons, related posts, etc.) #}
    <footer class="article-footer mt-12 pt-8 border-t border-gray-200">
        <div class="container mx-auto px-4 max-w-4xl">
            <a 
                href="{% pageurl page.get_parent %}" 
                class="text-primary-600 hover:text-primary-700 font-medium"
            >
                ← Back to all posts
            </a>
        </div>
    </footer>
    
</article>
{% endblock %}

{# Structured Data for SEO #}
{% block extra_head %}
{{ block.super }}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ page.title }}",
  "datePublished": "{{ page.published_date|date:'c' }}",
  "dateModified": "{{ page.last_published_at|date:'c' }}",
  {% if page.featured_image %}
  "image": "{{ page.featured_image.file.url }}",
  {% endif %}
  {% if page.author_name %}
  "author": {
    "@type": "Person",
    "name": "{{ page.author_name }}"
  },
  {% endif %}
  "publisher": {
    "@type": "Organization",
    "name": "{{ settings.site.site_name }}"
  }
}
</script>
{% endblock %}
```

### Template 3: _post_card.html

```django
{% load wagtailcore_tags wagtailimages_tags %}

<article class="post-card bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
    
    {# Featured Image #}
    {% if post.featured_image %}
    <a href="{% pageurl post %}" class="block">
        {% image post.featured_image fill-600x400 as card_img %}
        <img 
            src="{{ card_img.url }}" 
            alt="{{ post.title }}"
            class="w-full h-48 object-cover"
        />
    </a>
    {% endif %}
    
    {# Card Content #}
    <div class="p-6">
        
        {# Category #}
        <a 
            href="{% pageurl post.get_parent %}?category={{ post.category.slug }}"
            class="inline-block px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-medium mb-3 hover:bg-primary-200 transition"
        >
            {{ post.category.name }}
        </a>
        
        {# Title #}
        <h3 class="text-xl font-bold mb-2">
            <a href="{% pageurl post %}" class="hover:text-primary-600 transition">
                {{ post.title }}
            </a>
        </h3>
        
        {# Excerpt #}
        <p class="text-gray-600 mb-4 line-clamp-3">
            {{ post.get_excerpt }}
        </p>
        
        {# Meta #}
        <div class="flex items-center justify-between text-sm text-gray-500">
            <time datetime="{{ post.published_date|date:'c' }}">
                {{ post.published_date|date:"M j, Y" }}
            </time>
            <span>{{ post.reading_time }} min read</span>
        </div>
    </div>
    
</article>
```

### Template 4: _pagination.html

```django
{% if page_obj.has_other_pages %}
<nav class="pagination flex justify-center items-center gap-2 mt-12" aria-label="Pagination">
    
    {# Previous Page #}
    {% if page_obj.has_previous %}
    <a 
        href="?page={{ page_obj.previous_page_number }}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}"
        class="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 transition"
    >
        ← Previous
    </a>
    {% else %}
    <span class="px-4 py-2 bg-gray-100 border border-gray-200 rounded text-gray-400 cursor-not-allowed">
        ← Previous
    </span>
    {% endif %}
    
    {# Page Numbers #}
    <div class="flex gap-1">
        {% for num in page_obj.paginator.page_range %}
            {% if page_obj.number == num %}
            <span class="px-4 py-2 bg-primary-600 text-white rounded font-medium">
                {{ num }}
            </span>
            {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
            <a 
                href="?page={{ num }}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}"
                class="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 transition"
            >
                {{ num }}
            </a>
            {% endif %}
        {% endfor %}
    </div>
    
    {# Next Page #}
    {% if page_obj.has_next %}
    <a 
        href="?page={{ page_obj.next_page_number }}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}"
        class="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 transition"
    >
        Next →
    </a>
    {% else %}
    <span class="px-4 py-2 bg-gray-100 border border-gray-200 rounded text-gray-400 cursor-not-allowed">
        Next →
    </span>
    {% endif %}
    
</nav>
{% endif %}
```

### Template 5: _category_filter.html

```django
{% if categories %}
<div class="category-filter py-6 border-b border-gray-200">
    <div class="container mx-auto px-4">
        <div class="flex flex-wrap items-center gap-3">
            <span class="text-sm font-medium text-gray-700">Filter by category:</span>
            
            {# All Posts (clear filter) #}
            <a 
                href="{% pageurl page %}"
                class="px-4 py-2 rounded-full text-sm font-medium transition {% if not selected_category %}bg-primary-600 text-white{% else %}bg-gray-100 text-gray-700 hover:bg-gray-200{% endif %}"
            >
                All Posts
            </a>
            
            {# Category Tags #}
            {% for category in categories %}
            <a 
                href="?category={{ category.slug }}"
                class="px-4 py-2 rounded-full text-sm font-medium transition {% if selected_category == category %}bg-primary-600 text-white{% else %}bg-gray-100 text-gray-700 hover:bg-gray-200{% endif %}"
            >
                {{ category.name }}
            </a>
            {% endfor %}
        </div>
    </div>
</div>
{% endif %}
```

### Tailwind Styling Guidelines

- Use existing theme_a color palette (primary, secondary, gray)
- Responsive design: mobile-first approach
- Hover states on interactive elements
- Focus states for accessibility
- Card shadows and transitions for depth
- Prose plugin for article typography
- Line-clamp utility for excerpt truncation (may need to add to Tailwind config)

## Implementation Tasks

- [ ] Create `blog_index_page.html` with hero, filters, grid, pagination
- [ ] Create `blog_post_page.html` with header, meta, StreamField body
- [ ] Create `_post_card.html` reusable component
- [ ] Create `_pagination.html` with prev/next/numbers
- [ ] Create `_category_filter.html` with tag-style filters
- [ ] Add JSON-LD structured data to blog_post_page.html
- [ ] Ensure all templates use semantic HTML (article, nav, time, etc.)
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Test with no featured image (graceful handling)
- [ ] Test with long titles and excerpts (overflow handling)
- [ ] Test category filter preserves pagination
- [ ] Test pagination preserves category filter
- [ ] Verify SEO tags render from mixins
- [ ] Verify StreamField blocks render correctly
- [ ] Test dark mode if theme supports it

## Acceptance Criteria

- [ ] Blog index page renders with post grid
- [ ] Blog post page renders with all content
- [ ] Post cards display correctly in grid
- [ ] Pagination works and preserves filters
- [ ] Category filter works and updates URL
- [ ] Templates fully responsive on all screen sizes
- [ ] Images use Wagtail image renditions (optimized)
- [ ] Semantic HTML for accessibility
- [ ] JSON-LD structured data present
- [ ] No featured image handled gracefully
- [ ] Long content doesn't break layout
- [ ] Hover states smooth and consistent
- [ ] Templates match Sage & Stone UI aesthetic
- [ ] `make lint` passes (if templates are linted)

## Testing Commands

```bash
# Start development server
python core/sum_core/test_project/manage.py runserver

# Create test data:
# 1. Create BlogIndexPage at /blog/
# 2. Create 3+ categories
# 3. Create 15+ BlogPostPage instances (for pagination)
# 4. Add featured images, vary excerpt presence
# 5. Add DynamicFormBlock to some posts

# Test in browser:
# - /blog/ (index with all posts)
# - /blog/?category=<slug> (filtered)
# - /blog/?page=2 (pagination)
# - /blog/<post-slug>/ (individual post)
# - Resize browser (responsive)
# - Test with missing featured images

# Lighthouse audit
# lighthouse http://localhost:8000/blog/ --view

# Run HTML validation (optional)
# Use W3C validator or similar
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(blog): add blog templates for theme_a

- Create blog_index_page.html with grid layout
- Create blog_post_page.html with article structure
- Add reusable _post_card.html component
- Add _pagination.html with page numbers
- Add _category_filter.html with tag-style UI
- Include JSON-LD structured data for SEO
- Fully responsive with Tailwind CSS
- Semantic HTML for accessibility
- Optimized image renditions

Refs: BLOG.011"

git push origin feature/BLOG-011-blog-templates

gh pr create \
  --base develop \
  --title "feat(blog): Blog templates for theme_a" \
  --body "Implements BLOG.011 - Complete blog templates.

## Changes
- blog_index_page.html (listing with filters)
- blog_post_page.html (article with StreamField)
- _post_card.html (reusable component)
- _pagination.html (with page numbers)
- _category_filter.html (tag-style filtering)
- JSON-LD structured data
- Responsive Tailwind styling
- Semantic HTML markup

## Testing
- ✅ Blog index renders correctly
- ✅ Blog posts render correctly
- ✅ Pagination works
- ✅ Category filtering works
- ✅ Fully responsive
- ✅ Images optimized
- ✅ Structured data present
- ✅ Accessible markup

## Related
- Depends on: BLOG.009, BLOG.010
- **Critical path** - completes blog UI
- Ready for Lighthouse testing (Phase 4)"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Test thoroughly in browser, run Lighthouse audit
```

## Notes for AI Agents

- **Critical path** task - completes the blog feature frontend
- Match existing theme_a styling patterns exactly
- Use Wagtail image renditions (fill-WIDTHxHEIGHT) for optimization
- Ensure category filter preserves other query params
- Pagination should handle edge cases (no posts, single page)
- JSON-LD structured data improves SEO significantly
- Test with real content of varying lengths
- Consider adding "Back to top" button for long posts (optional)
- Verify DynamicFormBlock renders correctly in post body
- Ready for Lighthouse audit in Phase 4
