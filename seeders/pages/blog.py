"""Blog page seeder."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category

from seeders.base import BaseSeeder, SeederRegistry
from seeders.exceptions import SeederContentError
from seeders.pages.utils import (
    get_or_create_child_page,
    parse_datetime,
    resolve_streamfield_images,
)


@SeederRegistry.register("blog")
class BlogSeeder(BaseSeeder):
    """Seed blog index, categories, and posts from YAML content."""

    def __init__(self, *, home_page: Any, images: Mapping[str, Any]) -> None:
        self.home_page = home_page
        self.images = images
        self.blog_slug = "blog"
        self.category_slugs: list[str] = []

    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        if not isinstance(content, dict):
            raise SeederContentError("Blog page content must be a mapping")

        self.blog_slug = content.get("slug", self.blog_slug)
        categories_data = content.get("categories", [])
        if isinstance(categories_data, list):
            self.category_slugs = [
                slug
                for category in categories_data
                if isinstance(category, dict)
                if isinstance(slug := category.get("slug"), str) and slug
            ]
        if clear:
            self.clear()

        categories = self._seed_categories(categories_data)

        defaults: dict[str, Any] = {
            "title": content.get("title", "Blog"),
            "seo_title": content.get("seo_title", ""),
            "search_description": content.get("search_description", ""),
            "show_in_menus": content.get("show_in_menus", False),
            "intro": content.get("intro", ""),
            "posts_per_page": content.get("posts_per_page", 10),
        }

        blog_index, _ = get_or_create_child_page(
            self.home_page,
            page_class=BlogIndexPage,
            slug=self.blog_slug,
            defaults=defaults,
        )

        posts = content.get("posts", [])
        if not isinstance(posts, list):
            raise SeederContentError("Blog posts must be a list")
        for post_data in posts:
            if not isinstance(post_data, dict):
                raise SeederContentError("Blog post content must be a mapping")
            self._seed_post(blog_index, post_data, categories)

    def clear(self) -> None:
        blog_index = (
            BlogIndexPage.objects.child_of(self.home_page)
            .filter(slug=self.blog_slug)
            .first()
        )
        if blog_index is not None:
            BlogPostPage.objects.descendant_of(blog_index).delete()
            if not blog_index.get_descendants().exists():
                blog_index.delete()

        if self.category_slugs:
            Category.objects.filter(slug__in=self.category_slugs).delete()

    def _seed_categories(self, categories_data: Any) -> dict[str, Category]:
        if categories_data is None:
            return {}
        if not isinstance(categories_data, list):
            raise SeederContentError("Blog categories must be a list")

        categories: dict[str, Category] = {}
        for data in categories_data:
            if not isinstance(data, dict):
                raise SeederContentError("Blog category content must be a mapping")

            slug = data.get("slug")
            if not slug:
                raise SeederContentError("Blog category slug is required")

            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": data.get("name", slug),
                    "description": data.get("description", ""),
                },
            )
            if not created:
                category.name = data.get("name", category.name)
                category.description = data.get("description", category.description)
                category.save()
            categories[slug] = category
        return categories

    def _seed_post(
        self,
        blog_index: BlogIndexPage,
        post_data: dict[str, Any],
        categories: Mapping[str, Category],
    ) -> None:
        slug = post_data.get("slug")
        title = post_data.get("title", "Blog Post")
        if not slug:
            raise SeederContentError("Blog post slug is required")

        category_slug = post_data.get("category_slug")
        if not category_slug or category_slug not in categories:
            raise SeederContentError(f"Unknown blog category: {category_slug}")

        featured_image = self._resolve_featured_image(post_data)
        body = self._prepare_body(post_data)
        published_date = parse_datetime(
            post_data.get("published_date"), field=f"published_date:{slug}"
        )
        excerpt = post_data.get("excerpt", "")
        blog_title = blog_index.title or "Blog"
        site_name = self._resolve_site_name(blog_index)
        seo_title = f"{title} | {blog_title}"
        if site_name:
            seo_title = f"{seo_title} | {site_name}"

        defaults: dict[str, Any] = {
            "title": title,
            "category": categories[category_slug],
            "published_date": published_date,
            "featured_image": featured_image,
            "excerpt": excerpt,
            "author_name": post_data.get("author_name", ""),
            "seo_title": seo_title,
            "search_description": excerpt[:160],
            "body": body,
        }

        get_or_create_child_page(
            blog_index,
            page_class=BlogPostPage,
            slug=slug,
            defaults=defaults,
        )

    def _resolve_featured_image(self, post_data: Mapping[str, Any]) -> Any | None:
        image_key = post_data.get("image_key")
        if not image_key:
            return None
        image = self.images.get(image_key)
        if image is None:
            raise SeederContentError(f"Unknown blog image key: {image_key}")
        return image

    def _prepare_body(self, post_data: Mapping[str, Any]) -> list[dict[str, Any]]:
        raw_body = post_data.get("body", [])
        if not isinstance(raw_body, list):
            raise SeederContentError("Blog post body must be a list")
        body = [
            block.copy() if isinstance(block, dict) else block for block in raw_body
        ]

        image_key = post_data.get("image_key")
        for block in body:
            if not isinstance(block, dict):
                raise SeederContentError("Blog post block must be a mapping")
            if block.get("type") != "image_block":
                continue
            value = block.get("value") or {}
            if not isinstance(value, dict):
                continue
            if "image" not in value and image_key:
                updated_value = value.copy()
                updated_value["image"] = image_key
                block["value"] = updated_value
        return resolve_streamfield_images(body, self.images)

    def _resolve_site_name(self, blog_index: BlogIndexPage) -> str:
        site = blog_index.get_site()
        if site is None and hasattr(self.home_page, "get_site"):
            site = self.home_page.get_site()
        if site is None:
            return ""
        site_name = getattr(site, "site_name", "")
        if site_name is None:
            return ""
        return str(site_name).strip()
