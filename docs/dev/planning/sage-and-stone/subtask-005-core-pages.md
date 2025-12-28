# Subtask 005: Core Pages

## Overview

Create the main content pages: Home, About, Services, Portfolio using StreamField blocks with complete copy from wireframes.

## Deliverables

1. HomePage with full StreamField content
2. About StandardPage
3. Services StandardPage
4. Portfolio StandardPage
5. Contact StandardPage (for form)

## Page Hierarchy

```
Root (wagtail root)
└── Home (HomePage, slug="home")
    ├── About (StandardPage, slug="about")
    ├── Services (StandardPage, slug="services")
    ├── Portfolio (StandardPage, slug="portfolio")
    ├── Contact (StandardPage, slug="contact")
    ├── Journal (BlogIndexPage, slug="journal") [Subtask 6]
    └── Terms (LegalPage, slug="terms") [Subtask 7]
```

## Implementation

### 1. Page Creation Orchestrator

```python
from sum_core.pages.standard import StandardPage
from wagtail.models import Page

def create_pages(self, home_page):
    """Create all content pages under home."""

    pages = {"home": home_page}

    # Create child pages
    pages["about"] = self._create_about_page(home_page)
    pages["services"] = self._create_services_page(home_page)
    pages["portfolio"] = self._create_portfolio_page(home_page)
    pages["contact"] = self._create_contact_page(home_page)

    # Update home page with full content
    self._populate_home_content(home_page)

    self.stdout.write(f"Created {len(pages)} pages")
    return pages
```

### 2. HomePage Content

