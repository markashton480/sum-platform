# Theme A Fix Plan - Wireframe to Wagtail Mapping

**Problem:** Theme A block templates don't match wireframe closely enough  
**Solution:** Map wireframe components to blocks, fix templates to match exactly  
**Priority:** Hero, Manifesto, Portfolio (featured + cards), Trust Strip

---

## Part 1: Fast Iteration Setup (Do This First)

### Change test_project to point directly at theme_a

**File:** `core/sum_core/test_project/test_project/settings.py`

**Find this:**
```python
THEME_TEMPLATES_DIR: Path = BASE_DIR / "theme" / "active" / "templates"
```

**Change to:**
```python
THEME_TEMPLATES_DIR: Path = BASE_DIR.parent.parent.parent / "themes" / "theme_a" / "templates"
```

**This means:**
- Edit files in `themes/theme_a/templates/`
- test_project sees changes immediately
- No copying, no syncing
- Fast iteration loop

---

## Part 2: Wireframe → Block Mapping (Priority Blocks)

### 1. Hero Section

**Wireframe:** `index.html` lines 317-353

**Structure:**
```html
<section class="relative h-screen min-h-[700px] flex items-center justify-center overflow-hidden bg-sage-black">
  <!-- Background image with parallax -->
  <div class="absolute inset-0">
    <img src="..." class="w-full h-[120%] object-cover object-center -translate-y-10">
    <div class="absolute inset-0 bg-black/60"></div> <!-- Dark overlay -->
  </div>
  
  <!-- Content -->
  <div class="relative z-10 text-center px-4 max-w-5xl mx-auto mt-20">
    <p class="font-accent text-sage-oat text-xl italic mb-6">Trends are loud. Legacy is quiet.</p>
    <h1 class="font-display text-5xl md:text-7xl lg:text-8xl text-sage-linen mb-8">
      Rooms that <br/> <span class="italic text-sage-oat">remember.</span>
    </h1>
    <p class="text-sage-linen max-w-lg mx-auto mb-12 text-base md:text-lg">
      We don't make kitchens. We curate the cultural artifacts...
    </p>
    
    <!-- CTAs -->
    <div class="flex flex-col sm:flex-row gap-6">
      <!-- Primary CTA -->
      <a href="#contact" class="bg-sage-terra text-white px-12 py-5 uppercase...">
        Begin Your Commission
      </a>
      <!-- Secondary CTA -->
      <a href="#manifesto" class="border border-sage-linen/30 px-6 py-4...">
        Our Philosophy
      </a>
    </div>
  </div>
</section>
```

**Current Block:** `HeroImageBlock` (from blocks-reference.md)

**Fields Available:**
- `headline` (RichTextBlock)
- `subheadline` (TextBlock)
- `ctas` (ListBlock, max 2)
- `status` (CharBlock) - "eyebrow" text
- `image` (ImageChooserBlock)
- `image_alt`
- `overlay_opacity`
- `floating_card_label/value` (not in wireframe)

**The Problem:**
- Wireframe has: Status text → Headline → Subheadline → 2 CTAs
- Block template probably doesn't match this exact structure/styling

**Action Required:**
1. Create new template: `themes/theme_a/templates/sum_core/blocks/hero_image.html`
2. Match wireframe structure EXACTLY
3. Remove floating card (not in wireframe)
4. Use sage color classes
5. Match typography (font-display, font-accent)

---

### 2. Manifesto Section (Text Content)

**Wireframe:** `index.html` lines 380-400

