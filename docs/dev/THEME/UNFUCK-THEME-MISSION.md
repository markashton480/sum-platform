# Theme A Block Template Migration - Task Tickets

**Date**: 2024-12-18  
**Project**: SUM Platform - Theme A Completion  
**Strategy**: Option A - Theme Block Template Overrides  
**Reference**: FUCKED-THEME.md (diagnosis report)

---

## 📋 Overview

### Current Situation
- ✅ Theme architecture is correct
- ✅ Page templates resolve properly (`theme/home_page.html`)
- ✅ Theme A Tailwind CSS compiles correctly
- ❌ **Block templates hardcoded to `sum_core/blocks/` paths**
- ❌ **Theme A lacks block template overrides**
- ❌ **Header references non-existent `established_year` field**

### The Problem
When Theme A pages render StreamField content, blocks use core templates styled for vanilla CSS instead of Theme A's Tailwind styles.

### The Solution
Create block template overrides in Theme A at `theme_a/templates/sum_core/blocks/`. Django's template resolution will find these first (because `theme/active/templates/` is in DIRS before APP_DIRS).

### Success Criteria
- ✅ Fresh `sum init --theme theme_a` creates working site
- ✅ StreamField blocks render with Theme A Tailwind styles
- ✅ No vanilla CSS classes in rendered HTML
- ✅ No browser console errors about missing styles
- ✅ Visual match with Sage & Stone wireframe
- ✅ No hardcoded "Est. 2025" in header
- ✅ Changes work in ANY client project (not just test harness)

---

## 🚨 Critical Anti-Patterns to Avoid

Based on AGENT-ORIENTATION.md, agents must **NOT**:

- ❌ Fix things only in `test_project/settings.py`
- ❌ Add template paths only to test INSTALLED_APPS
- ❌ Create client-project-specific solutions
- ❌ Modify block Python code (template overrides only)
- ❌ Change core block templates in `sum_core/templates/sum_core/blocks/` (these are fallbacks)

**Golden Rule**: Changes must work in **any** client project that runs `sum init --theme theme_a`.

---

## 📊 Task Summary

| Task | Priority | Time | Type |
|------|----------|------|------|
| TASK 1: Audit Blocks | HIGH | 15m | Analysis |
| TASK 2: Create Directory | HIGH | 5m | Setup |
| TASK 3: Migrate Hero Blocks | CRITICAL | 30m | Implementation |
| TASK 4: Migrate Service Blocks | HIGH | 20m | Implementation |
| TASK 5: Migrate Testimonial Blocks | MEDIUM | 20m | Implementation |
| TASK 6: Migrate Remaining Blocks | MEDIUM | 45m | Implementation |
| TASK 7: Fix established_year | CRITICAL | 20m | Bug Fix |
| TASK 8: Remove Sage & Stone Branding | LOW | 30m | Cleanup |
| TASK 9: Verify CLI Copy | CRITICAL | 15m | Verification |
| TASK 10: End-to-End Test | CRITICAL | 20m | Testing |
| TASK 11: Update Documentation | MEDIUM | 30m | Documentation |

**Total Time**: ~4 hours  
**Critical Path**: Tasks 2, 3, 7, 9, 10 (~90 minutes)

---

## 🎯 TASK 1: Audit Block Templates Used by Theme A

**Priority**: HIGH | **Estimated Time**: 15 minutes  
**Type**: Analysis

### Objective
Identify all block templates that need Theme A overrides.

### Context
We need a complete inventory of blocks before we can migrate them. This prevents missing any blocks during the migration.

### Files to Examine
- `core/sum_core/blocks/*.py` (all block definitions)
- Look for `Meta.template` declarations

### Step-by-Step Actions

1. **List all block classes with templates**:
   ```bash
   cd core/sum_core/blocks
   grep -r "template = " *.py
   ```

2. **Document each block's template path**:
   Create a checklist in markdown format with:
   - Block class name
   - Current template path
   - Whether it's used in Theme A

3. **Prioritize by usage**:
   - Critical: Hero blocks (always used)
   - High: Service cards, testimonials (common)
   - Medium: Gallery, CTA blocks
   - Low: Specialized blocks

### Expected Blocks (Minimum)
Based on diagnosis, we know these exist:
- `HeroImageBlock` → `sum_core/blocks/hero_image.html`
- `HeroGradientBlock` → `sum_core/blocks/hero_gradient.html`
- `ServiceCardsBlock` → `sum_core/blocks/service_cards.html`
- `TestimonialsBlock` → `sum_core/blocks/testimonials.html`

### Deliverable
Create `BLOCK-MIGRATION-CHECKLIST.md` with format:
```markdown
# Block Migration Checklist

## Critical Blocks (Always Used)
- [ ] HeroGradientBlock → sum_core/blocks/hero_gradient.html
- [ ] HeroImageBlock → sum_core/blocks/hero_image.html

## High Priority Blocks (Common)
- [ ] ServiceCardsBlock → sum_core/blocks/service_cards.html
- [ ] TestimonialsBlock → sum_core/blocks/testimonials.html

## Medium Priority Blocks
- [ ] ...

## Low Priority Blocks
- [ ] ...
```

### Acceptance Criteria
- [ ] All blocks with `Meta.template` are documented
- [ ] Blocks are categorized by priority
- [ ] Template paths are accurate
- [ ] Checklist is ready for use in subsequent tasks

### Testing
```bash
# Verify all blocks are found
cd core/sum_core/blocks
python -c "
import os
import ast

for filename in os.listdir('.'):
    if filename.endswith('.py'):
        with open(filename) as f:
            tree = ast.parse(f.read())
            # Check for template definitions
"
```

