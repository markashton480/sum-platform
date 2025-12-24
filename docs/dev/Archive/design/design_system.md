# SolarCraft Premium - Design System 2.0 (Brand Agnostic)

# ARCHIVED

# **STATUS**: Obsolete

This document is now obsolete. Please refer to docs/dev/THEME-GUIDE.md for up-to-date information.

## 1. Core Philosophy: "The Frame, Not The Paint"

The goal is to provide a "White Glove" container for the client's brand. The premium feel comes from **structure**, not specific colors.

- **Logic-Based Theming**: We do not hardcode colors. We ingest a client's primary brand color and mathematically derive the surfaces, accents, and text colors to ensure perfect harmony.
- **Architectural Rigor**: Premium sites are defined by **strict alignment** and **generous negative space**. If elements feel crowded, the value proposition drops.
- **Materiality**: The UI should feel like physical materials (glass, heavy card stock, matte paper) rather than digital pixels.

## 2. Dynamic Token System (The "Engine")

We use an **HSL Relationship Model**. The client provides **ONE** primary color (e.g., Navy Blue). The system calculates the rest.

### The Input Variables (Wagtail Injected)

These variables are set in the `:root` by Wagtail based on the client's settings.

|              |                           |                           |
| ------------ | ------------------------- | ------------------------- |
| **Variable** | **Description**           | **Derivation Logic**      |
| `--brand-h`  | Brand Hue (0-360)         | Extracted from Client Hex |
| `--brand-s`  | Brand Saturation (0-100%) | Extracted from Client Hex |
| `--brand-l`  | Brand Lightness (0-100%)  | Extracted from Client Hex |

### The Derived Palette (CSS Calculated)

This logic ensures that whether the client is "Eco Green" or "Luxury Gold," the site looks cohesive.

|                      |                                                              |                                                                                                                                                    |
| -------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Token Name**       | **Formula (HSL)**                                            | **Purpose**                                                                                                                                        |
| **`--primary`**      | `var(--brand-h), var(--brand-s), var(--brand-l)`             | The main action color (Buttons, H1s).                                                                                                              |
| **`--primary-deep`** | `var(--brand-h), var(--brand-s), calc(var(--brand-l) - 15%)` | Hover states. Automatically darkens.                                                                                                               |
| **`--surface-tint`** | `var(--brand-h), 10%, 97%`                                   | **The Secret Sauce.** A mostly white background with a _tiny_ 3% tint of the brand color. Makes the site feel "warm" and branded, not stark white. |
| **`--surface-pure`** | `0, 0%, 100%`                                                | Cards/Modals that need to pop off the tinted background.                                                                                           |
| **`--text-main`**    | `var(--brand-h), 15%, 15%`                                   | Almost black, but tinted with brand hue for subconscious harmony.                                                                                  |
| **`--text-muted`**   | `var(--brand-h), 5%, 45%`                                    | Secondary text.                                                                                                                                    |
| **`--accent-pop`**   | `calc(var(--brand-h) + 30), 60%, 55%`                        | A calculated analogue color for italics/highlights.                                                                                                |

## 3. The "Material" System (Depth & Glass)

High-end home improvement is about materials. The UI mimics this using depth, not color.

### Glassmorphism (The "Lens")

Used for sticky headers, floating conversion bars, and wizard containers.

```
.glass-panel {
    background: hsla(var(--surface-pure), 0.85); /* High opacity for legibility */
    backdrop-filter: blur(12px); /* heavily blurred behind */
    border: 1px solid hsla(var(--brand-h), 10%, 10%, 0.05); /* Ultra-subtle border */
}
```

### Elevation (The "Lift")

We do not use standard black shadows. We use **colored shadows** derived from the brand hue for a glow effect.

```
.premium-shadow {
    /* Shadow is tinted with the brand hue, making it look integrated */
    box-shadow: 0 20px 40px -10px hsla(var(--brand-h), 40%, 20%, 0.1);
}
```

## 4. Typography Hierarchy (Contrast > Font Family)

While specific fonts can change per client, the **relationship** must remain fixed.

- **The Contrast Rule**:
  - **Headings**: Must be Distinct. If the client uses a Serif logo, use a Serif header (e.g., _Fraunces_, _Playfair_). If they are modern tech, use a Geometric Sans (e.g., _Space Grotesk_).
  - **Body**: Must be Utilitarian. Always high-legibility Sans (e.g., _Manrope_, _Inter_).
- **The "Editorial" Sizing**:
  - Body text should never be smaller than `16px` (1rem).
  - Line-height for body text is strict at `1.6` or `1.7`.
  - Headings use tight line-height `1.1`.

## 5. Layout & Spacing Rules

To maintain the "Luxury" feel, we enforce specific spatial rules that cannot be overridden by the client.

1. **The "Pinky" Rule**: Interactive elements (buttons, inputs) must have at least 12px (approx pinky width) padding.
2. **The "Gallery" Rule**: Images are never 100% width of their column. They act as "objects" with specific aspect ratios (4:5 vertical or 16:9 cinematic).
3. **The "Breath" Rule**: Section padding is fluid.

   - Mobile: `4rem` (64px)
   - Desktop: `8rem` (128px)

## 6. Component Blueprints

### Primary Button

- **Fill**: `--primary`
- **Text**: White (or Black if `--primary` is light - calculated via contrast check).
- **Shape**: `4px` radius (Technical/Precise) OR `50px` pill (Friendly/Soft). _Client Choice._
- **Motion**: `transform: translateY(-2px)` on hover.

### The "Curtain" Reveal

The signature animation for images.

1. **State 0**: Wrapper has `overflow: hidden`. Overlay div (`--surface-pure`) covers image.
2. **Trigger**: Intersection Observer fires.
3. **Action**: Image scales down from 1.1x to 1.0x. Overlay div slides away (ScaleY 1 -> 0).

### The Wizard Form

- **Layout**: Split screen. Questions on Left, Context/Progress on Right (Desktop).
- **Feel**: Like a conversation. One question at a time.
- **Feedback**: Instant visual feedback on selection (Border color change).

## 7. Wagtail Implementation Notes

### Branding Settings Model

Create a `BrandSettings` snippet in Wagtail:

- `primary_color` (ColorPicker)
- `secondary_color` (ColorPicker - Optional)
- `font_heading` (Dropdown: [Serif, Sans, Mono])
- `border_radius` (Dropdown: [Sharp (2px), Soft (8px), Round (50px)])

### Template Injection

In `base.html`, inject these values into a `<style>` block:

```
<style>
    :root {
        /* Wagtail injects these HSL values */
        --brand-h: {{ settings.brand.primary_color.hue }};
        --brand-s: {{ settings.brand.primary_color.saturation }}%;
        --brand-l: {{ settings.brand.primary_color.lightness }}%;

        --radius-base: {{ settings.brand.border_radius }}px;
    }
</style>
```
