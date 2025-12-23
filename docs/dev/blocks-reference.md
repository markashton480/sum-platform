# SUM Platform – Block Reference

> **Purpose:** Authoritative reference for all StreamField blocks in `sum_core`. Use this when implementing pages, writing tests, or understanding block field structures.

---

## Quick Reference Table

| Key                   | Block                  | Group        | Purpose                              |
| --------------------- | ---------------------- | ------------ | ------------------------------------ |
| `hero_image`          | HeroImageBlock         | Hero         | Full-width image hero with overlay   |
| `hero_gradient`       | HeroGradientBlock      | Hero         | Gradient background hero             |
| `service_cards`       | ServiceCardsBlock      | Services     | Service card grid section            |
| `service_detail`      | ServiceDetailBlock     | Services     | Two-column service section           |
| `testimonials`        | TestimonialsBlock      | Sections     | Customer testimonial cards           |
| `team_members`        | TeamMemberBlock        | Sections     | Team member grid section             |
| `gallery`             | GalleryBlock           | Sections     | Image gallery grid                   |
| `featured_case_study` | FeaturedCaseStudyBlock | Sections     | Large highlighted case study         |
| `manifesto`           | ManifestoBlock         | Sections     | Centered manifesto/prose section     |
| `portfolio`           | PortfolioBlock         | Sections     | Project portfolio with offset layout |
| `trust_strip_logos`   | TrustStripBlock        | Sections     | Logo strip (certifications/partners) |
| `stats`               | StatsBlock             | Sections     | Key metrics display                  |
| `process`             | ProcessStepsBlock      | Sections     | Timeline/process steps               |
| `timeline`            | TimelineBlock          | Sections     | Milestone timeline/history           |
| `faq`                 | FAQBlock               | Sections     | FAQ accordion with JSON-LD           |
| `page_header`         | PageHeaderBlock        | Page Content | Interior page header with breadcrumb |
| `editorial_header`    | EditorialHeaderBlock   | Page Content | Page/article header                  |
| `content`             | RichTextContentBlock   | Page Content | General rich text content            |
| `quote`               | QuoteBlock             | Page Content | Pull quote/blockquote                |
| `image_block`         | ImageBlock             | Page Content | Standalone image with caption        |
| `buttons`             | ButtonGroupBlock       | Page Content | CTA button group                     |
| `spacer`              | SpacerBlock            | Page Content | Vertical spacing control             |
| `divider`             | DividerBlock           | Page Content | Horizontal divider line              |
| `contact_form`        | ContactFormBlock       | Forms        | Contact form section                 |
| `quote_request_form`  | QuoteRequestFormBlock  | Forms        | Quote request form section           |

---

## Hero Blocks

### HeroImageBlock

**Key:** `hero_image`  
**Template:** `sum_core/blocks/hero_image.html`  
**Purpose:** Full-width hero section with background image, overlay, headline, and CTAs. Typically used at the top of landing pages and homepages.

#### Fields

| Field                 | Type                    | Required | Constraints                | Notes                         |
| --------------------- | ----------------------- | -------- | -------------------------- | ----------------------------- |
| `headline`            | RichTextBlock           | Yes      | features: `['italic']`     | Use italic for accent styling |
| `subheadline`         | TextBlock               | No       | -                          | Supporting text               |
| `ctas`                | ListBlock(HeroCTABlock) | No       | max: 2                     | Primary and secondary CTAs    |
| `status`              | CharBlock               | No       | max: 120                   | Eyebrow/status text           |
| `image`               | ImageChooserBlock       | Yes      | -                          | Background image              |
| `image_alt`           | CharBlock               | Yes      | max: 150                   | Accessibility alt text        |
| `overlay_opacity`     | ChoiceBlock             | No       | `none/light/medium/strong` | Default: `medium`             |
| `floating_card_label` | CharBlock               | No       | max: 50                    | e.g. "Est. Annual Savings"    |
| `floating_card_value` | CharBlock               | No       | max: 50                    | e.g. "£2,450"                 |

#### Notes

- The floating card appears on desktop only (hidden on mobile).
- Overlay helps text contrast over busy images.
- Headline RichText italic words get accent color via CSS.

---

### HeroGradientBlock

