"""
Name: Seed Orchestrator Tests
Path: tests/seeders/test_orchestrator.py
Purpose: Verify orchestration planning and dry-run behavior.
"""

from __future__ import annotations

from pathlib import Path

from seeders.base import BaseSeeder
from seeders.orchestrator import SeedOrchestrator, SeedPlan


class DummyImageManager:
    def generate_manifest(self, manifest) -> dict:
        return {}


class HomeSeeder(BaseSeeder):
    def seed(self, content, clear: bool = False):
        return {"home": "home"}

    def clear(self) -> None:
        return None


class AboutSeeder(BaseSeeder):
    def seed(self, content, clear: bool = False):
        return {"about": "about"}

    def clear(self) -> None:
        return None


def _write_profile(content_dir: Path, profile: str = "demo") -> None:
    profile_dir = content_dir / profile
    pages_dir = profile_dir / "pages"
    pages_dir.mkdir(parents=True)

    (profile_dir / "site.yaml").write_text(
        'brand:\n  company_name: "Test Co"\n',
        encoding="utf-8",
    )
    (profile_dir / "navigation.yaml").write_text(
        "footer:\n  tagline: Test\n",
        encoding="utf-8",
    )
    (pages_dir / "home.yaml").write_text('title: "Home"\nslug: "home"\n')
    (pages_dir / "about.yaml").write_text('title: "About"\nslug: "about"\n')


def test_seed_orchestrator_plan_orders_seeders(tmp_path) -> None:
    content_dir = tmp_path / "content"
    _write_profile(content_dir)

    orchestrator = SeedOrchestrator(
        content_dir=content_dir,
        image_manager=DummyImageManager(),
        image_manifest=[],
        page_seeder_classes={"about": AboutSeeder, "home": HomeSeeder},
    )

    plan = orchestrator.plan("demo")

    assert plan.seeders == ["home", "about"]
    assert plan.pages == ["home", "about"]


def test_seed_orchestrator_dry_run_returns_plan(tmp_path) -> None:
    content_dir = tmp_path / "content"
    _write_profile(content_dir)

    orchestrator = SeedOrchestrator(
        content_dir=content_dir,
        image_manager=DummyImageManager(),
        image_manifest=[],
        page_seeder_classes={"home": HomeSeeder},
    )

    plan = orchestrator.seed("demo", dry_run=True)

    assert isinstance(plan, SeedPlan)
