# Subtask

**Title:** `CLI-007: Enhanced Init Command (--full, --quick, --ci, --skip-*, --run)`

---

## Parent

**Work Order:** #WO-CLI-V2 — CLI v2 Enhanced Architecture (v2.0.0)

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-v2/007-enhanced-init` | `feature/cli-v2` |

```bash
git checkout feature/cli-v2
git pull origin feature/cli-v2
git checkout -b feature/cli-v2/007-enhanced-init
git push -u origin feature/cli-v2/007-enhanced-init
```

---

## Deliverable

This subtask will deliver:

- `cli/sum/commands/init.py` — Enhanced with all new flags and orchestrator integration
- `cli/tests/test_init.py` — Updated tests for new functionality

---

## Boundaries

### Do

- Add Click options to `sum init` command:
  - `--full` — Run complete setup
  - `--quick` — Scaffold + venv + deps only (no DB operations)
  - `--no-prompt` — Non-interactive mode, use defaults
  - `--ci` — CI mode (non-interactive, optimized output)
  - `--skip-venv` — Skip virtualenv creation
  - `--skip-migrations` — Skip database migrations
  - `--skip-seed` — Skip homepage seeding
  - `--skip-superuser` — Skip superuser creation
  - `--run` — Start development server after setup
  - `--port` — Development server port (default: 8000)
  - `--preset` — Content preset name (future)
- **Init is a thin wrapper:** Build config, resolve paths, call `SetupOrchestrator`
- Use `get_clients_dir()` and `find_monorepo_root()` from #CLI-001 for path resolution (works from any directory)
- Integrate with `SetupOrchestrator` from #CLI-006 (orchestrator owns all steps)
- Integrate with `PromptManager` from #CLI-001 for interactive flow
- Display success summary using `OutputFormatter.summary()`
- Maintain backward compatibility: bare `sum init project` still just scaffolds
- Add mutual exclusion check for `--full` and `--quick`

### Do NOT

- ❌ Do not implement `sum run` command — owned by #CLI-008
- ❌ Do not implement enhanced `sum check` — owned by #CLI-008
- ❌ Do not modify `cli.py` command registration (if already exists)

---

## Acceptance Criteria

- [ ] `sum init project` (no flags) scaffolds only — backward compatible
- [ ] `sum init project --full` runs complete 8-step setup
- [ ] `sum init project --quick` runs steps 1-4 only (no DB operations)
- [ ] `sum init project --full --ci` runs non-interactively with defaults
- [ ] `sum init project --full --no-prompt` runs non-interactively with defaults
- [ ] `sum init project --full --skip-venv` skips virtualenv creation
- [ ] `sum init project --full --skip-migrations` skips migrations
- [ ] `sum init project --full --skip-seed` skips homepage seeding
- [ ] `sum init project --full --skip-superuser` skips superuser creation
- [ ] `sum init project --full --run` starts server after setup
- [ ] Interactive prompts appear for each step when not in --ci/--no-prompt mode:
  - "Setup Python environment? (Y/n)"
  - "Run database migrations? (Y/n)"
  - "Seed initial homepage? (Y/n)"
  - "Create superuser? (Y/n)"
  - "Start development server? (Y/n)"
- [ ] Superuser credentials can be customized via prompts
- [ ] Success summary displays project location, URL, and credentials path
- [ ] All flags have proper Click help text
- [ ] `make lint && make test` passes

---

## Test Commands

```bash
make lint
make test

# Specific tests
python -m pytest tests/test_init.py -v

