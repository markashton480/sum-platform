# Sage & Stone: Wireframe vs Implementation FULL Audit

**Date:** 2026-01-03
**Purpose:** Document EVERY structural difference between wireframe and implementation
**Wireframe:** `docs/dev/design/wireframes/sage-and-stone/compiled/*.html`
**Implementation:** `https://sage-and-stone.lintel.site/`

---

## Executive Summary

The implementation is a **proof-of-concept** that reuses generic blocks with placeholder content. The wireframe is a **bespoke design** with unique page-specific structures, rich metadata, and specific copy.

**The implementation needs:**
1. **New specialized blocks** (not just CSS fixes)
2. **Page-specific content structures** (not reused generic blocks)
3. **Seeder rewrite** to match wireframe content EXACTLY
4. **Possibly new page types** for proper content modeling

---

## Page-by-Page Comparison

### Homepage (`index.html`)

#### Section 1: Alert Banner
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| "Waitlist open for Autumn 2026 Commissions" with dismiss button | May exist | **Verify exact text** |

#### Section 2: Hero
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Tagline: "Trends are loud. Legacy is quiet." | Missing | **ADD tagline field** |
| Headline: "Rooms that remember" | "Rooms that remember" | ✓ Match |
| Subheadline specific copy | Different copy | **UPDATE seeder** |
| Dual CTA: "Begin Your Commission" + "Our Philosophy" | May differ | **Verify CTAs** |
| Micro-CTA: "View the Provenance Plate" (opens modal) | Missing | **ADD micro-CTA** |

#### Section 3: Operational Proof Strip
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| 4-column stat strip directly under hero | Uses StatsBlock | **Verify exact content** |
| Capacity: "12 Commissions / Year" | Matches | ✓ |
| Timeline: "12–16 Week Build" | Matches | ✓ |
| Origin: "Workshop: Herefordshire" | Matches | ✓ |
| Promise: "Lifetime Joinery Guarantee" | Matches | ✓ |

#### Section 4: The Manifesto
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "The Manifesto" | "The Sage & Stone Philosophy" | **UPDATE seeder - exact copy** |
| Heading: "Good kitchens don't age. They season." | Matches | ✓ |
| Body: Specific 2 paragraphs about rebellion against disposable culture | Generic copy | **UPDATE seeder - exact copy** |
| Pull quote: "We build with solid timber, repairable joinery..." | Different | **UPDATE seeder** |
| NO image | May have image | **Verify layout** |

#### Section 5: Services/Offerings
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| 3x2 asymmetric grid layout | Cards layout | **DIFFERENT LAYOUT** |
| Featured Service (2-col span): "The Commission" with PRICE "£35k – £80k" | No price | **ADD price field to ServiceCardItemBlock** |
| Service 2 (1-col): "The Restoration" | Exists | Verify copy |
| Service 3 (1-col): "The Larder" | Exists | Verify copy |
| Large image block (2-col span) at bottom | Missing | **ADD IMAGE BLOCK** |

**NEW BLOCK NEEDED:** `ServiceGridBlock` with:
- Featured service (2-col) with price field
- Regular services (1-col each)
- Image block slot

#### Section 6: Provenance Section
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Interactive brass plate graphic with hover state | Static or missing | **VERIFY interactivity** |
| Click opens modal with "Artifact Dossier" | May not exist | **ADD modal** |
| Specific content: Maker, Source GPS, Completion date | Generic | **UPDATE content** |
| List: 3 bullet points about what plate contains | May differ | **Verify** |

#### Section 7: Portfolio / Case Files
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "Portfolio" + Heading: "Case Files" | "Case Files" / "Recent Commissions" | **Minor copy diff** |
| **3 projects with DETAILED metadata:** | Generic cards | **MAJOR GAP** |
| - The Kensington Commission | ✓ Title exists | |
| - Constraint: "Grade II Listed" | **MISSING** | **ADD field** |
| - Material: "Fumed Oak" | **MISSING** | **ADD field** |
| - Outcome: "Zero Alterations" | **MISSING** | **ADD field** |
| "View Full Archive" link | Exists | ✓ |