```python
def _populate_home_content(self, home_page):
    """Add StreamField content to homepage."""

    home_page.body = [
        # Hero Section
        {
            "type": "hero_image",
            "value": {
                "headline": "<em>Rooms that remember</em>",
                "subheadline": "Heirloom-quality kitchens, handcrafted in Herefordshire. 12 commissions per year. Lifetime guarantee.",
                "ctas": [
                    {"label": "Begin Your Commission", "url": "/contact/", "style": "primary", "open_in_new_tab": False},
                    {"label": "Our Philosophy", "url": "/about/", "style": "outline", "open_in_new_tab": False}
                ],
                "status": "",
                "image": self.images["HERO_IMAGE"].pk,
                "image_alt": "Bespoke kitchen interior with dark wood cabinetry",
                "overlay_opacity": "medium",
                "layout": "full",
                "floating_card_label": "",
                "floating_card_value": ""
            }
        },

        # Operational Proof Strip
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
        },

        # Manifesto Section
        {
            "type": "manifesto",
            "value": {
                "eyebrow": "The Sage & Stone Philosophy",
                "heading": "Good kitchens don't age. They <em>season</em>.",
                "body": "<p>We curate the room your great-grandchildren will fight over.</p><p>In a world of disposable design, we build against the grain—literally and figuratively. Every joint is cut by hand. Every surface is finished to last decades, not seasons.</p>",
                "quote": "Speed is the enemy of legacy"
            }
        },

        # Services Grid
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
                        "image": self.images["SERVICE_COMMISSION"].pk,
                        "title": "The Commission",
                        "description": "<p>A fully bespoke kitchen, designed and built from first principles. Your space, your needs, your legacy.</p>",
                        "link_url": "/services/#commission",
                        "link_label": "Learn more"
                    },
                    {
                        "icon": "",
                        "image": self.images["SERVICE_RESTORATION"].pk,
                        "title": "The Restoration",
                        "description": "<p>Breathing new life into antique furniture and period kitchens. Respect for heritage, executed with precision.</p>",
                        "link_url": "/services/#restoration",
                        "link_label": "Learn more"
                    },
                    {
                        "icon": "",
                        "image": self.images["SERVICE_LARDER"].pk,
                        "title": "The Larder",
                        "description": "<p>Standalone pantry units and storage solutions. The perfect introduction to Sage & Stone craftsmanship.</p>",
                        "link_url": "/services/#larder",
                        "link_label": "Learn more"
                    }
                ],
                "layout_style": "default"
            }
        },

        # Provenance Section
        {
            "type": "featured_case_study",
            "value": {
                "eyebrow": "Provenance Signature",
                "heading": "Every piece tells a story",
                "intro": "<p>Each Sage & Stone kitchen carries a hand-engraved brass plate documenting its maker, timber source, and completion date.</p>",
                "points": [
                    "Hand-engraved by our master craftsmen",
                    "GPS coordinates of timber source",
                    "Unique serial number for lifetime support"
                ],
                "cta_text": "Learn about our materials",
                "cta_url": "/about/#materials",
                "image": self.images["PROVENANCE_IMAGE"].pk,
                "image_alt": "Brass maker's plate with engraved details",
                "stats_label": "Kitchens completed",
                "stats_value": "247"
            }
        },

        # Portfolio Section
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
                        "image": self.images["PORTFOLIO_KENSINGTON"].pk,
                        "link_url": "/portfolio/#kensington",
                        "description": ""
                    },
                    {
                        "title": "The Cotswold Barn",
                        "category": "kitchen",
                        "image": self.images["PORTFOLIO_COTSWOLD"].pk,
                        "link_url": "/portfolio/#cotswold",
                        "description": ""
                    },
                    {
                        "title": "The Georgian Townhouse",
                        "category": "kitchen",
                        "image": self.images["PORTFOLIO_GEORGIAN"].pk,
                        "link_url": "/portfolio/#georgian",
                        "description": ""
                    }
                ]
            }
        },

        # Featured Case Study
        {
            "type": "featured_case_study",
            "value": {
                "eyebrow": "Featured Commission",
                "heading": "The Surrey Commission",
                "intro": "<p>A complete kitchen transformation for a Grade II listed property in the Surrey Hills.</p>",
                "points": [
                    "English oak from managed woodland",
                    "Hand-cut dovetail joints throughout",
                    "Integrated appliances from Gaggenau"
                ],
                "cta_text": "Read the full case study",
                "cta_url": "/portfolio/#surrey",
                "image": self.images["SURREY_IMAGE"].pk,
                "image_alt": "Surrey kitchen with oak cabinetry",
                "stats_label": "Project duration",
                "stats_value": "14 weeks"
            }
        },

        # Testimonial
        {
            "type": "social_proof_quote",
            "value": {
                "quote": "The attention to detail is extraordinary. Every drawer, every hinge—it's like working with artisans from another era.",
                "author": "Sarah M.",
                "role": "Homeowner",
                "company": "Surrey Hills",
                "logo": None
            }
        },

        # FAQ Section
        {
            "type": "faq",
            "value": {
                "eyebrow": "Commission Protocols",
                "heading": "How It Works",
                "intro": "",
                "items": [
                    {
                        "question": "Timeline & Pacing",
                        "answer": "<p>Every commission begins with a site visit and design consultation. From approval to installation typically takes 12-16 weeks. We limit ourselves to 12 commissions per year to ensure every project receives our full attention.</p>"
                    },
                    {
                        "question": "Material Provenance",
                        "answer": "<p>We source timber exclusively from managed British woodlands. Each piece is tracked from tree to kitchen, with full documentation of origin, seasoning time, and milling date.</p>"
                    },
                    {
                        "question": "International Works",
                        "answer": "<p>We undertake select international commissions in Europe and North America. International projects require a minimum engagement and extended lead times. Contact us to discuss feasibility.</p>"
                    }
                ],
                "allow_multiple_open": False
            }
        },

        # Contact Form
        {
            "type": "contact_form",
            "value": {
                "eyebrow": "Begin the Conversation",
                "heading": "Request a Consultation",
                "intro": "<p>Tell us about your project and we'll be in touch within 48 hours.</p>",
                "success_message": "Thank you for your enquiry. We'll be in touch shortly.",
                "submit_label": "Send Enquiry"
            }
        },
    ]

    home_page.save_revision().publish()
    self.stdout.write("  Populated homepage content")
```

### 3. About Page

