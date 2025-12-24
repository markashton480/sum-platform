# Theme System Post-Mortem & Diagnosis Report

**Date**: 2025-12-18  
**Investigator**: Claude (Opus 4.5)  
**Scope**: M6 Theme Implementation (Tailwind migration + Theme A / Sage & Stone)

---

## Executive Summary

The architecture is **correct and stable**. The spec (THEME-ARCHITECTURE-SPECv1) is sound. The implementation has been incrementally corrected through multiple CMs to match the spec.

**The actual problem is specific and narrow**: Block templates are hardcoded to `sum_core/blocks/` paths, so when Theme A pages render StreamField content, the blocks use **core templates styled for vanilla CSS**, not Theme A's Tailwind styles.

Everything else works:
- ✅ Page templates resolve correctly (`theme/home_page.html` → Theme A)
- ✅ Theme CSS compiles and contains required selectors
- ✅ `sum init --theme theme_a` copies theme to `theme/active/`
- ✅ Settings resolve `theme/active/templates/` first
- ❌ **Block templates hardcoded to `sum_core/blocks/`** — this is the main bug
- ❌ **Template references non-existent `established_year` field** — shows "Est. 2025" always
- ⚠️ **Sage & Stone branding baked into Theme A** — "Est. YYYY" pattern, default CTA text

---

## Additional Issue: Hardcoded Defaults in Templates & Models

You're also seeing "random bits" like "Est. 2025" and "Get a Quote" buttons. These aren't hardcoded HTML from the wireframe - they're **sensible defaults** that the agent baked into both templates and models:

### Template Fallbacks

