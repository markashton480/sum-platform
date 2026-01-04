# Creating Content Profiles

A content profile is a collection of YAML files that define a complete site's content. This guide walks through creating a new profile from scratch.

---

## Directory Structure

Create a new directory under `content/` with your profile name:

```
content/
└── my-brand/
    ├── site.yaml           # Required: Brand configuration
    ├── navigation.yaml     # Required: Header/footer navigation
    └── pages/              # Required: Page content directory
        ├── home.yaml       # Required: Homepage
        ├── about.yaml      # Recommended
        ├── services.yaml   # Recommended
        ├── portfolio.yaml  # Optional
        ├── blog.yaml       # Optional
        ├── contact.yaml    # Recommended
        └── legal.yaml      # Recommended
```

The profile name should be lowercase with hyphens (e.g., `my-brand`, `acme-plumbing`).

---

## site.yaml

Defines brand configuration, contact info, colors, and typography.

### Required Fields

```yaml
# Company identity
company_name: "My Brand"
tagline: "Your tagline here"

# Contact information
phone_number: "+44 123 456 7890"
email: "hello@mybrand.com"
address: |
  123 Main Street
  London EC1A 1BB
```

### Optional Fields

```yaml
# Additional company info
established_year: 2020
business_hours: |
  Monday - Friday: 9am - 5pm
  Saturday: By appointment
  Sunday: Closed

# Colors (hex values)
primary_color: "#1A2F23"
secondary_color: "#4A6350"
accent_color: "#A0563B"
background_color: "#F7F5F1"
text_color: "#1A2F23"
surface_color: "#EDE8E0"
surface_elevated_color: "#FFFFFF"
text_light_color: "#5A6E5F"

# Typography
heading_font: "Playfair Display"
body_font: "Lato"

# Social media URLs
instagram_url: "https://instagram.com/mybrand"
facebook_url: ""
linkedin_url: ""
twitter_url: ""
youtube_url: ""
tiktok_url: ""

# Analytics
gtm_container_id: ""
ga_measurement_id: ""

# Cookie banner
cookie_banner_enabled: false
```

### Field Aliases

The seeder accepts common aliases for convenience:

| Alias | Maps To |
|-------|---------|
| `phone` | `phone_number` |
| `instagram` | `instagram_url` |
| `facebook` | `facebook_url` |
| `primary` | `primary_color` |
| `secondary` | `secondary_color` |
| `accent` | `accent_color` |
| `background` | `background_color` |

---

## navigation.yaml

Defines the header menu and footer sections.

### Header Navigation

```yaml
header:
  # Phone number visibility
  show_phone_in_header: true

  # Header CTA button
  header_cta_enabled: true
  header_cta_text: "Contact Us"
  header_cta_link:
    - type: "link"
      value:
        link_type: "page"
        page: "contact"        # References page by slug
        link_text: "Contact Us"

  # Mobile CTA configuration
  mobile_cta_enabled: true
  mobile_cta_phone_enabled: true
  mobile_cta_button_enabled: true
  mobile_cta_button_text: "Enquire"
  mobile_cta_button_link:
    - type: "link"
      value:
        link_type: "page"
        page: "contact"
        link_text: "Enquire"

  # Main menu items
  menu_items:
    - type: "item"
      value:
        label: "About"
        link:
          link_type: "page"
          page: "about"
          link_text: "About"
        children: []

    - type: "item"
      value:
        label: "Services"
        link:
          link_type: "page"
          page: "services"
          link_text: "Services"
        children:
          - label: "Service A"
            link:
              link_type: "url"
              url: "/services/#service-a"
              link_text: "Service A"
          - label: "Service B"
            link:
              link_type: "url"
              url: "/services/#service-b"
              link_text: "Service B"
```

### Footer Navigation

```yaml
footer:
  tagline: "Your tagline here."
  auto_service_areas: false
  copyright_text: "© {year} My Brand Ltd. All rights reserved."

  # Social links (override site.yaml if needed)
  social_instagram: "https://instagram.com/mybrand"
  social_facebook: ""
  social_linkedin: ""
  social_youtube: ""
  social_x: ""

  # Footer sections
  link_sections:
    - type: "section"
      value:
        title: "Company"
        links:
          - link_type: "page"
            page: "about"
            link_text: "About Us"
          - link_type: "page"
            page: "contact"
            link_text: "Contact"

    - type: "section"
      value:
        title: "Legal"
        links:
          - link_type: "url"
            url: "/privacy/"
            link_text: "Privacy Policy"
          - link_type: "url"
            url: "/terms/"
            link_text: "Terms of Service"

    - type: "section"
      value:
        title: "Contact"
        links:
          - link_type: "email"
            email: "hello@mybrand.com"
            link_text: "hello@mybrand.com"
          - link_type: "phone"
            phone: "+44 123 456 7890"
            link_text: "+44 123 456 7890"
```

### Link Types

| Type | Fields | Example |
|------|--------|---------|
| `page` | `page` (slug) | `{"link_type": "page", "page": "about"}` |
| `url` | `url` | `{"link_type": "url", "url": "/services/"}` |
| `anchor` | `anchor` | `{"link_type": "anchor", "anchor": "contact-form"}` |
| `email` | `email` | `{"link_type": "email", "email": "hello@site.com"}` |
| `phone` | `phone` | `{"link_type": "phone", "phone": "+44123456"}` |

---

## Page YAML Files

Each page file defines the content for a single page.

### Required Fields

Every page YAML must include:

```yaml
title: "Page Title"
slug: "page-slug"
```

