# SQ-004 Follow-up: CTA Buttons Not Responding to Brand Settings

**Date**: 2025-12-21  
**Status**: ✅ **RESOLVED**  
**Root Cause**: Showroom's theme/active copy had OLD CSS format that didn't consume branding variables

---

## Summary

The CTA buttons were showing the old Sage & Stone terracotta colour instead of the brand settings.

**Root cause confirmed via testing**: The showroom's `theme/active/` copy had a **pre-THEME-010 CSS format** that used `rgb(var(--color-sage-terra,...))` instead of `hsl(var(--brand-h,...))`. This old format completely ignores the branding CSS variables injected by `{% branding_css %}`.

**Proof**: After syncing the canonical CSS to showroom, we changed the fallback to magenta (hue 300) and rebuilt. The site correctly showed the brand colour (not magenta), proving:

1. The new HSL-based CSS format IS consuming the branding variables
2. The `{% branding_css %}` tag IS correctly injecting `--brand-h`, `--brand-s`, `--brand-l`
3. `SUM_CANONICAL_THEME_ROOT` IS serving the canonical CSS correctly

---

## Investigation

### 1. Verified Tailwind Config (Correct)

`themes/theme_a/tailwind/tailwind.config.js` correctly maps `sage.terra` to branding variables:

```javascript
'terra': 'hsl(var(--brand-h, 16) var(--brand-s, 46%) var(--brand-l, 43%) / <alpha-value>)',
```

### 2. Verified branding_tags.py Output (Correct)

The `{% branding_css %}` tag correctly outputs HSL components:

- `--brand-h: {hue};` (just the number)
- `--brand-s: {saturation}%;` (with %)
- `--brand-l: {lightness}%;` (with %)

### 3. Compared Compiled CSS (Found the Issue!)

**Canonical `themes/theme_a/static/theme_a/css/main.css`:**

```css
.bg-sage-terra {
  background-color: hsl(
    var(--brand-h, 16) var(--brand-s, 46%) var(--brand-l, 43%) /...
  );
}
```

✅ Uses branding variables

**Showroom `clients/showroom/theme/active/static/theme_a/css/main.css`:**

```css
.bg-sage-terra {
  background-color: rgb(var(--color-sage-terra, 160 86 59) /...);
}
```

❌ Uses **OLD** hardcoded RGB format!

### 4. Confirmed Fingerprint Mismatch

| Location                    | Fingerprint                                |
| --------------------------- | ------------------------------------------ |
| Canonical `themes/theme_a/` | `f2f1d2d2514cdc057bc9e964fd83eb1a8b23fef1` |
| Showroom `theme/active/`    | `1c0b27baf0586fbf344da7d17d5c412e12e2a2db` |

The showroom had a pre-THEME-010 copy of the CSS.

---

## Fix Applied

Synced the canonical theme CSS to the showroom client:

```bash
cp themes/theme_a/static/theme_a/css/main.css clients/showroom/theme/active/static/theme_a/css/main.css
cp themes/theme_a/static/theme_a/css/input.css clients/showroom/theme/active/static/theme_a/css/input.css
cp themes/theme_a/static/theme_a/css/.build_fingerprint clients/showroom/theme/active/static/theme_a/css/.build_fingerprint
```

After sync, fingerprints match and `.bg-sage-terra` now uses `hsl(var(--brand-h,...))`.

---

## Verification

**To clear browser cache and force-refresh CSS:**

1. **Hard refresh**: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. **Or DevTools**: Open DevTools → Network tab → check "Disable cache" → refresh
3. **Or clear cache**: Browser settings → Clear browsing data → Cached images and files

After hard refresh, CTAs should now respond to SiteSettings brand colour changes.

---

## Systemic Issue Identified

The theme copy model (per THEME-ARCHITECTURE-SPECv1) means that client projects get a **snapshot** of the theme at init-time. When the canonical theme is updated, client copies become stale.

### Important: SUM_CANONICAL_THEME_ROOT DOES work for static files

After investigation, we confirmed that `SUM_CANONICAL_THEME_ROOT` correctly prepends the canonical theme's static directory to `STATICFILES_DIRS`. The magenta test proved the canonical CSS is now being served correctly.

**Remaining mystery**: Before the sync, `findstatic` showed the canonical path first, but the browser was showing the old terracotta. Possible explanations:

1. The canonical CSS itself was rebuilt AFTER `findstatic` was run (timing issue during THEME-010)
2. The dev server may have cached the static file in memory before we ran `findstatic`
3. Something with the specific browser session

Either way, syncing the showroom copy ensures consistency regardless of whether `SUM_CANONICAL_THEME_ROOT` is set.

### Current Workarounds

1. **SUM_CANONICAL_THEME_ROOT override** (SQ-003): For development, point Django directly at the canonical theme source.

2. **Manual sync**: Copy updated theme files to client's `theme/active/` directory:
   ```bash
   cp themes/theme_a/static/theme_a/css/main.css clients/showroom/theme/active/static/theme_a/css/
   ```

### Recommended Future Fix

Add a `sum sync-theme` CLI command that:

1. Detects the current theme from `theme/active/theme.json`
2. Syncs updated files from `themes/<slug>/` to `theme/active/`
3. Preserves any client-specific overrides (if we support that pattern)

This should be a separate task ticket.

---

## ChatGPT's Analysis Review

ChatGPT's analysis in SQ-004.md was **technically correct** – the issue was about CSS variable cascade. However, the actual root cause was simpler: the CSS file itself was old and **didn't even have** the variable-based declarations.

The key diagnostic that would have caught this faster:

```bash
grep -o '\.bg-sage-terra[^}]*}' clients/showroom/theme/active/static/theme_a/css/main.css
```

If this shows `rgb(var(--color-sage-terra,...))` instead of `hsl(var(--brand-h,...))`, the CSS is stale.

---

## Files Modified

- `clients/showroom/theme/active/static/theme_a/css/main.css` (overwritten with canonical)
- `clients/showroom/theme/active/static/theme_a/css/input.css` (overwritten with canonical)
- `clients/showroom/theme/active/static/theme_a/css/.build_fingerprint` (overwritten with canonical)
