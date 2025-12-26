# Subtask

**Title:** `CLI-008: Run Command & Enhanced Check (run.py, validation.py, check.py)`

---

## Parent

**Work Order:** #WO-CLI-V2 — CLI v2 Enhanced Architecture (v2.0.0)

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-v2/008-run-check` | `feature/cli-v2` |

```bash
git checkout feature/cli-v2
git pull origin feature/cli-v2
git checkout -b feature/cli-v2/008-run-check
git push -u origin feature/cli-v2/008-run-check
```

---

## Deliverable

This subtask will deliver:

- `cli/sum/commands/run.py` — New `sum run` command
- `cli/sum/utils/validation.py` — Enhanced validation checks
- `cli/sum/commands/check.py` — Enhanced with new validations
- `cli/tests/test_run.py` — Unit tests for run command
- `cli/tests/test_validation.py` — Unit tests for validation
- Updated `cli/sum/cli.py` — Register new `run` command

---

## Boundaries

### Do

- Implement `sum run [PROJECT]` command with:
  - Auto-detection of virtualenv and activation
  - Correct Python executable resolution per mode
  - Port conflict handling (try 8000, 8001, 8002...)
  - Clear startup message showing venv path, mode, Python version
  - `--port` option for custom port
- Implement enhanced validation checks in `utils/validation.py`:
  - `check_venv_exists()` — Verify `.venv` directory exists
  - `check_packages_installed()` — Verify key packages in venv
  - `check_env_local()` — Verify `.env.local` exists (if superuser created)
  - `check_migrations_applied()` — Query `django_migrations` table
  - `check_homepage_exists()` — Verify homepage is set as site root
- Enhance `sum check` command to include new validation checks
- Display clear `[OK]` / `[FAIL]` / `[SKIP]` status for each check
- Register `run` command in `cli.py`

### Do NOT

- ❌ Do not modify init command logic — owned by #CLI-007
- ❌ Do not modify setup modules — owned by previous tasks
- ❌ Do not implement advanced port scanning (simple sequential is fine)

---

## Acceptance Criteria

- [ ] `sum run` from within client project starts development server
- [ ] `sum run project-name` from anywhere in monorepo starts server for that project
- [ ] `sum run --port 8001` uses specified port
- [ ] Port conflict: if 8000 in use, tries 8001, 8002, etc.
- [ ] Startup message shows:
  ```
  🚀 Starting acme-kitchens...
  
  Using virtualenv: /path/to/clients/acme-kitchens/.venv
  Mode: monorepo
  Python: /path/to/.venv/bin/python3.12
  
  Django version 5.2.1, using settings 'acme_kitchens.settings.local'
  Starting development server at http://127.0.0.1:8000/
  ```
- [ ] `sum check` includes new validation checks:
  - `[OK] Virtualenv: .venv exists with required packages`
  - `[OK] Credentials: .env.local found`
  - `[OK] Database: Migrations up to date`
  - `[OK] Homepage: Set as site root page`
- [ ] `sum check` shows `[SKIP]` for optional checks when not applicable
- [ ] All validation checks have clear error messages with remediation steps
- [ ] `make lint && make test` passes

---

## Test Commands

```bash
make lint
make test

# Specific tests
python -m pytest tests/test_run.py -v
python -m pytest tests/test_validation.py -v
python -m pytest tests/test_check.py -v

# Integration tests
cd clients/test-project
sum run --port 8001 &
curl http://127.0.0.1:8001/
sum check
```

---

## Files Expected to Change

```
cli/sum/commands/run.py            # New
cli/sum/utils/validation.py        # New
cli/sum/utils/__init__.py          # Modified: add validation exports
cli/sum/commands/check.py          # Modified: add new checks
cli/sum/cli.py                     # Modified: register run command
cli/tests/test_run.py              # New
cli/tests/test_validation.py       # New
cli/tests/test_check.py            # Modified: add new check tests
```

---

## Dependencies

**Depends On:**
- [ ] #CLI-001 must be merged first (OutputFormatter)
- [ ] #CLI-002 must be merged first (DjangoCommandExecutor, ExecutionMode)
- [ ] #CLI-003 must be merged first (VenvManager)
- [ ] #CLI-007 must be merged first (init command complete)

**Blocks:**
- None — this is the final task

---

## Risk

**Level:** Low

**Why:**
- Additive features, not modifying critical paths
- Port conflict handling is simple sequential logic
- Validation checks are read-only operations
- No complex state management

---

## Labels

- [ ] `type:task`
- [ ] `agent:*`
- [ ] `component:cli`
- [ ] `risk:low`
- [ ] Milestone: `v2.0.0`

---

## Project Fields

- [ ] Agent: (assigned)
- [ ] Model Planned: (selected)
- [ ] Component: cli
- [ ] Change Type: feat
- [ ] Risk: low
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
feat(cli): add sum run command and enhance sum check

- Add sum run command for starting development server
- Handle port conflicts with sequential fallback
- Add enhanced validation checks for venv, packages, migrations, homepage
- Update sum check with new validation checks
- Show clear [OK]/[FAIL]/[SKIP] status for each check

Closes #CLI-008
```

