from __future__ import annotations

from dataclasses import dataclass


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

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.full and self.quick:
            raise ValueError("--full and --quick are mutually exclusive")
        if self.ci:
            self.no_prompt = True

    @classmethod
    def from_cli_args(cls, **kwargs: object) -> SetupConfig:
        """Create a SetupConfig from CLI arguments."""
        return cls(**kwargs)
