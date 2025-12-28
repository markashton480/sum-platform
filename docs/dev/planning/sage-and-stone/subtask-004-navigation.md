# Subtask 004: Navigation Structure

## Overview

Configure HeaderNavigation with mega menu structure and FooterNavigation with link sections for Sage & Stone.

## Deliverables

1. HeaderNavigation with 3-level menu hierarchy
2. Mobile CTA configuration
3. FooterNavigation with 3 link sections
4. Social links integration

## Navigation Requirements

### Header Navigation (Desktop)
- **Kitchens** (mega menu with 3 columns)
  - Collections: Heritage, Modernist, Utility
  - Fitted Joinery: Larder, Island, Wall, Boot Room
  - Freestanding: Prep Tables, Butcher Blocks, Dressers
- **What We Do** → Services page
- **Who We Are** → About page
- **Portfolio** → Portfolio page
- **Journal** → Blog index page
- **[Enquire]** → Contact page (CTA button)

### Footer Navigation
- Column 1: Explore (page links)
- Column 2: Legal (policy links)
- Column 3: Studio (contact info)

## Implementation

### 1. Header Navigation

```python
from sum_core.navigation.models import HeaderNavigation
from wagtail.models import Site

def create_navigation(self, site, pages):
    """Configure header and footer navigation."""

    # Unpack page references
    home = pages["home"]
    about = pages["about"]
    services = pages["services"]
    portfolio = pages["portfolio"]
    blog_index = pages["blog_index"]
    contact = pages.get("contact", home)  # Fallback to home if no contact page
    terms = pages["terms"]

    # === Header Navigation ===
    header_nav, _ = HeaderNavigation.objects.get_or_create(site=site)

    # Phone in header
    header_nav.show_phone_in_header = True

    # Desktop CTA
    header_nav.header_cta_enabled = True
    header_nav.header_cta_text = "Enquire"
    header_nav.header_cta_link = [
        {
            "type": "link",
            "value": {
                "link_type": "page",
                "page": contact.pk,
                "link_text": "Enquire",
            }
        }
    ]

    # Mobile Sticky CTA
    header_nav.mobile_cta_enabled = True
    header_nav.mobile_cta_phone_enabled = True
    header_nav.mobile_cta_button_enabled = True
    header_nav.mobile_cta_button_text = "Enquire"
    header_nav.mobile_cta_button_link = [
        {
            "type": "link",
            "value": {
                "link_type": "page",
                "page": contact.pk,
                "link_text": "Enquire",
            }
        }
    ]

    # Main menu items
    header_nav.menu_items = self._build_menu_items(pages)

    header_nav.save()
    self.stdout.write("Configured header navigation")

    # === Footer Navigation ===
    self._create_footer_navigation(site, pages)

    return header_nav


def _build_menu_items(self, pages):
    """Build the mega menu structure."""

    portfolio = pages["portfolio"]
    services = pages["services"]
    about = pages["about"]
    blog_index = pages["blog_index"]

    return [
        # Kitchens (Mega Menu)
        {
            "type": "menu_item",
            "value": {
                "label": "Kitchens",
                "link": {
                    "link_type": "page",
                    "page": portfolio.pk,
                    "link_text": "Kitchens",
                },
                "children": [
                    # Collections column
                    {
                        "type": "submenu_item",
                        "value": {
                            "label": "Collections",
                            "link": {
                                "link_type": "anchor",
                                "anchor": "",
                                "link_text": "Collections",
                            },
                            "children": [
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "The Heritage",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?collection=heritage",
                                            "link_text": "The Heritage",
                                        }
                                    }
                                },
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "The Modernist",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?collection=modernist",
                                            "link_text": "The Modernist",
                                        }
                                    }
                                },
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "The Utility",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?collection=utility",
                                            "link_text": "The Utility",
                                        }
                                    }
                                },
                            ]
                        }
                    },
                    # Fitted Joinery column
                    {
                        "type": "submenu_item",
                        "value": {
                            "label": "Fitted Joinery",
                            "link": {
                                "link_type": "anchor",
                                "anchor": "",
                                "link_text": "Fitted Joinery",
                            },
                            "children": [
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "Larder Cupboards",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?type=larder",
                                            "link_text": "Larder Cupboards",
                                        }
                                    }
                                },
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "Island Units",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?type=island",
                                            "link_text": "Island Units",
                                        }
                                    }
                                },
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "Wall Cabinetry",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?type=wall",
                                            "link_text": "Wall Cabinetry",
                                        }
                                    }
                                },
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "Boot Room Storage",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?type=bootroom",
                                            "link_text": "Boot Room Storage",
                                        }
                                    }
                                },
                            ]
                        }
                    },
                    # Freestanding column
                    {
                        "type": "submenu_item",
                        "value": {
                            "label": "Freestanding",
                            "link": {
                                "link_type": "anchor",
                                "anchor": "",
                                "link_text": "Freestanding",
                            },
                            "children": [
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "Prep Tables",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?type=prep-table",
                                            "link_text": "Prep Tables",
                                        }
                                    }
                                },
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "Butcher Blocks",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?type=butcher-block",
                                            "link_text": "Butcher Blocks",
                                        }
                                    }
                                },
                                {
                                    "type": "subsubmenu_item",
                                    "value": {
                                        "label": "Dressers",
                                        "link": {
                                            "link_type": "url",
                                            "url": "/portfolio/?type=dresser",
                                            "link_text": "Dressers",
                                        }
                                    }
                                },
                            ]
                        }
                    },
                ]
            }
        },
        # What We Do
        {
            "type": "menu_item",
            "value": {
                "label": "What We Do",
                "link": {
                    "link_type": "page",
                    "page": services.pk,
                    "link_text": "What We Do",
                },
                "children": []
            }
        },
        # Who We Are
        {
            "type": "menu_item",
            "value": {
                "label": "Who We Are",
                "link": {
                    "link_type": "page",
                    "page": about.pk,
                    "link_text": "Who We Are",
                },
                "children": []
            }
        },
        # Portfolio
        {
            "type": "menu_item",
            "value": {
                "label": "Portfolio",
                "link": {
                    "link_type": "page",
                    "page": portfolio.pk,
                    "link_text": "Portfolio",
                },
                "children": []
            }
        },
        # Journal
        {
            "type": "menu_item",
            "value": {
                "label": "Journal",
                "link": {
                    "link_type": "page",
                    "page": blog_index.pk,
                    "link_text": "Journal",
                },
                "children": []
            }
        },
    ]
```

