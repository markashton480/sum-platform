# Full Verification

**Purpose:** Comprehensive verification before declaring a site production-ready (30–60 minutes).  
**When to use:** After major upgrades, before production launch, or after significant changes.

---

## Overview

Full verification goes **beyond smoke tests** to verify:

- Navigation and content rendering across page types
- SEO baseline (metadata, sitemap, robots.txt)
- Block rendering spot checks
- Performance and accessibility basics

**Not a replacement for QA testing** — this is operational verification, not feature testing.

---

## Prerequisites

- [ ] Smoke tests passed (see [`smoke-tests.md`](smoke-tests.md))
- [ ] Site accessible via domain
- [ ] Admin credentials available
- [ ] Time allocated (30–60 min)

---

## Delta Section: What Changed Since Last Tag?

**Before running full verification, identify what changed.**

### Review release notes or Git log

```bash
# View changes between tags
git log v0.6.0..v0.6.1 --oneline
```

**Focus verification on:**

- New features introduced
- Blocks/pages added or modified
- SEO changes
- Performance optimizations

**Document what to focus on:**

**Example:**

- `v0.6.0` → `v0.6.1`: Added blog pages, dynamic forms, Theme A
  - **Focus:** Blog listing/detail pages, form submissions, new theme rendering

---

## Core Verification Checklist

### 1. Homepage and Core Pages

**Purpose:** Verify primary content renders correctly.

**Manual checks:**

- [ ] Homepage loads without errors
- [ ] Hero block displays correctly (if applicable)
- [ ] Key CTAs are visible and functional
- [ ] Images load (no broken images)
- [ ] Navigation menu renders (header, footer)
- [ ] Sticky CTA appears (mobile, if applicable)

**Browser check:**

- Desktop (Chrome/Firefox)
- Mobile (responsive design functional)

**✅ Pass if:** All core elements render, no visual breaks  
**❌ Flag if:** Missing content, layout breaks, broken images

---

### 2. Navigation Sanity

**Purpose:** Verify navigation structure works across levels.

**Manual checks:**

- [ ] Top-level menu items render
- [ ] Dropdown menus work (if multi-level nav)
- [ ] Footer links render and are clickable
- [ ] Mobile menu toggle works
- [ ] All navigation links resolve (no 404s)

**Spot check:**

- Click 3–5 random navigation links
- Verify pages load without errors

**✅ Pass if:** Navigation functional, no broken links  
**❌ Flag if:** Broken links, missing menu items, mobile menu broken

---

### 3. SEO Basics

**Purpose:** Verify technical SEO is functional.

#### 3.1 Meta Tags

**Check on 2–3 pages:**

**Homepage:**

```bash
curl -s "https://${DOMAIN}/" | grep -i "<title>"
curl -s "https://${DOMAIN}/" | grep -i "meta name=\"description\""
```

**Expected:**

- `<title>` present and reasonable
- `<meta name="description">` present

**Service/Standard page:**

- Check a service page or standard page
- Verify title and description unique per page

**✅ Pass if:** Title and description tags present on all checked pages  
**❌ Flag if:** Missing tags, duplicate titles across pages

---

#### 3.2 Sitemap

**Test:**

```bash
curl -I "https://${DOMAIN}/sitemap.xml"
```

**Expected:**

```
HTTP/2 200
Content-Type: application/xml
```

**Manual check:**

- Open `https://<domain>/sitemap.xml` in browser
- Verify pages listed (homepage, service pages, etc.)
- Check `<lastmod>` dates are reasonable

**✅ Pass if:** Sitemap loads, includes expected pages  
**❌ Flag if:** 404, empty sitemap, missing critical pages

---

#### 3.3 Robots.txt

**Test:**

```bash
curl "https://${DOMAIN}/robots.txt"
```

**Expected:**

```
User-agent: *
Disallow: /admin/
Sitemap: https://<domain>/sitemap.xml
```

**✅ Pass if:** robots.txt loads, includes sitemap reference  
**❌ Flag if:** 404, missing sitemap reference

---

### 4. Content and Block Rendering

**Purpose:** Spot-check that StreamField blocks render correctly.

**Manual checks (pick 2–3 pages with blocks):**

- [ ] Hero blocks display (image, text, CTA)
- [ ] Content blocks render (text, images, layout correct)
- [ ] Testimonial blocks display (if applicable)
- [ ] Gallery blocks functional (if applicable)
- [ ] FAQ accordion blocks work (expand/collapse)
- [ ] Service card blocks render (if applicable)

**✅ Pass if:** Blocks render as expected, no layout breaks  
**❌ Flag if:** Missing content, broken layout, images not loading

---

### 5. Forms and Lead Capture

**Purpose:** Verify lead capture pipeline end-to-end.

**⚠️ Skip if no forms deployed.**

**Manual test:**

1. Navigate to page with form (homepage CTA, contact page, etc.)
2. Fill in form with **test data** (use test email)
3. Submit form

