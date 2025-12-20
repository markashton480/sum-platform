# Implement M1_004 document instructions
_Exported on 12/10/2025 at 14:48:48 GMT from Cursor (2.1.50)_

---

**User**

Please carefully review the context and instructions in @docs/dev/M1/M1_004.md and implement accordingly. 

---

**Cursor**

Implemented the shared layout shell with branding hooks and semantic structure. `sum_core/base.html` now loads branding/fonts, resolves site name via `get_site_settings`/`wagtail_site`, links `main.css`, favicon rendition, and exposes head/body content blocks around the header/main/footer includes.```1:36:core/sum_core/templates/sum_core/base.html
{% load static wagtailcore_tags branding_tags wagtailimages_tags %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% get_site_settings as site_settings %}
    {% wagtail_site as current_site %}
    {% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
    <title>
      {% block title %}
        {% if page %}
          {% firstof page.seo_title page.title %}
        {% else %}
          {{ site_name }}
        {% endif %}
      {% endblock %}
    </title>
    {% if site_settings.favicon %}
      {% image site_settings.favicon fill-32x32 as favicon_rendition %}
      <link rel="icon" href="{{ favicon_rendition.url }}">
    {% endif %}
    <link rel="stylesheet" href="{% static 'sum_core/css/main.css' %}">
    {% branding_fonts %}
    {% branding_css %}
    {% block extra_head %}{% endblock %}
  </head>
  <body class="layout">
    <div class="layout__inner">
      {% include "sum_core/includes/header.html" %}
      <main class="layout__main">
        {% block content %}{% endblock %}
      </main>
      {% include "sum_core/includes/footer.html" %}
    </div>
    {% block extra_body %}{% endblock %}
  </body>
</html>
```

Created header/footer partials that render site logo/name, tagline, and contact info with BEM classes and Wagtail image renditions, plus a nav hook in the header.```1:24:core/sum_core/templates/sum_core/includes/header.html
{% load branding_tags wagtailcore_tags wagtailimages_tags %}
{% get_site_settings as site_settings %}
{% wagtail_site as current_site %}
{% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
<header class="layout__header site-header">
  <div class="container site-header__inner">
    <a href="/" class="site-header__brand">
      {% if site_settings.header_logo %}
        {% image site_settings.header_logo height-40 as header_logo %}
        <img
          src="{{ header_logo.url }}
```
```1:35:core/sum_core/templates/sum_core/includes/footer.html
{% load branding_tags wagtailcore_tags %}
{% get_site_settings as site_settings %}
{% wagtail_site as current_site %}
{% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
<footer class="layout__footer site-footer">
  <div class="container site-footer__inner">
    <div class="site-footer__brand">
      <div class="site-footer__title">
        {{ site_name }}
      </div>
      {% if site_settings.tagline %}
        <div class="site-footer__tagline">
          {{ site_settings.tagline }}
        </div>
```

Extended `main.css` with layout/header/footer styles using tokenized spacing, colours, and typography to enforce the shell rhythm.```284:398:core/sum_core/static/sum_core/css/main.css
/* ==========================================================================
   5. Layout Shell
   ========================================================================== */

.layout {
  min-height: 100vh;
  background-color: var(--color-background);
  color: var(--color-text);
}

.layout__inner {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout__header {
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.layout__main {
  flex: 1 0 auto;
}

.layout__footer {
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
}
```

Added template tests ensuring branding assets, CSS hooks, and header/footer settings render as expected.```23:74:tests/templates/test_base_template.py
def test_base_template_renders_with_branding_and_content() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    page = SimpleNamespace(title="Sample Page", seo_title="Custom SEO Title")

    template = Template(
        "{% extends 'sum_core/base.html' %}"
        "{% load branding_tags %}"
        "{% block content %}Hello{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": page}))

    assert "<title>" in rendered
    assert "Custom SEO Title" in rendered
    assert "sum_core/css/main.css" in rendered
```

Tests run: `pytest tests/templates/test_base_template.py` (pass).

```html

Created header/footer partials that render site logo/name, tagline, and contact info with BEM classes and Wagtail image renditions, plus a nav hook in the header.```1:24:core/sum_core/templates/sum_core/includes/header.html
{% load branding_tags wagtailcore_tags wagtailimages_tags %}
{% get_site_settings as site_settings %}
{% wagtail_site as current_site %}
{% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
<header class="layout__header site-header">
  <div class="container site-header__inner">
    <a href="/" class="site-header__brand">
      {% if site_settings.header_logo %}
        {% image site_settings.header_logo height-40 as header_logo %}
        <img
          src="{{ header_logo.url }}
```

```plaintext

Created header/footer partials that render site logo/name, tagline, and contact info with BEM classes and Wagtail image renditions, plus a nav hook in the header.```1:24:core/sum_core/templates/sum_core/includes/header.html
{% load branding_tags wagtailcore_tags wagtailimages_tags %}
{% get_site_settings as site_settings %}
{% wagtail_site as current_site %}
{% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
<header class="layout__header site-header">
  <div class="container site-header__inner">
    <a href="/" class="site-header__brand">
      {% if site_settings.header_logo %}
        {% image site_settings.header_logo height-40 as header_logo %}
        <img
          src="{{ header_logo.url }}
```

```html
{% load branding_tags wagtailcore_tags %}
{% get_site_settings as site_settings %}
{% wagtail_site as current_site %}
{% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
<footer class="layout__footer site-footer">
  <div class="container site-footer__inner">
    <div class="site-footer__brand">
      <div class="site-footer__title">
        {{ site_name }}
      </div>
      {% if site_settings.tagline %}
        <div class="site-footer__tagline">
          {{ site_settings.tagline }}
        </div>
```

```html
{% load branding_tags wagtailcore_tags %}
{% get_site_settings as site_settings %}
{% wagtail_site as current_site %}
{% firstof site_settings.company_name current_site.site_name WAGTAIL_SITE_NAME as site_name %}
<footer class="layout__footer site-footer">
  <div class="container site-footer__inner">
    <div class="site-footer__brand">
      <div class="site-footer__title">
        {{ site_name }}
      </div>
      {% if site_settings.tagline %}
        <div class="site-footer__tagline">
          {{ site_settings.tagline }}
        </div>
```

```html

Added template tests ensuring branding assets, CSS hooks, and header/footer settings render as expected.```23:74:tests/templates/test_base_template.py
def test_base_template_renders_with_branding_and_content() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    page = SimpleNamespace(title="Sample Page", seo_title="Custom SEO Title")

    template = Template(
        "{% extends 'sum_core/base.html' %}"
        "{% load branding_tags %}"
        "{% block content %}Hello{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": page}))

    assert "<title>" in rendered
    assert "Custom SEO Title" in rendered
    assert "sum_core/css/main.css" in rendered