---

## Implementation Notes

### Run Command

```python
"""
File: cli/sum/commands/run.py
Name: run command
Purpose: Start development server with auto-detection
Dependencies: click, subprocess, socket, sum.utils.environment, sum.setup.venv
Family: Main CLI command — convenience wrapper for starting server
"""

import os
import socket
import subprocess
from pathlib import Path
from typing import Optional

import click

from sum.utils.environment import detect_mode, get_clients_dir, find_monorepo_root, ExecutionMode
from sum.setup.venv import VenvManager


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts}")


def resolve_project_path(project: Optional[str]) -> Path:
    """Resolve project path from name or current directory.
    
    Uses monorepo-aware path resolution — works from any directory.
    """
    if project:
        # Look in clients directory (using monorepo-aware helper)
        try:
            clients_dir = get_clients_dir()
            project_path = clients_dir / project
            if project_path.exists():
                return project_path
        except FileNotFoundError:
            pass
        raise click.ClickException(f"Project not found: {project}")
    
    # Check if we're in a client project (has manage.py)
    cwd = Path.cwd()
    if (cwd / "manage.py").exists():
        return cwd
    
    raise click.ClickException(
        "Not in a project directory. Either cd into a project or specify project name."
    )


@click.command()
@click.argument('project', required=False)
@click.option('--port', default=8000, type=int, help='Development server port (default: 8000)')
def run(project: Optional[str], port: int) -> None:
    """Start development server for a project.
    
    Examples:
    
        cd clients/acme-kitchens && sum run    # From within project
        
        sum run acme-kitchens                   # From anywhere in monorepo
        
        sum run --port 8001                     # Custom port
    """
    project_path = resolve_project_path(project)
    project_name = project_path.name
    mode = detect_mode()
    
    venv_manager = VenvManager()
    
    # Verify venv exists
    if not venv_manager.exists(project_path):
        raise click.ClickException(
            f"Virtualenv not found at {project_path / '.venv'}. "
            "Run 'sum init --full' or create manually."
        )
    
    python_exe = venv_manager.get_python_executable(project_path)
    
    # Find available port
    actual_port = find_available_port(port)
    if actual_port != port:
        click.echo(f"⚠️  Port {port} in use, using {actual_port} instead")
    
    # Display startup message
    click.echo(f"🚀 Starting {project_name}...")
    click.echo()
    click.echo(f"Using virtualenv: {project_path / '.venv'}")
    click.echo(f"Mode: {mode.value}")
    click.echo(f"Python: {python_exe}")
    click.echo()
    
    # Build environment
    env = os.environ.copy()
    if mode == ExecutionMode.MONOREPO:
        # APPEND core/ to PYTHONPATH (don't replace)
        repo_root = find_monorepo_root(project_path)
        if repo_root:
            core_path = repo_root / "core"
            existing = env.get('PYTHONPATH', '')
            if existing:
                env['PYTHONPATH'] = f"{core_path}{os.pathsep}{existing}"
            else:
                env['PYTHONPATH'] = str(core_path)
    
    # Start server
    try:
        subprocess.run(
            [str(python_exe), "manage.py", "runserver", f"127.0.0.1:{actual_port}"],
            cwd=project_path,
            env=env
        )
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped")
```

### Validation Utilities

