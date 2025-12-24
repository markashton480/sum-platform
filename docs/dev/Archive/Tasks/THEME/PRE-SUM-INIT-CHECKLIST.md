# Pre `sum init` Checklist - Theme A Migration

**Purpose**: Verify all fixes are in place BEFORE running `sum init --theme theme_a`  
**Date**: 2024-12-18  
**Context**: Theme A was "unfucked" - need to verify everything before next client project setup

---

## ✅ COMPLETED FIXES - Verification Checklist

### 1. Block Template Overrides (20 files)
**Location**: `core/sum_core/themes/theme_a/templates/sum_core/blocks/`

- [x] contact_form.html - Tailwind contact form with grid layout
- [x] content_buttons.html - Button group with flex layout
- [x] content_divider.html - Horizontal divider with conditional styles
- [x] content_editorial_header.html - Rich text header section
- [x] content_image.html - Responsive image block
- [x] content_quote.html - Blockquote with border accent
- [x] content_richtext.html - Prose-styled rich text
- [x] content_spacer.html - Vertical spacing block
- [x] faq.html - Accordion with grid transitions
- [x] gallery.html - Image grid with zoom effect
- [x] hero_gradient.html - Gradient hero with radial backgrounds
- [x] hero_image.html - Hero with image and content columns
- [x] portfolio.html - Portfolio grid with categories
- [x] process_steps.html - Timeline/process visualization
- [x] quote_request_form.html - Quote form with validation
- [x] rich_text.html - Full-width prose content
- [x] service_cards.html - Service grid with hover effects
- [x] stats.html - Statistics counter display
- [x] testimonials.html - Testimonial cards
- [x] trust_strip_logos.html - Logo grid (clients/partners)

**Verify**: All 20 files exist and use Tailwind utility classes (no vanilla CSS classes)

```bash
# Quick verification
ls -1 core/sum_core/themes/theme_a/templates/sum_core/blocks/*.html | wc -l
# Should output: 21 (20 blocks + .gitkeep shows as 20 .html files)

# Check for vanilla CSS classes (should find NONE in block templates)
grep -r "class=\"card " core/sum_core/themes/theme_a/templates/sum_core/blocks/
# Expected: No matches (all use Tailwind)
```

---

### 2. Tailwind Configuration
**Location**: `core/sum_core/themes/theme_a/tailwind.config.js`

**Critical Fix**: Content paths must include block template directory

```javascript
content: [
  './templates/theme/**/*.html',      // ✅ Theme-level templates
  './templates/sum_core/**/*.html',   // ✅ CRITICAL: Block overrides
  '../../templates/**/*.html'         // ✅ Core fallbacks
]
```

**Plugins Required**:
```javascript
plugins: [
  require('@tailwindcss/typography')  // ✅ For prose classes
]
```

**Typography Config**:
```javascript
typography: {
  DEFAULT: {
    css: {
      '--tw-prose-body': 'rgba(26, 47, 35, 0.9)',
      '--tw-prose-headings': '#1a2f23',
      '--tw-prose-links': '#a0563b',
      // ... (full config in file)
    }
  }
}
```

**Verify**:
```bash
# Check content paths
grep "templates/sum_core" core/sum_core/themes/theme_a/tailwind.config.js

# Check typography plugin
grep "@tailwindcss/typography" core/sum_core/themes/theme_a/tailwind.config.js
```

---

### 3. NPM Dependencies
**Location**: `core/sum_core/themes/theme_a/package.json`

**Required Packages**:
```json
{
  "devDependencies": {
    "@tailwindcss/typography": "^0.5.19",  // ✅ Installed
    "tailwindcss": "^3.4.17"               // ✅ Installed
  }
}
```

**Verify**:
```bash
cd core/sum_core/themes/theme_a
npm list --depth=0
# Should show both packages
```

---

### 4. Compiled CSS
**Location**: `core/sum_core/themes/theme_a/static/theme_a/css/main.css`

