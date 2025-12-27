# Sage & Stone Content Mapping

This document maps every section of the Sage & Stone wireframes to sum_core models and blocks.

---

## Brand Constants

These values appear throughout and should be defined once:

```python
BRAND = {
    "company_name": "Sage & Stone",
    "established_year": 2005,
    "tagline": "Rooms that remember",
    "phone": "+44 (0) 20 1234 5678",
    "email": "hello@sageandstone.com",
    "address": "The Old Joinery\nUnit 4\nHerefordshire HR4 9AB",
    "founder": "Thomas J. Wright",
    "founder_title": "Master Joiner",
    "founder_years": 28,
}

COLORS = {
    "primary": "#1A2F23",      # sage-black (Obsidian Green)
    "secondary": "#4A6350",    # sage-darkmoss
    "accent": "#A0563B",       # sage-terra (Burnished Terra)
    "background": "#F7F5F1",   # sage-linen
    "text": "#1A2F23",         # sage-black
    "surface": "#EDE8E0",      # sage-oat
    "surface_elevated": "#FFFFFF",
    "text_light": "#5A6E5F",   # sage meta
}

TYPOGRAPHY = {
    "heading_font": "Playfair Display",
    "body_font": "Lato",
}
```

---

## Page 1: Home (`index.html`)

**Model:** `HomePage` (client model in `home/models.py`)

### Hero Section
**Block:** `HeroImageBlock`

```python
{
    "type": "hero_image",
    "value": {
        "headline": "Rooms that remember",  # RichText italic
        "subheadline": "Heirloom-quality kitchens, handcrafted in Herefordshire. 12 commissions per year. Lifetime guarantee.",
        "ctas": [
            {"label": "Begin Your Commission", "url": "/contact/", "style": "primary"},
            {"label": "Our Philosophy", "url": "/about/", "style": "outline"}
        ],
        "status": "",
        "image": "<HERO_IMAGE>",
        "image_alt": "Bespoke kitchen interior with dark wood cabinetry",
        "overlay_opacity": "medium",
        "layout": "full",
        "floating_card_label": "",
        "floating_card_value": ""
    }
}
```

### Operational Proof Strip
**Block:** `StatsBlock`

```python
{
    "type": "stats",
    "value": {
        "eyebrow": "",
        "intro": "",
        "items": [
            {"value": "12", "label": "Commissions per year", "prefix": "", "suffix": ""},
            {"value": "12-16", "label": "Week build time", "prefix": "", "suffix": ""},
            {"value": "Herefordshire", "label": "Workshop location", "prefix": "", "suffix": ""},
            {"value": "Lifetime", "label": "Joinery guarantee", "prefix": "", "suffix": ""}
        ]
    }
}
```

### Manifesto Section
**Block:** `ManifestoBlock`

```python
{
    "type": "manifesto",
    "value": {
        "eyebrow": "The Sage & Stone Philosophy",
        "heading": "Good kitchens don't age. They <em>season</em>.",
        "body": "We curate the room your great-grandchildren will fight over. In a world of disposable design, we build against the grain—literally and figuratively.",
        "quote": "Speed is the enemy of legacy"
    }
}
```

### Services Grid
**Block:** `ServiceCardsBlock`

```python
{
    "type": "service_cards",
    "value": {
        "eyebrow": "Our Services",
        "heading": "What We Create",
        "intro": "Three ways to begin your Sage & Stone journey.",
        "view_all_link": "/services/",
        "view_all_label": "View all services",
        "cards": [
            {
                "icon": "",
                "image": "<SERVICE_COMMISSION_IMAGE>",
                "title": "The Commission",
                "description": "A fully bespoke kitchen, designed and built from first principles.",
                "link_url": "/services/commission/",
                "link_label": "Learn more"
            },
            {
                "icon": "",
                "image": "<SERVICE_RESTORATION_IMAGE>",
                "title": "The Restoration",
                "description": "Breathing new life into antique furniture and period kitchens.",
                "link_url": "/services/restoration/",
                "link_label": "Learn more"
            },
            {
                "icon": "",
                "image": "<SERVICE_LARDER_IMAGE>",
                "title": "The Larder",
                "description": "Standalone pantry units and storage solutions.",
                "link_url": "/services/larder/",
                "link_label": "Learn more"
            }
        ],
        "layout_style": "default"
    }
}
```

### Provenance Signature Experience
**Block:** `FeaturedCaseStudyBlock`

*Note: The interactive brass plate is a theme presentation feature. We seed the content.*