In [theme/includes/header.html](core/sum_core/themes/theme_a/templates/theme/includes/header.html#L44):

```django
Est. {{ site_settings.established_year|default:"2025" }}
```

**Problem**: `established_year` doesn't exist as a field in `SiteSettings`. The agent referenced a non-existent field and gave it a fallback. So it always shows "Est. 2025".

### Model Defaults

In [navigation/models.py](core/sum_core/navigation/models.py#L120):

```python
header_cta_text = models.CharField(
    max_length=50,
    blank=True,
    default="Get a Quote",  # ← Default value
    ...
)
```

And again at [line 153](core/sum_core/navigation/models.py#L153):

```python
mobile_cta_button_text = models.CharField(
    max_length=50,
    blank=True,
    default="Get a Quote",  # ← Default value
    ...
)
```

**This is actually correct behavior** - these are navigation settings with sensible defaults. If a client hasn't configured their CTA text in Wagtail admin, they get "Get a Quote".

### The Real Issues Here

1. **`established_year` field doesn't exist** - Template references `site_settings.established_year` but it's not in `SiteSettings`. Either:
   - Add the field to `SiteSettings`, or
   - Remove the "Est. YYYY" line from the header template (it's Sage & Stone branding, not platform feature)

2. **Demo content vs empty defaults** - The theme was translated from a "Sage & Stone" demo site with specific branding. Some of that branding leaked into:
   - Template structure (the "Est. YYYY" pattern is very Sage & Stone specific)
   - Default values that only make sense for kitchen fitters

### What This Means

The "random bits" you're seeing are:
- ✅ **Model defaults working correctly** ("Get a Quote" - this is fine, can be changed in admin)
- ❌ **Template referencing non-existent field** (`established_year` - needs fixing)
- ⚠️ **Theme-specific branding in platform templates** (the whole "Est." concept is baked into Theme A)

Per **THEME-ARCHITECTURE-SPECv1**, the rendering contract is:

```
Client Project
├── theme/active/                     ← Theme copied here at init
│   ├── templates/theme/              ← Page templates
│   ├── static/theme_a/css/main.css   ← Compiled Tailwind CSS
│   └── theme.json
├── templates/overrides/              ← Client customizations
└── (APP_DIRS fallback to sum_core)
```

**Template resolution order** (per spec §9.3):
1. `theme/active/templates/` (theme wins)
2. `templates/overrides/` (client overrides)
3. APP_DIRS → `sum_core/templates/` (fallback)

**Page models** use `theme/...` paths:
- `HomePage` → `theme/home_page.html`
- `StandardPage` → `theme/standard_page.html`

This is all **correctly implemented**.

---

## The Actual Bug

### Block Templates Are Hardcoded to Core Paths

Look at [core/sum_core/blocks/hero.py](core/sum_core/blocks/hero.py#L77):

```python
class HeroImageBlock(BaseHeroBlock):
    class Meta:
        template = "sum_core/blocks/hero_image.html"  # ← HARDCODED
```

And [core/sum_core/blocks/hero.py](core/sum_core/blocks/hero.py#L97):

```python
class HeroGradientBlock(BaseHeroBlock):
    class Meta:
        template = "sum_core/blocks/hero_gradient.html"  # ← HARDCODED
```

**What this means:**

When a Theme A page renders StreamField content:
1. Page template loads from `theme/active/templates/theme/home_page.html` ✅
2. `{% include_block block %}` renders each block
3. Block looks up its template: `sum_core/blocks/hero_gradient.html`
4. Django finds this in `sum_core/templates/sum_core/blocks/` ❌

**Result**: The page shell is Theme A (Tailwind), but the blocks inside are core templates expecting vanilla CSS tokens.

### The Block Templates Use Theme A Classes Without Theme A CSS

Look at [core/sum_core/templates/sum_core/blocks/hero_gradient.html](core/sum_core/templates/sum_core/blocks/hero_gradient.html):

```html
<section class="section hero hero--gradient hero--gradient-{{ self.gradient_style }}">
    <div class="container hero-grid">
        <div class="hero-content reveal-group">
```

These classes (`.hero--gradient`, `.btn-primary`, `.reveal-group`) are defined in Theme A's Tailwind CSS. But when the block template loads from `sum_core/templates/`, it's inside a page that may or may not have Theme A's CSS loaded.

**The disconnect**: Block templates were updated to use Theme A class names, but they're still served from core, and they have no guarantee that Theme A CSS is present.

---

## Why This Happened

### CM-M6-A-004 Fixed the CSS, Not the Template Path

CM-M6-A-004 correctly identified that component classes were missing from compiled CSS and fixed the Tailwind config. But it didn't address that **block templates are served from `sum_core/`, not from the theme**.

### The v0.6 Contract Only Covers Page Templates

CM-M6-05 updated page models to use `theme/...` paths. It did NOT update block templates. The blocks still use `sum_core/blocks/...` because:

1. Blocks are defined in `sum_core` (the reusable core package)
2. Block templates are declared in Python code via `Meta.template`
3. Nobody considered that blocks also need theme-specific templates

---

## The Fix Options

### Option A: Theme Block Template Overrides (Recommended)

Themes should provide block template overrides at `theme/active/templates/sum_core/blocks/`.

Django template resolution will find these first because `theme/active/templates/` is in `DIRS` before APP_DIRS.

**Implementation:**
1. Copy block templates from `sum_core/templates/sum_core/blocks/` to `theme_a/templates/sum_core/blocks/`
2. Style them for Theme A
3. When theme is copied to `theme/active/`, block templates come along
4. Django resolves `sum_core/blocks/hero_gradient.html` → `theme/active/templates/sum_core/blocks/hero_gradient.html` ✅

**Pros:** Clean, follows existing resolution patterns, no code changes needed
**Cons:** Block templates duplicated across themes

### Option B: Dynamic Block Template Resolution

Make blocks resolve templates dynamically based on active theme.

**Implementation:**
```python
class HeroGradientBlock(BaseHeroBlock):
    def get_template(self, context=None):
        # Could read from context or settings
        return "theme/blocks/hero_gradient.html"  # or detect theme
```

**Pros:** No template duplication
**Cons:** More complex, requires code changes to all blocks

### Option C: Core Block Templates Become Theme-Agnostic

Make core block templates use only base HTML structure with no styling classes. Themes wrap/extend them.

**Pros:** Clean separation of concerns
**Cons:** Major refactor, breaks existing patterns

---

## Recommended Path Forward

**Do Option A** — it's the simplest and aligns with the existing architecture.

### Immediate Steps

1. **Create block templates in Theme A**:
   ```
   core/sum_core/themes/theme_a/templates/sum_core/blocks/
   ├── hero_gradient.html
   ├── hero_image.html
   ├── service_cards.html
   ├── testimonials.html
   └── ... (all blocks used by Theme A)
   ```

2. **Copy from wireframe patterns**: Use the compiled Sage & Stone HTML as reference for correct Tailwind classes and structure.

3. **Verify `sum init` copies them**: The theme copy should include `templates/sum_core/blocks/` alongside `templates/theme/`.

4. **Test with a real client**: `sum init test123 --theme theme_a`, then run dev server and visually inspect.

---

## What's NOT Broken

| Component | Status | Notes |
|-----------|--------|-------|
| Theme architecture spec | ✅ Correct | THEME-ARCHITECTURE-SPECv1 is sound |
| `sum init --theme` | ✅ Works | Copies theme to `theme/active/` |
| Page template resolution | ✅ Works | `theme/...` paths resolve correctly |
| Theme A Tailwind CSS | ✅ Compiles | All component classes present |
| Settings configuration | ✅ Correct | `TEMPLATES[DIRS]` and `STATICFILES_DIRS` are right |
| Block template path | ❌ Bug | Hardcoded to `sum_core/blocks/` |
| Block templates in theme | ❌ Missing | Theme A doesn't override block templates |

---

## Files to Modify

| File | Action |
|------|--------|
| `core/sum_core/themes/theme_a/templates/sum_core/blocks/` | Create directory, add block templates |
| Each block template in above dir | Copy from core, style for Theme A |
| `cli/sum_cli/commands/init.py` | Verify theme copy includes `templates/sum_core/` |

---

## Conclusion

The architecture is right. The page templates work. The CSS compiles correctly. 

**The single bug is: block templates are hardcoded to core paths and Theme A doesn't provide overrides for them.**

Once block templates exist in `theme_a/templates/sum_core/blocks/`, template resolution will find them first (because `theme/active/templates/` is in DIRS before APP_DIRS), and blocks will render with Theme A styling.

No architectural changes needed. No spec changes needed. Just add the missing block templates to Theme A.

---

*End of report.*