---

## 🎯 TASK 2: Create Theme A Block Template Directory Structure

**Priority**: HIGH | **Estimated Time**: 5 minutes  
**Type**: Setup

### Objective
Set up the directory structure for Theme A block template overrides.

### Context
Theme A needs to override block templates. Per Django template resolution, we place them at `theme_a/templates/sum_core/blocks/` so they're found before the core templates.

### Files to Create
```
core/sum_core/themes/theme_a/templates/sum_core/blocks/
└── .gitkeep  (to ensure directory is tracked)
```

### Step-by-Step Actions

1. **Create directory structure**:
   ```bash
   mkdir -p core/sum_core/themes/theme_a/templates/sum_core/blocks
   ```

2. **Add .gitkeep to track empty directory**:
   ```bash
   touch core/sum_core/themes/theme_a/templates/sum_core/blocks/.gitkeep
   ```

3. **Verify path is correct**:
   ```bash
   ls -la core/sum_core/themes/theme_a/templates/sum_core/blocks/
   ```

### Deliverable
- ✅ Directory exists: `core/sum_core/themes/theme_a/templates/sum_core/blocks/`
- ✅ Directory is tracked in git

### Acceptance Criteria
- [ ] Directory structure matches: `theme_a/templates/sum_core/blocks/`
- [ ] Path is relative to `core/sum_core/themes/`
- [ ] .gitkeep file is present
- [ ] Directory will be copied by `sum init --theme theme_a`

### Testing
```bash
# Verify directory exists
test -d core/sum_core/themes/theme_a/templates/sum_core/blocks && echo "✅ Directory exists"

# Verify it's in git
git status core/sum_core/themes/theme_a/templates/sum_core/blocks/
```

### Notes
This directory will be copied to `theme/active/templates/sum_core/blocks/` when a client runs `sum init --theme theme_a`. Django will then resolve block templates from here first.

---

## 🎯 TASK 3: Migrate Hero Block Templates to Theme A

**Priority**: CRITICAL | **Estimated Time**: 30 minutes  
**Type**: Implementation

### Objective
Create Tailwind-styled hero block templates for Theme A.

### Context
Hero blocks are the most visible components and are used on nearly every page. They currently use core templates with vanilla CSS classes. We need to create Theme A versions with Tailwind classes.

### Files to Create
- `core/sum_core/themes/theme_a/templates/sum_core/blocks/hero_gradient.html`
- `core/sum_core/themes/theme_a/templates/sum_core/blocks/hero_image.html`

### Reference Files
- Source: `core/sum_core/templates/sum_core/blocks/hero_gradient.html`
- Source: `core/sum_core/templates/sum_core/blocks/hero_image.html`
- Design ref: Sage & Stone wireframe (premium-trade-website-v3-final.html)

### Step-by-Step Actions

1. **Copy hero_gradient.html template**:
   ```bash
   cp core/sum_core/templates/sum_core/blocks/hero_gradient.html \
      core/sum_core/themes/theme_a/templates/sum_core/blocks/hero_gradient.html
   ```

2. **Update hero_gradient.html for Tailwind**:
   - Replace vanilla CSS classes with Tailwind equivalents
   - Ensure gradient styles use Theme A's Tailwind config
   - Verify button classes match Theme A design system
   - Check responsive classes are present

3. **Copy hero_image.html template**:
   ```bash
   cp core/sum_core/templates/sum_core/blocks/hero_image.html \
      core/sum_core/themes/theme_a/templates/sum_core/blocks/hero_image.html
   ```

4. **Update hero_image.html for Tailwind**:
   - Replace vanilla CSS classes with Tailwind
   - Ensure image rendering uses Theme A patterns
   - Verify layout matches Sage & Stone design

5. **Verify no vanilla CSS classes remain**:
   ```bash
   # Check for old class patterns
   grep -E "(\.hero--(gradient|image)|\.btn-primary)" \
        core/sum_core/themes/theme_a/templates/sum_core/blocks/hero_*.html
   ```

### Key Classes to Update

**Old (Vanilla CSS)**:
```html
<section class="section hero hero--gradient hero--gradient-{{ self.gradient_style }}">
    <div class="container hero-grid">
        <div class="hero-content reveal-group">
            <a href="#" class="btn btn-primary">...</a>
```

**New (Tailwind)**:
```html
<section class="relative py-20 lg:py-32 bg-gradient-to-br {{ gradient_classes }}">
    <div class="container mx-auto px-4">
        <div class="max-w-3xl animate-fade-in">
            <a href="#" class="inline-block px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors">...</a>
```

### Deliverable
- ✅ `theme_a/templates/sum_core/blocks/hero_gradient.html` (Tailwind-styled)
- ✅ `theme_a/templates/sum_core/blocks/hero_image.html` (Tailwind-styled)

### Acceptance Criteria
- [ ] Templates copied to correct location
- [ ] All vanilla CSS classes replaced with Tailwind
- [ ] Gradient styles use Theme A tokens (from tailwind.config.js)
- [ ] Button styles match Theme A design system
- [ ] Responsive classes present (lg:, md:, etc.)
- [ ] No references to removed CSS classes
- [ ] Templates render without errors

### Testing

1. **Local test with test_project**:
   ```bash
   cd core/sum_core/test_project
   python manage.py runserver
   # Visit page with hero blocks
   # Inspect element - should see Tailwind classes
   ```