```python
{
    "type": "featured_case_study",
    "value": {
        "eyebrow": "Provenance Signature",
        "heading": "Every piece tells a story",
        "intro": "Each Sage & Stone kitchen carries a hand-engraved brass plate documenting its maker, timber source, and completion date.",
        "points": [
            "Hand-engraved by our master craftsmen",
            "GPS coordinates of timber source",
            "Unique serial number for lifetime support"
        ],
        "cta_text": "Learn about our materials",
        "cta_url": "/about/#materials",
        "image": "<PROVENANCE_IMAGE>",
        "image_alt": "Brass maker's plate with engraved details",
        "stats_label": "Kitchens completed",
        "stats_value": "247"
    }
}
```

### Portfolio Section
**Block:** `PortfolioBlock`

```python
{
    "type": "portfolio",
    "value": {
        "eyebrow": "Case Files",
        "heading": "Recent Commissions",
        "intro": "",
        "view_all_link": "/portfolio/",
        "view_all_label": "View all projects",
        "items": [
            {
                "title": "The Kensington Commission",
                "category": "kitchen",
                "image": "<PORTFOLIO_KENSINGTON>",
                "link_url": "/portfolio/kensington/",
                "description": ""
            },
            {
                "title": "The Cotswold Barn",
                "category": "kitchen",
                "image": "<PORTFOLIO_COTSWOLD>",
                "link_url": "/portfolio/cotswold/",
                "description": ""
            },
            {
                "title": "The Georgian Townhouse",
                "category": "kitchen",
                "image": "<PORTFOLIO_GEORGIAN>",
                "link_url": "/portfolio/georgian/",
                "description": ""
            }
        ]
    }
}
```

### Featured Case Study (Surrey Commission)
**Block:** `FeaturedCaseStudyBlock`

```python
{
    "type": "featured_case_study",
    "value": {
        "eyebrow": "Featured Commission",
        "heading": "The Surrey Commission",
        "intro": "A complete kitchen transformation for a Grade II listed property in the Surrey Hills.",
        "points": [
            "English oak from managed woodland",
            "Hand-cut dovetail joints throughout",
            "Integrated appliances from Gaggenau"
        ],
        "cta_text": "Read the full case study",
        "cta_url": "/portfolio/surrey/",
        "image": "<SURREY_IMAGE>",
        "image_alt": "Surrey kitchen with oak cabinetry",
        "stats_label": "Project duration",
        "stats_value": "14 weeks"
    }
}
```

*Customer testimonial below case study:*
**Block:** `SocialProofQuoteBlock`

```python
{
    "type": "social_proof_quote",
    "value": {
        "quote": "The attention to detail is extraordinary. Every drawer, every hinge—it's like working with artisans from another era.",
        "author": "Sarah M.",
        "role": "Homeowner",
        "company": "Surrey Hills",
        "logo": None
    }
}
```

### FAQ Section (Commission Protocols)
**Block:** `FAQBlock`

```python
{
    "type": "faq",
    "value": {
        "eyebrow": "Commission Protocols",
        "heading": "How It Works",
        "intro": "",
        "items": [
            {
                "question": "Timeline & Pacing",
                "answer": "Every commission begins with a site visit and design consultation. From approval to installation typically takes 12-16 weeks. We limit ourselves to 12 commissions per year to ensure every project receives our full attention."
            },
            {
                "question": "Material Provenance",
                "answer": "We source timber exclusively from managed British woodlands. Each piece is tracked from tree to kitchen, with full documentation of origin, seasoning time, and milling date."
            },
            {
                "question": "International Works",
                "answer": "We undertake select international commissions in Europe and North America. International projects require a minimum engagement and extended lead times. Contact us to discuss feasibility."
            }
        ],
        "allow_multiple_open": False
    }
}
```

### Contact Form Section
**Block:** `ContactFormBlock`

```python
{
    "type": "contact_form",
    "value": {
        "eyebrow": "Begin the Conversation",
        "heading": "Request a Consultation",
        "intro": "Tell us about your project and we'll be in touch within 48 hours.",
        "success_message": "Thank you for your enquiry. We'll be in touch shortly.",
        "submit_label": "Send Enquiry"
    }
}
```

---

## Page 2: About (`about.html`)

**Model:** `StandardPage`

### Hero Section
**Block:** `HeroGradientBlock`

```python
{
    "type": "hero_gradient",
    "value": {
        "headline": "Craftsmanship built on <em>obsession</em>",
        "subheadline": "Three decades of refining our craft. One mission: kitchens that outlast trends.",
        "ctas": [],
        "status": "",
        "gradient_style": "primary"
    }
}
```

### Founder Letter Section
**Block:** `FeaturedCaseStudyBlock` (repurposed for founder story)