```python
def _create_about_page(self, home_page):
    """Create About page with full content."""

    try:
        page = StandardPage.objects.get(slug="about")
        return page
    except StandardPage.DoesNotExist:
        pass

    page = StandardPage(
        title="About Us",
        slug="about",
        seo_title="About Sage & Stone | Our Story & Craftsmen",
        search_description="Meet the makers behind Sage & Stone. 28 years of master joinery experience. Herefordshire workshop, lifetime guarantee.",
        show_in_menus=True,
        body=[
            # Hero
            {
                "type": "hero_gradient",
                "value": {
                    "headline": "Craftsmanship built on <em>obsession</em>",
                    "subheadline": "Three decades of refining our craft. One mission: kitchens that outlast trends.",
                    "ctas": [],
                    "status": "",
                    "gradient_style": "primary"
                }
            },

            # Founder Section
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "A Letter from the Founder",
                    "heading": "Thomas J. Wright",
                    "intro": "<p>I started Sage & Stone because I was tired of watching beautiful timber turned into forgettable furniture.</p><p>Every kitchen we build is an argument against disposability—a physical reminder that permanence is possible.</p><p>We don't chase trends. We don't cut corners. We build rooms that your grandchildren will cook Sunday lunch in.</p>",
                    "points": [],
                    "cta_text": "",
                    "cta_url": "",
                    "image": self.images["FOUNDER_IMAGE"].pk,
                    "image_alt": "Thomas J. Wright, Master Joiner and Founder",
                    "stats_label": "Years of experience",
                    "stats_value": "28"
                }
            },

            # Etiquette Section
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
                            "icon": "",
                            "image": None,
                            "title": "Invisible Tradesmen",
                            "description": "<p>You'll never know we were there. Sites are left cleaner than we found them. No radio, no mess, no drama.</p>",
                            "link_url": "",
                            "link_label": ""
                        },
                        {
                            "icon": "",
                            "image": None,
                            "title": "Obsessive Cleanliness",
                            "description": "<p>Daily dust extraction, floor protection, and sealed work areas. We treat your home like our workshop.</p>",
                            "link_url": "",
                            "link_label": ""
                        },
                        {
                            "icon": "",
                            "image": None,
                            "title": "Vetted & Permanent",
                            "description": "<p>Every team member has been with us for 5+ years. No subcontractors, no strangers in your home.</p>",
                            "link_url": "",
                            "link_label": ""
                        }
                    ],
                    "layout_style": "tight"
                }
            },

            # Team Section
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
                            "image": self.images["TEAM_JAMES"].pk
                        },
                        {
                            "name": "Sarah M.",
                            "role": "Finishing Specialist",
                            "bio": "Traditional hand-finishing techniques",
                            "image": self.images["TEAM_SARAH"].pk
                        },
                        {
                            "name": "David R.",
                            "role": "Master Joiner",
                            "bio": "Third-generation craftsman",
                            "image": self.images["TEAM_DAVID"].pk
                        },
                        {
                            "name": "Marcus T.",
                            "role": "Project Director",
                            "bio": "Your single point of contact",
                            "image": self.images["TEAM_MARCUS"].pk
                        }
                    ]
                }
            },

            # Workshop Section
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "The Workshop",
                    "heading": "Herefordshire, Est. 2005",
                    "intro": "<p>Our solar-powered facility in the Herefordshire countryside is where every Sage & Stone piece comes to life.</p><p>We maintain an open workshop policy—clients are welcome to visit and witness their kitchen taking shape.</p>",
                    "points": [
                        "4,000 sq ft purpose-built facility",
                        "Solar-powered operations",
                        "Open workshop visits available"
                    ],
                    "cta_text": "Schedule a workshop visit",
                    "cta_url": "/contact/",
                    "image": self.images["WORKSHOP_IMAGE"].pk,
                    "image_alt": "Sage & Stone workshop interior",
                    "stats_label": "Years at this location",
                    "stats_value": "20"
                }
            },

            # Final CTA
            {
                "type": "buttons",
                "value": {
                    "alignment": "center",
                    "buttons": [
                        {"label": "Request a Site Visit", "url": "/contact/", "style": "primary", "open_in_new_tab": False}
                    ]
                }
            },
        ]
    )

    home_page.add_child(instance=page)
    page.save_revision().publish()
    self.stdout.write("  Created About page")
    return page
```

### 4. Services Page

