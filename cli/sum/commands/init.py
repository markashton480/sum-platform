from __future__ import annotations

from types import ModuleType

from sum_cli.util import validate_project_name

from cli.sum.config import SetupConfig
from cli.sum.exceptions import SetupError
from cli.sum.setup.orchestrator import SetupOrchestrator
from cli.sum.setup.scaffold import DEFAULT_THEME_SLUG, scaffold_project
from cli.sum.utils.environment import detect_mode, get_clients_dir
from cli.sum.utils.output import OutputFormatter
from cli.sum.utils.prompts import PromptManager

click_module: ModuleType | None
try:
    import click as click_module
except ImportError:  # pragma: no cover - click is expected in the CLI runtime
    click_module = None

click: ModuleType | None = click_module


def _build_setup_config(
    *,
    prompts: PromptManager,
    full: bool,
    quick: bool,
    no_prompt: bool,
    ci: bool,
    skip_venv: bool,
    skip_migrations: bool,
    skip_seed: bool,
    skip_superuser: bool,
    run_server: bool,
    port: int,
    seed_preset: str | None,
    seed_site: str | None,
) -> SetupConfig:
    config = SetupConfig.from_cli_args(
        full=full,
        quick=quick,
        no_prompt=no_prompt,
        ci=ci,
        skip_venv=skip_venv,
        skip_migrations=skip_migrations,
        skip_seed=skip_seed,
        skip_superuser=skip_superuser,
        run_server=run_server,
        port=port,
        seed_preset=seed_preset,
        seed_site=seed_site,
    )

    if prompts.no_prompt or prompts.ci:
        return config

    if not config.skip_venv:
        config.skip_venv = not prompts.confirm(
            "Setup Python environment?", default=True
        )

    if config.full:
        if not config.skip_migrations:
            config.skip_migrations = not prompts.confirm(
                "Run database migrations?", default=True
            )
        if not config.skip_seed:
            config.skip_seed = not prompts.confirm(
                "Seed initial content?", default=True
            )
        if not config.skip_superuser:
            if prompts.confirm("Create superuser?", default=True):
                config.superuser_username = prompts.text(
                    "Username", default=config.superuser_username
                )
                config.superuser_email = prompts.text(
                    "Email", default=config.superuser_email
                )
                config.superuser_password = prompts.text(
                    "Password", default=config.superuser_password
                )
            else:
                config.skip_superuser = True

        if not config.run_server:
            config.run_server = prompts.confirm(
                "Start development server?", default=True
            )

    return config


def run_init(
    project_name: str,
    *,
    full: bool = False,
    quick: bool = False,
    no_prompt: bool = False,
    ci: bool = False,
    skip_venv: bool = False,
    skip_migrations: bool = False,
    skip_seed: bool = False,
    skip_superuser: bool = False,
    run_server: bool = False,
    port: int = 8000,
    preset: str | None = None,
    seed_site: str | None = None,
) -> int:
    try:
        naming = validate_project_name(project_name)
    except ValueError as exc:
        OutputFormatter.error(str(exc))
        return 1

    if full and quick:
        OutputFormatter.error("--full and --quick are mutually exclusive")
        return 1

    try:
        clients_dir = get_clients_dir()
    except FileNotFoundError as exc:
        OutputFormatter.error(str(exc))
        return 1

    project_path = clients_dir / naming.slug
    mode = detect_mode(project_path)

    if not full and not quick:
        try:
            project_path = scaffold_project(
                project_name=naming.slug,
                clients_dir=clients_dir,
                theme_slug=DEFAULT_THEME_SLUG,
            )
        except SetupError as exc:
            OutputFormatter.error(str(exc))
            return 1

        OutputFormatter.success(f"Project scaffolded at {project_path}")
        print("Next steps:")
        print(f"  cd {project_path}")
        print("  python -m venv .venv")
        print("  source .venv/bin/activate")
        print("  pip install -r requirements.txt")
        print("  python manage.py migrate")
        return 0

    prompts = PromptManager(no_prompt=no_prompt or ci, ci=ci)
    try:
        config = _build_setup_config(
            prompts=prompts,
            full=full,
            quick=quick,
            no_prompt=no_prompt,
            ci=ci,
            skip_venv=skip_venv,
            skip_migrations=skip_migrations,
            skip_seed=skip_seed,
            skip_superuser=skip_superuser,
            run_server=run_server,
            port=port,
            seed_preset=preset,
            seed_site=seed_site,
        )
    except ValueError as exc:
        OutputFormatter.error(str(exc))
        return 1

    orchestrator = SetupOrchestrator(project_path, mode)
    try:
        result = orchestrator.run_full_setup(config)
    except SetupError as exc:
        OutputFormatter.error(str(exc))
        return 1

    summary_data = {
        "location": str(result.project_path),
        "url": result.url,
        "credentials_path": (
            str(result.credentials_path) if result.credentials_path else "N/A"
        ),
    }
    if result.credentials_path:
        summary_data["username"] = config.superuser_username
        summary_data["password"] = config.superuser_password

    OutputFormatter.summary(project_name=naming.slug, data=summary_data)
    return 0