**Expected State**:
- File size: ~54KB (minified with all utilities)
- Contains prose classes: `.prose`, `.prose-lg`, etc.
- Contains common utilities: `.max-w-4xl`, `.rounded-xl`, `.shadow-md`, etc.
- Contains custom classes: `.section`, `.btn`, `.hero`, etc.

**Verify**:
```bash
# Check file size (should be ~54KB)
ls -lh core/sum_core/themes/theme_a/static/theme_a/css/main.css

# Check for prose classes
grep "\.prose" core/sum_core/themes/theme_a/static/theme_a/css/main.css | head -5

# Check for utility classes
grep -E "\.max-w-4xl|\.rounded-xl|\.shadow-md" core/sum_core/themes/theme_a/static/theme_a/css/main.css | head -3
```

**If CSS Needs Rebuild**:
```bash
cd core/sum_core/themes/theme_a
npm run build
# Should complete in ~1.7s with "Done in XXXXms"
```

---

### 5. Header Template
**Location**: `core/sum_core/themes/theme_a/templates/theme/includes/header.html`

**Fixes Applied**:
- ✅ Removed `established_year` field reference (no more "Est. 2025")
- ✅ Changed text colors: `text-sage-linen` → `text-sage-black` (visibility fix)
- ✅ Added header background: `bg-sage-linen/95 backdrop-blur-sm`
- ✅ Fixed accessibility (skip link, ARIA attributes)

**Verify**:
```bash
# Should NOT find established_year
grep "established_year" core/sum_core/themes/theme_a/templates/theme/includes/header.html
# Expected: No matches

# Should find dark text color
grep "text-sage-black" core/sum_core/themes/theme_a/templates/theme/includes/header.html
# Expected: Multiple matches
```

---

### 6. Base Template
**Location**: `core/sum_core/themes/theme_a/templates/theme/base.html`

**Fixes Applied**:
- ✅ Added `pt-24` to `<main>` element (accounts for fixed header)
- ✅ Loads compiled CSS: `{% static 'theme_a/css/main.css' %}`
- ✅ Loads theme JS: `{% static 'theme_a/js/main.js' %}`

**Verify**:
```bash
# Check for pt-24 on main element
grep '<main.*pt-24' core/sum_core/themes/theme_a/templates/theme/base.html
# Expected: <main id="main" class="pt-24">
```

---

### 7. Footer Template
**Location**: `core/sum_core/themes/theme_a/templates/theme/includes/footer.html`

**Fixes Applied**:
- ✅ Improved copyright rendering
- ✅ Conditional company name display
- ✅ Tailwind utility classes

**No specific verification needed** (minor improvements)

---

### 8. Template Tags (Copyright Fix)
**Location**: `core/sum_core/navigation/templatetags/navigation_tags.py`

**Fix Applied**:
- ✅ Regex cleanup: `"© 2025 . All rights"` → `"© 2025. All rights"`

**Verify**:
```bash
# Check for regex replacement
grep -A5 "def copyright" core/sum_core/navigation/templatetags/navigation_tags.py | grep "re.sub"
# Expected: Should find regex pattern
```

---

### 9. Sticky CTA Template
**Location**: `core/sum_core/themes/theme_a/templates/theme/includes/sticky_cta.html`

**Fix Applied**:
- ✅ Improved conditional: only shows if actually configured
- ✅ Checks for phone_number OR valid button_href (not just "#")

**No specific verification needed** (minor improvement)

---

## 🚀 PRE-INIT VERIFICATION COMMANDS

Run these commands to verify everything is ready:

```bash
# 1. Count block templates (should be 20)
find core/sum_core/themes/theme_a/templates/sum_core/blocks -name "*.html" | wc -l

# 2. Verify Tailwind config has correct content paths
grep -q "templates/sum_core/\*\*/\*.html" core/sum_core/themes/theme_a/tailwind.config.js && echo "✅ Config OK" || echo "❌ Config BROKEN"

# 3. Verify typography plugin installed
grep -q "@tailwindcss/typography" core/sum_core/themes/theme_a/package.json && echo "✅ Plugin OK" || echo "❌ Plugin MISSING"

# 4. Verify CSS is compiled and has prose classes
grep -q "\.prose{" core/sum_core/themes/theme_a/static/theme_a/css/main.css && echo "✅ CSS OK" || echo "❌ CSS BROKEN"

# 5. Verify header doesn't have established_year
! grep -q "established_year" core/sum_core/themes/theme_a/templates/theme/includes/header.html && echo "✅ Header OK" || echo "❌ Header BROKEN"

# 6. Verify main has pt-24 padding
grep -q 'pt-24' core/sum_core/themes/theme_a/templates/theme/base.html && echo "✅ Layout OK" || echo "❌ Layout BROKEN"
```