```python
{
    "type": "featured_case_study",
    "value": {
        "eyebrow": "A Letter from the Founder",
        "heading": "Thomas J. Wright",
        "intro": "I started Sage & Stone because I was tired of watching beautiful timber turned into forgettable furniture. Every kitchen we build is an argument against disposability—a physical reminder that permanence is possible.\n\nWe don't chase trends. We don't cut corners. We build rooms that your grandchildren will cook Sunday lunch in.",
        "points": [],
        "cta_text": "",
        "cta_url": "",
        "image": "<FOUNDER_IMAGE>",
        "image_alt": "Thomas J. Wright, Master Joiner and Founder",
        "stats_label": "Years of experience",
        "stats_value": "28"
    }
}
```

### Etiquette & Standards Section
**Block:** `ServiceCardsBlock` (used for pillars)

```python
{
    "type": "service_cards",
    "value": {
        "eyebrow": "Our Standards",
        "heading": "The Sage & Stone Etiquette",
        "intro": "Three non-negotiable principles that guide every commission.",
        "view_all_link": "",
        "view_all_label": "",
        "cards": [
            {
                "icon": "🤫",
                "image": None,
                "title": "Invisible Tradesmen",
                "description": "You'll never know we were there. Sites are left cleaner than we found them. No radio, no mess, no drama.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "✨",
                "image": None,
                "title": "Obsessive Cleanliness",
                "description": "Daily dust extraction, floor protection, and sealed work areas. We treat your home like our workshop.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "🔒",
                "image": None,
                "title": "Vetted & Permanent",
                "description": "Every team member has been with us for 5+ years. No subcontractors, no strangers in your home.",
                "link_url": "",
                "link_label": ""
            }
        ],
        "layout_style": "tight"
    }
}
```

### Meet the Makers Section
**Block:** `TeamMemberBlock`

```python
{
    "type": "team_members",
    "value": {
        "eyebrow": "Meet the Makers",
        "heading": "The people behind every commission",
        "members": [
            {
                "name": "James E.",
                "role": "Head of Installation",
                "bio": "15 years precision fitting",
                "image": "<TEAM_JAMES>"
            },
            {
                "name": "Sarah M.",
                "role": "Finishing Specialist",
                "bio": "Traditional hand-finishing techniques",
                "image": "<TEAM_SARAH>"
            },
            {
                "name": "David R.",
                "role": "Master Joiner",
                "bio": "Third-generation craftsman",
                "image": "<TEAM_DAVID>"
            },
            {
                "name": "Marcus T.",
                "role": "Project Director",
                "bio": "Your single point of contact",
                "image": "<TEAM_MARCUS>"
            }
        ]
    }
}
```

### Workshop Section
**Block:** `FeaturedCaseStudyBlock`

```python
{
    "type": "featured_case_study",
    "value": {
        "eyebrow": "The Workshop",
        "heading": "Herefordshire, Est. 2005",
        "intro": "Our solar-powered facility in the Herefordshire countryside is where every Sage & Stone piece comes to life. We maintain an open workshop policy—clients are welcome to visit and witness their kitchen taking shape.",
        "points": [
            "4,000 sq ft purpose-built facility",
            "Solar-powered operations",
            "Open workshop visits available"
        ],
        "cta_text": "Schedule a workshop visit",
        "cta_url": "/contact/",
        "image": "<WORKSHOP_IMAGE>",
        "image_alt": "Sage & Stone workshop interior",
        "stats_label": "Years at this location",
        "stats_value": "20"
    }
}
```

### Final CTA
**Block:** `ButtonGroupBlock`

```python
{
    "type": "buttons",
    "value": {
        "alignment": "center",
        "buttons": [
            {
                "label": "Request a Site Visit",
                "url": "/contact/",
                "style": "primary"
            }
        ]
    }
}
```

---

## Page 3: Services (`services.html`)

**Model:** `StandardPage`

### Hero Section
**Block:** `HeroGradientBlock`

```python
{
    "type": "hero_gradient",
    "value": {
        "headline": "Precision <em>Installation</em>",
        "subheadline": "Total project management from first measurement to final polish.",
        "ctas": [],
        "gradient_style": "primary"
    }
}
```

### White Glove Standard Section
**Block:** `ManifestoBlock`

```python
{
    "type": "manifesto",
    "value": {
        "eyebrow": "The White Glove Standard",
        "heading": "Installation is not an afterthought",
        "body": "Too many beautiful kitchens are ruined by poor installation. At Sage & Stone, installation is where our obsession with detail truly shows. Every gap, every alignment, every finish—measured to the millimetre.",
        "quote": "Millimetre-perfect is not a goal. It is the baseline."
    }
}
```

### Process Timeline Section
**Block:** `ProcessStepsBlock`

