# Implementation Plan: Blog v1 + Dynamic Forms v1

**Project:** SUM Platform Post-MVP Features  
**Version:** 1.0  
**Date:** December 23, 2025  
**Status:** Planning  
**Features:** Blog v1 (First Vertical Slice) + Dynamic Forms v1 (Enhanced Scope)

---

## Executive Summary

This plan covers the implementation of two interlinked features:

1. **Blog v1** — The first vertical slice exercising the full templating + theme system with minimal business-critical risk
2. **Dynamic Forms v1** — A flexible form builder system that enables rapid iteration on lead capture forms

These features are intentionally coupled: Blog CTAs must use DynamicFormBlock (selecting FormDefinition), preventing form fragmentation and maintaining consistency across all lead capture touchpoints.

### Success Criteria

| Metric | Target |
|--------|--------|
| Lighthouse Score | ≥90 across all metrics |
| Test Coverage (new code) | ≥80% |
| CSS Bundle Size | ≤100kb compressed |
| Form Submission Latency | <500ms p95 |
| Zero Lost Leads | Maintained |

---

## Feature Dependency Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        IMPLEMENTATION ORDER                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: Dynamic Forms Foundation                                   │
│  ┌──────────────────┐                                               │
│  │ FormDefinition   │ ──► Wagtail Snippet (site-scoped)             │
│  │ Model            │                                                │
│  └────────┬─────────┘                                               │
│           │                                                          │
│           ▼                                                          │
│  ┌──────────────────┐     ┌──────────────────┐                      │
│  │ Field Type       │ ◄──►│ DynamicFormBlock │                      │
│  │ Blocks           │     │                  │                      │
│  └────────┬─────────┘     └────────┬─────────┘                      │
│           │                        │                                 │
│           ▼                        ▼                                 │
│  Phase 2: Forms Rendering + Submission                               │
│  ┌──────────────────────────────────────────┐                       │
│  │ Runtime Django Form Generation           │                       │
│  │ POST /forms/submit/ enhancement          │                       │
│  │ Lead model integration (no schema change)│                       │
│  └────────────────────┬─────────────────────┘                       │
│                       │                                              │
│                       ▼                                              │
│  Phase 3: Blog Models + Templates                                    │
│  ┌──────────────────┐     ┌──────────────────┐                      │
│  │ BlogIndexPage    │ ◄──►│ BlogPostPage     │                      │
│  │ (listing)        │     │ (article)        │                      │
│  └────────┬─────────┘     └────────┬─────────┘                      │
│           │                        │                                 │
│           │    ┌───────────────────┘                                 │
│           ▼    ▼                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │ Blog Templates (theme_a)                 │                       │
│  │ Uses DynamicFormBlock for CTAs ◄─────────┼── CRITICAL CONSTRAINT │
│  └──────────────────────────────────────────┘                       │
│                                                                      │
│  Phase 4: Integration + Polish                                       │
│  ┌──────────────────────────────────────────┐                       │
│  │ Clone/Duplicate, Active Toggle           │                       │
│  │ Email notifications, Webhooks            │                       │
│  │ Admin UI enhancements                    │                       │
│  │ Performance optimization                 │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Dynamic Forms Foundation

**Duration:** ~3-4 days  
**Goal:** Establish FormDefinition model and field type blocks

### Task 1.1: FormDefinition Model

**Location:** `core/sum_core/forms/models.py`

```python
# File: core/sum_core/forms/models.py
# Purpose: FormDefinition Wagtail Snippet for dynamic form configuration
# Dependencies: wagtail.snippets, wagtail.fields (StreamField)
# Dependents: DynamicFormBlock, form submission handler
```

**Subtasks:**

- [ ] **1.1.1** Create `FormDefinition` model as Wagtail Snippet
  - Name (CharField, admin reference)
  - Slug (SlugField, unique per site)
  - Form fields (StreamField of field blocks)
  - Success message (TextField)
  - Active toggle (BooleanField, default=True)
  - Created/modified timestamps (auto)
  - Site scope (ForeignKey to wagtail Site)

- [ ] **1.1.2** Create `FormSubmissionSettings` (embedded in FormDefinition)
  - Email notification enabled (BooleanField)
  - Notification recipient emails (TextField, comma-separated)
  - Auto-reply enabled (BooleanField)
  - Auto-reply subject/body (CharField, TextField)
  - Webhook enabled (BooleanField)
  - Webhook URL (URLField)

- [ ] **1.1.3** Register in Wagtail admin with search and filtering
- [ ] **1.1.4** Create migration
- [ ] **1.1.5** Write unit tests for model validation

### Task 1.2: Field Type Blocks

**Location:** `core/sum_core/forms/fields.py` (new file)