**Structure:**
```html
<section class="py-24 md:py-32 bg-sage-linen">
  <div class="max-w-3xl mx-auto px-6 text-center">
    <span class="text-sage-terra font-accent italic text-2xl mb-6">The Manifesto</span>
    <h2 class="font-display text-4xl md:text-5xl text-sage-black mb-10">
      Good kitchens don't age.<br>They <span class="italic text-sage-moss">season.</span>
    </h2>
    <div class="prose prose-lg text-sage-black mx-auto font-light leading-relaxed">
      <p class="mb-6">In a market saturated with...</p>
      <p>Our customers don't want...</p>
      <div class="border-t border-sage-black/10 pt-8 mt-8">
        <p class="font-accent italic text-xl text-sage-darkmoss">"We build with solid timber..."</p>
      </div>
    </div>
  </div>
</section>
```

**Current Blocks:** Likely combination of:
- `EditorialHeaderBlock` (eyebrow + heading)
- `RichTextContentBlock` (body text)

**The Problem:**
- This is ONE semantic unit (manifesto section)
- Might be split across 2 blocks currently
- Styling doesn't match centered, prose-heavy layout

**Action Required:**
1. Update `EditorialHeaderBlock` template to match wireframe styling
2. Update `RichTextContentBlock` template for center-aligned prose
3. OR: Create single `ManifestoBlock` if this is a reusable pattern

---

### 3. Portfolio Cards Grid

**Wireframe:** `index.html` lines 527-591

**Structure:**
```html
<section class="py-24 bg-sage-linen">
  <!-- Header -->
  <div class="max-w-7xl mx-auto px-6 mb-12 flex justify-between items-end">
    <div>
      <span class="text-sage-terra font-accent italic text-2xl">Portfolio</span>
      <h2 class="font-display text-4xl text-sage-black">Case Files</h2>
    </div>
    <a href="#">View Full Archive</a>
  </div>

  <!-- Grid (horizontal scroll on mobile, 3-col on desktop) -->
  <div class="flex overflow-x-auto md:grid md:grid-cols-3 gap-8 px-6">
    
    <!-- Card -->
    <a href="#" class="block min-w-[85vw] md:min-w-0 relative group">
      <div class="aspect-[4/3] overflow-hidden bg-sage-oat mb-6">
        <img src="..." class="group-hover:scale-105 transition">
      </div>
      <div class="border-t border-sage-black/20 pt-4">
        <h3 class="font-display text-2xl text-sage-black group-hover:text-sage-terra">
          The Kensington Commission
        </h3>
        <div class="grid grid-cols-2 gap-y-2 text-xs font-display text-sage-black/70">
          <span>Constraint:</span> <span>Grade II Listed</span>
          <span>Material:</span> <span>Fumed Oak</span>
          <span>Outcome:</span> <span>Zero Alterations</span>
        </div>
      </div>
    </a>
    
    <!-- Repeat for 3 cards -->
  </div>
</section>
```

**Current Block:** `PortfolioBlock`

**Fields Available (from blocks-reference.md):**
- `eyebrow`
- `heading`
- `intro`
- `items` (ListBlock of PortfolioItemBlock)
  - `image`, `alt_text`, `title`, `location`, `services`, `link_url`

**The Problem:**
- Wireframe uses "Constraint/Material/Outcome" metadata
- Block has "location/services" metadata  
- Wireframe has specific card styling with hover states
- Horizontal scroll on mobile might not be implemented

**Action Required:**
1. Update `PortfolioBlock` Python: Add fields for constraint/material/outcome
2. Create new template: `themes/theme_a/templates/sum_core/blocks/portfolio.html`
3. Match wireframe card structure exactly
4. Implement horizontal scroll on mobile with gradient fade
5. Match typography and spacing

---

### 4. Featured Case Study (Split Layout)

**Wireframe:** `index.html` lines 594-624 (estimated, after portfolio grid)

