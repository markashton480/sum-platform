"""Site-level seeder for branding, settings, and navigation."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from wagtail.models import Site

from .base import BaseSeeder
from .content import ContentLoader
from .exceptions import SeederContentError, SeederPageError
from .images import ImageManager

SITE_SECTIONS = {
    "brand",
    "contact",
    "colors",
    "typography",
    "social",
    "analytics",
    "cookies",
}

FIELD_ALIASES = {
    "phone": "phone_number",
    "instagram": "instagram_url",
    "facebook": "facebook_url",
    "linkedin": "linkedin_url",
    "twitter": "twitter_url",
    "x": "twitter_url",
    "youtube": "youtube_url",
    "tiktok": "tiktok_url",
    "primary": "primary_color",
    "secondary": "secondary_color",
    "accent": "accent_color",
    "background": "background_color",
    "text": "text_color",
    "surface": "surface_color",
    "surface_elevated": "surface_elevated_color",
    "text_light": "text_light_color",
}

PAGE_REFERENCE_FIELDS = {
    "privacy_policy_page",
    "cookie_policy_page",
    "terms_page",
}

HEADER_FIELDS = {
    "menu_items",
    "show_phone_in_header",
    "header_cta_enabled",
    "header_cta_text",
    "header_cta_link",
    "mobile_cta_enabled",
    "mobile_cta_phone_enabled",
    "mobile_cta_button_enabled",
    "mobile_cta_button_text",
    "mobile_cta_button_link",
}

FOOTER_FIELDS = {
    "tagline",
    "link_sections",
    "auto_service_areas",
    "social_facebook",
    "social_instagram",
    "social_linkedin",
    "social_youtube",
    "social_x",
    "copyright_text",
}


class SiteSeeder(BaseSeeder):
    """Seed site settings, branding, and navigation."""

    def __init__(
        self,
        *,
        hostname: str = "localhost",
        port: int = 8000,
        is_default_site: bool = True,
        site_name: str | None = None,
        root_page: Any | None = None,
        pages: Mapping[str, Any] | None = None,
        content_loader: ContentLoader | None = None,
        image_manager: ImageManager | None = None,
        image_prefix: str = "SEED",
    ) -> None:
        """Initialize the site seeder.

        Args:
            hostname: Hostname for the Wagtail Site.
            port: Port for the Wagtail Site.
            is_default_site: Whether the site should be marked as default.
            site_name: Optional override for the site display name.
            root_page: Root page (or page id) to attach the site to.
            pages: Optional mapping of page slugs to page objects.
            content_loader: Loader for YAML content profiles.
            image_manager: Image manager for branding assets.
            image_prefix: Prefix for generated images when no manager is provided.
        """
        self.hostname = hostname
        self.port = port
        self.is_default_site = is_default_site
        self.site_name = site_name
        self.root_page = root_page
        self.pages = dict(pages or {})
        self.content_loader = content_loader or ContentLoader()
        self.image_manager = image_manager or ImageManager(prefix=image_prefix)

    def seed_profile(
        self,
        profile: str,
        *,
        pages: Mapping[str, Any] | None = None,
        clear: bool = False,
    ) -> None:
        """Load a content profile and seed site data.

        Args:
            profile: Content profile name to load from the content directory.
            pages: Optional page mapping for resolving navigation links.
            clear: When True, clear existing seeded data before seeding.
        """
        data = self.content_loader.load_profile(profile)
        content: dict[str, Any] = {"site": data.site, "navigation": data.navigation}
        if pages is not None:
            content["pages"] = pages
        self.seed(content, clear=clear)

    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        """Seed site settings, branding, and navigation from content.

        Args:
            content: Mapping containing site, navigation, and optional pages data.
            clear: When True, clear existing seeded data before seeding.
        """
        if clear:
            self.clear()

        site_content = self._extract_site_content(content)
        navigation = self._extract_navigation(content)
        pages = self._resolve_pages(content)

        normalized_site = self._normalize_site_content(site_content)
        site = self._ensure_site(normalized_site, pages)
        self._configure_branding(site, normalized_site, pages)
        self._configure_navigation(site, navigation, pages)

    def clear(self) -> None:
        """Remove seeded site settings, navigation, and generated images."""
        site = Site.objects.filter(hostname=self.hostname, port=self.port).first()
        if site is None:
            return

        SiteSettings.objects.filter(site=site).delete()
        HeaderNavigation.objects.filter(site=site).delete()
        FooterNavigation.objects.filter(site=site).delete()

        if self.image_manager:
            from wagtail.images.models import Image

            Image.objects.filter(
                title__startswith=f"{self.image_manager.prefix}_"
            ).delete()

        Site.clear_site_root_paths_cache()

    def _extract_site_content(self, content: dict[str, Any]) -> dict[str, Any]:
        site_content = content.get("site", content)
        if not isinstance(site_content, Mapping):
            raise SeederContentError("Site content must be a mapping.")
        return dict(site_content)

    def _extract_navigation(self, content: dict[str, Any]) -> dict[str, Any]:
        navigation = content.get("navigation", {}) or {}
        if not isinstance(navigation, Mapping):
            raise SeederContentError("Navigation content must be a mapping.")
        return dict(navigation)

    def _resolve_pages(self, content: dict[str, Any]) -> dict[str, Any]:
        pages = content.get("pages")
        if pages is None:
            pages = self.pages
        if not pages:
            return {}
        if not isinstance(pages, Mapping):
            raise SeederContentError("Pages mapping must be a mapping of slug to page.")
        return dict(pages)

    def _normalize_site_content(
        self, site_content: Mapping[str, Any]
    ) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in site_content.items():
            if isinstance(value, Mapping) and key in SITE_SECTIONS:
                for inner_key, inner_value in value.items():
                    normalized[self._alias_field(inner_key)] = inner_value
            else:
                normalized[self._alias_field(key)] = value
        return normalized

    def _alias_field(self, key: str) -> str:
        return FIELD_ALIASES.get(key, key)

    def _ensure_site(
        self, site_content: Mapping[str, Any], pages: Mapping[str, Any]
    ) -> Site:
        site_name = (
            self.site_name
            or site_content.get("site_name")
            or site_content.get("company_name")
            or "Site"
        )
        root_page = self._resolve_root_page(pages)
        root_page_id = self._resolve_page_id(root_page)
        if root_page_id is None:
            raise SeederPageError("Root page must be a Page or page id.")

        defaults = {
            "site_name": site_name,
            "root_page_id": root_page_id,
            "is_default_site": self.is_default_site,
        }
        site, created = Site.objects.get_or_create(
            hostname=self.hostname,
            port=self.port,
            defaults=defaults,
        )
        if not created:
            site.site_name = site_name
            site.root_page_id = root_page_id
            site.is_default_site = self.is_default_site
            site.save()
        Site.clear_site_root_paths_cache()
        return site

    def _resolve_root_page(self, pages: Mapping[str, Any]) -> Any:
        if self.root_page is not None:
            return self.root_page
        if "home" in pages:
            return pages["home"]
        raise SeederPageError("Root page is required for site seeding.")

    def _resolve_page_id(self, page: Any) -> int | None:
        if isinstance(page, int):
            return page
        page_id = getattr(page, "id", None)
        if isinstance(page_id, int):
            return page_id
        return None

    def _configure_branding(
        self, site: Site, site_content: Mapping[str, Any], pages: Mapping[str, Any]
    ) -> None:
        settings, _ = SiteSettings.objects.get_or_create(site=site)

        for key, value in site_content.items():
            if key in PAGE_REFERENCE_FIELDS:
                value = self._resolve_page_setting(value, pages)
            if hasattr(settings, key):
                setattr(settings, key, value)

        company_name = site_content.get("company_name")
        logo = self._generate_image(
            "LOGO",
            300,
            80,
            label=self._string_or_none(company_name),
            bg_color=site_content.get("primary_color"),
            text_color=site_content.get("text_light_color"),
        )
        favicon_label = self._favicon_label(company_name)
        favicon = self._generate_image(
            "FAVICON",
            64,
            64,
            label=favicon_label,
            bg_color=site_content.get("primary_color"),
            text_color=site_content.get("text_light_color"),
        )
        og_image = self._get_og_image(site_content)

        settings.header_logo = logo
        settings.footer_logo = logo
        settings.favicon = favicon
        if og_image is not None:
            settings.og_default_image = og_image

        settings.save()

    def _resolve_page_setting(self, value: Any, pages: Mapping[str, Any]) -> Any:
        if isinstance(value, str):
            page = pages.get(value)
            if page is None:
                raise SeederContentError(f"Page not found for slug: {value}")
            return page
        return value

    def _string_or_none(self, value: Any) -> str | None:
        if isinstance(value, str) and value.strip():
            return value
        return None

    def _favicon_label(self, company_name: Any) -> str:
        if isinstance(company_name, str) and company_name.strip():
            return company_name.strip()[0].upper()
        return "S"

    def _generate_image(
        self,
        key: str,
        width: int,
        height: int,
        *,
        label: str | None = None,
        bg_color: str | None = None,
        text_color: str | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if bg_color:
            kwargs["bg_color"] = bg_color
        if text_color:
            kwargs["text_color"] = text_color
        return self.image_manager.generate(
            key,
            width,
            height,
            label=label,
            **kwargs,
        )

    def _get_og_image(self, site_content: Mapping[str, Any]) -> Any | None:
        existing = self.image_manager.get("HERO_IMAGE")
        if existing is not None:
            return existing
        company_name = self._string_or_none(site_content.get("company_name"))
        return self.image_manager.generate(
            "HERO_IMAGE",
            1920,
            1080,
            label=company_name,
        )

    def _configure_navigation(
        self,
        site: Site,
        navigation: Mapping[str, Any],
        pages: Mapping[str, Any],
    ) -> None:
        header_data = deepcopy(navigation.get("header", {}) or {})
        footer_data = deepcopy(navigation.get("footer", {}) or {})

        self._resolve_page_links(header_data, pages)
        self._resolve_page_links(footer_data, pages)

        header = HeaderNavigation.for_site(site)
        for field in HEADER_FIELDS:
            if field in header_data:
                setattr(header, field, header_data[field])
        header.save()

        footer = FooterNavigation.for_site(site)
        for field in FOOTER_FIELDS:
            if field in footer_data:
                setattr(footer, field, footer_data[field])
        footer.save()

    def _resolve_page_links(self, data: Any, pages: Mapping[str, Any]) -> None:
        if isinstance(data, list):
            for item in data:
                self._resolve_page_links(item, pages)
            return
        if not isinstance(data, dict):
            return

        link_type = data.get("link_type")
        if link_type == "page":
            page_value = data.get("page")
            resolved = self._resolve_page_reference(page_value, pages)
            data["page"] = resolved

        for value in data.values():
            self._resolve_page_links(value, pages)

    def _resolve_page_reference(self, value: Any, pages: Mapping[str, Any]) -> int:
        page_id = self._resolve_page_id(value)
        if page_id is not None:
            return page_id
        if isinstance(value, str):
            page = pages.get(value)
            if page is None:
                raise SeederContentError(f"Page not found for slug: {value}")
            resolved_id = self._resolve_page_id(page)
            if resolved_id is not None:
                return resolved_id
        raise SeederContentError("Page reference must be a slug or page id.")
