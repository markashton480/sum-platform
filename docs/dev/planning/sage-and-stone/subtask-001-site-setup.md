# Subtask 001: Site & Root Setup

## Overview

Configure the Wagtail site and root page structure for Sage & Stone.

## Deliverables

1. Site object configuration
2. Root page (HomePage) creation
3. Site root assignment
4. Basic validation

## Implementation

### 1. Get or Create Site

```python
from django.contrib.sites.models import Site as DjangoSite
from wagtail.models import Site, Page

def setup_site(self, hostname="localhost", port=8000):
    """Configure Wagtail site with Sage & Stone root."""

    # Get default Wagtail root page
    root = Page.objects.get(depth=1)

    # Create HomePage as child of root
    home_page, created = self._get_or_create_home_page(root)

    # Get or create Site
    site, site_created = Site.objects.get_or_create(
        hostname=hostname,
        defaults={
            "site_name": "Sage & Stone",
            "root_page": home_page,
            "is_default_site": True,
            "port": port,
        }
    )

    if not site_created:
        # Update existing site
        site.site_name = "Sage & Stone"
        site.root_page = home_page
        site.is_default_site = True
        site.save()

    self.stdout.write(f"Site configured: {site.site_name}")
    return site, home_page
```

### 2. HomePage Creation

```python
from home.models import HomePage

def _get_or_create_home_page(self, root):
    """Create the Sage & Stone homepage."""

    try:
        home_page = HomePage.objects.get(slug="home")
        return home_page, False
    except HomePage.DoesNotExist:
        pass

    home_page = HomePage(
        title="Sage & Stone",
        slug="home",
        seo_title="Sage & Stone | Bespoke Kitchens, Herefordshire",
        search_description="Heirloom-quality kitchens, handcrafted in Herefordshire. 12 commissions per year. Lifetime guarantee.",
        show_in_menus=False,
    )

    root.add_child(instance=home_page)
    home_page.save_revision().publish()

    return home_page, True
```

### 3. Clear Existing Content (Optional)

```python
def clear_existing_content(self):
    """Remove all Sage & Stone content for fresh seed."""

    # Get pages to delete (exclude Wagtail root)
    HomePage.objects.filter(slug="home").delete()

    # Clear settings
    SiteSettings.objects.all().delete()
    HeaderNavigation.objects.all().delete()
    FooterNavigation.objects.all().delete()

    # Clear categories
    Category.objects.all().delete()

    # Clear images created by seeder
    # (Only if tagged with our prefix)
    from wagtail.images.models import Image
    Image.objects.filter(title__startswith="SS_").delete()

    self.stdout.write("Cleared existing Sage & Stone content")
```

## Acceptance Criteria

- [ ] Site object exists with correct hostname
- [ ] HomePage exists as site root
- [ ] Site is marked as default
- [ ] `--clear` flag removes previous content
- [ ] Idempotent: can run multiple times safely

## Dependencies

- `home.models.HomePage` must exist (client model)
- Database migrated

## Testing

```python
def test_setup_site_creates_site():
    call_command("seed_sage_stone")

    site = Site.objects.get(hostname="localhost")
    assert site.site_name == "Sage & Stone"
    assert site.root_page.slug == "home"
    assert site.is_default_site

def test_setup_site_idempotent():
    call_command("seed_sage_stone")
    call_command("seed_sage_stone")

    assert Site.objects.filter(hostname="localhost").count() == 1
    assert HomePage.objects.filter(slug="home").count() == 1
```