**Structure:**
```html
<section class="py-24 bg-sage-oat/20">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
      
      <!-- Image Side -->
      <div class="aspect-[4/5] overflow-hidden bg-sage-black/5 shadow-xl">
        <img src="..." class="w-full h-full object-cover">
        
        <!-- Floating card with stats/date -->
        <div class="absolute top-8 right-8 bg-sage-terra text-white p-6">
          <div>Completion</div>
          <div class="text-lg font-bold">OCTOBER 14, 2025</div>
        </div>
        
        <!-- Hover overlay -->
        <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100">
          <span class="bg-sage-linen text-sage-black px-6 py-3 uppercase">
            Inspect Artifact
          </span>
        </div>
      </div>

      <!-- Content Side -->
      <div>
        <span class="text-sage-moss uppercase text-xs mb-4">The Signature Experience</span>
        <h2 class="font-display text-4xl md:text-5xl mb-6">The Provenance Plate</h2>
        <p class="text-sage-linen text-lg leading-relaxed mb-8">
          Every Sage & Stone kitchen includes...
        </p>
        <ul class="space-y-4 mb-10">
          <li class="flex items-start">
            <span class="text-sage-terra mr-4 font-serif italic text-xl">1.</span>
            <span>The name of the Maker...</span>
          </li>
          <!-- More list items -->
        </ul>
        <button class="border-b-2 border-sage-terra text-sage-terra">
          Inspect the Artifact
        </button>
      </div>
      
    </div>
  </div>
</section>
```

**Current Block:** ??? (Might not exist)

**Closest Match:** Maybe `ImageTextBlock` or need to create `FeaturedCaseStudyBlock`

**Action Required:**
1. Check if this pattern exists as a block
2. If not: Create `FeaturedCaseStudyBlock` in sum_core
3. Create template matching wireframe exactly
4. Implement floating card with stats
5. Implement hover overlay effect

---

### 5. Trust Strip / Accreditations

**Wireframe:** `services.html` lines 629-652

**Structure:**
```html
<section class="py-16 border-t border-sage-black/10">
  <div class="max-w-7xl mx-auto px-6 text-center">
    <span class="text-xs font-bold uppercase tracking-widest text-sage-meta mb-8">
      Certified & Insured
    </span>
    
    <!-- Logos/Names (text-based in wireframe) -->
    <div class="flex flex-wrap justify-center items-center gap-12 md:gap-20 opacity-70">
      <span class="font-display text-2xl text-sage-black">Gas Safe</span>
      <span class="font-display text-2xl text-sage-black">NICEIC</span>
      <span class="font-display text-2xl text-sage-black">BiKBBI</span>
      <span class="font-display text-2xl text-sage-black">Guild of Master Craftsmen</span>
    </div>

    <!-- Additional info grid (optional) -->
    <div class="mt-12 grid grid-cols-1 md:grid-cols-2 max-w-2xl mx-auto gap-6">
      <div>
        <h4 class="font-bold text-sm uppercase mb-2">Warranty</h4>
        <p>Lifetime guarantee on all joinery integrity...</p>
      </div>
      <div>
        <h4 class="font-bold text-sm uppercase mb-2">Liability</h4>
        <p>Comprehensive £5M Public Liability Insurance...</p>
      </div>
    </div>
  </div>
</section>
```

**Current Block:** `TrustStripLogosBlock`

**Fields Available:**
- `eyebrow`
- `items` (ListBlock of TrustStripItemBlock)
  - `logo` (ImageChooserBlock)
  - `alt_text`
  - `url` (optional)

**The Problem:**
- Wireframe uses TEXT logos (font-display text-2xl)
- Block expects IMAGE logos
- Wireframe has optional warranty/liability grid below
- Current template might not match centered, text-based layout

**Action Required:**
1. Update template: `themes/theme_a/templates/sum_core/blocks/trust_strip_logos.html`
2. Support both image logos AND text-only fallback
3. Add centered layout with proper spacing
4. Match opacity (70%) on logo row
5. Consider: Add optional warranty/liability fields to block?

---

## Part 3: Implementation Order

### Phase 1: Setup (15 minutes)
1. ✅ Change test_project settings to point at `themes/theme_a/templates/`
2. ✅ Run test_project: `cd core/sum_core/test_project && python manage.py runserver`
3. ✅ Verify you can edit theme_a templates and see changes immediately