2. **Test with fresh client init**:
   ```bash
   sum init test_hero --theme theme_a
   cd test_hero
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   # Create page with hero block
   # Verify Tailwind styling
   ```

3. **Visual verification**:
   - Hero renders with correct colors
   - Gradients display properly
   - Buttons have hover states
   - Layout matches Sage & Stone design
   - No console errors about missing CSS

### Notes
Hero blocks are customer-facing and highly visible. Take extra care with styling accuracy.

---

## 🎯 TASK 4: Migrate Service Block Templates to Theme A

**Priority**: HIGH | **Estimated Time**: 20 minutes  
**Type**: Implementation

### Objective
Create service cards block template for Theme A with Tailwind styling.

### Context
Service cards are commonly used to showcase offerings. The current core template uses vanilla CSS. Theme A needs a Tailwind version.

### Files to Create
- `core/sum_core/themes/theme_a/templates/sum_core/blocks/service_cards.html`

### Reference Files
- Source: `core/sum_core/templates/sum_core/blocks/service_cards.html`
- Design ref: Sage & Stone wireframe service cards section

### Step-by-Step Actions

1. **Copy service_cards.html template**:
   ```bash
   cp core/sum_core/templates/sum_core/blocks/service_cards.html \
      core/sum_core/themes/theme_a/templates/sum_core/blocks/service_cards.html
   ```

2. **Update for Tailwind**:
   - Replace grid classes with Tailwind grid utilities
   - Update card styling (borders, shadows, padding)
   - Ensure icons render correctly
   - Verify hover states work
   - Check responsive breakpoints

3. **Test card variants**:
   - Cards with icons
   - Cards with images
   - Cards with CTAs
   - Grid layouts (2-col, 3-col, 4-col)

### Key Classes to Update

**Old (Vanilla CSS)**:
```html
<div class="service-cards-grid">
    <div class="service-card">
        <div class="service-card-icon">...</div>
        <h3 class="service-card-title">...</h3>
```

**New (Tailwind)**:
```html
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
    <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
        <div class="w-16 h-16 mb-4">...</div>
        <h3 class="text-xl font-semibold mb-2">...</h3>
```

### Deliverable
- ✅ `theme_a/templates/sum_core/blocks/service_cards.html` (Tailwind-styled)

### Acceptance Criteria
- [ ] Template copied to correct location
- [ ] Grid layout uses Tailwind grid utilities
- [ ] Card styling matches Theme A design
- [ ] Icons render correctly
- [ ] Hover states work
- [ ] Responsive at all breakpoints
- [ ] No vanilla CSS classes remain

### Testing
```bash
# Create test page with service cards
python manage.py shell
>>> from sum_core.pages.models import StandardPage
>>> from wagtail.models import Site
>>> from sum_core.blocks.services import ServiceCardsBlock
# Add service cards to page StreamField
# Verify rendering
```

Visual checks:
- Cards display in grid
- Spacing is correct
- Cards have shadows
- Hover effects work
- Layout is responsive

---

## 🎯 TASK 5: Migrate Testimonial Block Templates to Theme A

**Priority**: MEDIUM | **Estimated Time**: 20 minutes  
**Type**: Implementation

### Objective
Create testimonials block template for Theme A with Tailwind styling.

### Context
Testimonials build trust and are important for conversion. The core template uses vanilla CSS. Theme A needs a Tailwind version.

### Files to Create
- `core/sum_core/themes/theme_a/templates/sum_core/blocks/testimonials.html`

### Reference Files
- Source: `core/sum_core/templates/sum_core/blocks/testimonials.html`
- Design ref: Sage & Stone wireframe testimonials section

### Step-by-Step Actions

1. **Copy testimonials.html template**:
   ```bash
   cp core/sum_core/templates/sum_core/blocks/testimonials.html \
      core/sum_core/themes/theme_a/templates/sum_core/blocks/testimonials.html
   ```

2. **Update for Tailwind**:
   - Replace testimonial card classes
   - Update quote styling
   - Ensure author info displays correctly
   - Verify star ratings render
   - Check carousel/slider functionality (if applicable)

3. **Test testimonial variants**:
   - Testimonials with photos
   - Testimonials without photos
   - Different layouts (carousel, grid, single)
   - Star ratings display

### Key Classes to Update

**Old (Vanilla CSS)**:
```html
<div class="testimonials-wrapper">
    <div class="testimonial-card">
        <div class="testimonial-quote">...</div>
        <div class="testimonial-author">
            <img class="testimonial-avatar" />
```

**New (Tailwind)**:
```html
<div class="space-y-8">
    <div class="bg-white p-8 rounded-lg shadow-md">
        <div class="text-lg italic text-gray-700 mb-4">...</div>
        <div class="flex items-center gap-4">
            <img class="w-12 h-12 rounded-full" />
```

### Deliverable
- ✅ `theme_a/templates/sum_core/blocks/testimonials.html` (Tailwind-styled)

### Acceptance Criteria
- [ ] Template copied to correct location
- [ ] Quote styling matches Theme A design
- [ ] Author info displays correctly
- [ ] Avatar images render properly
- [ ] Star ratings work (if present)
- [ ] Layout is responsive
- [ ] No vanilla CSS classes remain

### Testing
Create test page with testimonials:
- With photos
- Without photos
- Single testimonial
- Multiple testimonials
- Verify all render correctly

---

## 🎯 TASK 6: Migrate Remaining Content Blocks

**Priority**: MEDIUM | **Estimated Time**: 45 minutes  
**Type**: Implementation

