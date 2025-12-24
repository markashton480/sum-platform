# THEME-007: Implement FeaturedCaseStudyBlock Follow-up

## Summary

Successfully implemented the `FeaturedCaseStudyBlock` as a core Wagtail StreamBlock with a distinct Theme A template.

## Changes

1.  **Block Definition**: Added `FeaturedCaseStudyBlock` to `core/sum_core/blocks/gallery.py` implementing the full contract (eyebrow, heading, intro, points, cta, image, stats).
2.  **Theme Adaptation**: Created a specific Theme A template at `themes/theme_a/templates/sum_core/blocks/featured_case_study.html` matched to the Figma design (grid layout, floating stats, aspect ratio).
3.  **Core Fallback**: Provided a semantic, unstyled template for core usage.
4.  **Registration**: Exposed the block in `PageStreamBlock` under the "Sections" group.
5.  **Guardrails**: Updated Theme A build fingerprint to account for the new template.

## Verification

- **Unit Tests**: Added `tests/themes/test_theme_a_featured_case_study.py` to verify rendering logic and class presence.
- **Integration**: Verified block availability via `makemigrations` and `PageStreamBlock` tests.
- **Manual**: Template location `themes/theme_a/...` verified as canonical.

## Notes for Maintainers

- The `FeaturedCaseStudyBlock` relies on the `image` field returning a Wagtail Image object.
- Theme A template uses `bg-sage-terra` and other theme-specific tokens. If these tokens change in `tailwind.config.js`, the template classes might need updates.