```python
# File: core/sum_core/forms/fields.py
# Purpose: StreamField blocks for form field definitions
# Dependencies: wagtail.blocks
# Dependents: FormDefinition model
```

**Subtasks:**

- [ ] **1.2.1** Create base `FormFieldBlock` with common properties
  - Field name (slug)
  - Label
  - Help text
  - Required toggle
  - CSS class (optional)

- [ ] **1.2.2** Implement field type blocks:
  - `TextInputBlock` (single line, max_length)
  - `EmailInputBlock` (with validation pattern)
  - `PhoneInputBlock` (optional formatting mask)
  - `TextareaBlock` (multi-line, rows config)
  - `SelectBlock` (choices as child blocks)
  - `CheckboxBlock` (single checkbox)
  - `CheckboxGroupBlock` (multiple choices)
  - `RadioButtonsBlock` (single choice from options)
  - `FileUploadBlock` (allowed extensions, max size)

- [ ] **1.2.3** Implement layout blocks:
  - `SectionHeadingBlock` (visual organization)
  - `HelpTextBlock` (instructions/descriptions)

- [ ] **1.2.4** Write unit tests for each field block

### Task 1.3: DynamicFormBlock

**Location:** `core/sum_core/blocks/forms.py`

```python
# File: core/sum_core/blocks/forms.py
# Purpose: StreamField block for embedding dynamic forms in pages
# Dependencies: sum_core.forms.models.FormDefinition
# Dependents: Page StreamFields (StandardPage, BlogPostPage, etc.)
```

**Subtasks:**

- [ ] **1.3.1** Create `DynamicFormBlock` StructBlock
  - Form selector (SnippetChooserBlock for FormDefinition)
  - Presentation style (ChoiceBlock: inline, modal, sidebar)
  - CTA button text override (optional)
  - Success redirect URL (optional, defaults to same page with message)

- [ ] **1.3.2** Add DynamicFormBlock to existing page StreamFields
  - Update `sum_core/blocks/__init__.py`
  - Add to StandardPage.body available blocks
  - Add to ServicePage.body available blocks

- [ ] **1.3.3** Write unit tests for block configuration

---

## Phase 2: Forms Rendering + Submission

**Duration:** ~3-4 days  
**Goal:** Runtime form generation and lead capture integration

### Task 2.1: Runtime Django Form Generation

**Location:** `core/sum_core/forms/dynamic.py` (new file)

```python
# File: core/sum_core/forms/dynamic.py
# Purpose: Generate Django Form classes from FormDefinition at runtime
# Dependencies: django.forms, FormDefinition
# Dependents: Form rendering templates, submission handler
```

**Subtasks:**

- [ ] **2.1.1** Create `DynamicFormGenerator` class
  - `generate_form_class(form_definition)` → Django Form class
  - Field type mapping (FormFieldBlock → Django field)
  - Validation rules preservation

- [ ] **2.1.2** Implement field rendering
  - Each field type → appropriate Django widget
  - Preserve help text, required, CSS classes
  - Handle file uploads correctly

- [ ] **2.1.3** Add form-level validation
  - Required field enforcement
  - Email format validation
  - File size/type validation

- [ ] **2.1.4** Write unit tests for form generation

### Task 2.2: Form Templates

**Location:** `themes/theme_a/templates/sum_core/blocks/dynamic_form_block.html`

**Subtasks:**

- [ ] **2.2.1** Create base dynamic form template
  - Renders generated Django form
  - Includes honeypot field (spam protection)
  - Includes timing token (bot detection)
  - CSRF token integration

- [ ] **2.2.2** Create presentation variants
  - Inline (default, renders in place)
  - Modal (button trigger, overlay form)
  - Sidebar (fixed position, slide-in)

- [ ] **2.2.3** Style forms with Tailwind (theme_a)
  - Field styling consistent with existing forms
  - Error state styling
  - Loading/submitting state

- [ ] **2.2.4** Add JavaScript for interactions
  - Modal open/close
  - Form submission (AJAX with fallback)
  - Success/error message display

### Task 2.3: Submission Handler Enhancement

**Location:** `core/sum_core/forms/views.py` (enhance existing)

**Subtasks:**

- [ ] **2.3.1** Extend `POST /forms/submit/` to handle dynamic forms
  - Detect form type (static vs dynamic)
  - Load FormDefinition
  - Validate against definition

- [ ] **2.3.2** Lead model integration (NO schema change)
  - Store form data in existing Lead.form_data JSONField
  - Preserve attribution (UTM, referrer, landing page)
  - Set Lead.form_type to FormDefinition.slug

- [ ] **2.3.3** Implement spam protection for dynamic forms
  - Honeypot field check
  - Timing validation
  - Rate limiting (existing per-IP)

