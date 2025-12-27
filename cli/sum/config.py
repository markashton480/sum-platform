from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, Unpack


class SetupConfigArgs(TypedDict, total=False):
    full: bool
    quick: bool
    ci: bool
    no_prompt: bool
    skip_venv: bool
    skip_migrations: bool
    skip_seed: bool
    skip_superuser: bool
    run_server: bool
    port: int
    superuser_username: str
    superuser_email: str
    superuser_password: str
    seed_preset: str | None
    theme_slug: str


@dataclass
class SetupConfig:
    """Configuration for setup orchestration."""

    full: bool = False
    quick: bool = False
    ci: bool = False
    no_prompt: bool = False

    skip_venv: bool = False
    skip_migrations: bool = False
    skip_seed: bool = False
    skip_superuser: bool = False

    run_server: bool = False
    port: int = 8000

    superuser_username: str = "admin"
    superuser_email: str = "admin@example.com"
    superuser_password: str = "admin"

    seed_preset: str | None = None
    theme_slug: str = "theme_a"

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.full and self.quick:
            raise ValueError("--full and --quick are mutually exclusive")
        if self.ci:
            self.no_prompt = True

    @classmethod
    def from_cli_args(cls, **kwargs: Unpack[SetupConfigArgs]) -> SetupConfig:
        """Create a SetupConfig from CLI arguments."""
        return cls(**kwargs)