```

```plaintext

Added template tests ensuring branding assets, CSS hooks, and header/footer settings render as expected.```23:74:tests/templates/test_base_template.py
def test_base_template_renders_with_branding_and_content() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    page = SimpleNamespace(title="Sample Page", seo_title="Custom SEO Title")

    template = Template(
        "{% extends 'sum_core/base.html' %}"
        "{% load branding_tags %}"
        "{% block content %}Hello{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": page}))

    assert "<title>" in rendered
    assert "Custom SEO Title" in rendered
    assert "sum_core/css/main.css" in rendered
```

```css
/* ==========================================================================
   5. Layout Shell
   ========================================================================== */

.layout {
  min-height: 100vh;
  background-color: var(--color-background);
  color: var(--color-text);
}

.layout__inner {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout__header {
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.layout__main {
  flex: 1 0 auto;
}

.layout__footer {
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
}
```

```python
def test_base_template_renders_with_branding_and_content() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Test Co"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    page = SimpleNamespace(title="Sample Page", seo_title="Custom SEO Title")

    template = Template(
        "{% extends 'sum_core/base.html' %}"
        "{% load branding_tags %}"
        "{% block content %}Hello{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": page}))

    assert "<title>" in rendered
    assert "Custom SEO Title" in rendered
    assert "sum_core/css/main.css" in rendered
```

---

**User**

1) Tweaks to apply 



**A. `core/sum_core/templates/sum_core/includes/header.html`**



1. **Fix the logo `<img>` tag syntax + alt text**

    

    Make sure it looks like this (or equivalent):

    

    ```django

    {% if site_settings.header_logo %}

      {% image site_settings.header_logo height-40 as header_logo %}

      <img

        src="{{ header_logo.url }}"

        alt="{{ site_name }}"

        class="site-header__logo"

      >

    {% else %}

      <span class="site-header__title">

        {{ site_name }}

      </span>

    {% endif %}

    ```

    

    - Ensure the `src` attribute has the closing quote.

        

    - Ensure the `<img>` tag is fully closed.

        

    - Provide a text fallback (`site_name`) when no logo is set.

        

2. **Ensure there’s a nav hook**

    

    After the brand block, make sure there is a block that can be overridden later:

    

    ```django

    {% block primary_nav %}{% endblock %}

    ```

    



---



**B. `core/sum_core/templates/sum_core/includes/footer.html`**



1. **Format address nicely**

    

    When rendering `address`, use `linebreaksbr` so multi-line addresses display properly:

    

    ```django

    {% if site_settings.address %}

      <div class="site-footer__item site-footer__address">

        {{ site_settings.address|linebreaksbr }}

      </div>

    {% endif %}

    ```

    

2. Keep using `site_name` / `tagline` as already implemented – that part’s good.

    



---



**C. `tests/templates/test_base_template.py`**



1. **Mark the module as DB-using**

    

    At the top of the file:

    

    ```python

    import pytest

    

    pytestmark = pytest.mark.django_db

    ```

    

2. **Slightly stronger assertions**

    

    In `test_base_template_renders_with_branding_and_content`, after `rendered = ...`, add:

    

    ```python

    assert "Custom SEO Title" in rendered

    assert "Test Co" in rendered          # header/footer brand

    assert "Hello" in rendered            # content block

    assert "sum_core/css/main.css" in rendered

    ```

    

    (Some of these are already present, just make sure we assert brand + content as well.)

    



---



**D. Optional but recommended – font tag warnings**



In `core/sum_core/branding/templatetags/branding_tags.py`:



- For the “no fonts” case, just return an empty string:

    

    ```python

    if not families:

        return ""

    ```

    

- For the case where we do emit links, switch from `format_html("\n".join(links))` to `mark_safe`:

    

    ```python

    from django.utils.safestring import mark_safe

    

    ...

    

    return mark_safe("\n".join(links))

    ```

    



This will remove the `RemovedInDjango60Warning` about `format_html()`.

---

**Cursor**

Changes applied per requests:

- Header include: logo `<img>` now correctly quoted/closed, uses `site_name` alt/fallback, and retains the `primary_nav` override hook.  
- Footer include: address already rendered via `linebreaksbr`; kept `site_name`/`tagline` usage.  
- Template tests: strengthened assertions to check title, brand, content, CSS and branding hook; module already marked `django_db`.  
- Branding fonts tag: returns empty string when no fonts and uses `mark_safe` to silence Django 6 warnings.  
- Tests run: `pytest tests/templates/test_base_template.py` (pass).