- [ ] **2.3.4** Write integration tests for submission flow

### Task 2.4: Notifications + Webhooks

**Location:** `core/sum_core/forms/tasks.py` (new file)

```python
# File: core/sum_core/forms/tasks.py
# Purpose: Celery tasks for async form processing
# Dependencies: celery, sum_core.leads, sum_core.integrations
# Dependents: Form submission handler
```

**Subtasks:**

- [ ] **2.4.1** Create `send_form_notification` Celery task
  - Admin notification email (HTML + plain text)
  - Per-FormDefinition recipient list

- [ ] **2.4.2** Create `send_auto_reply` Celery task
  - Submitter acknowledgment email
  - Template with form data interpolation

- [ ] **2.4.3** Integrate with existing webhook system
  - Fire webhook with form data
  - Include FormDefinition metadata
  - Retry logic (existing infrastructure)

- [ ] **2.4.4** Write tests for async tasks (using Celery eager mode)

---

## Phase 3: Blog Models + Templates

**Duration:** ~4-5 days  
**Goal:** Blog infrastructure matching Sage & Stone UI contract

### Task 3.1: Category Snippet

**Location:** `core/sum_core/pages/blog.py` (new file)

```python
# File: core/sum_core/pages/blog.py
# Purpose: Blog page types and supporting models
# Dependencies: wagtail.models, sum_core.pages.base
# Dependents: Blog templates, sitemap
```

**Subtasks:**

- [ ] **3.1.1** Create `Category` Wagtail Snippet
  - Name (CharField)
  - Slug (SlugField, unique)
  - Description (TextField, optional)

- [ ] **3.1.2** Register in Wagtail admin
- [ ] **3.1.3** Create migration
- [ ] **3.1.4** Write unit tests

### Task 3.2: BlogIndexPage Model

**Location:** `core/sum_core/pages/blog.py`

**Subtasks:**

- [ ] **3.2.1** Create `BlogIndexPage` model
  - Inherits from Page + SEO mixins (SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin)
  - Intro text (RichTextField, optional)
  - Posts per page (IntegerField, default=10)

- [ ] **3.2.2** Implement listing methods
  - `get_posts()` → QuerySet of live BlogPostPages
  - `get_posts_by_category(category)` → filtered QuerySet
  - Pagination support via `Paginator`

- [ ] **3.2.3** Add `get_context()` for template data
  - Paginated posts
  - All categories (for filter UI)
  - Current category filter (if active)

- [ ] **3.2.4** Configure parent/child page rules
  - Can only be child of HomePage or root
  - Can only contain BlogPostPage children

- [ ] **3.2.5** Write unit tests for listing logic

### Task 3.3: BlogPostPage Model

**Location:** `core/sum_core/pages/blog.py`

**Subtasks:**

- [ ] **3.3.1** Create `BlogPostPage` model
  - Inherits from Page + SEO mixins
  - Category (ForeignKey to Category, single-level only)
  - Published date (DateTimeField)
  - Featured image (ForeignKey to wagtailimages.Image)
  - Excerpt (TextField, optional)
  - Body (StreamField with existing blocks + DynamicFormBlock)
  - Author name (CharField, optional - no multi-author system)

- [ ] **3.3.2** Implement reading time
  - Option A: Calculated property (word count / 200 wpm)
  - Option B: Auto-populated on save
  - Store as IntegerField (minutes)

- [ ] **3.3.3** Implement excerpt fallback
  - Use excerpt if provided
  - Otherwise, first N characters of body (stripped of HTML)

- [ ] **3.3.4** Configure Wagtail admin panels
  - Content tab (title, category, featured image, body)
  - Meta tab (published date, excerpt, reading time display)
  - SEO tab (existing SEO mixin panels)

- [ ] **3.3.5** Write unit tests for model methods

### Task 3.4: Blog Templates (Theme A)

**Reference Designs:**
- `theme_a/templates/sum_core/pages/blog_index_page.html`
- `theme_a/templates/sum_core/pages/blog_post_page.html`

**Subtasks:**

- [ ] **3.4.1** Create/update `blog_index_page.html`
  - Hero section (optional intro)
  - Category filter UI (labels/badges)
  - Post cards grid:
    - Featured image
    - Category label
    - Published date
    - Reading time
    - Title
    - Excerpt
  - Pagination controls

- [ ] **3.4.2** Create/update `blog_post_page.html`
  - Featured image/hero section
  - Article header:
    - Title
    - Published date
    - Category label
    - Reading time
  - Body content (StreamField rendering)
  - CTA placements (DynamicFormBlock positions)

- [ ] **3.4.3** Create supporting includes
  - `_post_card.html` (reusable card component)
  - `_pagination.html` (pagination controls)
  - `_category_filter.html` (category filter UI)