### Optional Metadata

```yaml
seo_title: "SEO Title | Brand Name"
search_description: "Meta description for search engines."
show_in_menus: true
```

### Body Content

The `body` field contains a list of StreamField blocks:

```yaml
body:
  - type: "hero_image"
    value:
      headline: "Welcome"
      subheadline: "Your intro text here."
      image: HERO_IMAGE
      ctas:
        - label: "Learn More"
          url: "/about/"
          style: "primary"

  - type: "rich_text"
    value: "<p>Your content here.</p>"

  - type: "service_cards"
    value:
      heading: "Our Services"
      cards:
        - title: "Service A"
          description: "<p>Description here.</p>"
          image: SERVICE_A
```

### Block Types

Reference the [Block Catalog](blocks-reference.md) for all available block types and their fields.

Common blocks:

| Block Type | Purpose |
|------------|---------|
| `hero_image` | Full-width hero with background image |
| `hero_gradient` | Hero with gradient background |
| `rich_text` | HTML content |
| `service_cards` | Grid of service cards |
| `testimonials` | Customer testimonials |
| `faq` | Accordion FAQ section |
| `contact_form` | Contact form block |
| `stats` | Statistics display |
| `portfolio` | Portfolio gallery |
| `team_grid` | Team member grid |

---

## Image Keys

Reference images by key in your YAML. The seeder generates placeholder images automatically.

### Using Image Keys

```yaml
hero:
  image: HERO_IMAGE    # Will be resolved to a WagtailImage

cards:
  - title: "Card 1"
    image: SERVICE_A   # Another image key
```

### Standard Image Keys

The following keys are pre-defined in the image manifest:

| Key | Dimensions | Purpose |
|-----|------------|---------|
| `HERO_IMAGE` | 1920x1080 | Main hero background |
| `SURREY_IMAGE` | 1000x700 | Featured project |
| `WORKSHOP_IMAGE` | 1200x800 | Workshop/behind-the-scenes |
| `FOUNDER_IMAGE` | 800x1000 | Founder portrait |
| `TEAM_*` | 400x500 | Team member portraits |
| `SERVICE_*` | 600x400 | Service illustrations |
| `PORTFOLIO_*` | 800x600 | Portfolio images |
| `BLOG_*` | 1200x600 | Blog featured images |
| `DETAIL_*` | 600x600 | Detail/gallery images |
| `LOGO_*` | 200x80 | Certification logos |

### Custom Image Keys

You can use any key name. The seeder generates a placeholder if the key isn't in the manifest:

```yaml
hero:
  image: MY_CUSTOM_IMAGE  # Will generate a generic placeholder
```

---

## Interpolation

Use `${path.to.value}` syntax to reference values from other parts of the profile:

```yaml
# In site.yaml
company_name: "My Brand"
tagline: "Quality you can trust"

# In navigation.yaml
footer:
  tagline: "${tagline}"  # Resolves to "Quality you can trust"
```

### Available Context

| Path | Source |
|------|--------|
| `site.*` | Values from site.yaml |
| `navigation.*` | Values from navigation.yaml |
| `pages.*` | Page data (by filename) |
| Top-level keys | Direct values from site.yaml |

---

## Validation

The ContentLoader validates your YAML files:

### Required Structure

- `site.yaml` must be a non-empty mapping
- `navigation.yaml` must be a non-empty mapping
- Each page YAML must have `slug` and `title` fields

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Profile not found` | Directory doesn't exist | Check path and spelling |
| `Required content file missing` | Missing site.yaml or navigation.yaml | Create the required file |
| `YAML root must be a mapping` | File contains a list/scalar | Ensure file starts with key-value pairs |
| `Page missing valid slug` | Page lacks slug field | Add `slug: "page-slug"` |
| `Interpolation path not found` | Invalid `${}` reference | Check the reference path exists |

---

## Testing Your Profile

### Dry Run

Validate your profile without writing to the database:

```bash
python manage.py seed my-brand --dry-run
```

This prints the seed plan:

```
Seed plan
  Profile: my-brand
  Content dir: /path/to/content
  Pages:
    - home
    - about
    - services
    - contact
  Seeders:
    - home
    - about
    - services
    - contact
```

### Full Seed

Seed your profile:

```bash
# Clear existing and seed fresh
python manage.py seed my-brand --clear

# Or update existing content
python manage.py seed my-brand
```

### Verify in Admin

1. Open Wagtail Admin at `/admin/`
2. Navigate to Pages and verify structure
3. Check Settings > Site Settings for branding
4. Check Settings > Header/Footer Navigation

---

## Example: Minimal Profile

Here's a minimal profile with just the required files:

### content/minimal/site.yaml

```yaml
company_name: "Minimal Brand"
tagline: "Keep it simple"
phone_number: "+44 123 456 7890"
email: "hello@minimal.com"
address: "123 Simple Street"
```

### content/minimal/navigation.yaml

```yaml
header:
  show_phone_in_header: true
  header_cta_enabled: false
  menu_items: []

footer:
  tagline: "Keep it simple."
  link_sections: []
```

### content/minimal/pages/home.yaml

```yaml
title: "Home"
slug: "home"
body:
  - type: "rich_text"
    value: "<h1>Welcome</h1><p>This is a minimal site.</p>"
```

---

## See Also

- [Seeder Architecture](SEEDER-ARCHITECTURE.md) — Technical overview
- [Block Reference](blocks-reference.md) — Available block types
- [Sage & Stone Profile](../user/seed-sage-stone.md) — Complete example profile
