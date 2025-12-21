# THEME-015 — StatsBlock template rewrite (Theme A)

**ID:** THEME-015
**Area:** Theme A templates (homepage)
**Phase:** Phase 1 (Day 2–3: priority homepage blocks) 

## Mission

Update Theme A’s StatsBlock template so it matches the Sage & Stone reference (index stats strip, wireframe lines ~356–377). The goal is: **copy the structure + Tailwind classes from the compiled reference HTML**, then replace hardcoded content with dynamic block fields.

## Source of truth

* `new-theme-plan.md` homepage mapping + Phase 1 roadmap
* Block contract: `blocks-reference.md` → StatsBlock + StatItemBlock fields 
* Theme system rules / “don’t rebuild unless needed” are in Theme A README 

## Constraints (non-negotiable)

1. **Theme override only.** Change Theme A template(s), don’t “fix” core rendering logic.
2. **No hardcoded branding values.** Use theme tokens/classes only.
3. **No design interpretation.** Use the compiled reference HTML section as the base; only bind data + conditionals.
4. **Run tests and show evidence** in the work report (required).
5. **Do not rebuild Tailwind / fingerprint unless required** by the Theme A README rules. 

## Discovery step (required, fast)

Open `docs/dev/design/wireframes/sage-and-stone/compiled/index.html` and locate the **stats strip** section (lines ~356–377 per plan). Copy that section’s markup/classes into the Theme A Stats template as the starting point.

## Files to change

1. Theme template:

   * `themes/theme_a/templates/sum_core/blocks/stats.html` (create override if missing)

2. Tests (new):

   * `tests/themes/test_theme_a_stats_rendering.py`

3. Docs (only if needed):

   * If you discover block contract drift vs docs, patch `docs/dev/blocks-reference.md` minimally.

## Implementation requirements

### A) Structure + layout

* Use the reference section wrapper and container classes *exactly* (spacing rhythm, max width, grid, etc).
* Desktop should render as a clean multi-column strip (reference shows 4 metrics).

### B) Content binding (from block contract)

StatsBlock contract (per docs) is: `eyebrow` (optional), `intro` (optional), and `items` (2–4). Each item: `value`, `label`, optional `prefix`/`suffix`. 

Render:

* Eyebrow if present.
* Intro if present.
* For each stat item:

  * Compose displayed value as: `prefix + value + suffix` (only include prefix/suffix if provided).
  * Label under/alongside as per reference.

### C) Accessibility

* Ensure semantics are sensible (e.g., section headings if present; no weird heading nesting).
* No clickable wrappers unless reference indicates it.

## Tests (required)

Create `tests/themes/test_theme_a_stats_rendering.py` similar to other theme rendering tests:

1. **Markers test (structure/classes)**

* Render a StatsBlock with 4 items and assert key reference markers exist (container classes, grid classes, etc).
* Assert that 4 stat “value” outputs exist.

2. **Prefix/suffix composition test**

* Provide an item with prefix and suffix and assert final rendered value includes both.

3. **Optional content test**

* Ensure eyebrow/intro are absent when not set.

### Tests must be run (evidence required)

In the work report, include command outputs (or at least the final pass lines) for:

* `pytest tests/themes/test_theme_a_stats_rendering.py -q`
* `make test`

## Tailwind rebuild policy

Follow Theme A README:

* **Do not rebuild** if you only used classes already present in the scanned reference universe.
* **Rebuild + fingerprint** only if you introduce new utility/component CSS or new class patterns that don’t exist in the current `main.css`. 

## Acceptance criteria

* Stats strip visually matches the compiled reference section for index.html (spacing, layout, typography).
* Uses StatsBlock/StatItemBlock fields exactly as documented. 
* No hardcoded colours/branding.
* Tests added and **run**; full suite passes with evidence.

---

