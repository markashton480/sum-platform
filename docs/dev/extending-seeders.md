# Extending Seeders

Guide for creating additional site seeders based on the Sage & Stone patterns.

## Overview

Seeders are Django management commands that populate a Wagtail site with demo content. They follow consistent patterns for idempotency, configurability, and content structure.

## Seeder Architecture

### File Location

```
boilerplate/project_name/home/management/commands/seed_<name>.py
```

Seeders live in the boilerplate so they're available in scaffolded projects.

### Command Structure

```python
from django.core.management.base import BaseCommand, CommandParser
from wagtail.models import Page, Site

class Command(BaseCommand):
    help = "Create the <Brand> site with demo content."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--clear", action="store_true")
        parser.add_argument("--images-only", action="store_true")
        parser.add_argument("--hostname", default="localhost")
        parser.add_argument("--port", type=int, default=8000)

    def handle(self, *args, **options) -> None:
        hostname = options.get("hostname") or "localhost"
        port = options.get("port") or 8000

        if options.get("clear"):
            self._clear_existing_content(hostname=hostname, port=port)
            self.stdout.write(self.style.SUCCESS("Cleared existing content."))

        # Always generate images (outside transaction)
        self.create_images()

        if options.get("images_only"):
            self.stdout.write(self.style.SUCCESS("Images created."))
            return

        # Create site structure
        site, home_page = self._setup_site(hostname=hostname, port=port)
        self._configure_branding(site=site)
        self.create_pages(home_page=home_page)
        self._configure_navigation(site=site, home_page=home_page)

        self.stdout.write(self.style.SUCCESS("Site seeded successfully."))
```

## Idempotency Patterns

### Pages: Parent + Slug Lookup

Pages are unique by parent + slug. Use this pattern:

```python
def _get_or_create_standard_page(
    self,
    parent: Page,
    slug: str,
    title: str,
    body: list[dict],
) -> tuple[StandardPage, bool]:
    """Get or create a StandardPage, returning (page, created)."""
    try:
        page = parent.get_children().get(slug=slug).specific
        # Update existing page
        page.title = title
        page.body = body
        page.save_revision().publish()
        return page, False
    except Page.DoesNotExist:
        # Create new page
        page = StandardPage(
            slug=slug,
            title=title,
            body=body,
        )
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page, True
```

### Settings: get_or_create on Site

Site settings use Wagtail's `for_site()` pattern:

```python
def _configure_branding(self, site: Site) -> SiteSettings:
    settings = SiteSettings.for_site(site)
    settings.company_name = "Brand Name"
    settings.primary_color = "#123456"
    settings.save()
    return settings
```

### Images: Title Prefix

Use a consistent prefix for image titles:

```python
IMAGE_PREFIX = "BRAND"  # e.g., "SS" for Sage & Stone

def generate_image(self, key: str, width: int, height: int) -> Image:
    title = f"{IMAGE_PREFIX}_{key}"
    try:
        return Image.objects.get(title=title)
    except Image.DoesNotExist:
        # Generate and save new image
        return self._create_placeholder_image(title, width, height)
```

### Navigation: for_site with update

```python
def _configure_navigation(self, site: Site, home_page: Page) -> None:
    header = HeaderNavigation.for_site(site)
    header.menu_items = self._build_menu_items()
    header.header_cta_enabled = True
    header.save()
```

## Image Generation

### Image Manager

Use Pillow to generate branded placeholder images:

```python
class ImageManager:
    def __init__(self, prefix: str = IMAGE_PREFIX) -> None:
        self.prefix = prefix
        self.palette = {
            "primary": "#1A2F23",
            "secondary": "#4A6350",
            "accent": "#A0563B",
        }

    def generate(
        self,
        key: str,
        width: int,
        height: int,
        bg_color: str = "primary",
        label: str | None = None,
    ) -> Image:
        title = f"{self.prefix}_{key}"

        # Check for existing
        existing = Image.objects.filter(title=title).first()
        if existing:
            return existing

        # Create with Pillow
        bg = self.palette.get(bg_color, bg_color)
        img = PILImage.new("RGB", (width, height), bg)

        # Add label text if provided
        if label:
            draw = ImageDraw.Draw(img)
            draw.text((width // 2, height // 2), label, anchor="mm")

        # Save to Wagtail
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        wagtail_image = Image(title=title, width=width, height=height)
        wagtail_image.file.save(f"{key.lower()}.png", ContentFile(buffer.getvalue()))

        return wagtail_image
```

### Image Manifest

Define all required images in a manifest:

```python
IMAGE_MANIFEST = [
    {"key": "HERO_IMAGE", "width": 1920, "height": 1080, "label": "Hero"},
    {"key": "LOGO", "width": 400, "height": 100},
    {"key": "FAVICON", "width": 32, "height": 32},
    {"key": "SERVICE_1", "width": 600, "height": 400, "label": "Service 1"},
    # ...
]

def create_images(self) -> dict[str, Image]:
    manager = ImageManager(prefix=IMAGE_PREFIX)
    return manager.generate_manifest(IMAGE_MANIFEST)
```

## Content Configuration

### Brand Configuration

Keep brand-specific values in a configuration dict:

```python
BRAND_CONFIG = {
    "company_name": "Brand Name",
    "tagline": "Brand tagline",
    "phone_number": "+44 123 456 7890",
    "email": "hello@brand.com",
    "primary_color": "#1A2F23",
    "secondary_color": "#4A6350",
    "heading_font": "Playfair Display",
    "body_font": "Lato",
    "instagram_url": "https://instagram.com/brand",
}
```

### StreamField Content

Build StreamField content as lists of dicts:

```python
def _create_about_page(self, home_page: Page) -> StandardPage:
    body = [
        {
            "type": "hero_gradient",
            "value": {
                "title": "About Us",
                "subtitle": "Our story",
                "image": self.images["ABOUT_HERO"].id,
            },
        },
        {
            "type": "rich_text",
            "value": "<p>Company history...</p>",
        },
        {
            "type": "team_grid",
            "value": {
                "members": [
                    {"name": "Founder", "image": self.images["FOUNDER"].id},
                ],
            },
        },
    ]

    return self._get_or_create_standard_page(
        parent=home_page,
        slug="about",
        title="About",
        body=body,
    )
```

## Navigation Structure

### Mega Menu (3-Level)

```python
def _build_menu_items(self, pages: dict[str, Page]) -> list[dict]:
    return [
        {
            "type": "menu_item",
            "value": {
                "label": "Products",
                "page": pages["products"].id,
                "children": [
                    {
                        "label": "Category A",
                        "page": pages["category-a"].id,
                        "children": [
                            {"label": "Item 1", "page": pages["item-1"].id},
                            {"label": "Item 2", "page": pages["item-2"].id},
                        ],
                    },
                ],
            },
        },
        {
            "type": "menu_item",
            "value": {
                "label": "About",
                "page": pages["about"].id,
            },
        },
    ]
```

### Footer Sections

```python
def _configure_footer_navigation(self, site: Site, pages: dict[str, Page]) -> None:
    footer = FooterNavigation.for_site(site)
    footer.tagline = BRAND_CONFIG["tagline"]
    footer.link_sections = [
        {
            "type": "link_section",
            "value": {
                "title": "Company",
                "links": [
                    {"text": "About", "page": pages["about"].id},
                    {"text": "Contact", "page": pages["contact"].id},
                ],
            },
        },
        {
            "type": "link_section",
            "value": {
                "title": "Legal",
                "links": [
                    {"text": "Terms", "page": pages["terms"].id},
                    {"text": "Privacy", "page": pages["privacy"].id},
                ],
            },
        },
    ]
    footer.save()
```

## Blog Content

### Categories

```python
def create_categories(self) -> dict[str, Category]:
    categories = {}
    for name, slug in [
        ("Design Insights", "design-insights"),
        ("Behind the Scenes", "behind-the-scenes"),
        ("Client Stories", "client-stories"),
    ]:
        cat, _ = Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name},
        )
        categories[slug] = cat
    return categories
```

### Blog Posts

```python
BLOG_POSTS = [
    {
        "slug": "first-post",
        "title": "First Post Title",
        "excerpt": "Short description for listings.",
        "category": "design-insights",
        "image_key": "BLOG_1",
        "published_date": date(2025, 1, 15),
        "reading_time": 5,
        "body_content": "<p>Post content...</p>",
    },
    # ...
]

def create_blog_content(
    self,
    blog_index: BlogIndexPage,
    categories: dict[str, Category],
) -> list[BlogPostPage]:
    posts = []
    for post_data in BLOG_POSTS:
        post = self._create_blog_post(blog_index, categories, post_data)
        posts.append(post)
    return posts
```

## Testing Your Seeder

### Unit Tests

```python
@pytest.mark.django_db
def test_seeder_creates_site(wagtail_default_site):
    call_command("seed_brand")

    site = Site.objects.get(hostname="localhost", port=8000)
    assert site.site_name == "Brand Name"

@pytest.mark.django_db
def test_seeder_idempotent(wagtail_default_site):
    call_command("seed_brand")
    call_command("seed_brand")

    assert Site.objects.filter(hostname="localhost").count() == 1
```

### Integration Tests

```python
@pytest.mark.django_db
def test_full_seed_workflow(wagtail_default_site):
    call_command("seed_brand")

    site = Site.objects.get(hostname="localhost", port=8000)
    home = site.root_page.specific

    # Verify structure
    children = {p.slug for p in home.get_children()}
    assert "about" in children
    assert "contact" in children
    assert "blog" in children

    # Verify navigation
    header = HeaderNavigation.for_site(site)
    assert len(header.menu_items) >= 3

    # Verify branding
    settings = SiteSettings.for_site(site)
    assert settings.primary_color is not None
```

## Checklist for New Seeders

- [ ] Command file in `boilerplate/.../commands/seed_<name>.py`
- [ ] `--clear` flag for full reset
- [ ] `--images-only` flag for image generation
- [ ] `--hostname` and `--port` options
- [ ] Idempotent page creation (parent + slug lookup)
- [ ] Unique image prefix (e.g., `BRAND_`)
- [ ] Brand configuration dict
- [ ] Image manifest with all required images
- [ ] Unit tests for each component
- [ ] Integration tests for full workflow
- [ ] User documentation in `docs/user/`

## See Also

- [Sage & Stone Seeder](../user/seed-sage-stone.md) — Reference implementation
- [Theme Guide](THEME-GUIDE.md) — Block types and templates
