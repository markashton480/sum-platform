/**
 * Name: Tailwind Configuration
 * Path: core/sum_core/themes/theme_a/tailwind.config.js
 * Purpose: Configure Tailwind CSS for Theme A (Sage & Stone), mapping theme colours
 *          to CSS variables so branding overrides work without rebuilding CSS.
 * Family: Theme A
 * Dependencies: Tailwind (authoring only)
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Theme A templates
    './templates/**/*.html',

    // Core templates rendered within Theme A pages (e.g. StreamField blocks)
    // Without this, Tailwind JIT may tree-shake @layer component selectors
    // that are only referenced by core block templates.
    '../../templates/**/*.html',
  ],

  // Classes composed dynamically in templates won't be discovered by the
  // content scanner. Safelist them so the associated @layer component
  // selectors are retained in the compiled CSS.
  safelist: [
    'hero--gradient-primary',
    'hero--gradient-secondary',
    'hero--gradient-accent',
  ],
  theme: {
    extend: {
      // Custom font families - Sage & Stone typography
      fontFamily: {
        'display': ['Playfair Display', 'Georgia', 'serif'],
        'body': ['Lato', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        'accent': ['Crimson Text', 'Georgia', 'serif'],
        'mono': ['ui-monospace', 'SFMono-Regular', 'monospace'],
      },

      // Colours mapped to CSS variables for branding overrides
      // Uses rgb() format so Tailwind opacity modifiers work (e.g. bg-sage-black/50)
      colors: {
        'sage': {
          // Core Sage & Stone palette
          'black': 'rgb(var(--color-sage-black, 26 47 35) / <alpha-value>)',        // #1A2F23 Obsidian Green
          'linen': 'rgb(var(--color-sage-linen, 247 245 241) / <alpha-value>)',     // #F7F5F1 Warm Linen
          'oat': 'rgb(var(--color-sage-oat, 227 222 212) / <alpha-value>)',         // #E3DED4 Oat
          'moss': 'rgb(var(--color-sage-moss, 85 111 97) / <alpha-value>)',         // #556F61 Moss
          'terra': 'rgb(var(--color-sage-terra, 160 86 59) / <alpha-value>)',       // #A0563B Terra
          'stone': 'rgb(var(--color-sage-stone, 143 141 136) / <alpha-value>)',     // #8F8D88 Stone
        },
        // Semantic aliases (using CSS variables for branding override)
        'primary': 'rgb(var(--color-primary, 160 86 59) / <alpha-value>)',
        'secondary': 'rgb(var(--color-secondary, 85 111 97) / <alpha-value>)',
        'accent': 'rgb(var(--color-accent, 160 86 59) / <alpha-value>)',
      },

      // Custom breakpoints
      screens: {
        'desktop': '1024px', // Matches Theme A mega menu breakpoint
      },

      // Animation easings from Theme A
      transitionTimingFunction: {
        'expo-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'smooth': 'cubic-bezier(0.25, 1, 0.5, 1)',
      },
    },
  },
  plugins: [],
};