**Key:** `hero_gradient`  
**Template:** `sum_core/blocks/hero_gradient.html`  
**Purpose:** Text-focused hero with gradient background. Good for interior pages or when no hero image is available.

#### Fields

| Field            | Type                    | Required | Constraints                | Notes                         |
| ---------------- | ----------------------- | -------- | -------------------------- | ----------------------------- |
| `headline`       | RichTextBlock           | Yes      | features: `['italic']`     | Use italic for accent styling |
| `subheadline`    | TextBlock               | No       | -                          | Supporting text               |
| `ctas`           | ListBlock(HeroCTABlock) | No       | max: 2                     | Primary and secondary CTAs    |
| `status`         | CharBlock               | No       | max: 120                   | Eyebrow/status text           |
| `gradient_style` | ChoiceBlock             | No       | `primary/secondary/accent` | Default: `primary`            |

---

### HeroCTABlock (Child Block)

Used within hero blocks for CTA buttons.

| Field             | Type         | Required | Default   |
| ----------------- | ------------ | -------- | --------- |
| `label`           | CharBlock    | Yes      | -         |
| `url`             | URLBlock     | Yes      | -         |
| `style`           | ChoiceBlock  | No       | `primary` |
| `open_in_new_tab` | BooleanBlock | No       | `False`   |

---

## Service Blocks

### ServiceCardsBlock

**Key:** `service_cards`  
**Template:** `sum_core/blocks/service_cards.html`  
**Purpose:** Grid of service cards with icons, titles, and descriptions. Horizontal scroll on mobile, 3-column grid on desktop.

#### Fields

| Field          | Type                            | Required | Constraints                    | Notes                 |
| -------------- | ------------------------------- | -------- | ------------------------------ | --------------------- |
| `eyebrow`      | CharBlock                       | No       | max: 120                       | e.g. "Our Services"   |
| `heading`      | RichTextBlock                   | Yes      | features: `['italic', 'bold']` | Use italic for accent |
| `intro`        | TextBlock                       | No       | -                              | Supporting paragraph  |
| `cards`        | ListBlock(ServiceCardItemBlock) | Yes      | min: 1, max: 12                | The service cards     |
| `layout_style` | ChoiceBlock                     | No       | `default/tight`                | Spacing variant       |

### ServiceCardItemBlock (Child Block)

| Field         | Type              | Required | Notes                        |
| ------------- | ----------------- | -------- | ---------------------------- |
| `icon`        | CharBlock         | No       | Emoji or short text (max: 4) |
| `image`       | ImageChooserBlock | No       | Alternative to emoji icon    |
| `title`       | CharBlock         | Yes      | max: 120                     |
| `description` | RichTextBlock     | No       | Limited features             |
| `link_url`    | URLBlock          | No       | -                            |
| `link_label`  | CharBlock         | No       | Defaults to "Learn more"     |

### ServiceDetailBlock

**Key:** `service_detail`  
**Template:** `sum_core/blocks/service_detail.html`  
**Purpose:** Reusable service section with headline, rich copy, optional highlights, and flexible media alignment.

#### Fields

| Field        | Type              | Required | Constraints                         | Notes                                       |
| ------------ | ----------------- | -------- | ----------------------------------- | ------------------------------------------- |
| `eyebrow`    | CharBlock         | No       | max: 120                            | Short label above heading                   |
| `heading`    | RichTextBlock     | Yes      | features: `['italic', 'bold']`      | Section heading                             |
| `body`       | RichTextBlock     | Yes      | features: `['bold', 'italic', 'link', 'ol', 'ul']` | Core service description           |
| `highlights` | ListBlock(CharBlock) | No    | -                                   | Optional bullet points                      |
| `image`      | ImageChooserBlock | No       | -                                   | Optional supporting image                   |
| `image_alt`  | CharBlock         | No       | max: 150                            | Recommended when image is provided          |
| `layout`     | ChoiceBlock       | No       | `image_left/image_right/no_image`   | Controls desktop alignment                  |
| `cta_text`   | CharBlock         | No       | max: 80                             | CTA label (requires URL to render)          |
| `cta_url`    | URLBlock          | No       | -                                   | CTA link (requires label to render)         |

---

## Testimonials Block

### TestimonialsBlock

**Key:** `testimonials`  
**Template:** `sum_core/blocks/testimonials.html`  
**Purpose:** Customer testimonials in a dark-themed section. Horizontal scroll on mobile, 3-column grid on desktop.

