# SUM Core

A Django/Wagtail foundation for launching lead-focused websites for home improvement trades. SUM Core provides a complete content management system with built-in forms, lead capture, analytics, and technical SEO—ready to theme and deploy.

## Features

- **Content Management**: Page types (Home, Services, Standard pages) built on Wagtail CMS with StreamField blocks for flexible content authoring
- **Lead Capture**: Contact and quote request forms with spam protection, attribution tracking, and email/webhook notifications
- **Branding System**: Configurable colors, fonts, logos, and business info through the admin interface
- **Navigation**: Header menus (3 levels), footer sections, and mobile sticky CTA—all managed through Wagtail settings
- **Technical SEO**: Automatic sitemaps, robots.txt, meta tags, Open Graph, and JSON-LD structured data
- **Analytics**: GA4/GTM integration with lead tracking dashboard
- **Email & Webhooks**: Lead notifications via SMTP and Zapier integration
- **Observability**: Health checks, Sentry integration, and structured logging

## Installation

### Requirements

- Python 3.12+
- PostgreSQL (recommended) or SQLite

### Install from PyPI

```bash
pip install sum-core
```

### Create a New Project

```bash
django-admin startproject myproject
cd myproject
```

Add to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... Django apps
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    'modelcluster',
    'taggit',

    # SUM Core apps
    'sum_core',
    'sum_core.analytics',
    'sum_core.blocks',
    'sum_core.branding',
    'sum_core.forms',
    'sum_core.navigation',
    'sum_core.ops',
    'sum_core.pages',
    'sum_core.seo',

    # Your apps
    'home',  # Create your HomePage model here
]
```

Include SUM Core URLs in your `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('', include('sum_core.urls')),
    # ... other patterns
]
```

Run migrations:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Quick Start

1. **Access the admin**: Visit `http://localhost:8000/admin/`
2. **Configure your site**: Go to Settings → Site settings to set your branding, colors, fonts, and business info
3. **Set up navigation**: Configure your header and footer menus in Settings → Header/Footer Navigation
4. **Create content**: Add pages using the Wagtail page tree
5. **Configure forms**: Set lead notification emails and rate limits in Django admin

## Documentation

- **[Platform Handbook](docs/HANDBOOK.md)**: Complete guide to the platform
- **[Wiring Guide](docs/dev/WIRING-INVENTORY.md)**: How to integrate SUM Core into your project
- **[Block Reference](docs/dev/blocks-reference.md)**: Available StreamField blocks
- **[Design System](docs/dev/design/css-architecture-and-tokens.md)**: CSS tokens and theming

## Environment Configuration

Key environment variables (see [`.env.example`](.env.example) for complete list):

```bash
# Database
DJANGO_DB_NAME=your_db
DJANGO_DB_USER=your_user
DJANGO_DB_PASSWORD=your_password
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432

# Email notifications
DEFAULT_FROM_EMAIL=noreply@yoursite.com
LEAD_NOTIFICATION_EMAIL=leads@yoursite.com

# Optional integrations
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/...
SENTRY_DSN=https://...
```

## Example Projects

- **[sum_client](clients/sum_client/)**: Reference implementation showing recommended project structure
- **[showroom](clients/showroom/)**: Demonstration site with sample content

## Support

For issues, questions, or contributions, please see the [repository documentation](docs/dev/DEV-README.md).

## License

TBD