- [ ] **3.4.4** Style with Tailwind
  - Responsive grid layout
  - Card hover states
  - Typography hierarchy
  - Dark mode support (if theme supports)

- [ ] **3.4.5** Ensure SEO tags render correctly
  - Reuses existing SEO system (no new infrastructure)
  - Article-specific structured data (JSON-LD)

### Task 3.5: Blog URL Routing

**Location:** `core/sum_core/pages/blog.py`

**Subtasks:**

- [ ] **3.5.1** Verify Wagtail page routing works
  - BlogIndexPage at `/blog/`
  - BlogPostPage at `/blog/<slug>/`

- [ ] **3.5.2** Implement category filtering URL pattern
  - `/blog/?category=<slug>` (query param approach)
  - OR `/blog/category/<slug>/` (path approach - choose one)

- [ ] **3.5.3** Add to sitemap (automatic via existing system)

---

## Phase 4: Integration + Polish

**Duration:** ~3-4 days  
**Goal:** First-class capabilities, admin UX, performance

### Task 4.1: Form Management Features

**Location:** `core/sum_core/forms/` (various files)

**Subtasks:**

- [ ] **4.1.1** Implement Clone/Duplicate FormDefinition
  - Admin action: "Clone this form"
  - Copies all fields, settings
  - Appends "-copy" to name/slug