#### Fields

| Field          | Type                        | Required | Constraints                    | Notes                 |
| -------------- | --------------------------- | -------- | ------------------------------ | --------------------- |
| `eyebrow`      | CharBlock                   | No       | -                              | e.g. "Client Stories" |
| `heading`      | RichTextBlock               | No       | features: `['bold', 'italic']` | Section heading       |
| `testimonials` | ListBlock(TestimonialBlock) | Yes      | min: 1, max: 12                | The testimonials      |

### TestimonialBlock (Child Block)

| Field         | Type              | Required | Constraints    |
| ------------- | ----------------- | -------- | -------------- |
| `quote`       | TextBlock         | Yes      | -              |
| `author_name` | CharBlock         | Yes      | -              |
| `company`     | CharBlock         | No       | -              |
| `photo`       | ImageChooserBlock | No       | -              |
| `rating`      | IntegerBlock      | No       | min: 1, max: 5 |

#### Notes

- If no photo provided, initials are displayed as fallback.
- Rating displays as stars (1-5).

---

## Team Members Block

### TeamMemberBlock

**Key:** `team_members`  
**Template:** `sum_core/blocks/team_members.html`  
**Purpose:** Team member grid section with photo, name, role, and bio.

#### Fields

| Field     | Type                           | Required | Constraints                    | Notes                       |
| --------- | ------------------------------ | -------- | ------------------------------ | --------------------------- |
| `eyebrow` | CharBlock                      | No       | max: 100                       | Small label above heading   |
| `heading` | RichTextBlock                  | No       | features: `['bold', 'italic']` | Section heading             |
| `members` | ListBlock(TeamMemberItemBlock) | Yes      | min: 1, max: 12                | Team member cards           |

### TeamMemberItemBlock (Child Block)

| Field      | Type              | Required | Notes                        |
| ---------- | ----------------- | -------- | ---------------------------- |
| `photo`    | ImageChooserBlock | Yes      | Rendered via Wagtail renditions |
| `alt_text` | CharBlock         | Yes      | Accessible description for the photo |
| `name`     | CharBlock         | Yes      | -                            |
| `role`     | CharBlock         | No       | e.g. "Founder"               |
| `bio`      | TextBlock         | No       | Short description            |

---

## Trust & Stats Blocks

### TrustStripBlock (Logos)

**Key:** `trust_strip_logos`  
**Template:** `sum_core/blocks/trust_strip_logos.html`  
**Purpose:** Horizontal row of partner/certification logos. Good for social proof.

#### Fields

| Field     | Type                           | Required | Constraints    | Notes             |
| --------- | ------------------------------ | -------- | -------------- | ----------------- |
| `eyebrow` | CharBlock                      | No       | max: 100       | e.g. "Trusted by" |
| `items`   | ListBlock(TrustStripItemBlock) | Yes      | min: 2, max: 8 | Logo items        |

### TrustStripItemBlock (Child Block)

| Field      | Type              | Required | Notes         |
| ---------- | ----------------- | -------- | ------------- |
| `logo`     | ImageChooserBlock | Yes      | -             |
| `alt_text` | CharBlock         | Yes      | max: 255      |
| `url`      | URLBlock          | No       | Optional link |

---

### StatsBlock

**Key:** `stats`  
**Template:** `sum_core/blocks/stats.html`  
**Purpose:** Display key metrics/statistics (2-4 items). Good for highlighting achievements.

#### Fields

| Field     | Type                     | Required | Constraints    | Notes                 |
| --------- | ------------------------ | -------- | -------------- | --------------------- |
| `eyebrow` | CharBlock                | No       | max: 100       | e.g. "By the Numbers" |
| `intro`   | TextBlock                | No       | -              | Optional intro text   |
| `items`   | ListBlock(StatItemBlock) | Yes      | min: 2, max: 4 | The statistics        |

### StatItemBlock (Child Block)

| Field    | Type      | Required | Notes                     |
| -------- | --------- | -------- | ------------------------- |
| `value`  | CharBlock | Yes      | e.g. "500+", "15", "98%"  |
| `label`  | CharBlock | Yes      | e.g. "Projects Completed" |
| `prefix` | CharBlock | No       | e.g. ">", "£"             |
| `suffix` | CharBlock | No       | e.g. "+", "yrs", "%"      |