**Expected Output**: All should show ✅

---

## 🎯 WHAT TO EXPECT AFTER `sum init`

After running `sum init --theme theme_a project-name`:

### 1. Files Copied to Client Project
The CLI will copy ALL theme files using `shutil.copytree()`:
- `theme/active/templates/` (including `sum_core/blocks/` overrides)
- `theme/active/static/` (including compiled main.css)
- `theme/active/tailwind.config.js` (with fixed content paths)
- `theme/active/package.json` (with typography plugin)

### 2. What Should Work Immediately
- ✅ Header visible (dark text on light background)
- ✅ Layout correct (content not hidden under fixed header)
- ✅ All StreamField blocks styled with Tailwind
- ✅ Rich text content has prose styling
- ✅ No "Est. 2025" in header
- ✅ Copyright displays correctly

### 3. Browser Check (After Server Starts)
1. Open browser dev tools (F12)
2. Check Console: Should see NO CSS-related errors
3. Check Network tab: `main.css` should load (54KB, status 200)
4. Inspect any block element: Should see Tailwind utility classes
5. Check rich text: Should see `.prose` classes applied

---

## 🐛 TROUBLESHOOTING (If Things Still Look Wrong)

### Problem: Blocks Still Look Unstyled
**Likely Cause**: CSS cached in browser

**Solution**:
```
Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

### Problem: "Est. 2025" Still Shows
**Likely Cause**: Template cached or old theme files in client project

**Solution**:
```bash
# Delete client project and re-init
rm -rf test-client-project/
sum init --theme theme_a test-client-project
```

### Problem: Prose Classes Don't Style Text
**Likely Cause**: Typography plugin missing or CSS not rebuilt

**Solution**:
```bash
cd core/sum_core/themes/theme_a
npm install -D @tailwindcss/typography
npm run build
# Then re-init client project
```

### Problem: Specific Utility Class Missing
**Likely Cause**: Class used in template but Tailwind config doesn't scan that file

**Solution**:
1. Check if template is in content paths
2. Rebuild CSS
3. Verify class exists: `grep "\.your-class" main.css`

---

## 📝 COMMIT CHECKLIST

Before committing these changes:

- [x] All 20 block templates created
- [x] tailwind.config.js content paths fixed
- [x] Typography plugin installed in package.json
- [x] CSS rebuilt and verified (54KB, prose classes present)
- [x] Header fixed (no established_year, visible text)
- [x] Base template has pt-24 on main
- [x] Copyright tag fixed (regex cleanup)
- [x] Sticky CTA conditional improved
- [x] Documentation updated (this file + UNFUCK-THEME-MISSION.md)

**Commit Message Template**:
```
fix(theme_a): complete Tailwind migration for all StreamField blocks

- Created 20 block template overrides with Tailwind classes
- Fixed Tailwind config content paths to include block templates
- Installed @tailwindcss/typography plugin for prose styling
- Rebuilt CSS (54KB) with all utility classes compiled
- Fixed header visibility and removed hardcoded established_year
- Fixed layout with pt-24 on main element
- Improved copyright rendering and sticky CTA conditionals

CRITICAL: tailwind.config.js must include './templates/sum_core/**/*.html'
in content paths or all block utility classes will be tree-shaken out.

Closes: #M0-XXX (theme A styling issues)
```

---

## 🎉 YOU'RE READY!

If all verification commands pass with ✅, you can confidently run:

```bash
sum init --theme theme_a my-new-client-project
```

Everything should work perfectly in the new project. No more iterations needed! 🚀