### Objective
Migrate all other blocks identified in TASK 1 checklist to Theme A.

### Context
After completing hero, service, and testimonial blocks, we need to migrate any remaining blocks that Theme A uses.

### Process for Each Block

1. **Identify block from TASK 1 checklist**
2. **Copy core template to Theme A**
3. **Update classes to Tailwind**
4. **Test rendering**
5. **Check off in checklist**

### Likely Remaining Blocks

Based on common Wagtail StreamField patterns:
- Text blocks (rich text, headings)
- Image blocks (single image, image gallery)
- CTA blocks (call-to-action banners)
- Accordion/FAQ blocks
- Video embed blocks
- Contact form blocks
- Trust indicator blocks (logos, badges)

### Step-by-Step Actions

1. **Work through TASK 1 checklist systematically**:
   ```bash
   # For each unchecked block:
   BLOCK_NAME="text_block"  # example
   
   # Copy template
   cp core/sum_core/templates/sum_core/blocks/${BLOCK_NAME}.html \
      core/sum_core/themes/theme_a/templates/sum_core/blocks/${BLOCK_NAME}.html
   
   # Edit for Tailwind
   # Test rendering
   # Check off in checklist
   ```

2. **Keep styling consistent**:
   - Use Theme A color tokens
   - Match spacing from other migrated blocks
   - Ensure responsive patterns are consistent

3. **Test each block individually**:
   - Create test page
   - Add block to StreamField
   - Verify rendering
   - Check console for errors

### Deliverable
- ✅ All blocks from TASK 1 checklist migrated
- ✅ All blocks styled with Tailwind
- ✅ All blocks tested and working

### Acceptance Criteria
- [ ] Every block in TASK 1 checklist is completed
- [ ] All templates use Tailwind classes
- [ ] No vanilla CSS classes remain
- [ ] All blocks render correctly
- [ ] Styling is consistent across blocks

### Testing
```bash
# Create comprehensive test page with all blocks
python manage.py shell
>>> # Add one of each block type to a test page
>>> # Visual inspection of all blocks
```

### Time Management
If this task is taking too long:
1. Prioritize blocks actually used in Theme A
2. Mark low-priority blocks as "deferred"
3. Document which blocks still need migration

---

## 🎯 TASK 7: Fix established_year Field Issue

**Priority**: CRITICAL | **Estimated Time**: 20 minutes  
**Type**: Bug Fix

### Objective
Remove or properly implement the non-existent `established_year` field reference in header template.

### Context
The header template references `site_settings.established_year` which doesn't exist as a field in SiteSettings. This causes "Est. 2025" to always display. This is Sage & Stone specific branding that shouldn't be in the platform.

### The Problem
In `theme/includes/header.html` (line 44):
```django
Est. {{ site_settings.established_year|default:"2025" }}
```

### Recommended Solution: REMOVE (Option A)
**Rationale**: "Est. YYYY" is Sage & Stone branding, not a platform feature. Most clients won't need this.

### Files to Modify
- `core/sum_core/themes/theme_a/templates/theme/includes/header.html`

### Step-by-Step Actions

1. **Open header template**:
   ```bash
   # Edit this file
   core/sum_core/themes/theme_a/templates/theme/includes/header.html
   ```

2. **Locate the problematic line** (around line 44):
   ```django
   Est. {{ site_settings.established_year|default:"2025" }}
   ```

3. **Remove the entire line**

4. **Adjust layout if needed**:
   - The header may need slight adjustment after removal
   - Ensure remaining elements are properly spaced
   - Verify mobile layout still works

5. **Test header rendering**:
   ```bash
   python manage.py runserver
   # Visit any page
   # Verify header renders correctly
   # Verify no "Est. 2025" text
   ```

### Alternative: Implement Field (Option B - NOT RECOMMENDED)

If you really want the "Est." feature:

1. **Add field to SiteSettings**:
   ```python
   # In core/sum_core/branding/models.py
   established_year = models.PositiveIntegerField(
       blank=True,
       null=True,
       help_text="Year the business was established"
   )
   ```

2. **Create migration**:
   ```bash
   cd core/sum_core
   python manage.py makemigrations branding
   python manage.py migrate branding
   ```

3. **Update header template**:
   ```django
   {% if site_settings.established_year %}
       Est. {{ site_settings.established_year }}
   {% endif %}
   ```

**However**: This adds platform complexity for a single theme's branding. **Option A (removal) is better.**

### Deliverable
- ✅ Header template no longer references `established_year`
- ✅ Header renders correctly without "Est. 2025"
- ✅ No template errors

### Acceptance Criteria
- [ ] `established_year` reference removed from header
- [ ] Header renders without errors
- [ ] No "Est. 2025" visible on any page
- [ ] Header layout still looks correct
- [ ] Mobile layout unaffected

### Testing
```bash
# Start dev server
python manage.py runserver

# Test pages:
# - Home page
# - Standard pages
# - Service pages
# 
# Verify:
# - No "Est. 2025" text
# - Header looks correct
# - No console errors
# - Mobile view works
```

### Notes
This is Sage & Stone-specific branding leaking into the platform. Removing it makes Theme A more generic and reusable.

---

## 🎯 TASK 8: Remove Sage & Stone Branding from Theme A

**Priority**: LOW | **Estimated Time**: 30 minutes  
**Type**: Cleanup

### Objective
Make Theme A more generic and less tied to the Sage & Stone demo site.

### Context
Theme A was originally translated from a Sage & Stone (kitchen fitters) demo site. Some specific branding patterns leaked into the theme. While these don't break functionality, they make the theme less reusable.