```python
{
    "type": "process",
    "value": {
        "eyebrow": "The Process",
        "heading": "Five Phases to Completion",
        "intro": "Every installation follows our proven methodology.",
        "steps": [
            {
                "number": 1,
                "title": "Consultation",
                "description": "Site survey, design brief, and feasibility assessment."
            },
            {
                "number": 2,
                "title": "Strip-Out",
                "description": "Careful removal of existing fixtures with full site protection."
            },
            {
                "number": 3,
                "title": "Installation",
                "description": "Precision fitting of cabinetry, worktops, and integrated appliances."
            },
            {
                "number": 4,
                "title": "Calibration",
                "description": "Fine-tuning of doors, drawers, and hardware for perfect operation."
            },
            {
                "number": 5,
                "title": "Handover",
                "description": "Full demonstration, documentation, and aftercare guidance."
            }
        ]
    }
}
```

### Lead Magnet Section
**Block:** `ContactFormBlock` (simplified for email capture)

*Note: This captures email for a PDF download. Use ContactFormBlock with appropriate copy.*

```python
{
    "type": "contact_form",
    "value": {
        "eyebrow": "Free Guide",
        "heading": "The Installation Guide",
        "intro": "Download our 24-page guide to understanding the bespoke kitchen installation process.",
        "success_message": "Check your inbox for your download link.",
        "submit_label": "Send me the guide"
    }
}
```

### Service Breakdown Section
**Block:** `ServiceCardsBlock`

```python
{
    "type": "service_cards",
    "value": {
        "eyebrow": "What We Handle",
        "heading": "Complete Project Management",
        "intro": "",
        "cards": [
            {
                "icon": "",
                "image": "<SERVICE_APPLIANCE>",
                "title": "Appliance Integration",
                "description": "Seamless fitting of all integrated appliances, from refrigeration to extraction.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "",
                "image": "<SERVICE_JOINERY>",
                "title": "Bespoke Joinery",
                "description": "On-site adjustments and custom fitting to accommodate period properties.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "",
                "image": "<SERVICE_TECHNICAL>",
                "title": "Technical Integration",
                "description": "Plumbing, electrical, and gas connections by certified specialists.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "",
                "image": "<SERVICE_STONE>",
                "title": "Stone & Surfaces",
                "description": "Precision templating and installation of worktops and splashbacks.",
                "link_url": "",
                "link_label": ""
            }
        ],
        "layout_style": "default"
    }
}
```

### Cleanliness Pledge Section
**Block:** `ServiceCardsBlock` (using icon-only cards)

```python
{
    "type": "service_cards",
    "value": {
        "eyebrow": "The Cleanliness Pledge",
        "heading": "Four Guarantees",
        "intro": "Your home deserves the same respect as our workshop.",
        "cards": [
            {
                "icon": "🧹",
                "image": None,
                "title": "Daily Clean",
                "description": "Work areas cleaned and vacuumed at the end of every day.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "🛡️",
                "image": None,
                "title": "Floor Protection",
                "description": "Heavy-duty floor coverings throughout the project duration.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "🌬️",
                "image": None,
                "title": "Dust Extraction",
                "description": "Industrial extraction at source for all cutting and sanding.",
                "link_url": "",
                "link_label": ""
            },
            {
                "icon": "🚪",
                "image": None,
                "title": "Sealed Zones",
                "description": "Work areas sealed from living spaces with temporary partitions.",
                "link_url": "",
                "link_label": ""
            }
        ],
        "layout_style": "tight"
    }
}
```

### Proof Gallery Section
**Block:** `GalleryBlock`

```python
{
    "type": "gallery",
    "value": {
        "eyebrow": "The Details",
        "heading": "Obsession in every joint",
        "intro": "",
        "images": [
            {"image": "<DETAIL_1>", "alt_text": "Hand-cut dovetail joint detail", "caption": ""},
            {"image": "<DETAIL_2>", "alt_text": "Precision hinge alignment", "caption": ""},
            {"image": "<DETAIL_3>", "alt_text": "Hand-finished oak surface", "caption": ""}
        ]
    }
}
```

### Certifications Section
**Block:** `TrustStripBlock` (logos)

```python
{
    "type": "trust_strip_logos",
    "value": {
        "eyebrow": "Certifications & Memberships",
        "items": [
            {"logo": "<LOGO_GASSAFE>", "alt_text": "Gas Safe Registered", "url": ""},
            {"logo": "<LOGO_NICEIC>", "alt_text": "NICEIC Approved", "url": ""},
            {"logo": "<LOGO_BIKBBI>", "alt_text": "BiKBBI Member", "url": ""},
            {"logo": "<LOGO_GUILD>", "alt_text": "Guild of Master Craftsmen", "url": ""}
        ]
    }
}
```