def _init_command(
    project_name: str,
    full: bool,
    quick: bool,
    no_prompt: bool,
    ci: bool,
    skip_venv: bool,
    skip_migrations: bool,
    skip_seed: bool,
    skip_superuser: bool,
    run_server: bool,
    port: int,
    preset: str | None,
    seed_site: str | None,
) -> None:
    """Initialize a new client project."""
    result = run_init(
        project_name,
        full=full,
        quick=quick,
        no_prompt=no_prompt,
        ci=ci,
        skip_venv=skip_venv,
        skip_migrations=skip_migrations,
        skip_seed=skip_seed,
        skip_superuser=skip_superuser,
        run_server=run_server,
        port=port,
        preset=preset,
        seed_site=seed_site,
    )
    if result != 0:
        raise SystemExit(result)


def _missing_click(*_args: object, **_kwargs: object) -> None:
    raise RuntimeError("click is required to use the init command")


if click is None:
    init = _missing_click
else:

    @click.command()
    @click.argument("project_name")
    @click.option(
        "--full",
        is_flag=True,
        help="Run complete setup (venv, deps, migrations, seed, superuser)",
    )
    @click.option(
        "--quick",
        is_flag=True,
        help="Scaffold + venv + deps only (no database operations)",
    )
    @click.option(
        "--no-prompt",
        is_flag=True,
        help="Non-interactive mode, use defaults",
    )
    @click.option(
        "--ci",
        is_flag=True,
        help="CI mode (non-interactive, optimized output)",
    )
    @click.option(
        "--skip-venv",
        is_flag=True,
        help="Skip virtualenv creation",
    )
    @click.option(
        "--skip-migrations",
        is_flag=True,
        help="Skip database migrations",
    )
    @click.option(
        "--skip-seed",
        is_flag=True,
        help="Skip content seeding",
    )
    @click.option(
        "--skip-superuser",
        is_flag=True,
        help="Skip superuser creation",
    )
    @click.option(
        "--run",
        "run_server",
        is_flag=True,
        help="Start development server after setup",
    )
    @click.option(
        "--port",
        default=8000,
        type=int,
        show_default=True,
        help="Development server port",
    )
    @click.option(
        "--preset",
        default=None,
        help="Content preset name (future)",
    )
    @click.option(
        "--seed-site",
        default=None,
        type=click.Choice(["sage-and-stone"], case_sensitive=False),
        help="Seed site content (supported: sage-and-stone)",
    )
    def _click_init(
        project_name: str,
        full: bool,
        quick: bool,
        no_prompt: bool,
        ci: bool,
        skip_venv: bool,
        skip_migrations: bool,
        skip_seed: bool,
        skip_superuser: bool,
        run_server: bool,
        port: int,
        preset: str | None,
        seed_site: str | None,
    ) -> None:
        _init_command(
            project_name,
            full=full,
            quick=quick,
            no_prompt=no_prompt,
            ci=ci,
            skip_venv=skip_venv,
            skip_migrations=skip_migrations,
            skip_seed=skip_seed,
            skip_superuser=skip_superuser,
            run_server=run_server,
            port=port,
            preset=preset,
            seed_site=seed_site,
        )

    init = _click_init