**NEW BLOCK NEEDED:** `CaseStudyCardBlock` with:
- title
- image
- constraint_label + constraint_value
- material_label + material_value
- outcome_label + outcome_value
- link_url

#### Section 8: Featured Story / Case Study
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Full section with image left, testimonial right | Exists as `FeaturedCaseStudyBlock` | **Verify content** |
| Project badge: "Project 042" | Generic | **UPDATE** |
| Title: "The Surrey Commission" | Different | **UPDATE** |
| Quote icon + testimonial text | May exist | **Verify** |
| Challenge section with heading + text | May differ | **Verify** |
| Outcome section with heading + text | May differ | **Verify** |
| Client attribution: "Eleanor & James, Haslemere, UK" | Generic | **UPDATE** |
| "View Full Case Study" CTA | May exist | **Verify** |

#### Section 9: FAQ / Commission Protocols
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "The Methodology" | Different | **UPDATE** |
| Heading: "Commission Protocols" | Different | **UPDATE** |
| Reference number: "Ref: 2025-OP-V4" | **MISSING** | **ADD field** |
| 3 accordion items with specific copy | May differ | **Verify exact copy** |

#### Section 10: Contact Form
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| "Commission Availability: Limited" label | May be missing | **ADD** |
| Headline: "Begin the conversation." | Matches? | **Verify** |
| Phone number prominent | May differ | **Verify** |
| Form fields: Name, Email, Dropdown, Message | May differ | **Verify** |

---

### About Page (`about.html`)

#### Section 1: Page Hero
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "The Guardians" | Different? | **Verify** |
| Headline: "Craftsmanship built on obsession." | Different? | **Verify** |
| Right-side intro text | May differ | **Verify** |
| "Meet the Makers" CTA button | May exist | **Verify** |

#### Section 2: Founder Letter
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Large quote icon | May exist | ✓ |
| Headline as quote: "I was tired of seeing kitchens..." | Verify | **Check** |
| 3 paragraphs of specific founder story | May be generic | **UPDATE seeder** |
| Founder signature: "Thomas J. Wright" | Exists | ✓ |
| Founder photo with overlay badge | May exist | **Verify** |

#### Section 3: Etiquette & Standards
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "Etiquette & Standards" | May differ | **Verify** |
| Heading: "Respect for the Sanctuary" | May differ | **Verify** |
| 3 numbered principles in dark section | May exist | **Verify layout** |
| 01. The Invisible Tradesmen | Verify copy | |
| 02. Obsessive Cleanliness | Verify copy | |
| 03. Vetted & Permanent | Verify copy | |

#### Section 4: Team Section
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "The Artisans" | May differ | **Verify** |
| Heading: "Meet the Makers" | May match | ✓ |
| "Combined Experience: 142 Years" badge | May be missing | **ADD** |
| 4 team members with quotes | May exist | **Verify quote field** |

**Team members in wireframe:**
- James E. - Head of Installation - quote: "Measure twice, cut once."
- Sarah M. - Finishing Specialist - no quote shown
- David R. - Master Joiner - no quote shown
- Marcus T. - Project Director - no quote shown

**VERIFY:** TeamMemberItemBlock has optional quote field

#### Section 5: Workshop Section
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "The Workshop" | May match | **Verify** |
| Heading: "From Herefordshire to Your Home" | May differ | **Verify** |
| 3 bullet points about workshop | May differ | **Verify** |
| Image with "Est. 2005" badge | May exist | **Verify** |

#### Section 6: Final CTA
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Icon (home icon) | May exist | **Verify** |
| Quote: "We treat your home as if it were our own..." | May differ | **Verify** |
| "Request a Site Visit" CTA | May differ | **Verify** |

---

### Services Page (`services.html`)

#### Section 1: Hero
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "Our Process" | May differ | **Verify** |
| Headline: "Precision Installation." | May differ | **Verify** |
| Right-side intro text | May exist | **Verify** |

#### Section 2: The "White Glove" Standard
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Large heading: "The 'White Glove' Standard." | May differ | **Verify** |
| 3 paragraphs of copy | May differ | **UPDATE seeder** |
| Dual CTAs: "Schedule Consultation" + "View Portfolio" | May exist | **Verify** |
| Phone number block | May exist | **Verify** |
| Two large stats: "100%" + "Zero" | May be different | **Verify** |
| Large image with overlay quote | May exist | **Verify** |

