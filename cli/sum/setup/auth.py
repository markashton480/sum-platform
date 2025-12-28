"""Superuser management for CLI setup."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cli.sum.exceptions import SuperuserError
from cli.sum.utils.django import DjangoCommandExecutor

logger = logging.getLogger(__name__)


@dataclass
class SuperuserResult:
    """Result of a superuser creation operation.

    Note:
        credentials_path points to .env.local regardless of the created flag.
        When created=False (user already existed), the file may not exist or
        may contain different credentials. Only trust credentials_path when
        created=True.
    """

    success: bool
    username: str
    credentials_path: Path
    created: bool  # True if newly created, False if already existed


def _escape_env_value(value: str) -> str:
    """Escape value for .env file (wrap in quotes if needed).

    Args:
        value: The raw value to escape.

    Returns:
        The value wrapped in quotes with proper escaping.
    """
    # Always quote to handle spaces, #, etc.
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


class SuperuserManager:
    """Manages Django superuser creation."""

    def __init__(
        self, django_executor: DjangoCommandExecutor, project_path: Path
    ) -> None:
        self.django = django_executor
        self.project_path = project_path

    def user_exists(self, username: str) -> bool:
        """Check if a specific username already exists.

        Args:
            username: The username to check.

        Returns:
            True if the user exists, False otherwise.

        Raises:
            SuperuserError: If the Django shell command fails or returns unexpected output.
        """
        # Use JSON serialization to safely pass username and prevent injection
        username_json = json.dumps(username)
        result = self.django.run_command(
            [
                "shell",
                "-c",
                f"import json; "
                f"from django.contrib.auth import get_user_model; "
                f"username = json.loads({username_json}); "
                f"print(get_user_model().objects.filter(username=username).exists())",
            ],
            check=False,
        )

        # Check return code before parsing output
        if result.returncode != 0:
            raise SuperuserError(
                f"Failed to check if user '{username}' exists: {result.stderr}"
            )

        # Validate output before returning
        output = result.stdout.strip().lower()
        if output not in {"true", "false"}:
            raise SuperuserError(
                f"Unexpected output when checking if user '{username}' exists: "
                f"{result.stdout!r}"
            )

        return output == "true"

    def create(
        self,
        username: str = "admin",
        email: str = "admin@example.com",
        password: str = "admin",
    ) -> SuperuserResult:
        """Create superuser and store credentials.

        Idempotency: If user already exists, skips both creation and .env.local
        writing to avoid creating a credentials file that doesn't match reality.

        Args:
            username: The username for the superuser (default: "admin").
            email: The email for the superuser (default: "admin@example.com").
            password: The password for the superuser (default: "admin").

        Raises:
            SuperuserError: If superuser creation fails.

        Returns:
            SuperuserResult with success=True, username, credentials path,
            and created flag indicating if the user was newly created.
        """
        # Check FIRST - don't attempt creation if user exists
        if self.user_exists(username):
            logger.info(f"User '{username}' already exists, skipping creation")
            return SuperuserResult(
                success=True,
                username=username,
                credentials_path=self.project_path / ".env.local",
                created=False,
            )

        # User doesn't exist - create it
        result = self.django.run_command(
            [
                "createsuperuser",
                "--noinput",
                "--username",
                username,
                "--email",
                email,
            ],
            env={"DJANGO_SUPERUSER_PASSWORD": password},
            check=False,
        )

        if result.returncode != 0:
            details = result.stderr or result.stdout or "Unknown error"
            raise SuperuserError(f"Creation failed: {details}")

        # Only write .env.local if we actually created the user
        self._save_credentials(username, email, password)

        return SuperuserResult(
            success=True,
            username=username,
            credentials_path=self.project_path / ".env.local",
            created=True,
        )

    def _save_credentials(self, username: str, email: str, password: str) -> None:
        """Save credentials to .env.local with proper escaping.

        Args:
            username: The superuser username.
            email: The superuser email.
            password: The superuser password.
        """
        env_local = self.project_path / ".env.local"
        date_str = datetime.now().strftime("%Y-%m-%d")

        content = f"""# .env.local
# Auto-generated by sum init on {date_str}
# DO NOT COMMIT THIS FILE
DJANGO_SUPERUSER_USERNAME={_escape_env_value(username)}
DJANGO_SUPERUSER_EMAIL={_escape_env_value(email)}
DJANGO_SUPERUSER_PASSWORD={_escape_env_value(password)}
"""
        # Write the file
        env_local.write_text(content)

        # Set restrictive permissions (owner read/write only) for security
        env_local.chmod(0o600)