```python
"""
File: cli/sum/utils/validation.py
Name: validation utilities
Purpose: Enhanced validation checks for project state
Dependencies: sum.utils.django, sum.utils.environment, sum.setup.venv
Family: Used by check command
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sum.utils.django import DjangoCommandExecutor
from sum.utils.environment import ExecutionMode
from sum.setup.venv import VenvManager


@dataclass
class ValidationResult:
    passed: bool
    message: str
    remediation: Optional[str] = None


class ProjectValidator:
    """Validates project setup state."""
    
    def __init__(self, project_path: Path, mode: ExecutionMode):
        self.project_path = project_path
        self.mode = mode
        self.venv_manager = VenvManager()
    
    def check_venv_exists(self) -> ValidationResult:
        """Check if virtualenv exists."""
        venv_path = self.project_path / ".venv"
        if venv_path.is_dir():
            return ValidationResult(True, ".venv exists")
        return ValidationResult(
            False, 
            ".venv not found",
            "Run 'sum init --full' or 'python -m venv .venv'"
        )
    
    def check_packages_installed(self) -> ValidationResult:
        """Check if key packages are installed in venv."""
        if not self.venv_manager.exists(self.project_path):
            return ValidationResult(False, "Cannot check packages - venv missing")
        
        python = self.venv_manager.get_python_executable(self.project_path)
        
        for package in ["django", "wagtail"]:
            result = subprocess.run(
                [str(python), "-c", f"import {package}"],
                capture_output=True
            )
            if result.returncode != 0:
                return ValidationResult(
                    False,
                    f"Package '{package}' not installed",
                    "Run 'pip install -r requirements.txt'"
                )
        
        return ValidationResult(True, "Required packages installed")
    
    def check_env_local(self) -> ValidationResult:
        """Check if .env.local exists."""
        env_local = self.project_path / ".env.local"
        if env_local.is_file():
            return ValidationResult(True, ".env.local found")
        return ValidationResult(
            False,
            ".env.local not found",
            "Run 'sum init --full' or create superuser manually"
        )
    
    def check_migrations_applied(self) -> ValidationResult:
        """Check if migrations are up to date."""
        try:
            executor = DjangoCommandExecutor(self.project_path, self.mode)
            result = executor.run_command(["migrate", "--check"], check=False)
            
            if result.returncode == 0:
                return ValidationResult(True, "Migrations up to date")
            return ValidationResult(
                False,
                "Pending migrations",
                "Run 'python manage.py migrate'"
            )
        except Exception as e:
            return ValidationResult(False, f"Migration check failed: {e}")
    
    def check_homepage_exists(self) -> ValidationResult:
        """Check if homepage is set as site root."""
        try:
            executor = DjangoCommandExecutor(self.project_path, self.mode)
            result = executor.run_command(
                ["shell", "-c", 
                 "from wagtail.models import Site; "
                 "site = Site.objects.get(is_default_site=True); "
                 "print(site.root_page.slug)"],
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip() == "home":
                return ValidationResult(True, "Homepage set as site root")
            return ValidationResult(
                False,
                "Homepage not configured",
                "Run 'python manage.py seed_homepage'"
            )
        except Exception as e:
            return ValidationResult(False, f"Homepage check failed: {e}")
```

### Enhanced Check Command

```python
"""
File: cli/sum/commands/check.py (enhanced section)
Name: check command enhancements
Purpose: Run enhanced validation checks for project state
Dependencies: click, sys, pathlib, sum.utils.validation, sum.utils.environment
Family: Main CLI command
"""

import sys
from pathlib import Path
from typing import Callable, List, Tuple

import click

from sum.utils.environment import detect_mode, ExecutionMode
from sum.utils.validation import ProjectValidator, ValidationResult


def run_enhanced_checks(project_path: Path, mode: ExecutionMode) -> None:
    """Run enhanced validation checks."""
    validator = ProjectValidator(project_path, mode)
    
    checks: List[Tuple[str, Callable[[], ValidationResult]]] = [
        ("Virtualenv", validator.check_venv_exists),
        ("Packages", validator.check_packages_installed),
        ("Credentials", validator.check_env_local),
        ("Database", validator.check_migrations_applied),
        ("Homepage", validator.check_homepage_exists),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        result = check_func()
        
        if result.passed:
            click.echo(f"[OK] {name}: {result.message}")
        else:
            click.echo(f"[FAIL] {name}: {result.message}")
            if result.remediation:
                click.echo(f"      → {result.remediation}")
            all_passed = False
    
    if all_passed:
        click.echo("\n✅ All checks passed")
    else:
        click.echo("\n❌ Some checks failed")
        sys.exit(1)
```

### Register in CLI

```python
# cli/sum/cli.py
from sum.commands.run import run

# In the CLI group
cli.add_command(run)
```