### Phase 2: Hero Block (1-2 hours)
1. Copy wireframe hero HTML structure
2. Map to HeroImageBlock fields
3. Create `themes/theme_a/templates/sum_core/blocks/hero_image.html`
4. Remove S&S branding (use block fields instead)
5. Test with demo content
6. Verify responsive behavior

### Phase 3: Portfolio Blocks (2-3 hours)
1. Update `PortfolioBlock` Python (add constraint/material/outcome fields)
2. Create template matching wireframe cards
3. Implement horizontal scroll on mobile
4. Test hover states
5. Decide on Featured Case Study block (create new or adapt existing)

### Phase 4: Manifesto/Content Blocks (1-2 hours)
1. Update `EditorialHeaderBlock` template
2. Update `RichTextContentBlock` template for centered prose
3. Test combined rendering

### Phase 5: Trust Strip (1 hour)
1. Update `TrustStripLogosBlock` template
2. Support text-only mode
3. Add centered layout
4. Test with both image and text logos

---

## Part 4: Strip S&S Branding

### Files to Update

**Theme templates:**
- Remove hardcoded "Sage & Stone" text
- Remove hardcoded "Est. 2025"
- Remove hardcoded sage color palette references (keep classes)

**Management Command Pattern:**

**Generic Demo:**
```python
# management/commands/load_theme_demo.py
# Creates: Homepage with generic content
# Uses: Block fields WITHOUT specific brand mentions
```

**S&S Demo:**
```python
# management/commands/load_sage_and_stone_demo.py
# Creates: Homepage with S&S content
# Updates: SiteSettings with S&S branding
# Sets: Colors, fonts, business name, "Est. 2025"
# Populates: Content matching wireframe exactly
```

### SiteSettings Fields Needed

Verify these exist:
- `business_name` (e.g., "Sage & Stone")
- `tagline` (e.g., "Rooms that remember")
- `established_year` (NEW FIELD - add via migration)
- Primary/accent colors (already exists in branding system)
- Fonts (might need to add font selection fields)

---

## Part 5: Testing Checklist

For each block:
- [ ] Matches wireframe HTML structure exactly
- [ ] Uses sage color classes correctly
- [ ] Typography matches (font-display, font-accent, font-body)
- [ ] Spacing matches wireframe
- [ ] Hover states work
- [ ] Responsive behavior correct (mobile horizontal scroll, etc.)
- [ ] S&S branding is NOT hardcoded (uses block fields)
- [ ] Accessibility preserved (proper landmarks, alt text, ARIA)

---

## Part 6: Questions to Answer

Before starting implementation:

1. **Portfolio block fields** - Should I create a migration to add constraint/material/outcome fields to PortfolioItemBlock?

2. **Featured case study** - Should this be a new block type or can we adapt an existing one?

3. **established_year** - Should I create migration to add this to SiteSettings?

4. **Font selection** - Should SiteSettings have font family fields or just hardcode in theme?

5. **Manifesto pattern** - Is this a one-off or should we create a reusable ManifestoBlock?

---

## Expected Results

After completing this:

1. ✅ Edit theme_a templates → refresh → see changes (< 5 seconds)
2. ✅ Hero matches wireframe exactly
3. ✅ Portfolio cards match wireframe exactly
4. ✅ Manifesto section matches wireframe exactly
5. ✅ Trust strip matches wireframe exactly
6. ✅ No S&S branding hardcoded in templates
7. ✅ `load_theme_demo` → generic site
8. ✅ `load_sage_and_stone_demo` → S&S branded site
9. ✅ Fast iteration workflow established

---

## Next Steps

Answer the 5 questions above, then I'll create:
1. Exact template code for priority blocks
2. Python code for any new blocks needed
3. Migration code for new fields
4. Management command code for both demo types

Ready when you are.
