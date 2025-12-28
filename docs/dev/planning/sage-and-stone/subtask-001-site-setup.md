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
    # Include port in lookup since (hostname, port) is unique constraint in Wagtail
    site, site_created = Site.objects.get_or_create(
        hostname=hostname,
        port=port,
        defaults={
            "site_name": "Sage & Stone",
            "root_page": home_page,
            "is_default_site": True,
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
    """Create the Sage & Stone homepage.

    Uses parent+slug lookup for proper Wagtail tree handling.
    Updates existing page if found (idempotent).
    """

    # Look up by parent + slug to respect tree structure
    try:
        home_page = root.get_children().type(HomePage).get(slug="home")
        # Update existing page
        home_page.title = "Sage & Stone"
        home_page.seo_title = "Sage & Stone | Bespoke Kitchens, Herefordshire"
        home_page.search_description = "Heirloom-quality kitchens, handcrafted in Herefordshire. 12 commissions per year. Lifetime guarantee."
        home_page.save_revision().publish()
        return home_page, False
    except HomePage.DoesNotExist:
        pass

    # Create new page
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
def clear_existing_content(self, hostname="localhost", port=8000):
    """Remove Sage & Stone content for fresh seed.

    IMPORTANT: Scoped to the specific site to avoid data loss in multi-site setups.
    """
    from wagtail.images.models import Image
    from wagtail.models import Site

    # Find the Sage & Stone site
    try:
        site = Site.objects.get(hostname=hostname, port=port)
    except Site.DoesNotExist:
        self.stdout.write("No existing Sage & Stone site found, nothing to clear")
        return

    # Delete entire page tree under site root (if it's a HomePage)
    if site.root_page and site.root_page.specific_class.__name__ == 'HomePage':
        # Delete all descendants and the root page itself
        # This cascades to all child pages (About, Services, Blog, etc.)
        site.root_page.get_descendants(inclusive=True).delete()
        self.stdout.write(f"Deleted {site.root_page.title} and all descendant pages")

    # Clear site-specific settings
    # Note: SiteSettings is a singleton per site via ParentalKey
    from sum_core.branding.models import SiteSettings
    SiteSettings.for_site(site).delete()

    # Clear navigation for this site
    # Note: If HeaderNavigation/FooterNavigation are site-specific via FK,
    # filter by site. Otherwise, consider prefixing or documenting manual cleanup.
    from sum_core.navigation.models import HeaderNavigation, FooterNavigation
    HeaderNavigation.objects.filter(site=site).delete()
    FooterNavigation.objects.filter(site=site).delete()

    # Clear categories - prefix-based approach to avoid deleting unrelated categories
    from sum_core.blog.models import Category
    Category.objects.filter(name__in=[
        "Commission Stories",
        "Material Science",
        "The Workshop",
        "Sage & Stone Updates"  # Any Sage & Stone specific categories
    ]).delete()

    # Clear images created by seeder (prefix-based)
    Image.objects.filter(title__startswith="SS_").delete()

    # Delete the site object itself
    site.delete()

    self.stdout.write("Cleared existing Sage & Stone content (scoped to site)")
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