---

## Process & FAQ Blocks

### ProcessStepsBlock

**Key:** `process`  
**Template:** `sum_core/blocks/process_steps.html`  
**Purpose:** Timeline/steps layout showing a process or workflow. Sticky header on desktop.

#### Fields

| Field     | Type                        | Required | Constraints                    | Notes               |
| --------- | --------------------------- | -------- | ------------------------------ | ------------------- |
| `eyebrow` | CharBlock                   | No       | -                              | e.g. "How It Works" |
| `heading` | RichTextBlock               | Yes      | features: `['italic', 'bold']` | Section heading     |
| `intro`   | RichTextBlock               | No       | -                              | Supporting text     |
| `steps`   | ListBlock(ProcessStepBlock) | Yes      | min: 3, max: 8                 | The process steps   |

### ProcessStepBlock (Child Block)

| Field         | Type          | Required | Notes                           |
| ------------- | ------------- | -------- | ------------------------------- |
| `number`      | IntegerBlock  | No       | Auto-numbered if omitted (1-20) |
| `title`       | CharBlock     | Yes      | -                               |
| `description` | RichTextBlock | No       | -                               |

---

### TimelineBlock

**Key:** `timeline`  
**Template:** `sum_core/blocks/timeline.html`  
**Purpose:** Chronological history/milestones section with optional imagery and intro copy.

#### Fields

| Field     | Type                         | Required | Constraints                    | Notes                                   |
| --------- | ---------------------------- | -------- | ------------------------------ | --------------------------------------- |
| `eyebrow` | CharBlock                    | No       | -                              | Accent label above the heading          |
| `heading` | RichTextBlock                | No       | features: `['italic', 'bold']` | Timeline heading                        |
| `intro`   | RichTextBlock                | No       | features: `['bold', 'italic', 'link']` | Short intro/lede              |
| `items`   | ListBlock(TimelineItemBlock) | Yes      | min: 1                         | Timeline milestones                     |

### TimelineItemBlock (Child)