**Expected:**

- Success message displayed
- No errors
- Redirect or confirmation shown

**Admin verification:**

- Log into Wagtail admin
- Navigate to Leads section
- Verify test lead captured
- Check all form fields saved correctly

**✅ Pass if:** Form submits successfully, lead appears in admin  
**❌ Flag if:** Submission errors, lead not saved, missing fields

---

### 6. Admin Interface

**Purpose:** Verify Wagtail admin is functional.

**Manual checks:**

- [ ] Admin login works (`/admin/`)
- [ ] Dashboard loads without errors
- [ ] Pages section loads (can view pages tree)
- [ ] Can create a new page (don't publish, just test)
- [ ] Can edit an existing page
- [ ] Snippets accessible (if applicable)
- [ ] Settings accessible (SiteSettings)

**✅ Pass if:** Admin fully functional, no errors  
**❌ Flag if:** Login fails, sections inaccessible, errors on page load

---

### 7. Performance and Accessibility Spot Check

**Purpose:** Basic Lighthouse audit to catch regressions.

**Tool:** Chrome DevTools Lighthouse

**Test:**

1. Open homepage in Chrome
2. Open DevTools (F12)
3. Go to Lighthouse tab
4. Run audit (mobile or desktop)

**Expected scores (post-MVP baseline):**

- **Performance:** ≥ 90
- **Accessibility:** ≥ 90
- **SEO:** ≥ 90

**✅ Pass if:** Scores meet or exceed baseline  
**❌ Flag if:** Scores significantly below baseline (investigate)

**Common issues:**

- Performance: Unoptimized images, large CSS/JS bundles
- Accessibility: Missing alt text, poor contrast, missing ARIA labels
- SEO: Missing meta tags, broken links

---

## What Changed Focus

**Based on delta section, check:**

### If blog added:

- [ ] Blog listing page renders (`/blog/`)
- [ ] Blog post pages render
- [ ] Categories display correctly
- [ ] Reading time displays
- [ ] Featured images load

### If dynamic forms added:

- [ ] FormDefinition appears in admin (Snippets)
- [ ] Can create new form definition
- [ ] DynamicFormBlock appears in page editor
- [ ] Form submissions save to Leads

### If theme changed:

- [ ] New theme applies correctly
- [ ] Branding (colors, fonts, logo) displays
- [ ] Layout consistent across pages
- [ ] Mobile responsive

---

## End Section: What Broke / What Surprised / What to Automate Next

**After verification, answer these questions:**

### What broke?

**Did anything fail verification?**

- List specific issues found
- For each: severity (critical / minor)
- For each: resolution status (fixed / deferred)

**Example:**

- ❌ Sitemap missing service pages (critical) — **FIXED**
- ⚠️ Lighthouse performance score 85 (minor) — **DEFERRED** (optimize images in next sprint)

---

### What surprised?

**Unexpected behavior (good or bad):**

- Things that worked better than expected
- Things that behaved differently than assumed
- Edge cases discovered

**Example:**

- ✅ Blog pagination worked without issues (expected manual tuning needed)
- ⚠️ Footer rendering slowly on mobile (investigate caching)

---

### What to automate next?

**Which checks could be automated?**

- Lighthouse CI for performance regression detection
- Automated sitemap validation
- Form submission test (Playwright/Selenium)
- Link checker (crawl site for 404s)

**Prioritize based on:**

- Time spent on manual check
- Frequency of regressions

---

## Record Results

### Update loop sites matrix

Open [`loop-sites-matrix.md`](loop-sites-matrix.md) and update:

- Full verification: Pass / Partial Pass / Fail
- Date verified
- Notes (issues found, resolved, deferred)

---

### Log issues

Open [`what-broke-last-time.md`](what-broke-last-time.md) and append any issues:

- **Check failed:** `<which check>`
- **Symptom:** `<description>`
- **Fix:** `<resolution>`
- **Follow-up:** `<automation idea>`

---

## Checklist Summary

- [ ] Delta section completed (reviewed what changed)
- [ ] Homepage and core pages verified
- [ ] Navigation sanity checked
- [ ] SEO basics verified (meta tags, sitemap, robots.txt)
- [ ] Content and blocks render correctly
- [ ] Forms and lead capture tested
- [ ] Admin interface functional
- [ ] Lighthouse audit run (performance/a11y/SEO)
- [ ] Delta-specific checks completed
- [ ] "What broke / surprised / automate" section documented
- [ ] Loop sites matrix updated
- [ ] Issues logged

---

## Next Steps

**If full verification passes:**

- ✅ Site is **production-ready**
- Deploy to production (if staging) or monitor in production
- Schedule next verification (after next major change)

**If issues found:**

- Fix critical issues before production
- Document minor issues for next sprint
- Re-run verification after fixes

---

**END OF VERIFICATION**