#### Section 3: Process Timeline
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| 5-phase timeline with connecting line | Uses ProcessStepsBlock | **Verify layout matches** |
| Phase 3 (Installation) is HIGHLIGHTED (dark card) | May not be highlighted | **CSS or block change** |
| Each phase has number, title, description | May match | **Verify** |
| "Start Your Project" CTA below timeline | May exist | **Verify** |
| Email capture box: "Get Our Installation Guide" | **LIKELY MISSING** | **ADD lead magnet block** |

**NEW BLOCK POSSIBLY NEEDED:** `LeadMagnetBlock` for email capture

#### Section 4: Service Grid
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| 4 service cards in 4-column grid | May exist | **Verify** |
| Each has icon, title, description | May match | **Verify** |
| Appliance Integration, Bespoke Joinery, Technical Integration, Stone & Surfaces | May match | **Verify** |

#### Section 5: Cleanliness Pledge
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Dark section with 2-column layout | May exist | **Verify layout** |
| Heading: "We leave only the Kitchen." | May differ | **Verify** |
| 4 checkmark items in 2x2 grid | May exist | **Verify** |

#### Section 6: Visual Proof
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| 3 square images with overlay labels | May exist | **Verify** |
| Each links to portfolio | May exist | **Verify** |
| "The Scribe", "The Hidden", "The Joint" labels | May be generic | **UPDATE seeder** |

#### Section 7: Accreditations
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| 4 certification logos | May exist | **Verify** |
| Warranty + Liability info boxes | May exist | **Verify** |

#### Section 8: FAQ
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| 3 questions specific to services | May exist | **Verify copy** |

#### Section 9: Sticky Footer CTA
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Appears on scroll, fixed to bottom | **LIKELY MISSING** | **ADD** (JS + HTML) |

---

### Portfolio Page (`portfolio.html`)

#### Section 1: Hero
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Eyebrow: "The Archive" | May differ | **Verify** |
| Headline: "Work of Permanent Value." | May differ | **Verify** |
| Right-side intro text | May exist | **Verify** |
| **FILTER BUTTONS:** All Commissions, Kitchens, Restoration, Furniture | **LIKELY MISSING** | **ADD** |

**NEW FEATURE NEEDED:** Portfolio filtering (JS + possible HTMX or Django view)

#### Section 2: Featured Project (Full Width)
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Project 042: The Highland Commission | May be different project | **UPDATE** |
| Ultra-wide aspect ratio image | May differ | **Verify** |
| Floating label with project number | May be missing | **ADD** |
| 4-column metadata: Location, Material, Quote, CTA | **LIKELY MISSING STRUCTURE** | **ADD** |

**NEW BLOCK NEEDED:** `FeaturedPortfolioItemBlock` with:
- project_number
- title
- location
- material
- quote
- image
- cta_url

#### Section 3: Project Grid
| Wireframe | Implementation | Gap |
|-----------|----------------|-----|
| Asymmetric masonry-style grid | Standard grid? | **Verify layout** |
| 5 projects total with varying sizes | May be different | **Verify** |
| Each project has specific metadata | Generic? | **Verify** |
| Quote block between projects | May be missing | **ADD** |

**Projects in wireframe:**
1. The Highland Commission (featured, full width)
2. The Pantry Larder (2/3 width)
3. The Georgian Restoration (1/3 width)
4. The Brutalist Barn (2/3 width)
5. The Utility Room (1/3 width)

---

### Blog List Page (`blog_list.html`)

Need to fetch and compare - likely similar structure issues.

---

### Blog Article Page (`blog_article.html`)

Need to fetch and compare - likely similar structure issues.

---

## NEW BLOCKS NEEDED

Based on this audit, the following NEW or MODIFIED blocks are required:

### 1. `CaseStudyMetadataBlock` (NEW)
For portfolio items with constraint/material/outcome fields:
```python
class CaseStudyMetadataBlock(blocks.StructBlock):
    constraint_label = blocks.CharBlock(default="Constraint")
    constraint_value = blocks.CharBlock()
    material_label = blocks.CharBlock(default="Material")
    material_value = blocks.CharBlock()
    outcome_label = blocks.CharBlock(default="Outcome")
    outcome_value = blocks.CharBlock()
```