### FAQ Section
**Block:** `FAQBlock`

```python
{
    "type": "faq",
    "value": {
        "eyebrow": "Common Questions",
        "heading": "Installation FAQs",
        "intro": "",
        "items": [
            {
                "question": "What is the typical lead time for installation?",
                "answer": "Installation typically begins 10-12 weeks after design approval, allowing time for material sourcing and workshop production. The installation phase itself takes 2-3 weeks depending on project scope."
            },
            {
                "question": "Do you install flat-pack kitchens?",
                "answer": "No. We only install kitchens built in our Herefordshire workshop. Every piece is crafted specifically for your space—flat-pack has no place in our process."
            },
            {
                "question": "How do you manage other trades?",
                "answer": "We coordinate all required trades including plumbing, electrical, and plastering. Our project director serves as your single point of contact, managing the entire installation timeline."
            }
        ],
        "allow_multiple_open": False
    }
}
```

---

## Page 4: Portfolio (`portfolio.html`)

**Model:** `StandardPage`

### Page Header with Filters
**Block:** `EditorialHeaderBlock`

*Note: Category filtering is handled by theme/JS. We provide the content.*

```python
{
    "type": "editorial_header",
    "value": {
        "align": "center",
        "eyebrow": "Our Work",
        "heading": "The Portfolio"
    }
}
```

### Featured Project (Highland Commission)
**Block:** `FeaturedCaseStudyBlock`

```python
{
    "type": "featured_case_study",
    "value": {
        "eyebrow": "Featured",
        "heading": "The Highland Commission",
        "intro": "A complete kitchen and utility suite for a Scottish estate, featuring locally-sourced larch and hand-forged ironmongery.",
        "points": [],
        "cta_text": "View project",
        "cta_url": "/portfolio/highland/",
        "image": "<PORTFOLIO_HIGHLAND>",
        "image_alt": "Highland Commission kitchen interior",
        "stats_label": "",
        "stats_value": ""
    }
}
```

### Project Grid
**Block:** `PortfolioBlock`

```python
{
    "type": "portfolio",
    "value": {
        "eyebrow": "",
        "heading": "",
        "intro": "",
        "view_all_link": "",
        "view_all_label": "",
        "items": [
            {
                "title": "The Pantry Larder",
                "category": "furniture",
                "image": "<PORTFOLIO_LARDER>",
                "link_url": "/portfolio/pantry-larder/",
                "description": "Freestanding larder unit in English oak"
            },
            {
                "title": "The Georgian Restoration",
                "category": "restoration",
                "image": "<PORTFOLIO_GEORGIAN_REST>",
                "link_url": "/portfolio/georgian-restoration/",
                "description": "Period-sympathetic kitchen for a 1780s townhouse"
            },
            {
                "title": "The Brutalist Barn",
                "category": "kitchen",
                "image": "<PORTFOLIO_BRUTALIST>",
                "link_url": "/portfolio/brutalist-barn/",
                "description": "Contemporary design meets agricultural character"
            },
            {
                "title": "The Utility Room",
                "category": "furniture",
                "image": "<PORTFOLIO_UTILITY>",
                "link_url": "/portfolio/utility-room/",
                "description": "Boot room and utility suite"
            }
        ]
    }
}
```

### Quote Interlude
**Block:** `QuoteBlock`

```python
{
    "type": "quote",
    "value": {
        "quote": "We don't build against nature. We negotiate with it.",
        "author": "Thomas J. Wright",
        "role": "Founder"
    }
}
```

### Final CTA
**Block:** `ButtonGroupBlock`

```python
{
    "type": "buttons",
    "value": {
        "alignment": "center",
        "buttons": [
            {"label": "Enquire for 2026", "url": "/contact/", "style": "primary"},
            {"label": "Read about our process", "url": "/services/", "style": "outline"}
        ]
    }
}
```

---

## Page 5: Blog List (`blog_list.html`)

**Model:** `BlogIndexPage`

### Configuration
```python
BlogIndexPage(
    title="The Ledger",
    slug="journal",
    intro="Notes from the workshop. Stories of timber, craft, and the kitchens we build.",
    posts_per_page=9
)
```

### Categories to Create
```python
CATEGORIES = [
    {"name": "Commission Stories", "slug": "commission-stories", "description": "Behind the scenes of our kitchen commissions"},
    {"name": "Material Science", "slug": "material-science", "description": "Deep dives into timber, joinery, and craft"},
    {"name": "The Workshop", "slug": "the-workshop", "description": "News and updates from Herefordshire"},
]
```

*Note: "All Entries" filter is built into BlogIndexPage template.*

---

## Page 6: Blog Article (`blog_article.html`)

**Model:** `BlogPostPage`

