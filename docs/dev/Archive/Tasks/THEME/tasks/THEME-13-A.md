# THEME-014 — PortfolioBlock template: lock to reference markup (no “design interpretation”)

## Mission

Update `themes/theme_a/templates/sum_core/blocks/portfolio.html` so the rendered HTML structure + Tailwind classes match the reference snippet you provided (light gallery section), while preserving the block’s dynamic fields and metadata fallback logic.

This is a **visual correction** ticket: the goal is “looks like the reference”, not “roughly similar”.

## Source of truth

* `new-theme-plan.md` Task 6 (mobile scroll + fade + metadata rules) 
* **Reference HTML**:

```HTML
    <section id="gallery" class="py-24 bg-sage-linen">
        <div class="max-w-7xl mx-auto px-6 mb-12 flex justify-between items-end">
            <div>
                <span class="text-sage-terra font-accent italic text-2xl block mb-2">Portfolio</span>
                <h2 class="font-display text-4xl text-sage-black">Case Files</h2>
            </div>
            <a href="#" class="hidden md:block text-xs font-bold uppercase tracking-widest border-b border-sage-black/20 pb-1 hover:border-sage-terra transition-colors py-2">View Full Archive</a>
        </div>

        <div class="relative">
            <div class="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-sage-linen to-transparent pointer-events-none md:hidden z-10"></div>

            <div class="flex overflow-x-auto md:grid md:grid-cols-3 gap-8 px-6 md:px-0 md:max-w-7xl md:mx-auto pb-8 md:pb-0 no-scrollbar snap-x snap-mandatory">

                <!-- Case File 1 -->
                <a href="#" class="block min-w-[85vw] md:min-w-0 relative group cursor-pointer snap-center reveal focus:outline-none focus:ring-4 focus:ring-sage-terra">
                    <div class="aspect-[4/3] overflow-hidden bg-sage-oat mb-6">
                        <!-- REPLACE: assets/case-study-1.jpg -->
                        <img src="images/3hEGHI4b4gg.jpg" alt="The Kensington Commission kitchen view" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105">
                    </div>
                    <div class="border-t border-sage-black/20 pt-4">
                        <h3 class="font-display text-2xl text-sage-black mb-2 group-hover:text-sage-terra transition-colors">The Kensington Commission</h3>
                        <div class="grid grid-cols-2 gap-y-2 gap-x-4 text-xs font-display text-sage-black/70">
                            <span>Constraint:</span> <span class="text-sage-black">Grade II Listed</span>
                            <span>Material:</span> <span class="text-sage-black">Fumed Oak</span>
                            <span>Outcome:</span> <span class="text-sage-black">Zero Alterations</span>
                        </div>
                    </div>
                </a>

                <!-- Case File 2 -->
                <a href="#" class="block min-w-[85vw] md:min-w-0 relative group cursor-pointer snap-center reveal delay-100 focus:outline-none focus:ring-4 focus:ring-sage-terra">
                    <div class="aspect-[4/3] overflow-hidden bg-sage-oat mb-6">
                        <!-- REPLACE: assets/case-study-2.jpg -->
                        <img src="images/Cw5_evbWyI.jpg" alt="The Cotswold Barn rustic kitchen" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105">
                    </div>
                    <div class="border-t border-sage-black/20 pt-4">
                        <h3 class="font-display text-2xl text-sage-black mb-2 group-hover:text-sage-terra transition-colors">The Cotswold Barn</h3>
                        <div class="grid grid-cols-2 gap-y-2 gap-x-4 text-xs font-display text-sage-black/70">
                            <span>Constraint:</span> <span class="text-sage-black">Uneven Stone</span>
                            <span>Material:</span> <span class="text-sage-black">Reclaimed Elm</span>
                            <span>Outcome:</span> <span class="text-sage-black">Scribed to Fit</span>
                        </div>
                    </div>
                </a>

                <!-- Case File 3 -->
                <a href="#" class="block min-w-[85vw] md:min-w-0 relative group cursor-pointer snap-center reveal delay-200 focus:outline-none focus:ring-4 focus:ring-sage-terra">
                    <div class="aspect-[4/3] overflow-hidden bg-sage-oat mb-6">
                        <!-- REPLACE: assets/case-study-3.jpg -->
                        <img src="images/VgyN_CWXQVM.jpg" alt="The Georgian Townhouse minimalistic kitchen" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105">
                    </div>
                    <div class="border-t border-sage-black/20 pt-4">
                        <h3 class="font-display text-2xl text-sage-black mb-2 group-hover:text-sage-terra transition-colors">The Georgian Townhouse</h3>
                        <div class="grid grid-cols-2 gap-y-2 gap-x-4 text-xs font-display text-sage-black/70">
                            <span>Constraint:</span> <span class="text-sage-black">Awkward Chimney</span>
                            <span>Material:</span> <span class="text-sage-black">Painted Poplar</span>
                            <span>Outcome:</span> <span class="text-sage-black">Seamless Wrap</span>
                        </div>
                    </div>
                </a>

            </div>
        </div>
    </section>
```