```python
def _create_services_page(self, home_page):
    """Create Services page with full content."""

    try:
        page = StandardPage.objects.get(slug="services")
        return page
    except StandardPage.DoesNotExist:
        pass

    page = StandardPage(
        title="Services",
        slug="services",
        seo_title="Our Services | Bespoke Kitchen Installation | Sage & Stone",
        search_description="Total project management from first measurement to final polish. Precision installation, white glove service.",
        show_in_menus=True,
        body=[
            # Hero
            {
                "type": "hero_gradient",
                "value": {
                    "headline": "Precision <em>Installation</em>",
                    "subheadline": "Total project management from first measurement to final polish.",
                    "ctas": [],
                    "gradient_style": "primary"
                }
            },

            # White Glove Standard
            {
                "type": "manifesto",
                "value": {
                    "eyebrow": "The White Glove Standard",
                    "heading": "Installation is not an afterthought",
                    "body": "<p>Too many beautiful kitchens are ruined by poor installation. At Sage & Stone, installation is where our obsession with detail truly shows. Every gap, every alignment, every finish—measured to the millimetre.</p>",
                    "quote": "Millimetre-perfect is not a goal. It is the baseline."
                }
            },

            # Process Steps
            {
                "type": "process",
                "value": {
                    "eyebrow": "The Process",
                    "heading": "Five Phases to Completion",
                    "intro": "Every installation follows our proven methodology.",
                    "steps": [
                        {"number": 1, "title": "Consultation", "description": "<p>Site survey, design brief, and feasibility assessment.</p>"},
                        {"number": 2, "title": "Strip-Out", "description": "<p>Careful removal of existing fixtures with full site protection.</p>"},
                        {"number": 3, "title": "Installation", "description": "<p>Precision fitting of cabinetry, worktops, and integrated appliances.</p>"},
                        {"number": 4, "title": "Calibration", "description": "<p>Fine-tuning of doors, drawers, and hardware for perfect operation.</p>"},
                        {"number": 5, "title": "Handover", "description": "<p>Full demonstration, documentation, and aftercare guidance.</p>"}
                    ]
                }
            },

            # Service Cards
            {
                "type": "service_cards",
                "value": {
                    "eyebrow": "What We Handle",
                    "heading": "Complete Project Management",
                    "intro": "",
                    "cards": [
                        {
                            "icon": "",
                            "image": self.images["SERVICE_APPLIANCE"].pk,
                            "title": "Appliance Integration",
                            "description": "<p>Seamless fitting of all integrated appliances, from refrigeration to extraction.</p>",
                            "link_url": "",
                            "link_label": ""
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_JOINERY"].pk,
                            "title": "Bespoke Joinery",
                            "description": "<p>On-site adjustments and custom fitting to accommodate period properties.</p>",
                            "link_url": "",
                            "link_label": ""
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_TECHNICAL"].pk,
                            "title": "Technical Integration",
                            "description": "<p>Plumbing, electrical, and gas connections by certified specialists.</p>",
                            "link_url": "",
                            "link_label": ""
                        },
                        {
                            "icon": "",
                            "image": self.images["SERVICE_STONE"].pk,
                            "title": "Stone & Surfaces",
                            "description": "<p>Precision templating and installation of worktops and splashbacks.</p>",
                            "link_url": "",
                            "link_label": ""
                        }
                    ],
                    "layout_style": "default"
                }
            },

            # Cleanliness Pledge
            {
                "type": "service_cards",
                "value": {
                    "eyebrow": "The Cleanliness Pledge",
                    "heading": "Four Guarantees",
                    "intro": "Your home deserves the same respect as our workshop.",
                    "cards": [
                        {"icon": "", "image": None, "title": "Daily Clean", "description": "<p>Work areas cleaned and vacuumed at the end of every day.</p>", "link_url": "", "link_label": ""},
                        {"icon": "", "image": None, "title": "Floor Protection", "description": "<p>Heavy-duty floor coverings throughout the project duration.</p>", "link_url": "", "link_label": ""},
                        {"icon": "", "image": None, "title": "Dust Extraction", "description": "<p>Industrial extraction at source for all cutting and sanding.</p>", "link_url": "", "link_label": ""},
                        {"icon": "", "image": None, "title": "Sealed Zones", "description": "<p>Work areas sealed from living spaces with temporary partitions.</p>", "link_url": "", "link_label": ""}
                    ],
                    "layout_style": "tight"
                }
            },

            # Gallery
            {
                "type": "gallery",
                "value": {
                    "eyebrow": "The Details",
                    "heading": "Obsession in every joint",
                    "intro": "",
                    "images": [
                        {"image": self.images["DETAIL_1"].pk, "alt_text": "Hand-cut dovetail joint detail", "caption": ""},
                        {"image": self.images["DETAIL_2"].pk, "alt_text": "Precision hinge alignment", "caption": ""},
                        {"image": self.images["DETAIL_3"].pk, "alt_text": "Hand-finished oak surface", "caption": ""}
                    ]
                }
            },

            # Trust Strip
            {
                "type": "trust_strip_logos",
                "value": {
                    "eyebrow": "Certifications & Memberships",
                    "items": [
                        {"logo": self.images["LOGO_GASSAFE"].pk, "alt_text": "Gas Safe Registered", "url": ""},
                        {"logo": self.images["LOGO_NICEIC"].pk, "alt_text": "NICEIC Approved", "url": ""},
                        {"logo": self.images["LOGO_BIKBBI"].pk, "alt_text": "BiKBBI Member", "url": ""},
                        {"logo": self.images["LOGO_GUILD"].pk, "alt_text": "Guild of Master Craftsmen", "url": ""}
                    ]
                }
            },

            # FAQ
            {
                "type": "faq",
                "value": {
                    "eyebrow": "Common Questions",
                    "heading": "Installation FAQs",
                    "intro": "",
                    "items": [
                        {
                            "question": "What is the typical lead time for installation?",
                            "answer": "<p>Installation typically begins 10-12 weeks after design approval, allowing time for material sourcing and workshop production. The installation phase itself takes 2-3 weeks depending on project scope.</p>"
                        },
                        {
                            "question": "Do you install flat-pack kitchens?",
                            "answer": "<p>No. We only install kitchens built in our Herefordshire workshop. Every piece is crafted specifically for your space—flat-pack has no place in our process.</p>"
                        },
                        {
                            "question": "How do you manage other trades?",
                            "answer": "<p>We coordinate all required trades including plumbing, electrical, and plastering. Our project director serves as your single point of contact, managing the entire installation timeline.</p>"
                        }
                    ],
                    "allow_multiple_open": False
                }
            },
        ]
    )

    home_page.add_child(instance=page)
    page.save_revision().publish()
    self.stdout.write("  Created Services page")
    return page
```