### Example Article: "The Art of Seasoning Timber"

```python
BlogPostPage(
    title="The Art of Seasoning Timber",
    slug="art-of-seasoning-timber",
    category=Category.objects.get(slug="material-science"),
    published_date="2025-11-15",
    featured_image="<BLOG_TIMBER_IMAGE>",
    excerpt="Why we wait years before a single plank touches our workshop. The ancient practice that separates heirloom furniture from firewood.",
    author_name="Thomas J. Wright",
    body=[
        # Table of Contents
        {
            "type": "table_of_contents",
            "value": {
                "items": [
                    {"anchor": "understanding-moisture", "label": "Understanding Moisture"},
                    {"anchor": "the-waiting-game", "label": "The Waiting Game"},
                    {"anchor": "modern-shortcuts", "label": "Modern Shortcuts"},
                    {"anchor": "our-approach", "label": "Our Approach"}
                ]
            }
        },
        # Introduction
        {
            "type": "rich_text",
            "value": {
                "align": "left",
                "body": "<p class=\"lead\">There's a reason antique furniture survives centuries while modern pieces warp within years. The secret isn't in the joinery or the finish—it's in the waiting.</p><p>When a tree is felled, its wood contains up to 80% moisture. Use it immediately, and you're building with a ticking time bomb. As that moisture escapes over months and years, the wood shrinks, twists, and cracks. Every joint loosens. Every surface cups.</p>"
            }
        },
        # Section heading
        {
            "type": "editorial_header",
            "value": {
                "align": "left",
                "eyebrow": "",
                "heading": "<h2 id=\"understanding-moisture\">Understanding Moisture Content</h2>"
            }
        },
        # Content continues...
        {
            "type": "rich_text",
            "value": {
                "align": "left",
                "body": "<p>Freshly cut timber has a moisture content (MC) of 60-80%. For furniture making, we need to bring this down to 8-12%—equilibrium with a typical heated home. Get this wrong, and disaster follows.</p><blockquote>Wood remembers. Every stress, every rush, every shortcut—it will express them eventually.</blockquote>"
            }
        },
        # Image
        {
            "type": "image_block",
            "value": {
                "image": "<BLOG_TIMBER_STACK>",
                "alt_text": "Oak boards stacked for air drying",
                "caption": "Our timber stacks: each board separated by spacers for airflow",
                "full_width": True
            }
        }
        # ... additional content blocks
    ]
)
```

### Additional Blog Posts to Create

| Title | Category | Published |
|-------|----------|-----------|
| The Art of Seasoning Timber | Material Science | 2025-11-15 |
| Inside the Kensington Commission | Commission Stories | 2025-10-28 |
| Hand-Cut vs Machine Dovetails | Material Science | 2025-10-15 |
| Workshop Update: New Finishing Room | The Workshop | 2025-09-30 |
| The Georgian Restoration: A 12-Month Journey | Commission Stories | 2025-09-15 |
| Why We Don't Use MDF | Material Science | 2025-08-20 |
| Meet Marcus: Our New Project Director | The Workshop | 2025-08-01 |

---

## Page 7: Terms of Supply (`terms.html`)

**Model:** `LegalPage`

