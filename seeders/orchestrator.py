"""Orchestrate seeding across content profiles and registered seeders."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.db import transaction

from .base import BaseSeeder, SeederRegistry
from .content import ContentLoader, ProfileData
from .exceptions import SeederNotFoundError
from .images import IMAGE_MANIFEST, ImageManager, ImageSpec
from .site import SiteSeeder

DEFAULT_PAGE_ORDER = (
    "home",
    "about",
    "services",
    "portfolio",
    "blog",
    "contact",
    "legal",
)


@dataclass(frozen=True)
class SeedPlan:
    """Dry-run output for a seed profile."""

    profile: str
    content_dir: Path
    pages: list[str]
    seeders: list[str]


@dataclass(frozen=True)
class SeedResult:
    """Result data from a seeding run."""

    profile: str
    pages: dict[str, Any]


class SeedOrchestrator:
    """Coordinate the seeding flow for content profiles.

    Seeder classes can optionally declare ``content_loader`` and/or ``image_manager``
    keyword arguments in their constructor. When present, the orchestrator will
    inject its configured dependencies when instantiating the seeder.
    """

    def __init__(
        self,
        *,
        content_dir: Path | None = None,
        content_loader: ContentLoader | None = None,
        image_manager: ImageManager | None = None,
        image_manifest: Iterable[ImageSpec] | None = None,
        image_prefix: str = "SEED",
        page_order: Iterable[str] | None = None,
        page_seeder_classes: dict[str, type[BaseSeeder]] | None = None,
        site_seeder_class: type[BaseSeeder] = SiteSeeder,
        auto_discover: bool = True,
    ) -> None:
        self.content_loader = content_loader or ContentLoader(content_dir=content_dir)
        self.image_manager = image_manager or ImageManager(prefix=image_prefix)
        self.image_manifest = list(image_manifest or IMAGE_MANIFEST)
        self.page_order = list(page_order or DEFAULT_PAGE_ORDER)
        self.page_seeder_classes = (
            dict(page_seeder_classes) if page_seeder_classes is not None else None
        )
        self.site_seeder_class = site_seeder_class
        self.auto_discover = auto_discover

    def list_profiles(self) -> list[str]:
        return self.content_loader.list_profiles()

    def plan(self, profile: str) -> SeedPlan:
        data = self.content_loader.load_profile(profile)
        seeders = self._resolve_page_seeders(data)
        return SeedPlan(
            profile=profile,
            content_dir=self.content_loader.content_dir,
            pages=self._order_page_names(data.pages),
            seeders=[name for name, _ in seeders],
        )

    def seed(
        self,
        profile: str,
        *,
        clear: bool = False,
        dry_run: bool = False,
    ) -> SeedPlan | SeedResult:
        if dry_run:
            return self.plan(profile)

        data = self.content_loader.load_profile(profile)
        page_seeders = self._resolve_page_seeders(data)

        with transaction.atomic():
            images = self._generate_images()
            seeders = [(name, self._init_seeder(cls)) for name, cls in page_seeders]
            site_seeder = self._init_seeder(self.site_seeder_class)

            if clear:
                self._clear_seeders(seeders + [("site", site_seeder)])

            pages = self._seed_pages(
                profile=profile,
                data=data,
                seeders=seeders,
                images=images,
            )
            self._seed_site(
                profile=profile,
                data=data,
                site_seeder=site_seeder,
                pages=pages,
                images=images,
            )

        return SeedResult(profile=profile, pages=pages)

    def _discover_page_seeders(self) -> None:
        try:
            package = importlib.import_module("seeders.pages")
        except ModuleNotFoundError as exc:
            if exc.name == "seeders.pages":
                return
            raise
        if not hasattr(package, "__path__"):
            return
        for module in pkgutil.iter_modules(package.__path__):
            importlib.import_module(f"{package.__name__}.{module.name}")

    def _resolve_page_seeders(
        self, data: ProfileData
    ) -> list[tuple[str, type[BaseSeeder]]]:
        if self.page_seeder_classes is None:
            if self.auto_discover:
                self._discover_page_seeders()
            seeders = SeederRegistry.all()
        else:
            seeders = dict(self.page_seeder_classes)

        if not seeders:
            raise SeederNotFoundError("No page seeders registered.")

        ordered: list[tuple[str, type[BaseSeeder]]] = []
        remaining = dict(seeders)
        for name in self.page_order:
            if name in remaining:
                ordered.append((name, remaining.pop(name)))
        for name in sorted(remaining):
            ordered.append((name, remaining[name]))

        return ordered

    def _order_page_names(self, pages: Iterable[str]) -> list[str]:
        remaining = set(pages)
        ordered: list[str] = []
        for name in self.page_order:
            if name in remaining:
                ordered.append(name)
                remaining.remove(name)
        ordered.extend(sorted(remaining))
        return ordered

    def _init_seeder(self, seeder_class: type[BaseSeeder]) -> BaseSeeder:
        """Instantiate a seeder, injecting optional dependencies.

        Seeders may declare ``content_loader`` and/or ``image_manager`` keyword
        arguments in their constructor; when present, those objects are passed in
        automatically.
        """
        signature = inspect.signature(seeder_class)
        kwargs: dict[str, Any] = {}
        if "content_loader" in signature.parameters:
            kwargs["content_loader"] = self.content_loader
        if "image_manager" in signature.parameters:
            kwargs["image_manager"] = self.image_manager
        return seeder_class(**kwargs)

    def _generate_images(self) -> dict[str, Any]:
        if not self.image_manifest:
            return {}
        return self.image_manager.generate_manifest(self.image_manifest)

    def _clear_seeders(self, seeders: list[tuple[str, BaseSeeder]]) -> None:
        for _, seeder in reversed(seeders):
            seeder.clear()

    def _seed_pages(
        self,
        *,
        profile: str,
        data: ProfileData,
        seeders: list[tuple[str, BaseSeeder]],
        images: dict[str, Any],
    ) -> dict[str, Any]:
        pages: dict[str, Any] = {}
        for name, seeder in seeders:
            content = {
                "profile": profile,
                "site": data.site,
                "navigation": data.navigation,
                "pages_data": data.pages,
                "page_data": data.pages.get(name, {}),
                "pages": pages,
                "images": images,
            }
            # Clearing is coordinated by `_clear_seeders` before this runs. We
            # always pass `clear=False` to avoid double-clearing within a single
            # orchestrated run.
            result = seeder.seed(content, clear=False)
            self._collect_pages(name=name, seeder=seeder, result=result, pages=pages)
        return pages

    def _collect_pages(
        self,
        *,
        name: str,
        seeder: BaseSeeder,
        result: Any,
        pages: dict[str, Any],
    ) -> None:
        if isinstance(result, dict):
            pages.update(result)
        elif result is not None:
            pages[name] = result

        seeder_pages = getattr(seeder, "pages", None)
        if isinstance(seeder_pages, dict):
            pages.update(seeder_pages)

    def _seed_site(
        self,
        *,
        profile: str,
        data: ProfileData,
        site_seeder: BaseSeeder,
        pages: dict[str, Any],
        images: dict[str, Any],
    ) -> None:
        content = {
            "profile": profile,
            "site": data.site,
            "navigation": data.navigation,
            "pages": pages,
            "images": images,
        }
        # Clearing is coordinated by `_clear_seeders` before this runs. We always
        # pass `clear=False` to avoid double-clearing within a single run.
        site_seeder.seed(content, clear=False)
