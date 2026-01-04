# Sage & Stone Demo Site Seeder

Generate a complete demonstration website for "Sage & Stone," a fictional bespoke kitchen company.

## Quick Start

### Via Management Command

```bash
python manage.py seed sage-stone
```

This creates a fully populated Wagtail site with pages, navigation, branding, blog content, and placeholder images.
The legacy `seed_sage_stone` command has been replaced by `seed` with the `sage-stone` profile.

## What Gets Created

| Component | Details |
|-----------|---------|
| **Site** | Wagtail Site at localhost:8000 |
| **Homepage** | Hero, featured content, testimonials |
| **Core Pages** | About, Services, Portfolio, Contact |
| **Blog** | Index + 7 articles across 3 categories |
| **Legal Pages** | Terms of Supply (with ToC), Privacy, Accessibility |
| **Navigation** | 3-level mega menu header, sectioned footer |
| **Branding** | Colors, typography, logos, favicon |
| **Images** | 30+ branded placeholder images |

## Command Options

```bash
# Full site seed (default profile)
python manage.py seed sage-stone

# Clear existing content and rebuild
python manage.py seed sage-stone --clear

# Override the content directory
python manage.py seed sage-stone --content-path ./content

# Validate content and print the plan without writing
python manage.py seed sage-stone --dry-run
```

### Option Reference

| Option | Description |
|--------|-------------|
| `--clear` | Delete existing Sage & Stone content before re-seeding |
| `--content-path` | Override the content directory (defaults to `./content`) |
| `--dry-run` | Print the seed plan without writing data |

## Idempotency

The seeder is safe to run multiple times:

- **Pages** are looked up by parent + slug; updated if existing, created if not
- **Navigation** uses `get_or_create` on the site
- **Images** are matched by title (prefixed with `SS_`)
- **Settings** are updated, not duplicated

For structural changes (reordering pages, changing parent relationships), use `--clear` first.

## Site Structure

```
Sage & Stone (HomePage)
├── About (StandardPage)
├── Services (StandardPage)
├── Portfolio (StandardPage)
├── Contact (StandardPage)
├── The Ledger (BlogIndexPage) ─ journal/
│   ├── Art of Seasoning Timber (BlogPostPage)
│   ├── ... (6 more posts)
├── Terms of Supply (LegalPage)
├── Privacy (StandardPage)
└── Accessibility (StandardPage)
```

## Blog Categories

| Category | Slug | Description |
|----------|------|-------------|
| Material Science | `material-science` | Wood, stone, and craftsmanship |
| Commission Stories | `commission-stories` | Client project narratives |
| The Workshop | `the-workshop` | Behind the scenes |

## Branding Configuration

The seeder uses the Sage & Stone brand palette:

| Color | Hex | Usage |
|-------|-----|-------|
| Sage Black | `#1A2F23` | Primary, text |
| Dark Moss | `#4A6350` | Secondary |
| Terra | `#A0563B` | Accent |
| Linen | `#F7F5F1` | Background |
| Oat | `#EDE8E0` | Surface |

Typography:
- **Headings:** Playfair Display
- **Body:** Lato

## Placeholder Images

All generated images are prefixed with `SS_` for easy identification:

- `SS_HERO_IMAGE` — Main hero (1920×1080)
- `SS_LOGO` — Header/footer logo (400×100)
- `SS_FAVICON` — Favicon (32×32)
- `SS_FOUNDER_IMAGE` — Team portrait (800×1000)
- `SS_SERVICE_*` — Service illustrations (600×400)
- `SS_BLOG_*` — Article featured images (1200×630)

To replace with real images:
1. Go to Wagtail Admin → Images
2. Search for `SS_`
3. Replace each placeholder with actual photography

## Troubleshooting

### "Site already exists" error

The default Wagtail site may conflict. Clear and rebuild:

```bash
python manage.py seed sage-stone --clear
```

### Missing blocks error

Ensure Theme A is applied and all sum_core blocks are registered. Check that `sum_core` is in `INSTALLED_APPS`.

### Image generation fails

Requires Pillow:

```bash
pip install Pillow
```

### Pages not appearing

Check that pages are published (live). Run the seeder again to ensure all pages are created:

```bash
python manage.py seed sage-stone
```

## Integration with Theme A

Sage & Stone is designed for Theme A. The seeder populates StreamField blocks that correspond to Theme A's template components:

- Hero sections
- Feature grids
- Testimonial carousels
- Team member cards
- Contact forms
- Blog listings

## See Also

- [Extending Seeders](../dev/extending-seeders.md) — Create custom seeders
- [Theme Guide](../dev/THEME-GUIDE.md) — Theme A documentation