### Known Issues
- ✅ "Est. YYYY" pattern (fixed in TASK 7)
- ⚠️ Default CTA text "Get a Quote" (actually fine - this is a reasonable default)
- ⚠️ Potential kitchen-fitter-specific copy in templates

### Files to Review
- `core/sum_core/themes/theme_a/templates/theme/includes/header.html`
- `core/sum_core/themes/theme_a/templates/theme/includes/footer.html`
- `core/sum_core/themes/theme_a/templates/theme/*.html` (all page templates)

### Step-by-Step Actions

1. **Audit templates for Sage & Stone references**:
   ```bash
   cd core/sum_core/themes/theme_a/templates
   grep -ri "sage" .
   grep -ri "stone" .
   grep -ri "kitchen" .
   grep -ri "quote" .
   ```

2. **Review findings**:
   - Is this copy hardcoded in template?
   - Or is it editable via Wagtail admin?
   - Is it demo-specific or a reasonable default?

3. **Remove/genericize hardcoded demo content**:
   - Replace kitchen-specific examples with generic ones
   - Remove any "Sage & Stone" references
   - Keep reasonable defaults (like "Get a Quote" CTA)

4. **Document intentional defaults**:
   Create a comment in templates explaining defaults:
   ```django
   {# Default CTA text - clients can override in Wagtail admin #}
   {{ header_cta_text|default:"Get a Quote" }}
   ```

### Model Defaults to Review

In `sum_core/navigation/models.py`:
```python
header_cta_text = models.CharField(
    max_length=50,
    blank=True,
    default="Get a Quote",  # This is fine - reasonable default
    ...
)
```

**Decision**: Keep this. "Get a Quote" is a reasonable default CTA for trade businesses. Clients can change it in Wagtail admin.

### Deliverable
- ✅ No Sage & Stone specific content in templates
- ✅ Reasonable defaults are kept and documented
- ✅ Theme A is generic and reusable

### Acceptance Criteria
- [ ] No "Sage & Stone" references in templates
- [ ] No kitchen-fitter-specific hardcoded copy
- [ ] Reasonable defaults are kept (like "Get a Quote")
- [ ] Defaults are documented with comments
- [ ] Theme A can be used for any trade business

### Testing
```bash
# Visual inspection of all templates
# Check for demo-specific content
# Verify defaults make sense generically
```

### Notes
This is a cleanup task. The theme works fine with Sage & Stone branding, but removing it makes Theme A more professionally reusable. Focus on hardcoded content, not editable defaults.

---

## 🎯 TASK 9: Verify CLI Theme Copy Includes Block Templates

**Priority**: CRITICAL | **Estimated Time**: 15 minutes  
**Type**: Verification

### Objective
Ensure `sum init --theme theme_a` copies block templates correctly to client projects.

### Context
For block template overrides to work, the CLI must copy `templates/sum_core/blocks/` from the theme to the client project's `theme/active/` directory. This task verifies that happens.

### Files to Check
- `cli/sum_cli/commands/init.py` - Theme copy logic

### Step-by-Step Actions

1. **Review CLI theme copy code**:
   ```bash
   # Open and examine
   cli/sum_cli/commands/init.py
   
   # Look for theme copy logic
   # Find where theme files are copied
   # Verify templates/ directory is included
   ```

2. **Check theme copy function**:
   The CLI should copy the entire `theme_a/` directory, including:
   - `templates/theme/` (page templates)
   - `templates/sum_core/blocks/` (block overrides) ← **This is critical**
   - `static/theme_a/css/` (compiled CSS)
   - `theme.json` (theme metadata)

3. **Test theme copy manually**:
   ```bash
   # Create fresh test project
   sum init test_cli_copy --theme theme_a
   cd test_cli_copy
   
   # Verify block templates were copied
   ls -la theme/active/templates/sum_core/blocks/
   
   # Should see:
   # hero_gradient.html
   # hero_image.html
   # service_cards.html
   # testimonials.html
   # ... (all blocks from TASK 1-6)
   ```

4. **If block templates NOT copied**:
   Update `cli/sum_cli/commands/init.py` to ensure full theme copy:
   ```python
   # Should copy entire theme directory
   shutil.copytree(
       src=theme_source_dir,  # e.g., core/sum_core/themes/theme_a/
       dst=client_theme_dir,  # e.g., client_project/theme/active/
       dirs_exist_ok=True
   )
   ```

### Deliverable
- ✅ CLI copies entire theme including block templates
- ✅ `theme/active/templates/sum_core/blocks/` exists after init
- ✅ All block templates are present in client project

### Acceptance Criteria
- [ ] `sum init --theme theme_a` copies full theme
- [ ] Block templates exist in `theme/active/templates/sum_core/blocks/`
- [ ] No manual copying required by user
- [ ] Theme is fully functional after init

### Testing
```bash
# Test 1: Fresh init
sum init test_verify_1 --theme theme_a
cd test_verify_1
ls -la theme/active/templates/sum_core/blocks/
echo "Expected: hero_gradient.html, hero_image.html, service_cards.html, ..."

# Test 2: Verify block rendering works
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Create page with blocks
# Verify Tailwind styling appears

# Clean up
cd ..
rm -rf test_verify_1
```