### 2. Footer Navigation

```python
from sum_core.navigation.models import FooterNavigation

def _create_footer_navigation(self, site, pages):
    """Configure footer navigation."""

    about = pages["about"]
    services = pages["services"]
    portfolio = pages["portfolio"]
    blog_index = pages["blog_index"]
    terms = pages["terms"]

    footer_nav, _ = FooterNavigation.objects.get_or_create(site=site)

    # Override tagline
    footer_nav.tagline = "Rooms that remember."

    # Social links (Instagram only for this brand)
    footer_nav.social_instagram = "https://instagram.com/sageandstone"
    footer_nav.social_facebook = ""
    footer_nav.social_linkedin = ""
    footer_nav.social_youtube = ""
    footer_nav.social_x = ""

    # Copyright
    footer_nav.copyright_text = "© {year} Sage & Stone Ltd. All rights reserved."

    # Link sections (3 columns)
    footer_nav.link_sections = [
        # Column 1: Explore
        {
            "type": "footer_section",
            "value": {
                "title": "Explore",
                "links": [
                    {
                        "type": "link",
                        "value": {
                            "link_type": "page",
                            "page": about.pk,
                            "link_text": "Who We Are",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "page",
                            "page": services.pk,
                            "link_text": "What We Do",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "page",
                            "page": blog_index.pk,
                            "link_text": "Journal",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "page",
                            "page": portfolio.pk,
                            "link_text": "Our Portfolio",
                        }
                    },
                ]
            }
        },
        # Column 2: Legal
        {
            "type": "footer_section",
            "value": {
                "title": "Legal",
                "links": [
                    {
                        "type": "link",
                        "value": {
                            "link_type": "url",
                            "url": "/privacy/",
                            "link_text": "Privacy Policy",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "page",
                            "page": terms.pk,
                            "link_text": "Terms of Service",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "url",
                            "url": "/accessibility/",
                            "link_text": "Accessibility",
                        }
                    },
                ]
            }
        },
        # Column 3: Studio (contact info)
        {
            "type": "footer_section",
            "value": {
                "title": "Studio",
                "links": [
                    {
                        "type": "link",
                        "value": {
                            "link_type": "anchor",
                            "anchor": "",
                            "link_text": "The Old Joinery, Unit 4",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "anchor",
                            "anchor": "",
                            "link_text": "Herefordshire HR4 9AB",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "email",
                            "email": "hello@sageandstone.com",
                            "link_text": "hello@sageandstone.com",
                        }
                    },
                    {
                        "type": "link",
                        "value": {
                            "link_type": "phone",
                            "phone": "+44 (0) 20 1234 5678",
                            "link_text": "+44 (0) 20 1234 5678",
                        }
                    },
                ]
            }
        },
    ]

    footer_nav.save()
    self.stdout.write("Configured footer navigation")
```

## Acceptance Criteria

- [ ] Header navigation has 5 main items
- [ ] Kitchens has 3-level mega menu
- [ ] Desktop CTA links to contact/home
- [ ] Mobile CTA configured
- [ ] Phone shown in header
- [ ] Footer has 3 link columns
- [ ] Footer tagline set
- [ ] Social links configured (Instagram)
- [ ] Copyright text includes year placeholder
- [ ] All page links resolve correctly

## Dependencies

- Subtask 001 (Site exists)
- Subtask 005 (Pages created) - circular dependency
  - **Resolution:** Navigation created after pages

## Menu Item Hierarchy

```
HeaderNavigation.menu_items (max 8)
└── MenuItemBlock
    ├── label
    ├── link (UniversalLinkBlock)
    └── children (max 8 SubmenuItemBlock)
        └── SubmenuItemBlock
            ├── label
            ├── link
            └── children (max 8 SubSubmenuItemBlock)
                └── SubSubmenuItemBlock
                    ├── label
                    └── link
```

## Testing

```python
def test_header_navigation_created():
    call_command("seed_sage_stone")

    site = Site.objects.get(hostname="localhost")
    header = HeaderNavigation.objects.get(site=site)

    assert header.header_cta_enabled
    assert header.header_cta_text == "Enquire"
    assert len(header.menu_items) == 5

def test_mega_menu_structure():
    call_command("seed_sage_stone")

    site = Site.objects.get(hostname="localhost")
    header = HeaderNavigation.objects.get(site=site)

    kitchens = header.menu_items[0]
    assert kitchens["value"]["label"] == "Kitchens"
    assert len(kitchens["value"]["children"]) == 3  # 3 columns

def test_footer_navigation_created():
    call_command("seed_sage_stone")

    site = Site.objects.get(hostname="localhost")
    footer = FooterNavigation.objects.get(site=site)

    assert footer.tagline == "Rooms that remember."
    assert len(footer.link_sections) == 3
```

## Notes

- Mega menu URLs use query params for filtering (theme handles display)
- Contact info in footer uses anchor links (non-clickable)
- Phone and email links are functional (tel:, mailto:)
- Year placeholder {year} replaced by theme template