- [ ] **4.1.2** Implement Active toggle behavior
  - Inactive forms don't appear in DynamicFormBlock chooser
  - Inactive forms show warning if embedded
  - Preserves audit trail (don't delete, just deactivate)

- [ ] **4.1.3** Support multiple forms on same page
  - Test rendering multiple DynamicFormBlocks
  - Ensure unique form IDs in HTML
  - Handle multiple submissions correctly

- [ ] **4.1.4** Form versioning (via active + timestamps)
  - Admin shows created/modified dates
  - Consider read-only "archived" state for old versions

### Task 4.2: Admin UI Enhancements

**Subtasks:**

- [ ] **4.2.1** FormDefinition admin polish
  - Preview button (render form in modal)
  - Usage report (which pages use this form)
  - Submission count display

- [ ] **4.2.2** Blog admin polish
  - Category filtering in post list
  - Reading time auto-calculation display
  - Featured image preview in list

- [ ] **4.2.3** Lead admin enhancements
  - Filter by FormDefinition
  - Show form type in list columns
  - Form-specific field display in detail view

### Task 4.3: Performance Optimization

**Subtasks:**

- [ ] **4.3.1** Blog listing performance
  - Select_related for category, featured_image
  - Pagination query optimization
  - Consider caching for category counts

- [ ] **4.3.2** Dynamic form performance
  - FormDefinition caching (per-request or short TTL)
  - Generated form class caching

- [ ] **4.3.3** Template optimization
  - Minimize template includes
  - Lazy load blog images (if not already)

- [ ] **4.3.4** Lighthouse audit
  - Run against blog listing
  - Run against blog article
  - Address any regressions

### Task 4.4: Backwards Compatibility Verification

**Subtasks:**

- [ ] **4.4.1** Verify static forms still work
  - ContactFormBlock unchanged
  - QuoteRequestFormBlock unchanged
  - Existing form submissions work

- [ ] **4.4.2** Verify Lead model compatibility
  - Existing leads unaffected
  - New leads have form_type set
  - Admin views work for both types

- [ ] **4.4.3** Verify existing pages unaffected
  - StandardPage, ServicePage work
  - No template regressions
  - SEO still renders correctly

---

## Phase 5: Testing + Deployment

**Duration:** ~2-3 days  
**Goal:** Comprehensive testing, Sage & Stone deployment

### Task 5.1: Unit + Integration Tests

**Location:** `tests/` (matching sum_core structure)

**Subtasks:**

- [ ] **5.1.1** Forms test suite (`tests/forms/`)
  - `test_form_definition.py` - Model validation
  - `test_field_blocks.py` - Field type tests
  - `test_dynamic_form_block.py` - Block tests
  - `test_form_generation.py` - Runtime generation
  - `test_form_submission.py` - Full submission flow

- [ ] **5.1.2** Blog test suite (`tests/pages/`)
  - `test_category.py` - Category snippet
  - `test_blog_index_page.py` - Listing, pagination, filtering
  - `test_blog_post_page.py` - Model, reading time, excerpt
  - `test_blog_templates.py` - Template rendering

- [ ] **5.1.3** Integration tests
  - Blog with DynamicFormBlock CTA
  - Form submission from blog post
  - Email notification delivery
  - Webhook firing

### Task 5.2: Theme Tests

**Location:** `tests/themes/`

**Subtasks:**

- [ ] **5.2.1** Template contract tests
  - Blog templates exist in theme_a
  - Required blocks render correctly
  - Form templates render correctly

- [ ] **5.2.2** Visual regression tests (optional)
  - Screenshot comparison for blog listing
  - Screenshot comparison for blog article

### Task 5.3: Sage & Stone Deployment

**Subtasks:**

- [ ] **5.3.1** Deploy to Sage & Stone demo site
- [ ] **5.3.2** Create at least 3 distinct FormDefinitions
  - Newsletter signup
  - Contact/callback request
  - Quote request
- [ ] **5.3.3** Create sample blog posts
  - At least 5 posts for testing pagination
  - Multiple categories
  - Each post with DynamicFormBlock CTA
- [ ] **5.3.4** Verify all Definition of Done criteria
- [ ] **5.3.5** Lighthouse audit (target ≥90)

---

## Task Matrix

### By Priority (P1 = Must Have, P2 = Should Have, P3 = Nice to Have)

| Task ID | Task | Priority | Phase | Est. Hours | Dependencies |
|---------|------|----------|-------|------------|--------------|
| 1.1.1 | FormDefinition model | P1 | 1 | 4h | - |
| 1.1.2 | FormSubmissionSettings | P1 | 1 | 2h | 1.1.1 |
| 1.1.3 | Admin registration | P1 | 1 | 1h | 1.1.1 |
| 1.1.4 | Migration | P1 | 1 | 0.5h | 1.1.1-1.1.3 |
| 1.1.5 | Model unit tests | P1 | 1 | 2h | 1.1.4 |
| 1.2.1 | Base FormFieldBlock | P1 | 1 | 2h | - |
| 1.2.2 | Field type blocks | P1 | 1 | 6h | 1.2.1 |
| 1.2.3 | Layout blocks | P2 | 1 | 2h | 1.2.1 |
| 1.2.4 | Field block tests | P1 | 1 | 3h | 1.2.2 |
| 1.3.1 | DynamicFormBlock | P1 | 1 | 3h | 1.1.1 |
| 1.3.2 | Add to page StreamFields | P1 | 1 | 1h | 1.3.1 |
| 1.3.3 | Block tests | P1 | 1 | 2h | 1.3.2 |
| 2.1.1 | DynamicFormGenerator | P1 | 2 | 4h | 1.2.2 |
| 2.1.2 | Field rendering | P1 | 2 | 3h | 2.1.1 |
| 2.1.3 | Form validation | P1 | 2 | 2h | 2.1.2 |
| 2.1.4 | Generation tests | P1 | 2 | 2h | 2.1.3 |
| 2.2.1 | Base form template | P1 | 2 | 3h | 2.1.1 |
| 2.2.2 | Presentation variants | P2 | 2 | 4h | 2.2.1 |
| 2.2.3 | Tailwind styling | P1 | 2 | 3h | 2.2.1 |
| 2.2.4 | Form JavaScript | P1 | 2 | 4h | 2.2.1 |
| 2.3.1 | Submission handler | P1 | 2 | 4h | 2.1.1 |
| 2.3.2 | Lead integration | P1 | 2 | 2h | 2.3.1 |
| 2.3.3 | Spam protection | P1 | 2 | 2h | 2.3.1 |
| 2.3.4 | Submission tests | P1 | 2 | 3h | 2.3.3 |
| 2.4.1 | Notification task | P1 | 2 | 3h | 2.3.2 |
| 2.4.2 | Auto-reply task | P2 | 2 | 2h | 2.4.1 |
| 2.4.3 | Webhook integration | P1 | 2 | 2h | 2.3.2 |
| 2.4.4 | Async task tests | P1 | 2 | 2h | 2.4.3 |
| 3.1.1 | Category snippet | P1 | 3 | 2h | - |
| 3.1.2 | Category admin | P1 | 3 | 0.5h | 3.1.1 |
| 3.1.3 | Category migration | P1 | 3 | 0.5h | 3.1.2 |
| 3.1.4 | Category tests | P1 | 3 | 1h | 3.1.3 |
| 3.2.1 | BlogIndexPage model | P1 | 3 | 3h | 3.1.1 |
| 3.2.2 | Listing methods | P1 | 3 | 2h | 3.2.1 |
| 3.2.3 | Context method | P1 | 3 | 1h | 3.2.2 |
| 3.2.4 | Page rules | P1 | 3 | 1h | 3.2.1 |
| 3.2.5 | Index tests | P1 | 3 | 2h | 3.2.4 |
| 3.3.1 | BlogPostPage model | P1 | 3 | 4h | 3.1.1, 1.3.1 |
| 3.3.2 | Reading time | P1 | 3 | 1h | 3.3.1 |
| 3.3.3 | Excerpt fallback | P1 | 3 | 1h | 3.3.1 |
| 3.3.4 | Admin panels | P1 | 3 | 2h | 3.3.1 |
| 3.3.5 | Post tests | P1 | 3 | 2h | 3.3.4 |
| 3.4.1 | Index template | P1 | 3 | 4h | 3.2.3 |
| 3.4.2 | Post template | P1 | 3 | 4h | 3.3.1 |
| 3.4.3 | Template includes | P1 | 3 | 2h | 3.4.1 |
| 3.4.4 | Tailwind styling | P1 | 3 | 4h | 3.4.3 |
| 3.4.5 | SEO tags | P1 | 3 | 2h | 3.4.2 |
| 3.5.1 | Page routing | P1 | 3 | 1h | 3.2.1, 3.3.1 |
| 3.5.2 | Category filtering | P2 | 3 | 2h | 3.5.1 |
| 3.5.3 | Sitemap | P1 | 3 | 0.5h | 3.5.1 |
| 4.1.1 | Clone/Duplicate | P1 | 4 | 3h | 1.1.1 |
| 4.1.2 | Active toggle | P1 | 4 | 2h | 1.1.1 |
| 4.1.3 | Multiple forms/page | P1 | 4 | 2h | 2.2.1 |
| 4.1.4 | Form versioning | P3 | 4 | 2h | 4.1.2 |
| 4.2.1 | Form admin polish | P2 | 4 | 3h | 4.1.1 |
| 4.2.2 | Blog admin polish | P2 | 4 | 2h | 3.3.4 |
| 4.2.3 | Lead admin enhancements | P2 | 4 | 2h | 2.3.2 |
| 4.3.1 | Blog performance | P1 | 4 | 2h | 3.4.1 |
| 4.3.2 | Form performance | P2 | 4 | 2h | 2.1.1 |
| 4.3.3 | Template optimization | P2 | 4 | 2h | 3.4.4 |
| 4.3.4 | Lighthouse audit | P1 | 4 | 2h | 4.3.3 |
| 4.4.1 | Static forms compat | P1 | 4 | 1h | 2.3.1 |
| 4.4.2 | Lead model compat | P1 | 4 | 1h | 2.3.2 |
| 4.4.3 | Existing pages compat | P1 | 4 | 1h | 3.4.2 |
| 5.1.1 | Forms test suite | P1 | 5 | 4h | Phase 2 |
| 5.1.2 | Blog test suite | P1 | 5 | 4h | Phase 3 |
| 5.1.3 | Integration tests | P1 | 5 | 4h | 5.1.1, 5.1.2 |
| 5.2.1 | Theme contract tests | P1 | 5 | 2h | 3.4.4 |
| 5.2.2 | Visual regression | P3 | 5 | 4h | 5.2.1 |
| 5.3.1 | Deploy to Sage & Stone | P1 | 5 | 2h | Phase 4 |
| 5.3.2 | Create FormDefinitions | P1 | 5 | 2h | 5.3.1 |
| 5.3.3 | Create blog posts | P1 | 5 | 2h | 5.3.1 |
| 5.3.4 | DoD verification | P1 | 5 | 2h | 5.3.3 |
| 5.3.5 | Lighthouse audit | P1 | 5 | 1h | 5.3.4 |

### By Phase

| Phase | P1 Tasks | P2 Tasks | P3 Tasks | Total Hours |
|-------|----------|----------|----------|-------------|
| 1: Forms Foundation | 10 | 1 | 0 | ~28h |
| 2: Rendering + Submission | 12 | 2 | 0 | ~45h |
| 3: Blog Models + Templates | 18 | 1 | 0 | ~42h |
| 4: Integration + Polish | 8 | 5 | 1 | ~27h |
| 5: Testing + Deployment | 8 | 0 | 1 | ~27h |
| **TOTAL** | **56** | **9** | **2** | **~169h** |

### Critical Path

```
1.1.1 → 1.2.2 → 1.3.1 → 2.1.1 → 2.3.1 → 3.3.1 → 3.4.2 → 5.3.1
  │                                            │
  └─────────────────────────────────────────────┴──► Blog with DynamicFormBlock CTAs
```

The critical path runs through:
1. FormDefinition model (foundation)
2. Field type blocks (form structure)
3. DynamicFormBlock (embedding mechanism)
4. Form generation (runtime rendering)
5. Submission handler (lead capture)
6. BlogPostPage model (with DynamicFormBlock in body)
7. Blog post template (rendering)
8. Sage & Stone deployment (validation)

---

## File Inventory (New + Modified)

### New Files

| File | Purpose |
|------|---------|
| `core/sum_core/forms/fields.py` | Field type block definitions |
| `core/sum_core/forms/dynamic.py` | Runtime form generation |
| `core/sum_core/forms/tasks.py` | Celery tasks for notifications/webhooks |
| `core/sum_core/pages/blog.py` | BlogIndexPage, BlogPostPage, Category |
| `themes/theme_a/templates/sum_core/blocks/dynamic_form_block.html` | Form block template |
| `themes/theme_a/templates/sum_core/pages/blog_index_page.html` | Listing template |
| `themes/theme_a/templates/sum_core/pages/blog_post_page.html` | Article template |
| `themes/theme_a/templates/sum_core/includes/_post_card.html` | Post card component |
| `themes/theme_a/templates/sum_core/includes/_pagination.html` | Pagination component |
| `tests/forms/test_form_definition.py` | FormDefinition tests |
| `tests/forms/test_field_blocks.py` | Field block tests |
| `tests/forms/test_dynamic_form_block.py` | DynamicFormBlock tests |
| `tests/forms/test_form_generation.py` | Form generation tests |
| `tests/forms/test_form_submission.py` | Submission flow tests |
| `tests/pages/test_category.py` | Category tests |
| `tests/pages/test_blog_index_page.py` | BlogIndexPage tests |
| `tests/pages/test_blog_post_page.py` | BlogPostPage tests |
| `tests/pages/test_blog_templates.py` | Blog template tests |

### Modified Files

| File | Changes |
|------|---------|
| `core/sum_core/forms/models.py` | Add FormDefinition model |
| `core/sum_core/forms/views.py` | Extend submission handler |
| `core/sum_core/forms/urls.py` | Add dynamic form submission route |
| `core/sum_core/blocks/__init__.py` | Export DynamicFormBlock |
| `core/sum_core/blocks/forms.py` | Add DynamicFormBlock |
| `core/sum_core/pages/__init__.py` | Export blog page types |
| `core/sum_core/leads/admin.py` | Add form_type filtering |
| `core/sum_core/templates/sum_core/admin/lead_detail.html` | Form-specific display |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| FormDefinition migration conflicts | Low | High | Single migration for all form models |
| Lead model schema assumptions | Medium | High | No schema changes; use existing JSONField |
| Template override conflicts | Medium | Medium | Follow established theme → core fallback |
| Performance regression (blog listing) | Medium | Medium | Early Lighthouse testing, query optimization |
| Static form backward compat break | Low | Critical | Dedicated compatibility tests |
| Multiple forms on page ID collision | Medium | Medium | Unique form ID generation strategy |
| Celery task failures | Low | Medium | Existing retry infrastructure |

---

## Definition of Done Checklist

### Dynamic Forms v1

- [ ] FormDefinition creatable as Wagtail Snippet
- [ ] All field types work and validate
- [ ] DynamicFormBlock selectable in page StreamFields
- [ ] Submissions save to Lead model
- [ ] Email notifications send
- [ ] Webhooks fire correctly
- [ ] Clone/duplicate form works
- [ ] Active toggle works (forms can be deactivated)
- [ ] Multiple forms on same page tested
- [ ] Backwards compatible with existing static forms

### Blog v1

- [ ] Blog pages creatable in Wagtail admin
- [ ] Listing pagination works
- [ ] Category filtering works
- [ ] Featured images display correctly
- [ ] Reading time displays correctly
- [ ] SEO tags render correctly (reuses existing system)
- [ ] Lighthouse targets met (≥90 across all metrics)
- [ ] Templates match Sage & Stone UI contract

### Integration

- [ ] Deployed to Sage & Stone with at least 3 distinct form placements
- [ ] Blog uses DynamicFormBlock for CTAs
- [ ] Used in blog (via DynamicFormBlock)
- [ ] Used for real blog posts on Sage & Stone

---

## Appendix: Code Scaffolds

### FormDefinition Model Scaffold

```python
# File: core/sum_core/forms/models.py
# Purpose: FormDefinition Wagtail Snippet for dynamic form configuration
# Dependencies: wagtail.snippets, wagtail.fields (StreamField), wagtail.models
# Dependents: DynamicFormBlock, form submission handler, admin

from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet

from .fields import FORM_FIELD_BLOCKS


@register_snippet
class FormDefinition(models.Model):
    """
    A reusable form definition that can be embedded in any page via DynamicFormBlock.
    
    Site-scoped to support multi-site deployments.
    """
    
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="form_definitions",
    )
    name = models.CharField(
        max_length=255,
        help_text="Internal name for admin reference",
    )
    slug = models.SlugField(
        max_length=100,
        help_text="Unique identifier for this form",
    )
    fields = StreamField(
        FORM_FIELD_BLOCKS,
        blank=False,
        use_json_field=True,
    )
    success_message = models.TextField(
        default="Thank you for your submission!",
        help_text="Message shown after successful submission",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive forms won't appear in form selectors",
    )
    
    # Notification settings
    email_notification_enabled = models.BooleanField(default=True)
    notification_emails = models.TextField(
        blank=True,
        help_text="Comma-separated email addresses for notifications",
    )
    auto_reply_enabled = models.BooleanField(default=False)
    auto_reply_subject = models.CharField(max_length=255, blank=True)
    auto_reply_body = models.TextField(blank=True)
    
    # Webhook settings  
    webhook_enabled = models.BooleanField(default=False)
    webhook_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel("name"),
            FieldPanel("slug"),
            FieldPanel("is_active"),
        ], heading="Form Identity"),
        FieldPanel("fields"),
        FieldPanel("success_message"),
        MultiFieldPanel([
            FieldPanel("email_notification_enabled"),
            FieldPanel("notification_emails"),
            FieldPanel("auto_reply_enabled"),
            FieldPanel("auto_reply_subject"),
            FieldPanel("auto_reply_body"),
        ], heading="Email Notifications"),
        MultiFieldPanel([
            FieldPanel("webhook_enabled"),
            FieldPanel("webhook_url"),
        ], heading="Webhook Integration"),
    ]
    
    class Meta:
        unique_together = [("site", "slug")]
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name
```

### BlogPostPage Model Scaffold

```python
# File: core/sum_core/pages/blog.py
# Purpose: Blog page types and Category snippet
# Dependencies: wagtail.models, sum_core.pages.base, sum_core.blocks
# Dependents: Blog templates, sitemap, RSS feed

from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

from sum_core.blocks import CONTENT_BLOCKS
from sum_core.pages.mixins import SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin


@register_snippet
class Category(models.Model):
    """Single-level blog category (no hierarchy)."""
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
    ]
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name


class BlogIndexPage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """Blog listing page with pagination and category filtering."""
    
    intro = RichTextField(blank=True)
    posts_per_page = models.PositiveIntegerField(default=10)
    
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("posts_per_page"),
    ]
    
    subpage_types = ["sum_core.BlogPostPage"]
    parent_page_types = ["home.HomePage", "wagtailcore.Page"]
    
    def get_posts(self):
        """Return all live blog posts, newest first."""
        return (
            BlogPostPage.objects
            .live()
            .descendant_of(self)
            .order_by("-published_date")
            .select_related("category", "featured_image")
        )
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        posts = self.get_posts()
        
        # Category filtering
        category_slug = request.GET.get("category")
        if category_slug:
            posts = posts.filter(category__slug=category_slug)
            context["current_category"] = Category.objects.filter(
                slug=category_slug
            ).first()
        
        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(posts, self.posts_per_page)
        page_num = request.GET.get("page", 1)
        context["posts"] = paginator.get_page(page_num)
        context["categories"] = Category.objects.all()
        
        return context


class BlogPostPage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """Individual blog post with category, featured image, and body content."""
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    published_date = models.DateTimeField(default=timezone.now)
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    excerpt = models.TextField(
        blank=True,
        help_text="Optional summary. Falls back to first 200 chars of body.",
    )
    reading_time = models.PositiveIntegerField(
        default=0,
        help_text="Estimated reading time in minutes (auto-calculated on save)",
    )
    author_name = models.CharField(max_length=255, blank=True)
    
    # Body includes DynamicFormBlock for CTAs
    body = StreamField(
        CONTENT_BLOCKS,  # This should include DynamicFormBlock
        blank=True,
        use_json_field=True,
    )
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("category"),
            FieldPanel("published_date"),
            FieldPanel("author_name"),
        ], heading="Post Meta"),
        FieldPanel("featured_image"),
        FieldPanel("excerpt"),
        FieldPanel("body"),
    ]
    
    parent_page_types = ["sum_core.BlogIndexPage"]
    subpage_types = []
    
    def get_excerpt(self) -> str:
        """Return excerpt or fallback to truncated body text."""
        if self.excerpt:
            return self.excerpt
        # Strip HTML and truncate body
        from django.utils.html import strip_tags
        body_text = strip_tags(str(self.body))
        return body_text[:200] + "..." if len(body_text) > 200 else body_text
    
    def calculate_reading_time(self) -> int:
        """Calculate reading time based on word count (200 wpm)."""
        from django.utils.html import strip_tags
        body_text = strip_tags(str(self.body))
        word_count = len(body_text.split())
        return max(1, round(word_count / 200))
    
    def save(self, *args, **kwargs):
        self.reading_time = self.calculate_reading_time()
        super().save(*args, **kwargs)
```

---

*Document generated: December 23, 2025*  
*Estimated total effort: ~169 hours (~4-5 weeks with buffer)*