# Integration tests
sum init test-project --full --ci
cd clients/test-project
ls -la .venv/
cat .env.local
```

---

## Files Expected to Change

```
cli/sum/commands/init.py           # Modified: add flags and orchestrator
cli/tests/test_init.py             # Modified: add new flag tests
```

---

## Dependencies

**Depends On:**
- [ ] #CLI-001 must be merged first (PromptManager, OutputFormatter)
- [ ] #CLI-002 must be merged first (SetupConfig)
- [ ] #CLI-006 must be merged first (SetupOrchestrator)

**Blocks:**
- #CLI-008 Run Command & Enhanced Check is waiting for this

---

## Risk

**Level:** Medium

**Why:**
- Many integration points with orchestrator and utilities
- Complex flag interaction logic
- Must preserve backward compatibility with v1 behavior
- Primary user-facing interface for CLI v2

---

## Labels

- [ ] `type:task`
- [ ] `agent:*`
- [ ] `component:cli`
- [ ] `risk:medium`
- [ ] Milestone: `v2.0.0`

---

## Project Fields

- [ ] Agent: (assigned)
- [ ] Model Planned: (selected)
- [ ] Component: cli
- [ ] Change Type: feat
- [ ] Risk: medium
- [ ] Release: `v2.0.0`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied
- [ ] Parent Work Order updated

---

## Commit Message

```
feat(cli): enhance init command with --full, --quick, --ci flags

- Add --full flag for complete setup (venv, deps, migrate, seed, superuser)
- Add --quick flag for scaffold + venv + deps only
- Add --ci and --no-prompt flags for non-interactive mode
- Add --skip-* flags for granular control
- Add --run flag to start server after setup
- Integrate SetupOrchestrator for setup flow
- Add interactive prompts for each setup step
- Display success summary with project info

Closes #CLI-007
```

---

## Implementation Notes

### Enhanced Click Command

```python
"""
File: cli/sum/commands/init.py
Name: init command
Purpose: Initialize new client projects with optional full setup
Dependencies: click, sum.setup.orchestrator, sum.utils.prompts, sum.config
Family: Main CLI command — thin wrapper around SetupOrchestrator
"""

from pathlib import Path
from typing import Optional

import click

from sum.config import SetupConfig
from sum.setup.orchestrator import SetupOrchestrator
from sum.utils.environment import detect_mode, get_clients_dir
from sum.utils.output import OutputFormatter
from sum.utils.prompts import PromptManager


@click.command()
@click.argument('project_name')
@click.option('--full', is_flag=True, help='Run complete setup (venv, deps, migrations, seed, superuser)')
@click.option('--quick', is_flag=True, help='Scaffold + venv + deps only (no database operations)')
@click.option('--no-prompt', is_flag=True, help='Non-interactive mode, use all defaults')
@click.option('--ci', is_flag=True, help='CI mode (non-interactive, optimized output)')
@click.option('--skip-venv', is_flag=True, help='Skip virtualenv creation')
@click.option('--skip-migrations', is_flag=True, help='Skip database migrations')
@click.option('--skip-seed', is_flag=True, help='Skip homepage seeding')
@click.option('--skip-superuser', is_flag=True, help='Skip superuser creation')
@click.option('--run', 'run_server', is_flag=True, help='Start development server after setup')
@click.option('--port', default=8000, type=int, help='Development server port (default: 8000)')
@click.option('--preset', default=None, help='Content preset name')
def init(
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
    preset: Optional[str]
) -> None:
    """Initialize a new client project.
    
    Examples:
    
        sum init acme-kitchens           # Scaffold only (v1 behavior)
        
        sum init acme-kitchens --full    # Complete setup
        
        sum init acme-kitchens --quick   # Scaffold + venv + deps
        
        sum init acme-kitchens --full --ci  # CI mode, non-interactive
    """
    # Validate mutual exclusion
    if full and quick:
        raise click.UsageError("--full and --quick are mutually exclusive")
    
    click.echo(f"🚀 Initializing project: {project_name}")
    
    # Resolve project path using monorepo-aware helper (works from any directory)
    clients_dir = get_clients_dir()
    project_path = clients_dir / project_name
    mode = detect_mode()
    
    # If not --full or --quick, just scaffold (v1 behavior)
    if not full and not quick:
        _scaffold_only(project_name, project_path)
        return
    
    # Create prompt manager
    prompts = PromptManager(no_prompt=no_prompt or ci, ci=ci)
    
    # Build config (with interactive prompts if applicable)
    config = _build_config_interactive(
        prompts=prompts,
        full=full,
        quick=quick,
        skip_venv=skip_venv,
        skip_migrations=skip_migrations,
        skip_seed=skip_seed,
        skip_superuser=skip_superuser,
        run_server=run_server,
        port=port,
        seed_preset=preset
    )
    
    # Run orchestrated setup (orchestrator owns ALL steps)
    orchestrator = SetupOrchestrator(project_path, mode)
    result = orchestrator.run_full_setup(config)
    
    # Display summary
    OutputFormatter.summary(
        project_name=project_name,
        data={
            'location': str(result.project_path),
            'relative_path': f"clients/{project_name}",
            'url': result.url,
            'username': config.superuser_username,
            'password': config.superuser_password,
            'credentials_path': str(result.credentials_path) if result.credentials_path else 'N/A'
        }
    )