### 5. Portfolio Page

```python
def _create_portfolio_page(self, home_page):
    """Create Portfolio page with full content."""

    try:
        page = StandardPage.objects.get(slug="portfolio")
        return page
    except StandardPage.DoesNotExist:
        pass

    page = StandardPage(
        title="Portfolio",
        slug="portfolio",
        seo_title="Our Portfolio | Bespoke Kitchen Projects | Sage & Stone",
        search_description="Explore our collection of bespoke kitchen commissions. Heritage, modernist, and utility designs crafted in Herefordshire.",
        show_in_menus=True,
        body=[
            # Header
            {
                "type": "editorial_header",
                "value": {
                    "align": "center",
                    "eyebrow": "Our Work",
                    "heading": "The Portfolio"
                }
            },

            # Featured Project
            {
                "type": "featured_case_study",
                "value": {
                    "eyebrow": "Featured",
                    "heading": "The Highland Commission",
                    "intro": "<p>A complete kitchen and utility suite for a Scottish estate, featuring locally-sourced larch and hand-forged ironmongery.</p>",
                    "points": [],
                    "cta_text": "View project",
                    "cta_url": "#highland",
                    "image": self.images["PORTFOLIO_HIGHLAND"].pk,
                    "image_alt": "Highland Commission kitchen interior",
                    "stats_label": "",
                    "stats_value": ""
                }
            },

            # Portfolio Grid
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
                            "image": self.images["PORTFOLIO_LARDER"].pk,
                            "link_url": "#pantry-larder",
                            "description": "Freestanding larder unit in English oak"
                        },
                        {
                            "title": "The Georgian Restoration",
                            "category": "restoration",
                            "image": self.images["PORTFOLIO_GEORGIAN_REST"].pk,
                            "link_url": "#georgian-restoration",
                            "description": "Period-sympathetic kitchen for a 1780s townhouse"
                        },
                        {
                            "title": "The Brutalist Barn",
                            "category": "kitchen",
                            "image": self.images["PORTFOLIO_BRUTALIST"].pk,
                            "link_url": "#brutalist-barn",
                            "description": "Contemporary design meets agricultural character"
                        },
                        {
                            "title": "The Utility Room",
                            "category": "furniture",
                            "image": self.images["PORTFOLIO_UTILITY"].pk,
                            "link_url": "#utility-room",
                            "description": "Boot room and utility suite"
                        }
                    ]
                }
            },

            # Quote
            {
                "type": "quote",
                "value": {
                    "quote": "We don't build against nature. We negotiate with it.",
                    "author": "Thomas J. Wright",
                    "role": "Founder"
                }
            },

            # CTA
            {
                "type": "buttons",
                "value": {
                    "alignment": "center",
                    "buttons": [
                        {"label": "Enquire for 2026", "url": "/contact/", "style": "primary", "open_in_new_tab": False},
                        {"label": "Read about our process", "url": "/services/", "style": "outline", "open_in_new_tab": False}
                    ]
                }
            },
        ]
    )

    home_page.add_child(instance=page)
    page.save_revision().publish()
    self.stdout.write("  Created Portfolio page")
    return page
```

