# THEME-014-A — Theme A design-system lock: validate breakpoints + reveal strategy + test evidence

**ID:** THEME-014-A
**Area:** Theme A Tailwind system + utilities + guardrails
**Depends on:** THEME-014 (already implemented)
**Primary intent:** Make Phase 1 template work “CSS-quiet” from here onward.

## Context

THEME-014 widened Theme A’s Tailwind “class universe” by scanning the Sage & Stone compiled reference HTML, added `ipad` and a modified `desktop` breakpoint, consolidated bespoke CSS into Tailwind layers, updated reveal utilities, rebuilt CSS/fingerprint, and added guardrail tests + README notes.

Two clarifications are now blocking “lockdown”:

1. **Breakpoints:** `desktop` moved to **1200px** to prevent the header/nav looking awkward on mid-size (iPad-ish / small laptop) widths. This is *intentional* (component-fit), not “reference purity”.
2. **Reveal:** reveal now hides elements until `.active`, which creates a no-JS trap unless we explicitly do progressive enhancement.
3. **Evidence:** Tests were added, but the report doesn’t include **pytest / make test pass evidence**.

This follow-up closes those decisions, confirms we haven’t introduced global breakpoint confusion, and proves the guardrails hold.

---

## Mission

Lock down Theme A’s design system so that subsequent block tickets can be “paste reference Tailwind HTML → swap in template tags” without repeated CSS archaeology.

This ticket is complete only when:

* the breakpoint strategy is explicit and safe,
* reveal behaviour is intentionally decided and robust,
* Tailwind scanning strategy is intentional (and not accidental bloat/coupling),
* **tests are run and evidenced**, not just written.

---

## Non-negotiables

* **Do not edit prior ticket files** (THEME-014 stays as-is). This is a new corrective task.
* **Do not blindly import giant CSS dumps.** Keep bespoke CSS in Tailwind layers and refactor for DRY.
* **Run tests and provide evidence** in the work report.

---

## Tasks

### A) Run tests (evidence required)

Run and include the results in the work report:

1. Targeted:

   * `pytest tests/themes/test_theme_a_css_contract.py -q`

2. Full suite:

   * `make test`

If `make test` is slow, still run it. Report elapsed time and the final summary line(s). No “should pass”.

---

### B) Breakpoint strategy: make it explicit and prevent future confusion

**Intent (given by Mark):** the header/nav shouldn’t switch into “full desktop” mode until there’s enough width, because it looks weird at mid-size. That’s why `desktop` was effectively pushed later.

Now make sure this doesn’t accidentally redefine “desktop” everywhere.

Do this:

1. **Inventory usage**

   * Search for `desktop:` usage in Theme A templates and CSS.
   * Categorise usage:

     * “header/nav layout switch”
     * “general layout/grid spacing”
   * If `desktop:` is used for general layout, that’s likely a risk (1200 may be too late).

2. **Decide and implement one clean approach**
   Pick the smallest change that keeps intent clear:

   **Preferred approach:** keep standard breakpoints for general layout (e.g. Tailwind `lg` / `xl`) and use a *custom* breakpoint only for the header/nav switch.

   * Option 1: introduce a new screen name like `nav` / `wide` at 1200 and migrate header/nav to that, while restoring `desktop` semantics (if `desktop` is widely used).
   * Option 2: keep `desktop=1200` but add a second alias like `laptop=1024` (or rely on `lg`) and migrate *non-header* uses away from `desktop:`.

   The key is: **one breakpoint name should not mean two different things** (general desktop vs full-nav desktop).

3. **Document in Theme A README**
   Add a short “Breakpoints” section:

   * what `ipad` means (where it applies),
   * what triggers the header/nav switch (1200),
   * what to use for general layout (`lg` etc.) so future template tickets don’t misuse `desktop:`.

4. **Validate manually and report**
   Confirm header/nav looks correct at:

   * 1024–1199px (mid-size / awkward zone)
   * ≥1200px (full desktop nav)

Include a short note of what you checked (and ideally one screenshot per range if easy).

---

### C) Reveal strategy: no-JS fallback vs JS-required (choose intentionally)

Right now reveal matches the reference behaviour (“hidden until `.active`”), but that can hide content forever without JS.

Pick one strategy and implement + document it:

**Preferred: Progressive enhancement (recommended)**

* `.reveal` is visible by default.
* Only hide/animate when `<html>` has a class like `.reveal-ready`.
* Ensure `.reveal-ready` is added early (via Theme A JS or a tiny inline script in the base template).
* Keep `.reveal.active` for the animated “in” state.
* Document it in the README as: “Animations are progressive enhancement; content is readable without JS.”

**Alternative: JS-required reveal**

* Keep current behaviour, but document clearly that reveal content requires JS.
* This is only acceptable if we explicitly decide that’s okay.

Also resolve the open question from the report:

* If `.reveal-ready` is not used in CSS, remove the JS class addition.
* If we choose progressive enhancement, **reintroduce `.reveal-ready` usage** and keep the JS hook.

---

### D) Tailwind scan strategy: compiled reference HTML coupling + size

THEME-014 added a content glob that includes `docs/dev/design/wireframes/sage-and-stone/compiled/*.html`.

Confirm this is intentional and acceptable:

1. Report current `main.css` size (and whether it feels reasonable).
2. Decide one approach:

* **Keep scanning all compiled pages** (max coverage; possible bloat)
* **Scan only `index.html`** (smaller; might miss classes used on other compiled pages)
* **Create a theme-local scan source** (recommended compromise):

  * Copy/compose a minimal “reference scan” file into Theme A (e.g. `themes/theme_a/tailwind/reference-scan.html`) containing the canonical sections/classes we rely on.
  * Point Tailwind `content` at that file instead of coupling to docs paths.

3. Update README + tests to match the chosen strategy (so this can’t silently drift later).

---

## Deliverables

* Updated Tailwind config (screens + content) and README documenting the intent.
* Updated reveal implementation + README documenting behaviour.
* Any necessary updates to the CSS layers (only if required by reveal changes).
* Guardrail tests updated if the scan strategy changed.
* Work report includes:

  * test command outputs (pytest + make test),
  * breakpoint validation notes (and screenshots if feasible),
  * scan strategy decision + CSS size note.

---

## Acceptance criteria

* `pytest tests/themes/test_theme_a_css_contract.py -q` passes (evidence included).
* `make test` passes (evidence included).
* Breakpoint naming/usage is unambiguous and documented.
* Header/nav looks correct across mid-size and full desktop widths.
* Reveal behaviour is intentional and documented (preferred: progressive enhancement).
* Tailwind scan strategy is intentional, documented, and guarded by tests.
* From this point: **template tickets should not need CSS changes** except for truly new utilities/components.

