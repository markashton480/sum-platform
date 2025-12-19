# Block Migration Checklist

**Date**: 2024-12-18  
**Project**: SUM Platform - Theme A Block Template Migration  
**Purpose**: Track migration of block templates from vanilla CSS (core) to Tailwind (Theme A)

---

## Critical Blocks (Always Used)
- [x] **HeroGradientBlock** → `sum_core/blocks/hero_gradient.html` ✅
- [x] **HeroImageBlock** → `sum_core/blocks/hero_image.html` ✅

## High Priority Blocks (Common in Trade Sites)
- [x] **ServiceCardsBlock** → `sum_core/blocks/service_cards.html` ✅
- [x] **TestimonialsBlock** → `sum_core/blocks/testimonials.html` ✅
- [x] **TrustStripLogosBlock** → `sum_core/blocks/trust_strip_logos.html` ✅
- [x] **StatsBlock** → `sum_core/blocks/stats.html` ✅
- [x] **ContactFormBlock** → `sum_core/blocks/contact_form.html` ✅
- [ ] **QuoteRequestFormBlock** → `sum_core/blocks/quote_request_form.html`

## Medium Priority Blocks (Content Blocks)
- [x] **ProcessStepsBlock** → `sum_core/blocks/process_steps.html` ✅
- [x] **FAQBlock** → `sum_core/blocks/faq.html` ✅
- [x] **GalleryBlock** → `sum_core/blocks/gallery.html` ✅
- [x] **PortfolioBlock** → `sum_core/blocks/portfolio.html` ✅
- [x] **ContentRichTextBlock** → `sum_core/blocks/content_richtext.html` ✅
- [x] **ContentEditorialHeaderBlock** → `sum_core/blocks/content_editorial_header.html` ✅
- [x] **ContentQuoteBlock** → `sum_core/blocks/content_quote.html` ✅
- [x] **ContentImageBlock** → `sum_core/blocks/content_image.html` ✅
- [x] **ContentButtonsBlock** → `sum_core/blocks/content_buttons.html` ✅

## Low Priority Blocks (Specialized/Utility)
- [x] **RichTextBlock** → `sum_core/blocks/rich_text.html` ✅
- [x] **ContentSpacerBlock** → `sum_core/blocks/content_spacer.html` ✅
- [x] **ContentDividerBlock** → `sum_core/blocks/content_divider.html` ✅
- [ ] **TrustStripBlock** → `sum_core/blocks/trust_strip.html` (no template file found)
- [ ] **FeaturesListBlock** → `sum_core/blocks/features_list.html` (no template file found)
- [ ] **ComparisonBlock** → `sum_core/blocks/comparison.html` (no template file found)
- [ ] **ButtonBlock** → `sum_core/blocks/button.html` (no template file found)
- [ ] **HeroBlock** → `sum_core/blocks/hero.html` (no template file found)

---

## Missing Template Files

The following blocks declare templates but the template files don't exist in `core/sum_core/templates/sum_core/blocks/`:
- `button.html`
- `hero.html` (generic, may be unused - we have hero_gradient and hero_image)
- `features_list.html`
- `comparison.html`

**Action Required**: Verify if these blocks are actually used. If yes, create core fallback templates first.

---

## Migration Priority Order

1. **Phase 1 - Critical (TASK 3)**: Hero blocks (most visible)
2. **Phase 2 - High (TASK 4-5)**: Services, Testimonials, Forms
3. **Phase 3 - Medium (TASK 6)**: Content blocks, Process, FAQ, Gallery
4. **Phase 4 - Low (TASK 6)**: Utility blocks (spacer, divider)

---

## Notes

- Focus on blocks that are commonly used in trade/home improvement sites
- Blocks without template files may be incomplete/deprecated - verify before migrating
- Each migrated template should:
  - Use Tailwind classes instead of vanilla CSS
  - Match Theme A design tokens
  - Be responsive (mobile-first)
  - Include proper semantic HTML