### Expected Structure After Init
```
client_project/
└── theme/
    └── active/
        ├── templates/
        │   ├── theme/              # Page templates
        │   │   ├── home_page.html
        │   │   └── standard_page.html
        │   └── sum_core/           # Block overrides
        │       └── blocks/
        │           ├── hero_gradient.html
        │           ├── hero_image.html
        │           ├── service_cards.html
        │           └── testimonials.html
        ├── static/
        │   └── theme_a/
        │       └── css/
        │           └── main.css
        └── theme.json
```

### Notes
This is **critical**. If the CLI doesn't copy block templates, none of our work in TASK 3-6 will help clients. The templates must be present in client projects for Django to find them.

---

## 🎯 TASK 10: End-to-End Integration Test

**Priority**: CRITICAL | **Estimated Time**: 20 minutes  
**Type**: Testing

### Objective
Verify the entire theme renders correctly in a fresh client project created via CLI.

### Context
This is the ultimate test. We create a brand new client project using the CLI, add content, and verify everything works. This simulates the real client experience.

### Prerequisites
- All previous tasks completed
- TASK 9 verified (CLI copies correctly)

### Step-by-Step Actions

1. **Create fresh test project**:
   ```bash
   # Clean slate
   sum init theme_integration_test --theme theme_a
   cd theme_integration_test
   ```

2. **Set up project**:
   ```bash
   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   # Username: admin
   # Password: admin123 (for testing)
   
   # Start server
   python manage.py runserver
   ```

3. **Create test content in Wagtail admin**:
   - Visit http://localhost:8000/admin/
   - Log in with superuser credentials
   - Navigate to Pages
   - Create a Home Page with StreamField content:
     - Add HeroGradientBlock (test gradient hero)
     - Add HeroImageBlock (test image hero)
     - Add ServiceCardsBlock (add 3 test services)
     - Add TestimonialsBlock (add 2 test testimonials)
   - Publish page

4. **Visual inspection checklist**:
   Visit http://localhost:8000/

   **Hero Blocks**:
   - [ ] Hero gradient displays with correct colors
   - [ ] Hero image displays with proper layout
   - [ ] Hero CTAs are styled correctly
   - [ ] Hero text is readable
   - [ ] Responsive on mobile (check browser dev tools)

   **Service Cards**:
   - [ ] Cards display in grid
   - [ ] Card spacing is correct
   - [ ] Icons/images render
   - [ ] Hover effects work
   - [ ] Responsive grid (3 cols → 2 cols → 1 col)

   **Testimonials**:
   - [ ] Testimonials display correctly
   - [ ] Quotes are styled
   - [ ] Author info shows
   - [ ] Layout is responsive

   **Overall**:
   - [ ] Page uses Tailwind classes
   - [ ] No vanilla CSS artifacts visible
   - [ ] Colors match Theme A palette
   - [ ] Typography is correct
   - [ ] Spacing/padding is consistent

5. **Browser console check**:
   - Open browser dev tools (F12)
   - Check Console tab
   - **Should see**: No errors
   - **Should NOT see**: Missing CSS warnings, 404s, JavaScript errors

6. **HTML inspection**:
   - Right-click hero → Inspect Element
   - Check classes in HTML:
   ```html
   <!-- GOOD - Tailwind classes -->
   <section class="relative py-20 lg:py-32 bg-gradient-to-br ...">
   
   <!-- BAD - Vanilla CSS classes -->
   <section class="section hero hero--gradient ...">
   ```

7. **Template resolution verification**:
   ```bash
   # Check Django template debugging
   # Add this temporarily to settings.py:
   DEBUG = True
   TEMPLATES[0]['OPTIONS']['debug'] = True
   
   # Restart server
   # Django will show which template is being used
   # Should see: theme/active/templates/sum_core/blocks/hero_gradient.html
   # NOT: sum_core/templates/sum_core/blocks/hero_gradient.html
   ```

### Test Scenarios

**Scenario 1: Happy Path**
- Fresh init
- Add content
- Everything renders beautifully
- **Result**: ✅ PASS

**Scenario 2: Missing Block Template**
- Block renders but looks wrong
- Inspect - sees vanilla CSS classes
- **Result**: ❌ FAIL - Block template wasn't copied
- **Action**: Fix TASK 9, re-test

**Scenario 3: CSS Not Loading**
- Block templates use Tailwind classes
- But styles don't apply
- **Result**: ❌ FAIL - CSS not loaded or compiled wrong
- **Action**: Check STATICFILES_DIRS, check CSS compilation

### Deliverable
- ✅ Fresh client project renders correctly
- ✅ All blocks display with Theme A styling
- ✅ No console errors
- ✅ No vanilla CSS artifacts
- ✅ Visual match with Sage & Stone design

### Acceptance Criteria
- [ ] Fresh `sum init theme_integration_test --theme theme_a` succeeds
- [ ] Page with all block types renders correctly
- [ ] Browser console shows no errors
- [ ] HTML inspection shows Tailwind classes, not vanilla CSS
- [ ] Visual appearance matches Theme A design
- [ ] Responsive on mobile, tablet, desktop
- [ ] No "Est. 2025" in header
- [ ] All images load
- [ ] All links work

### If Tests Fail

**Problem**: Block renders but uses vanilla CSS
- **Cause**: Block template not in `theme/active/templates/sum_core/blocks/`
- **Fix**: Check TASK 9 - CLI not copying correctly

**Problem**: Block template exists but styles don't apply
- **Cause**: CSS not loaded or wrong CSS file
- **Fix**: Check STATICFILES_DIRS, verify main.css contains Tailwind

**Problem**: Header shows "Est. 2025"
- **Cause**: TASK 7 not completed
- **Fix**: Remove established_year reference