### 2. Modify `PortfolioItemBlock`
Add metadata fields:
```python
# Add to existing block:
constraint = blocks.CharBlock(required=False)
material = blocks.CharBlock(required=False)
outcome = blocks.CharBlock(required=False)
project_number = blocks.CharBlock(required=False)  # e.g., "042"
location = blocks.CharBlock(required=False)
```

### 3. Modify `ServiceCardItemBlock`
Add price field:
```python
# Add to existing block:
price_range = blocks.CharBlock(required=False, help_text="e.g., £35k – £80k")
is_featured = blocks.BooleanBlock(required=False, default=False)
```

### 4. `LeadMagnetBlock` (NEW)
For email capture forms:
```python
class LeadMagnetBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False)
    heading = blocks.CharBlock()
    description = blocks.TextBlock()
    button_text = blocks.CharBlock(default="Download")
    # Links to form definition for processing
```

### 5. `FeaturedPortfolioHeroBlock` (NEW)
For portfolio page featured project:
```python
class FeaturedPortfolioHeroBlock(blocks.StructBlock):
    project_number = blocks.CharBlock()
    title = blocks.CharBlock()
    image = ImageChooserBlock()
    location = blocks.CharBlock()
    material = blocks.CharBlock()
    quote = blocks.TextBlock(required=False)
    cta_url = blocks.URLBlock()
```

### 6. `PortfolioFilterBlock` (NEW or use existing?)
If filtering is needed as a visible UI element.

### 7. Modify `TeamMemberItemBlock`
Verify quote field exists, if not add:
```python
quote = blocks.CharBlock(required=False)
```

### 8. Modify `FAQBlock`
Add reference number field:
```python
reference_number = blocks.CharBlock(required=False, help_text="e.g., Ref: 2025-OP-V4")
```

---

## SEEDER CHANGES NEEDED

The seeder (`seed_sage_stone.py`) needs updates to use EXACT wireframe copy:

### Homepage Content Updates
1. Hero tagline: Add "Trends are loud. Legacy is quiet."
2. Manifesto: Update to exact wireframe copy
3. Services: Add price to featured service
4. Portfolio: Add constraint/material/outcome metadata
5. Featured story: Update to Surrey Commission with exact copy

### About Page Content Updates
1. All section copy needs verification against wireframe
2. Team member quotes need to be added
3. Combined experience badge text

### Services Page Content Updates
1. White Glove section exact copy
2. Process timeline highlighting Phase 3
3. Add lead magnet block
4. Visual proof section with exact labels
5. Add sticky footer CTA

### Portfolio Page Content Updates
1. Add filter UI
2. Featured project structure
3. All project metadata
4. Asymmetric grid layout

---

## TEMPLATE CHANGES NEEDED

Theme A templates need updates for:

1. **Case study cards** - new template for metadata display
2. **Featured portfolio hero** - new template
3. **Lead magnet block** - new template
4. **Sticky footer CTA** - new template + JS
5. **Portfolio filtering** - JS/HTMX integration
6. **Service grid with featured item** - layout adjustments

---

## PRIORITY ORDER

### P0 - Critical (Without these, site is structurally wrong)
1. Add metadata fields to PortfolioItemBlock
2. Add price field to ServiceCardItemBlock
3. Update seeder with exact wireframe copy
4. Create FeaturedPortfolioHeroBlock

### P1 - High (Noticeable differences)
1. Portfolio filtering UI
2. Lead magnet block
3. Sticky footer CTA
4. Team member quotes

### P2 - Medium (Polish items)
1. FAQ reference number
2. Project number badges
3. Process timeline Phase 3 highlighting
4. Various exact copy matches

---

## CONCLUSION

This is NOT a CSS polish job. This requires:
- **Block model changes** (new fields, new blocks)
- **Seeder content rewrite** (exact copy from wireframe)
- **Template additions** (new block templates)
- **JavaScript additions** (filtering, sticky CTA)

The current Issue #461 scope is insufficient. A new Work Order is needed for "Wireframe Fidelity Implementation."
