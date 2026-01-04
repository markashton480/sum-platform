"""
Seed the test project using YAML content profiles.

Usage:
    python manage.py seed sage-stone
    python manage.py seed sage-stone --clear
    python manage.py seed sage-stone --content-path ./content
    python manage.py seed sage-stone --dry-run
"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError, CommandParser

from seeders import SeedOrchestrator, SeedPlan
from seeders.exceptions import SeederError


class Command(BaseCommand):
    help = "Seed the test project from YAML content profiles."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "profile",
            nargs="?",
            help="Content profile to seed (e.g., sage-stone).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seeded content before re-seeding.",
        )
        parser.add_argument(
            "--content-path",
            default=None,
            help="Override the content directory (defaults to ./content).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate content and print the plan without writing.",
        )

    def handle(self, *args, **options) -> None:
        content_path = options.get("content_path")
        content_dir = Path(content_path).expanduser() if content_path else None
        orchestrator = SeedOrchestrator(content_dir=content_dir)

        profile = options.get("profile") or self._default_profile(orchestrator)
        if not profile:
            profiles = orchestrator.list_profiles()
            if profiles:
                raise CommandError(
                    "Missing profile. Available profiles: "
                    + ", ".join(sorted(profiles))
                )
            raise CommandError("Missing profile and no content profiles were found.")

        try:
            if options.get("dry_run"):
                plan = orchestrator.plan(profile)
                self._print_plan(plan)
                return
            orchestrator.seed(profile, clear=options.get("clear", False))
        except SeederError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"Seeded profile '{profile}'."))

    def _default_profile(self, orchestrator: SeedOrchestrator) -> str | None:
        """Return a sensible default profile, if one can be inferred.

        The test project ships with a sample profile called ``sage-stone``. When
        present, it's used as a convenient default to keep the command terse for
        local development and CI.
        """
        profiles = orchestrator.list_profiles()
        if "sage-stone" in profiles:
            return "sage-stone"
        if len(profiles) == 1:
            return profiles[0]
        return None

    def _print_plan(self, plan: SeedPlan) -> None:
        self.stdout.write(self.style.MIGRATE_HEADING("Seed plan"))
        self.stdout.write(self.style.NOTICE(f"  Profile: {plan.profile}"))
        self.stdout.write(self.style.NOTICE(f"  Content dir: {plan.content_dir}"))
        if plan.pages:
            self.stdout.write(self.style.SUCCESS("  Pages:"))
            for page in plan.pages:
                self.stdout.write(f"    - {page}")
        if plan.seeders:
            self.stdout.write(self.style.SUCCESS("  Seeders:"))
            for seeder in plan.seeders:
                self.stdout.write(f"    - {seeder}")