**Problem**: Can't create content in admin
- **Cause**: Migrations not run or models not registered
- **Fix**: Run migrations, check admin.py registrations

### Clean Up
```bash
# After successful test
cd ..
rm -rf theme_integration_test

# Or keep it as reference
mv theme_integration_test theme_integration_test_PASSING
```

### Notes
This is the **MOST IMPORTANT TEST**. If this passes, Theme A is production-ready. If it fails, something in TASK 1-9 needs fixing. Don't skip this task.

---

## 🎯 TASK 11: Update Documentation

**Priority**: MEDIUM | **Estimated Time**: 30 minutes  
**Type**: Documentation

### Objective
Document the block template override pattern for future theme creators.

### Context
We've proven that block template overrides work for themes. This pattern should be documented so future themes (Theme B, C, etc.) can follow the same approach.

### Files to Modify
- `docs/dev/master-docs/THEME-ARCHITECTURE-SPECv1.md` - Add block template override section
- `docs/dev/themes/theme-creation-guide.md` - Document process (create if doesn't exist)
- `docs/dev/FUCKED-THEME.md` - Mark as RESOLVED

### Step-by-Step Actions

1. **Update THEME-ARCHITECTURE-SPECv1.md**:
   
   Add new section after Â§9.3 (Template Resolution):
   
   ```markdown
   ### Â§9.4 Block Template Overrides
   
   Themes can override StreamField block templates by providing templates at:
   `theme_name/templates/sum_core/blocks/{block_name}.html`
   
   **Resolution Order for Block Templates**:
   1. `theme/active/templates/sum_core/blocks/` (theme override)
   2. `templates/overrides/sum_core/blocks/` (client override)
   3. APP_DIRS → `sum_core/templates/sum_core/blocks/` (core fallback)
   
   **Example**: When `HeroGradientBlock` renders:
   - Block declares: `template = "sum_core/blocks/hero_gradient.html"`
   - Django looks in `theme/active/templates/sum_core/blocks/hero_gradient.html`
   - If found: Uses theme template (Tailwind styled)
   - If not found: Falls back to core template (vanilla CSS)
   
   **Theme Requirements**:
   All themes MUST provide block template overrides for any blocks they use.
   Blocks should be styled to match the theme's CSS framework (Tailwind, Bootstrap, etc.).
   
   **Testing Block Templates**:
   ```bash
   # Verify block template is in theme
   ls theme_name/templates/sum_core/blocks/hero_gradient.html
   
   # Test rendering
   sum init test_theme --theme theme_name
   cd test_theme
   # Create page with blocks, verify styling
   ```
   ```

2. **Create Theme Creation Guide**:
   
   Create `docs/dev/themes/theme-creation-guide.md`:
   
   ```markdown
   # Theme Creation Guide
   
   ## Overview
   Creating a new theme for SUM Platform involves:
   1. Page templates (required)
   2. Block templates (required)
   3. CSS/styling (required)
   4. Theme metadata (required)
   
   ## Directory Structure
   ```
   core/sum_core/themes/theme_name/
   ├── templates/
   │   ├── theme/                    # Page templates
   │   │   ├── home_page.html
   │   │   ├── standard_page.html
   │   │   └── ...
   │   └── sum_core/                 # Block template overrides
   │       └── blocks/
   │           ├── hero_gradient.html
   │           ├── hero_image.html
   │           ├── service_cards.html
   │           └── ... (all blocks used by theme)
   ├── static/
   │   └── theme_name/
   │       └── css/
   │           └── main.css          # Compiled CSS
   └── theme.json                    # Theme metadata
   ```
   
   ## Step 1: Create Page Templates
   [Document page template creation]
   
   ## Step 2: Create Block Template Overrides
   
   **Critical**: Block templates must be styled for your theme's CSS framework.
   
   1. List all blocks your theme will use
   2. Copy core templates from `sum_core/templates/sum_core/blocks/`
   3. Update classes to match your CSS framework
   4. Test each block individually
   
   Example - Hero Block for Tailwind theme:
   ```html
   <!-- core/sum_core/themes/theme_tailwind/templates/sum_core/blocks/hero_gradient.html -->
   <section class="relative py-20 lg:py-32 bg-gradient-to-br {{ gradient_classes }}">
       <div class="container mx-auto px-4">
           <h1 class="text-4xl lg:text-6xl font-bold mb-6">{{ self.heading }}</h1>
       </div>
   </section>
   ```
   
   Example - Hero Block for Bootstrap theme:
   ```html
   <!-- core/sum_core/themes/theme_bootstrap/templates/sum_core/blocks/hero_gradient.html -->
   <section class="hero py-5 bg-primary bg-gradient">
       <div class="container">
           <h1 class="display-1 fw-bold mb-4">{{ self.heading }}</h1>
       </div>
   </section>
   ```
   
   ## Step 3: Compile CSS
   [Document CSS compilation]
   
   ## Step 4: Test Theme
   ```bash
   sum init test_my_theme --theme my_theme
   cd test_my_theme
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   # Create page with all block types
   # Verify styling is correct
   ```
   
   ## Checklist
   - [ ] Page templates created
   - [ ] Block templates created for all blocks
   - [ ] CSS compiled
   - [ ] theme.json present
   - [ ] CLI copies theme correctly
   - [ ] Fresh init renders correctly
   - [ ] All blocks styled consistently
   - [ ] Responsive on all devices
   - [ ] No console errors
   ```

3. **Mark FUCKED-THEME.md as Resolved**:
   
   Add to top of `docs/dev/FUCKED-THEME.md`:
   
   ```markdown
   # ✅ RESOLVED - 2024-12-18
   
   **Status**: Fixed via Theme A Block Template Migration  
   **Solution**: Option A - Theme Block Template Overrides  
   **Tasks**: See THEME-A-BLOCK-MIGRATION-TASKS.md  
   
   ---
   
   # Theme System Post-Mortem & Diagnosis Report
   [Rest of original document...]
   ```

4. **Create troubleshooting section**:
   
   Add to THEME-ARCHITECTURE-SPECv1.md:
   
   ```markdown
   ### Â§10 Troubleshooting Block Rendering
   
   **Problem**: Blocks render but use wrong styles (vanilla CSS instead of theme CSS)
   
   **Diagnosis**:
   ```bash
   # Check if block template exists in theme
   ls theme/active/templates/sum_core/blocks/hero_gradient.html
   
   # If missing: Theme doesn't have block override
   # If present: Check template resolution
   ```
   
   **Solution**: Create block template override in theme
   
   ---
   
   **Problem**: Block template exists but styles don't apply
   
   **Diagnosis**: CSS not loaded or wrong CSS file
   
   **Solution**: Check STATICFILES_DIRS includes `theme/active/static/`
   
   ---
   
   **Problem**: Some blocks styled correctly, others aren't
   
   **Diagnosis**: Partial theme - some block templates missing
   
   **Solution**: Audit all blocks used, create overrides for missing ones
   ```

### Deliverable
- ✅ THEME-ARCHITECTURE-SPECv1.md updated with block override pattern
- ✅ Theme creation guide created
- ✅ FUCKED-THEME.md marked as resolved
- ✅ Troubleshooting guide added

### Acceptance Criteria
- [ ] Documentation explains block template override pattern
- [ ] Examples are clear and accurate
- [ ] Theme creation guide is comprehensive
- [ ] Future theme creators can follow the guide
- [ ] Troubleshooting section covers common issues

### Testing
Have someone unfamiliar with the system:
1. Read the theme creation guide
2. Attempt to create a new theme
3. Note any confusion or missing info
4. Update docs accordingly

### Notes
Good documentation prevents future "WTF is broken?" moments. Be thorough.

---

## 🚀 Quick Win Path (Minimum Viable Fix)

If you need Theme A working ASAP, do these tasks in order:

| Order | Task | Time | Why Critical |
|-------|------|------|--------------|
| 1 | TASK 2 | 5 min | Create directory structure |
| 2 | TASK 3 | 30 min | Hero blocks are most visible |
| 3 | TASK 7 | 20 min | Remove "Est. 2025" bug |
| 4 | TASK 9 | 15 min | Verify CLI copies correctly |
| 5 | TASK 10 | 20 min | Test everything works |

**Total: ~90 minutes to functional theme**

Then complete remaining tasks for full polish:
- TASK 1: Audit (for documentation)
- TASK 4-6: Remaining blocks (for completeness)
- TASK 8: Remove branding (for professional appearance)
- TASK 11: Documentation (for future themes)

---

## 📊 Task Dependencies

```
TASK 1 (Audit)
    â†"
TASK 2 (Create Directory)
    â†"
TASK 3 (Hero Blocks) ───┐
TASK 4 (Service Blocks) ─┤
TASK 5 (Testimonials) ───┼→ TASK 9 (Verify CLI) → TASK 10 (E2E Test) → ✅ DONE
TASK 6 (Remaining) ──────┤
TASK 7 (Fix Field) ──────┘

TASK 8 (Branding) ──→ Can run anytime, independent

TASK 11 (Docs) ──→ After TASK 10 passes
```

---

## ✅ Definition of Done

Theme A migration is **COMPLETE** when:

1. ✅ Fresh `sum init --theme theme_a` creates working site
2. ✅ All blocks render with Theme A Tailwind styles
3. ✅ No vanilla CSS classes in rendered block HTML
4. ✅ No browser console errors about missing styles
5. ✅ Visual appearance matches Sage & Stone wireframe
6. ✅ No hardcoded "Est. 2025" in header
7. ✅ Changes work in ANY client project (not just test harness)
8. ✅ Documentation updated for future themes
9. ✅ TASK 10 end-to-end test passes completely
10. ✅ Code review approved

---

## 🎭 Handoff Format for VS Code Agents

When handing each task to an AI agent in VS Code, use this format:

```markdown
## TASK X: [Task Name]

**Context**: [1-2 sentences from this document]

**Objective**: [What success looks like]

**Reference Documents**:
- THEME-A-BLOCK-MIGRATION-TASKS.md (this document)
- FUCKED-THEME.md (original diagnosis)
- AGENT-ORIENTATION.md (platform vs test harness rules)

**Files to Modify**: [List from task]

**Step-by-Step Actions**: [Copy from task]

**Acceptance Criteria**: [Copy from task]

**Testing**: [Copy from task]
```

---

## 📞 Questions or Issues?

If any task is unclear or reveals unexpected issues:

1. ✅ Document the issue
2. ✅ Check FUCKED-THEME.md for related context
3. ✅ Verify you're not falling into anti-patterns (AGENT-ORIENTATION.md)
4. ✅ Test in fresh client project, not just test harness
5. ✅ Escalate if architectural assumption needs revisiting

---

**Good luck! You've got this.** 🚀

The diagnosis was excellent, the fix is straightforward, and the architecture is solid. Just execute the tasks systematically and Theme A will be production-ready.

---

*End of task document*