def _scaffold_only(project_name: str, project_path: Path) -> None:
    """Scaffold project without full setup (v1 backward compatibility)."""
    # ... existing scaffolding logic ...
    
    click.echo(f"\n✅ Project scaffolded at {project_path}")
    click.echo("\nNext steps:")
    click.echo(f"  cd clients/{project_name}")
    click.echo("  python -m venv .venv")
    click.echo("  source .venv/bin/activate")
    click.echo("  pip install -r requirements.txt")
    click.echo("  python manage.py migrate")


def _build_config_interactive(
    prompts: PromptManager,
    full: bool,
    quick: bool,
    skip_venv: bool,
    skip_migrations: bool,
    skip_seed: bool,
    skip_superuser: bool,
    run_server: bool,
    port: int,
    seed_preset: Optional[str]
) -> SetupConfig:
    """Build SetupConfig with interactive prompts if needed."""
    
    config = SetupConfig(
        full=full,
        quick=quick,
        skip_venv=skip_venv,
        skip_migrations=skip_migrations,
        skip_seed=skip_seed,
        skip_superuser=skip_superuser,
        run_server=run_server,
        port=port,
        seed_preset=seed_preset
    )
    
    # If --full and interactive, ask for confirmation of each step
    if full and not prompts.ci and not prompts.no_prompt:
        if not config.skip_migrations:
            config.skip_migrations = not prompts.confirm("Run database migrations?", default=True)
        
        if not config.skip_seed:
            config.skip_seed = not prompts.confirm("Seed initial homepage?", default=True)
        
        if not config.skip_superuser:
            if prompts.confirm("Create superuser?", default=True):
                config.superuser_username = prompts.text("Username", default="admin")
                config.superuser_email = prompts.text("Email", default="admin@example.com")
                config.superuser_password = prompts.text("Password", default="admin")
            else:
                config.skip_superuser = True
        
        config.run_server = prompts.confirm("Start development server?", default=True)
    
    return config
```

### Interactive Flow Example

```
🚀 Initializing project: acme-kitchens

[1/8] Scaffolding project structure... ✅
[2/8] Validating structure... ✅
[3/8] Creating virtualenv (.venv)... ✅
[4/8] Installing dependencies... ⏳ (this may take a minute)
[4/8] Installing dependencies... ✅

Run database migrations? (Y/n): y
[5/8] Running migrations... ✅

Seed initial homepage? (Y/n): y
[6/8] Creating homepage... ✅

Create superuser? (Y/n): y
Username [admin]: admin
Email [admin@example.com]: 
Password [admin]: 
[7/8] Creating superuser... ✅

Start development server? (Y/n): y
[8/8] Starting server... ✅

============================================================
🎉 Project 'acme-kitchens' is ready!
============================================================

📍 Location: /path/to/clients/acme-kitchens
🔗 URL: http://127.0.0.1:8000/
👤 Admin: admin / admin
📝 Credentials: clients/acme-kitchens/.env.local

Next steps:
  cd clients/acme-kitchens
  source .venv/bin/activate
  python manage.py runserver  # if not running

Or use:
  sum run acme-kitchens
```