```python
LegalPage(
    title="Terms of Supply",
    slug="terms",
    last_updated=date(2025, 1, 15),
    sections=[
        {
            "type": "legal_section",
            "value": {
                "anchor": "definitions",
                "heading": "1. Definitions",
                "body": "<p>In these Terms of Supply:</p><ul><li><strong>\"The Company\"</strong> means Sage & Stone Ltd, registered in England and Wales.</li><li><strong>\"The Client\"</strong> means the individual or entity commissioning works.</li><li><strong>\"The Works\"</strong> means all furniture, joinery, and installation services commissioned.</li><li><strong>\"The Contract\"</strong> means the agreement formed by acceptance of our quotation.</li></ul>"
            }
        },
        {
            "type": "legal_section",
            "value": {
                "anchor": "scope",
                "heading": "2. Scope of Works",
                "body": "<p>The scope of works is defined exclusively by the accepted quotation and accompanying drawings. Any variations must be agreed in writing and may affect the contract price and timeline.</p><h3>In Plain English</h3><p>What's in the quote is what you get. Want changes? No problem—but let's discuss the impact first.</p>"
            }
        },
        {
            "type": "legal_section",
            "value": {
                "anchor": "payment",
                "heading": "3. Payment Structure",
                "body": "<p>Payment is due in three stages:</p><ul><li><strong>40%</strong> upon acceptance of quotation (deposit)</li><li><strong>40%</strong> upon completion of workshop production</li><li><strong>20%</strong> upon completion of installation</li></ul><p>All payments are due within 14 days of invoice date. We reserve the right to charge interest on overdue amounts at 4% above Bank of England base rate.</p><h3>In Plain English</h3><p>We don't ask for full payment upfront. You pay as we progress, with the final balance due only when you're completely happy with the finished kitchen.</p>"
            }
        },
        {
            "type": "legal_section",
            "value": {
                "anchor": "materials",
                "heading": "4. Living Materials",
                "body": "<p>Solid timber is a natural material that responds to its environment. Minor movement, checking, and colour variation are inherent characteristics, not defects. We select and season our timber to minimise these effects, but some degree of natural behaviour should be expected and embraced.</p><h3>In Plain English</h3><p>Wood is alive—even after it becomes furniture. Small cracks, colour changes, and seasonal movement are signs of authenticity, not failure. It's what separates real craftsmanship from plastic pretenders.</p>"
            }
        },
        {
            "type": "legal_section",
            "value": {
                "anchor": "access",
                "heading": "5. Access & Logistics",
                "body": "<p>The Client agrees to provide:</p><ul><li>Clear access to work areas during agreed installation dates</li><li>Reasonable facilities for our installation team</li><li>Timely decisions when variations arise</li></ul><p>Delays caused by lack of access or client decisions may affect the project timeline and could incur additional costs.</p>"
            }
        },
        {
            "type": "legal_section",
            "value": {
                "anchor": "guarantee",
                "heading": "6. The Guarantee",
                "body": "<p>All Sage & Stone joinery carries our Lifetime Joinery Guarantee. This covers:</p><ul><li>Structural integrity of all joints and carcasses</li><li>Drawer and door mechanisms</li><li>Finish adhesion and integrity</li></ul><p>The guarantee does not cover:</p><ul><li>Natural timber movement and colour change</li><li>Damage from misuse or accident</li><li>Appliances (covered by manufacturer warranty)</li><li>Consumables (handles, hinges after 5 years)</li></ul><h3>In Plain English</h3><p>If our joinery fails, we fix it. Forever. But we can't be responsible for accidents, natural aging, or appliance issues.</p>"
            }
        }
    ]
)
```

---

## Navigation Structure

### HeaderNavigation Configuration

```python
HeaderNavigation(
    site=site,
    show_phone_in_header=True,
    header_cta_enabled=True,
    header_cta_text="Enquire",
    header_cta_link=[{"link_type": "page", "page": contact_page}],
    mobile_cta_enabled=True,
    mobile_cta_phone_enabled=True,
    mobile_cta_button_enabled=True,
    mobile_cta_button_text="Enquire",
    mobile_cta_button_link=[{"link_type": "page", "page": contact_page}],
    menu_items=[
        {
            "label": "Kitchens",
            "link": {"link_type": "page", "page": portfolio_page},
            "children": [
                {
                    "label": "Collections",
                    "link": {"link_type": "anchor", "anchor": ""},
                    "children": [
                        {"label": "The Heritage", "link": {"link_type": "url", "url": "/portfolio/?category=heritage"}},
                        {"label": "The Modernist", "link": {"link_type": "url", "url": "/portfolio/?category=modernist"}},
                        {"label": "The Utility", "link": {"link_type": "url", "url": "/portfolio/?category=utility"}}
                    ]
                },
                {
                    "label": "Fitted Joinery",
                    "link": {"link_type": "anchor", "anchor": ""},
                    "children": [
                        {"label": "Larder Cupboards", "link": {"link_type": "url", "url": "/portfolio/?type=larder"}},
                        {"label": "Island Units", "link": {"link_type": "url", "url": "/portfolio/?type=island"}},
                        {"label": "Wall Cabinetry", "link": {"link_type": "url", "url": "/portfolio/?type=wall"}}
                    ]
                },
                {
                    "label": "Freestanding",
                    "link": {"link_type": "anchor", "anchor": ""},
                    "children": [
                        {"label": "Prep Tables", "link": {"link_type": "url", "url": "/portfolio/?type=prep"}},
                        {"label": "Butcher Blocks", "link": {"link_type": "url", "url": "/portfolio/?type=butcher"}},
                        {"label": "Dressers", "link": {"link_type": "url", "url": "/portfolio/?type=dresser"}}
                    ]
                }
            ]
        },
        {"label": "What We Do", "link": {"link_type": "page", "page": services_page}, "children": []},
        {"label": "Who We Are", "link": {"link_type": "page", "page": about_page}, "children": []},
        {"label": "Portfolio", "link": {"link_type": "page", "page": portfolio_page}, "children": []},
        {"label": "Journal", "link": {"link_type": "page", "page": blog_index_page}, "children": []}
    ]
)
```

### FooterNavigation Configuration