## What must change (diff-level guidance)

### 1) Section wrapper must match reference

Replace the current:

* `bg-sage-darkmoss text-sage-linen`

with reference:

* `py-24 bg-sage-linen`

No dark section styling here.

Add `data-block-id="{{ block.id }}"` rather than changing the id.

### 2) Header must match reference structure and classes

Reference header wrapper:

```html
<div class="max-w-7xl mx-auto px-6 mb-12 flex justify-between items-end">
```

* Eyebrow: `text-sage-terra font-accent italic text-2xl block mb-2`
* Heading: `font-display text-4xl text-sage-black`
* View all link: `hidden md:block text-xs font-bold uppercase tracking-widest border-b border-sage-black/20 pb-1 hover:border-sage-terra transition-colors py-2`

Current implementation has different sizing, colors, and link treatment — replace to match reference.

### 3) Scroll container must match reference classes

Reference container:

```html
<div class="flex overflow-x-auto md:grid md:grid-cols-3 gap-8 px-6 md:px-0 md:max-w-7xl md:mx-auto pb-8 md:pb-0 no-scrollbar snap-x snap-mandatory">
```

Current implementation uses `-mx-4 px-4` and different snapping — replace to match reference.

**Important:** ensure `no-scrollbar` actually exists. If it doesn’t, add a small Tailwind utility (in theme CSS) rather than inventing a different class name.

### 4) Edge fade overlay must match reference

Reference:

```html
<div class="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-sage-linen to-transparent pointer-events-none md:hidden z-10"></div>
```

Current overlay uses `from-sage-darkmoss` and lacks z-index positioning details — replace.

### 5) Cards must match reference markup + interaction

Reference cards are basically:

* Wrapper is an `<a>` (or a non-link element with identical classes if no `link_url`)
* Classes:

  * `block min-w-[85vw] md:min-w-0 relative group cursor-pointer snap-center reveal`
  * focus: `focus:outline-none focus:ring-4 focus:ring-sage-terra`

Image wrapper:

* `aspect-[4/3] overflow-hidden bg-sage-oat mb-6`
* image: `transition-transform duration-700 group-hover:scale-105`

Text wrapper:

* `border-t border-sage-black/20 pt-4`
* title: `font-display text-2xl text-sage-black mb-2 group-hover:text-sage-terra transition-colors`
* metadata grid: `grid grid-cols-2 gap-y-2 gap-x-4 text-xs font-display text-sage-black/70`

  * label span e.g. `Constraint:` and value span `class="text-sage-black"`

Your current implementation changed this into an uppercase label/value block UI — it needs to be reverted to the reference layout.

### 6) Metadata logic stays, but render in reference format

Keep the logic:

* Prefer constraint/material/outcome
* Fallback to location/services

But render as **label span + value span pairs**, like the reference.

### 7) Reveal delays (nice-to-have but reference includes)

Reference adds `delay-100` and `delay-200` on items 2 and 3. Apply that based on `forloop.counter`:

* 1 → `reveal`
* 2 → `reveal delay-100`
* 3 → `reveal delay-200`

## Tests (update existing, don’t delete history)

Update `tests/themes/test_theme_a_portfolio_rendering.py` so it asserts **reference markers**, e.g.:

* section has `bg-sage-linen`
* header wrapper has `max-w-7xl mx-auto px-6 mb-12 flex justify-between items-end`
* view-all link has `hidden md:block` and border classes
* scroll container has `no-scrollbar snap-x snap-mandatory`
* card wrapper includes `snap-center` and `focus:ring-4 focus:ring-sage-terra`
* image wrapper includes `bg-sage-oat mb-6`
* title hover includes `group-hover:text-sage-terra`
* metadata grid uses `text-xs font-display text-sage-black/70`

Run:

* `pytest tests/themes/test_theme_a_portfolio_rendering.py`
* `make test`

## Build artifacts

Only rebuild Tailwind + fingerprint if you:

* introduce a new utility (e.g., implementing `no-scrollbar`), or
* add classes that aren’t currently in the compiled CSS.

Otherwise, template-only change may still require rebuild depending on how aggressively Tailwind is scanning templates in your build pipeline — follow your established rule of “if class isn’t in main.css, rebuild”.

## Work Report

When you're done, file a full, comprehensive work report in `THEME-13-A_followup.md` (same directory)

## Notes

- activate .venv if needed for tests
- see `Makefile` and `README.md` and `AGENTS.md`if you're stuck, lost or confused.

## Acceptance criteria

* Portfolio section visually matches the reference snippet (light linen background, black text, border-top cards, correct spacing, fade overlay).
* Mobile scroll + fade works; desktop is 3 columns.
* Hover image zoom and title color change match reference.
* Focus ring present and visible.
* Tests updated + full suite passes.

---