### 6. Contact Page

```python
def _create_contact_page(self, home_page):
    """Create Contact page."""

    try:
        page = StandardPage.objects.get(slug="contact")
        return page
    except StandardPage.DoesNotExist:
        pass

    page = StandardPage(
        title="Contact",
        slug="contact",
        seo_title="Contact Us | Begin Your Commission | Sage & Stone",
        search_description="Ready to begin your bespoke kitchen journey? Contact Sage & Stone for a consultation.",
        show_in_menus=False,
        body=[
            # Hero
            {
                "type": "hero_gradient",
                "value": {
                    "headline": "Begin Your <em>Commission</em>",
                    "subheadline": "Tell us about your project and we'll be in touch within 48 hours.",
                    "ctas": [],
                    "gradient_style": "primary"
                }
            },

            # Contact Form
            {
                "type": "contact_form",
                "value": {
                    "eyebrow": "",
                    "heading": "Request a Consultation",
                    "intro": "<p>Whether you're ready to begin or simply exploring possibilities, we'd love to hear from you.</p>",
                    "success_message": "Thank you for your enquiry. We'll be in touch within 48 hours.",
                    "submit_label": "Send Enquiry"
                }
            },
        ]
    )

    home_page.add_child(instance=page)
    page.save_revision().publish()
    self.stdout.write("  Created Contact page")
    return page
```

## Acceptance Criteria

- [ ] All 5 pages created and published
- [ ] Pages in correct hierarchy under Home
- [ ] All StreamField blocks populated
- [ ] All copy matches wireframes
- [ ] All images linked correctly
- [ ] SEO fields populated
- [ ] Pages visible in navigation where specified
- [ ] Idempotent: existing pages not duplicated

## Dependencies

- Subtask 001 (Site and home page exist)
- Subtask 002 (Images generated)

## Testing

```python
def test_all_pages_created():
    call_command("seed_sage_stone")

    assert StandardPage.objects.filter(slug="about").exists()
    assert StandardPage.objects.filter(slug="services").exists()
    assert StandardPage.objects.filter(slug="portfolio").exists()
    assert StandardPage.objects.filter(slug="contact").exists()

def test_pages_have_content():
    call_command("seed_sage_stone")

    about = StandardPage.objects.get(slug="about")
    assert len(about.body) > 0

    services = StandardPage.objects.get(slug="services")
    assert len(services.body) > 0

def test_pages_are_children_of_home():
    call_command("seed_sage_stone")

    home = HomePage.objects.get(slug="home")
    about = StandardPage.objects.get(slug="about")

    assert about.get_parent() == home
```
