"""Content seeding for CLI setup."""

from __future__ import annotations

import re
from dataclasses import dataclass

from cli.sum.exceptions import SeedError
from cli.sum.utils.django import DjangoCommandExecutor


@dataclass
class SeedResult:
    """Result of a seed operation."""

    success: bool
    page_id: int | None = None


class ContentSeeder:
    """Seeds initial Wagtail content."""

    def __init__(self, django_executor: DjangoCommandExecutor) -> None:
        self.django = django_executor

    def seed_homepage(self, preset: str | None = None) -> SeedResult:
        """Create initial homepage.

        Args:
            preset: Optional theme preset to use for seeding.

        Raises:
            SeedError: If seeding fails.

        Returns:
            SeedResult with success=True and optional page_id.
        """
        cmd = ["seed_homepage"]
        if preset:
            cmd.extend(["--preset", preset])

        result = self.django.run_command(cmd, check=False)

        if result.returncode != 0:
            # Check if it's just "already exists" warning
            if "already exists" in result.stdout.lower():
                return SeedResult(success=True)
            raise SeedError(f"Seeding failed: {result.stderr}")

        return SeedResult(success=True, page_id=self._extract_page_id(result.stdout))

    def seed_sage_stone(self) -> SeedResult:
        """Run the Sage & Stone site seeder.

        Raises:
            SeedError: If seeding fails.

        Returns:
            SeedResult with success=True.
        """
        result = self.django.run_command(["seed_sage_stone"], check=False)

        if result.returncode != 0:
            details = result.stderr or result.stdout
            raise SeedError(f"Seeding failed: {details}")

        return SeedResult(success=True)

    def check_homepage_exists(self) -> bool:
        """Check if homepage is already created.

        Returns:
            True if homepage exists, False otherwise.

        Raises:
            SeedError: If the Django shell command fails.
        """
        result = self.django.run_command(
            [
                "shell",
                "-c",
                (
                    "from home.models import HomePage; "
                    "print(HomePage.objects.filter(slug='home').exists())"
                ),
            ],
            check=False,
        )

        if result.returncode != 0:
            raise SeedError(
                f"Failed to check homepage existence: {result.stderr or result.stdout}"
            )

        return result.stdout.strip().lower() == "true"

    def _extract_page_id(self, output: str) -> int | None:
        """Extract page ID from command output.

        Args:
            output: The command output to parse.

        Returns:
            The extracted page ID or None if not found.
        """
        match = re.search(r"ID: (\d+)", output)
        return int(match.group(1)) if match else None