```python
FooterNavigation(
    site=site,
    tagline="Rooms that remember.",
    link_sections=[
        {
            "title": "Explore",
            "links": [
                {"link_type": "page", "page": about_page, "link_text": "Who We Are"},
                {"link_type": "page", "page": services_page, "link_text": "What We Do"},
                {"link_type": "page", "page": blog_index_page, "link_text": "Journal"},
                {"link_type": "page", "page": portfolio_page, "link_text": "Our Portfolio"}
            ]
        },
        {
            "title": "Legal",
            "links": [
                {"link_type": "url", "url": "/privacy/", "link_text": "Privacy Policy"},
                {"link_type": "page", "page": terms_page, "link_text": "Terms of Service"},
                {"link_type": "url", "url": "/accessibility/", "link_text": "Accessibility"}
            ]
        },
        {
            "title": "Studio",
            "links": [
                {"link_type": "anchor", "anchor": "", "link_text": "The Old Joinery, Unit 4"},
                {"link_type": "anchor", "anchor": "", "link_text": "Herefordshire HR4 9AB"},
                {"link_type": "email", "email": "hello@sageandstone.com", "link_text": "hello@sageandstone.com"},
                {"link_type": "phone", "phone": "+44 (0) 20 1234 5678", "link_text": "+44 (0) 20 1234 5678"}
            ]
        }
    ],
    social_instagram="https://instagram.com/sageandstone",
    copyright_text="© {year} Sage & Stone Ltd. All rights reserved."
)
```

---

## Image Requirements

### Placeholder Images to Generate

| Key | Dimensions | Aspect | Description |
|-----|------------|--------|-------------|
| HERO_IMAGE | 1920x1080 | 16:9 | Dark kitchen hero |
| FOUNDER_IMAGE | 800x1000 | 4:5 | Thomas Wright portrait |
| TEAM_JAMES | 400x500 | 4:5 | Team member headshot |
| TEAM_SARAH | 400x500 | 4:5 | Team member headshot |
| TEAM_DAVID | 400x500 | 4:5 | Team member headshot |
| TEAM_MARCUS | 400x500 | 4:5 | Team member headshot |
| WORKSHOP_IMAGE | 1200x800 | 3:2 | Workshop interior |
| SERVICE_COMMISSION | 600x400 | 3:2 | Kitchen interior |
| SERVICE_RESTORATION | 600x400 | 3:2 | Antique restoration |
| SERVICE_LARDER | 600x400 | 3:2 | Larder cupboard |
| SERVICE_APPLIANCE | 600x400 | 3:2 | Appliance detail |
| SERVICE_JOINERY | 600x400 | 3:2 | Joinery close-up |
| SERVICE_TECHNICAL | 600x400 | 3:2 | Technical work |
| SERVICE_STONE | 600x400 | 3:2 | Stone worktop |
| PORTFOLIO_KENSINGTON | 800x600 | 4:3 | Kitchen project |
| PORTFOLIO_COTSWOLD | 800x600 | 4:3 | Barn kitchen |
| PORTFOLIO_GEORGIAN | 800x600 | 4:3 | Georgian kitchen |
| PORTFOLIO_HIGHLAND | 1200x600 | 2:1 | Featured project |
| PORTFOLIO_LARDER | 600x800 | 3:4 | Larder unit |
| PORTFOLIO_GEORGIAN_REST | 600x800 | 3:4 | Restoration |
| PORTFOLIO_BRUTALIST | 800x500 | 8:5 | Modern barn |
| PORTFOLIO_UTILITY | 600x800 | 3:4 | Utility room |
| SURREY_IMAGE | 1000x700 | 10:7 | Case study |
| PROVENANCE_IMAGE | 800x600 | 4:3 | Brass plate |
| DETAIL_1 | 600x600 | 1:1 | Dovetail close-up |
| DETAIL_2 | 600x600 | 1:1 | Hinge detail |
| DETAIL_3 | 600x600 | 1:1 | Surface finish |
| LOGO_GASSAFE | 200x80 | auto | Certification logo |
| LOGO_NICEIC | 200x80 | auto | Certification logo |
| LOGO_BIKBBI | 200x80 | auto | Certification logo |
| LOGO_GUILD | 200x80 | auto | Certification logo |
| BLOG_TIMBER_IMAGE | 1200x600 | 2:1 | Featured blog image |
| BLOG_TIMBER_STACK | 1000x600 | 5:3 | Timber stacking |

**Total: ~35 placeholder images**

---

## Summary

This mapping document provides:
- Complete page → model mapping
- Block-by-block content structure
- All copy text from wireframes
- Navigation hierarchy
- Image specifications

Implementation should follow this document to ensure content fidelity.
