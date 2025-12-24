### THEME-014 — Theme A Tailwind config/tokens parity with reference prototype

**Mission:** Make Theme A’s Tailwind build output behave like the reference prototype *without* blindly dumping CSS in. Bring over the reference design system thoughtfully, keep it DRY, and keep the SiteSettings variable bridge intact. (This directly follows the theme contract + styling strategy in the spec.)  

#### Scope

1. **Locate reference design system sources**

   * In `docs/dev/design/wireframes/sage-and-stone/compiled/…` identify:

     * any Tailwind config used (or implied)
     * any “input.css” / component CSS
     * any bespoke utilities (`reveal`, scrollbar hiding, named group patterns, etc.)
   * The agent must treat this as the canonical design system to match (like we did for the Portfolio structure). 

2. **Update Theme A Tailwind config so it compiles the *full* reference class universe**

   * In `themes/theme_a/tailwind/tailwind.config.js`:

     * Ensure `content` globs include:

       * `themes/theme_a/templates/**/*.html`
       * **the compiled reference HTML** (`docs/dev/design/wireframes/sage-and-stone/compiled/index.html`)
     * This is the big unlock: once the compiled reference HTML is in the scan set, the CSS output already contains the classes we’ll paste into templates later — reducing the need to rebuild per-block.
   * If the reference uses named groups (`group/card` + `group-hover/card:`), make sure we’re using them correctly and consistently (and document the pattern). The Portfolio incident suggests we should standardise this to avoid future weirdness. 

3. **Move any bespoke CSS into proper Tailwind layers**

   * Keep Tailwind-first. Only keep bespoke CSS for things Tailwind isn’t good at (animations/utilities), per spec guidance. 
   * Ensure utilities like `no-scrollbar` and `reveal` live in the theme’s Tailwind input (e.g. `@layer utilities/components`) and are imported cleanly. The work report already confirms `no-scrollbar` existed and was used. 

4. **Confirm wiring: base template + branding vars + correct static asset resolution**

   * Verify Theme A base template still has the required hook points and that branding vars injection is present where expected (that’s part of the architecture + wiring contract).  
   * Confirm static CSS served is the theme one (and not a core fallback).

5. **Add guardrail tests so we don’t re-live this**

   * New test file idea: `tests/themes/test_theme_a_css_contract.py`:

     * Assert theme CSS file exists via staticfiles finder.
     * Assert it contains a handful of sentinel selectors/strings that represent the design system being present (e.g. the custom utilities and a couple of “sage palette” outputs).
   * Add a test that asserts `tailwind.config.js` includes the compiled reference HTML path in `content`. This is a cheap but powerful “don’t regress” check.

6. ** Update Documentation **

   * Update `themes/theme_a/README.md` accordingly

6. **Write a full, comprehensive work report**

   * File in same directory under `THEME-014_followup.md`

#### Acceptance criteria

* Theme A compiled CSS demonstrably includes the full reference class set (because reference HTML is part of scan).
* No bespoke CSS dump; anything moved is justified + lives in Tailwind layers.
* Branding variable bridge still works.
* Tests added; `make test` passes.
* From this ticket onward: **template-only tickets should not touch CSS/fingerprint unless a *new* utility/component layer is introduced.**

---