| Field        | Type              | Required | Notes                                           |
| ------------ | ----------------- | -------- | ----------------------------------------------- |
| `date_label` | CharBlock         | Yes      | Short date marker (e.g., \"2020\", \"Q3 2024\")     |
| `heading`    | CharBlock         | Yes      | Milestone heading                               |
| `body`       | RichTextBlock     | Yes      | features: `['bold', 'italic', 'link', 'ol', 'ul']` |
| `image`      | ImageChooserBlock | No       | Optional supporting image                       |
| `image_alt`  | CharBlock         | No       | Provide when `image` is set for accessibility   |

---

### FAQBlock

**Key:** `faq`  
**Template:** `sum_core/blocks/faq.html`  
**Purpose:** Accordion-style FAQ section. Generates JSON-LD schema for SEO.

#### Fields

| Field                 | Type                    | Required | Constraints                    | Notes              |
| --------------------- | ----------------------- | -------- | ------------------------------ | ------------------ |
| `eyebrow`             | CharBlock               | No       | -                              | e.g. "Questions"   |
| `heading`             | RichTextBlock           | Yes      | features: `['italic', 'bold']` | Section heading    |
| `intro`               | RichTextBlock           | No       | -                              | Supporting text    |
| `items`               | ListBlock(FAQItemBlock) | Yes      | min: 1, max: 20                | The FAQ items      |
| `allow_multiple_open` | BooleanBlock            | No       | Default: `True`                | Accordion behavior |

### FAQItemBlock (Child Block)

| Field      | Type          | Required | Notes            |
| ---------- | ------------- | -------- | ---------------- |
| `question` | CharBlock     | Yes      | -                |
| `answer`   | RichTextBlock | Yes      | Full feature set |

#### Notes

- Automatically generates valid FAQPage JSON-LD schema.
- If `allow_multiple_open` is `False`, opening one item closes others.

---

## Gallery & Portfolio Blocks

### GalleryBlock

**Key:** `gallery`  
**Template:** `sum_core/blocks/gallery.html`  
**Purpose:** Image gallery grid for showcasing project photos. Responsive 1/2/3 column layout.

#### Fields

| Field     | Type                         | Required | Constraints                    | Notes                 |
| --------- | ---------------------------- | -------- | ------------------------------ | --------------------- |
| `eyebrow` | CharBlock                    | No       | max: 80                        | e.g. "Selected Works" |
| `heading` | RichTextBlock                | No       | features: `['bold', 'italic']` | Section heading       |
| `intro`   | TextBlock                    | No       | -                              | Supporting text       |
| `images`  | ListBlock(GalleryImageBlock) | Yes      | min: 1, max: 24                | Gallery images        |

### GalleryImageBlock (Child Block)

| Field      | Type              | Required | Notes                     |
| ---------- | ----------------- | -------- | ------------------------- |
| `image`    | ImageChooserBlock | Yes      | -                         |
| `alt_text` | CharBlock         | No       | Falls back to image title |
| `caption`  | CharBlock         | No       | max: 255                  |

---

### FeaturedCaseStudyBlock

**Key:** `featured_case_study`
**Template:** `sum_core/blocks/featured_case_study.html`
**Purpose:** High-impact case study feature with split layout (image + stats vs content).

#### Fields

| Field         | Type              | Required | Constraints     | Notes                      |
| ------------- | ----------------- | -------- | --------------- | -------------------------- |
| `eyebrow`     | CharBlock         | No       | max: 100        | e.g. "Case Study"          |
| `heading`     | RichTextBlock     | Yes      | -               | Main title                 |
| `intro`       | RichTextBlock     | No       | -               | Supporting text            |
| `points`      | ListBlock(Text)   | No       | max_length: 500 | Key features/outcomes list |
| `cta_text`    | CharBlock         | No       | max: 50         | e.g. "Read more"           |
| `cta_url`     | URLBlock          | No       | -               | Link destination           |
| `image`       | ImageChooserBlock | Yes      | -               | Main visual                |
| `image_alt`   | CharBlock         | Yes      | max: 255        | Accessibility text         |
| `stats_label` | CharBlock         | No       | max: 50         | Floating card label        |
| `stats_value` | CharBlock         | No       | max: 100        | Floating card value        |

#### Notes

- **CTA behavior:** Only renders if **both** `cta_text` and `cta_url` are present.
- **Stats card:** Only renders if at least one of `stats_label` or `stats_value` is present.
- **Theme A:**
  - Image aspect ratio: 4:5
  - Hovering image reveals "INSPECT ARTIFACT" overlay.
  - Stats card floats top-right over image.

---

### ManifestoBlock

**Key:** `manifesto`  
**Template:** `sum_core/blocks/manifesto.html`  
**Purpose:** Centered prose section with eyebrow + heading + body, plus optional pull quote.

#### Fields

| Field     | Type          | Required | Constraints                                        | Notes                           |
| --------- | ------------- | -------- | -------------------------------------------------- | ------------------------------- |
| `eyebrow` | CharBlock     | No       | max: 100                                           | e.g. "The Manifesto"            |
| `heading` | RichTextBlock | Yes      | features: `['italic', 'bold']`                     | Italic words get accent styling |
| `body`    | RichTextBlock | Yes      | features: `['bold', 'italic', 'link', 'ol', 'ul']` | Main prose content              |
| `quote`   | TextBlock     | No       | -                                                  | Optional pull quote             |

#### Notes

- Theme A renders this block as a single semantic unit matching the wireframe manifesto section.

---

### PortfolioBlock

**Key:** `portfolio`  
**Template:** `sum_core/blocks/portfolio.html`  
**Purpose:** Project portfolio gallery. Theme A uses a horizontal editorial carousel on mobile and a 3-column grid on desktop.

#### Fields

| Field            | Type                          | Required | Constraints                    | Notes                       |
| ---------------- | ----------------------------- | -------- | ------------------------------ | --------------------------- |
| `eyebrow`        | CharBlock                     | No       | -                              | e.g. "Our Work"             |
| `heading`        | RichTextBlock                 | Yes      | features: `['bold', 'italic']` | Section heading             |
| `intro`          | TextBlock                     | No       | -                              | Supporting text             |
| `view_all_link`  | URLBlock                      | No       | -                              | Link to main portfolio page |
| `view_all_label` | CharBlock                     | No       | max: 50                        | e.g. "View full gallery"    |
| `items`          | ListBlock(PortfolioItemBlock) | Yes      | min: 1, max: 12                | Project items               |

### PortfolioItemBlock (Child Block)

| Field        | Type              | Required | Notes                     |
| ------------ | ----------------- | -------- | ------------------------- |
| `image`      | ImageChooserBlock | Yes      | -                         |
| `alt_text`   | CharBlock         | Yes      | -                         |
| `title`      | CharBlock         | Yes      | -                         |
| `category`   | CharBlock         | No       | max: 50                  |
| `location`   | CharBlock         | No       | e.g. "Kensington, London" |
| `services`   | CharBlock         | No       | e.g. "Solar • Battery"    |
| `constraint` | CharBlock         | No       | max: 100                  |
| `material`   | CharBlock         | No       | max: 100                  |
| `outcome`    | CharBlock         | No       | max: 100                  |
| `link_url`   | URLBlock          | No       | Link to case study        |

---

## Content Blocks

### PageHeaderBlock

**Key:** `page_header`  
**Template:** `sum_core/blocks/page_header.html`  
**Purpose:** Interior page header with breadcrumbs, heading, and optional intro.

#### Fields

| Field     | Type          | Required | Constraints                    | Notes                       |
| --------- | ------------- | -------- | ------------------------------ | -------------------------- |
| `eyebrow` | CharBlock     | No       | -                              | Small label above heading  |
| `heading` | RichTextBlock | No       | features: `['italic', 'bold']` | Falls back to page title   |
| `intro`   | TextBlock     | No       | -                              | Short supporting intro     |

---

### RichTextContentBlock

**Key:** `content`  
**Template:** `sum_core/blocks/content_richtext.html`  
**Purpose:** Flexible block for general rich text content sections.

#### Fields

| Field   | Type          | Required | Constraints                | Notes           |
| ------- | ------------- | -------- | -------------------------- | --------------- |
| `align` | ChoiceBlock   | No       | `left/center`              | Default: `left` |
| `body`  | RichTextBlock | Yes      | Full heading/list features | Main content    |

---

### EditorialHeaderBlock

**Key:** `editorial_header`  
**Template:** `sum_core/blocks/content_editorial_header.html`  
**Purpose:** Text-heavy header for editorial pages/blog posts.

#### Fields

| Field     | Type          | Required | Constraints                    | Notes             |
| --------- | ------------- | -------- | ------------------------------ | ----------------- |
| `align`   | ChoiceBlock   | No       | `left/center`                  | Default: `center` |
| `eyebrow` | CharBlock     | No       | -                              | e.g. "Case Study" |
| `heading` | RichTextBlock | Yes      | features: `['italic', 'bold']` | Main title        |

---

### QuoteBlock

**Key:** `quote`  
**Template:** `sum_core/blocks/content_quote.html`  
**Purpose:** Editorial pull-quote with animated reveal.

#### Fields

| Field    | Type      | Required | Notes                 |
| -------- | --------- | -------- | --------------------- |
| `quote`  | TextBlock | Yes      | 1-3 sentences         |
| `author` | CharBlock | No       | -                     |
| `role`   | CharBlock | No       | e.g. "Property Owner" |

---

### ImageBlock

**Key:** `image_block`  
**Template:** `sum_core/blocks/content_image.html`  
**Purpose:** Standalone image with optional caption. Has reveal animation.

#### Fields

| Field        | Type              | Required | Notes                |
| ------------ | ----------------- | -------- | -------------------- |
| `image`      | ImageChooserBlock | Yes      | -                    |
| `alt_text`   | CharBlock         | Yes      | max: 255             |
| `caption`    | CharBlock         | No       | -                    |
| `full_width` | BooleanBlock      | No       | Stretch to container |

---

### ButtonGroupBlock

**Key:** `buttons`  
**Template:** `sum_core/blocks/content_buttons.html`  
**Purpose:** Group of CTA buttons (1-3).

#### Fields

| Field       | Type                          | Required | Constraints         | Notes           |
| ----------- | ----------------------------- | -------- | ------------------- | --------------- |
| `alignment` | ChoiceBlock                   | No       | `left/center/right` | Default: `left` |
| `buttons`   | ListBlock(ContentButtonBlock) | Yes      | min: 1, max: 3      | The buttons     |

### ContentButtonBlock (Child Block)

| Field   | Type        | Required | Notes               |
| ------- | ----------- | -------- | ------------------- |
| `label` | CharBlock   | Yes      | -                   |
| `url`   | URLBlock    | Yes      | -                   |
| `style` | ChoiceBlock | No       | `primary/secondary` |

---

### SpacerBlock

**Key:** `spacer`  
**Template:** `sum_core/blocks/content_spacer.html`  
**Purpose:** Add vertical spacing between content blocks.

#### Fields

| Field  | Type        | Required | Constraints                 | Notes             |
| ------ | ----------- | -------- | --------------------------- | ----------------- |
| `size` | ChoiceBlock | No       | `small/medium/large/xlarge` | Default: `medium` |

**Size mapping:**

- `small`: 24px (`--space-6`)
- `medium`: 40px (`--space-10`)
- `large`: 64px (`--space-16`)
- `xlarge`: 96px (`--space-24`)

---

### DividerBlock

**Key:** `divider`  
**Template:** `sum_core/blocks/content_divider.html`  
**Purpose:** Horizontal divider line between content sections.

#### Fields

| Field   | Type        | Required | Constraints           | Notes            |
| ------- | ----------- | -------- | --------------------- | ---------------- |
| `style` | ChoiceBlock | No       | `muted/strong/accent` | Default: `muted` |

---

## Form Blocks

### ContactFormBlock

**Key:** `contact_form`  
**Template:** `sum_core/blocks/contact_form.html`  
**Purpose:** Contact form section with sticky header on desktop.

#### Fields

| Field             | Type          | Required | Constraints             | Notes                |
| ----------------- | ------------- | -------- | ----------------------- | -------------------- |
| `eyebrow`         | CharBlock     | No       | -                       | e.g. "Enquiries"     |
| `heading`         | RichTextBlock | Yes      | -                       | Section heading      |
| `intro`           | RichTextBlock | No       | -                       | Supporting text      |
| `success_message` | TextBlock     | No       | Default provided        | Form success message |
| `submit_label`    | CharBlock     | No       | Default: "Send enquiry" | Button text          |

#### Meta

- `form_type`: `"contact"` (for leads system)

---

### QuoteRequestFormBlock

**Key:** `quote_request_form`  
**Template:** `sum_core/blocks/quote_request_form.html`  
**Purpose:** Quote request form with optional compact layout.

#### Fields

| Field               | Type          | Required | Constraints                | Notes                       |
| ------------------- | ------------- | -------- | -------------------------- | --------------------------- |
| `eyebrow`           | CharBlock     | No       | -                          | e.g. "Project Application"  |
| `heading`           | RichTextBlock | Yes      | -                          | Section heading             |
| `intro`             | RichTextBlock | No       | -                          | Supporting text             |
| `success_message`   | TextBlock     | No       | Default provided           | Form success message        |
| `submit_label`      | CharBlock     | No       | Default: "Request a quote" | Button text                 |
| `show_compact_meta` | BooleanBlock  | No       | -                          | Compact layout for sidebars |

#### Meta

- `form_type`: `"quote"` (for leads system)

---

## Usage Guidelines

### 1. RichText Accent Styling

Many blocks use RichText for headings with `['italic']` or `['bold', 'italic']` features. When editors use italic formatting, the CSS applies accent color styling:

```html
<!-- Editor enters: "Our <em>Services</em>" -->
<!-- Rendered with accent color on "Services" -->
```

### 2. Shared Header Pattern

Section blocks should use the shared header pattern from `layout.css`:

```html
<section class="section [block-name]">
  <div class="container">
    <header class="section__header">
      <span class="section__eyebrow">{{ self.eyebrow }}</span>
      <div class="section__heading">{{ self.heading|richtext }}</div>
      <p class="section__intro">{{ self.intro }}</p>
    </header>
    <!-- Block content -->
  </div>
</section>
```

### 3. PageStreamBlock Groups

Blocks are organized into groups in the admin chooser:

- **Hero**: Hero blocks (top of page)
- **Sections**: Major page sections
- **Page Content**: Inline content blocks
- **Forms**: Form sections
- **Legacy Sections**: Older block variants (maintained for compatibility)

---

## Changelog

| Date       | Change                                 |
| ---------- | -------------------------------------- |
| 2025-12-12 | Initial documentation created (M2-012) |
