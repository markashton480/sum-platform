# Subtask

**Title:** `CLI-006: Seeding & Orchestrator (seed.py, orchestrator.py)`

---

## Parent

**Work Order:** #WO-CLI-V2 — CLI v2 Enhanced Architecture (v2.0.0)

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-v2/006-seed-orchestrator` | `feature/cli-v2` |

```bash
git checkout feature/cli-v2
git pull origin feature/cli-v2
git checkout -b feature/cli-v2/006-seed-orchestrator
git push -u origin feature/cli-v2/006-seed-orchestrator
```

---

## Deliverable

This subtask will deliver:

- `cli/sum/setup/seed.py` — ContentSeeder class for homepage seeding
- `cli/sum/setup/orchestrator.py` — SetupOrchestrator class for coordinating setup flow
- `cli/tests/test_seed.py` — Unit tests for seeding
- `cli/tests/test_orchestrator.py` — Unit tests for orchestrator

---

## Boundaries

### Do

- Implement `ContentSeeder` class with:
  - `seed_homepage(preset)` — run `manage.py seed_homepage`
  - `check_homepage_exists()` — verify homepage is created
- Implement `SetupOrchestrator` class with:
  - `__init__(project_path, mode)` — initialize with path and execution mode
  - `run_full_setup(config)` — run complete setup based on SetupConfig
  - **Orchestrator owns ALL 8 steps** (scaffold through server) — init command is a thin wrapper
  - Progress tracking using `OutputFormatter`
- **Build step list dynamically** based on mode/flags:
  - If `quick` mode: only include steps 1-4 (no DB operations)
  - Set `total_steps = len(active_steps)` to avoid confusing progress like `[6/4]`
- Implement step sequencing:
  1. Scaffolding project structure
  2. Validating structure
  3. Creating virtualenv
  4. Installing dependencies
  5. Running migrations
  6. Seeding homepage
  7. Creating superuser
  8. Starting server (if `--run` flag)
- Handle `--skip-*` flags by excluding steps from the active list
- Use all setup modules from #CLI-003, #CLI-004
- Use `SeedError` exception from #CLI-001
- **Implement server start** in `_start_server()` (not deferred) — subprocess.Popen for background server
- Wrap unexpected exceptions into `SetupError` with helpful messages

### Do NOT

- ❌ Do not modify `commands/init.py` — owned by #CLI-007 (but init will be thin wrapper around orchestrator)
- ❌ Do not implement `sum run` standalone command — owned by #CLI-008
- ❌ Do not implement enhanced validation checks — owned by #CLI-008

---

## Acceptance Criteria

- [ ] `ContentSeeder(executor).seed_homepage()` runs `manage.py seed_homepage`
- [ ] `ContentSeeder(executor).seed_homepage(preset="theme-x")` passes preset argument
- [ ] `ContentSeeder(executor).check_homepage_exists()` returns boolean
- [ ] `SetupOrchestrator(path, mode).run_full_setup(config)` executes all steps in order
- [ ] **Step list is built dynamically** — `total_steps` matches actual number of steps to run
- [ ] Progress displays correctly: `[1/8]`, `[2/8]`, ... or `[1/4]`, `[2/4]`, ... for quick mode
- [ ] `config.quick = True` builds step list with only 4 steps (no DB operations)
- [ ] `config.skip_venv = True` excludes venv step from active list
- [ ] `config.skip_migrations = True` excludes migration step from active list
- [ ] `config.skip_seed = True` excludes seeding step from active list
- [ ] `config.skip_superuser = True` excludes superuser step from active list
- [ ] `config.run_server = True` includes server start step
- [ ] **Server start is implemented** (not deferred) — starts Django dev server
- [ ] Errors raise appropriate exceptions with helpful messages
- [ ] Unexpected exceptions are wrapped with user-friendly messages
- [ ] Unit tests mock all underlying setup modules
- [ ] `make lint && make test` passes

---

## Test Commands

```bash
make lint
make test

# Specific tests
python -m pytest tests/test_seed.py -v
python -m pytest tests/test_orchestrator.py -v
```

---

## Files Expected to Change

```
cli/sum/setup/__init__.py          # Modified: add exports
cli/sum/setup/seed.py              # New
cli/sum/setup/orchestrator.py      # New
cli/tests/test_seed.py             # New
cli/tests/test_orchestrator.py     # New
```

---

## Dependencies

**Depends On:**
- [ ] #CLI-001 must be merged first (exceptions, OutputFormatter)
- [ ] #CLI-002 must be merged first (DjangoCommandExecutor, SetupConfig)
- [ ] #CLI-003 must be merged first (VenvManager, DependencyManager)
- [ ] #CLI-004 must be merged first (DatabaseManager, SuperuserManager)
- [ ] #CLI-005 must be merged first (seed_homepage command exists)

**Blocks:**
- #CLI-007 Enhanced Init Command is waiting for this

---

## Risk

**Level:** High

**Why:**
- Central coordinator — errors cascade to all operations
- Integrates all setup modules — any module bug surfaces here
- Complex flow control with skip flags and modes
- Critical path for entire CLI v2 functionality

---

## Labels

- [ ] `type:task`
- [ ] `agent:*`
- [ ] `component:cli`
- [ ] `risk:high`
- [ ] Milestone: `v2.0.0`

---

## Project Fields

- [ ] Agent: (assigned)
- [ ] Model Planned: (selected)
- [ ] Component: cli
- [ ] Change Type: feat
- [ ] Risk: high
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
feat(cli): add content seeding and setup orchestrator

- Add ContentSeeder for running seed_homepage command
- Add SetupOrchestrator to coordinate full setup flow
- Implement 8-step setup sequence with progress tracking
- Support --quick mode and all --skip-* flags
- Add comprehensive error handling with recovery guidance

Closes #CLI-006
```

---

## Implementation Notes

### ContentSeeder

```python
"""
File: cli/sum/setup/seed.py
Name: ContentSeeder
Purpose: Seeds initial Wagtail content via Django management commands
Dependencies: sum.exceptions, sum.utils.django
Family: Setup module, used by SetupOrchestrator
"""

import re
from dataclasses import dataclass
from typing import Optional

from sum.exceptions import SeedError
from sum.utils.django import DjangoCommandExecutor


@dataclass
class SeedResult:
    success: bool
    page_id: Optional[int] = None


class ContentSeeder:
    """Seeds initial Wagtail content."""
    
    def __init__(self, django_executor: DjangoCommandExecutor):
        self.django = django_executor
    
    def seed_homepage(self, preset: Optional[str] = None) -> SeedResult:
        """Create initial homepage."""
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
    
    def check_homepage_exists(self) -> bool:
        """Check if homepage is already created."""
        result = self.django.run_command(
            ["shell", "-c", "from home.models import HomePage; print(HomePage.objects.filter(slug='home').exists())"],
            check=False
        )
        return result.stdout.strip().lower() == "true"
    
    def _extract_page_id(self, output: str) -> Optional[int]:
        """Extract page ID from command output."""
        match = re.search(r'ID: (\d+)', output)
        return int(match.group(1)) if match else None
```

### SetupOrchestrator

```python
"""
File: cli/sum/setup/orchestrator.py
Name: SetupOrchestrator
Purpose: Orchestrates the full project setup flow
Dependencies: All setup modules, config, utils
Family: Central coordinator, used by init command
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from sum.config import SetupConfig
from sum.exceptions import (
    SetupError, VenvError, DependencyError, 
    MigrationError, SeedError, SuperuserError
)
from sum.utils.environment import ExecutionMode
from sum.utils.output import OutputFormatter
from sum.utils.django import DjangoCommandExecutor
from sum.setup.venv import VenvManager
from sum.setup.deps import DependencyManager
from sum.setup.database import DatabaseManager
from sum.setup.auth import SuperuserManager
from sum.setup.seed import ContentSeeder


@dataclass
class SetupResult:
    success: bool
    project_path: Path
    credentials_path: Optional[Path] = None
    url: str = "http://127.0.0.1:8000/"


class SetupOrchestrator:
    """Orchestrates the full project setup flow.
    
    Owns ALL 8 steps — init command is a thin wrapper around this.
    """
    
    def __init__(self, project_path: Path, mode: ExecutionMode):
        self.project_path = project_path
        self.mode = mode
        
        # Initialize components
        self.venv_manager = VenvManager()
        self.deps_manager = DependencyManager()
    
    def run_full_setup(self, config: SetupConfig) -> SetupResult:
        """Run complete setup based on configuration."""
        
        # Build step list dynamically based on config
        steps = self._build_step_list(config)
        total_steps = len(steps)
        
        credentials_path: Optional[Path] = None
        
        for step_num, (step_name, step_func) in enumerate(steps, 1):
            self._show_progress(step_num, total_steps, step_name, "⏳")
            try:
                result = step_func(config)
                if step_name == "Creating superuser" and result:
                    credentials_path = result
                self._show_progress(step_num, total_steps, step_name, "✅")
            except SetupError:
                self._show_progress(step_num, total_steps, step_name, "❌")
                raise
            except Exception as e:
                # Wrap unexpected exceptions
                self._show_progress(step_num, total_steps, step_name, "❌")
                raise SetupError(f"Unexpected error in '{step_name}': {e}") from e
        
        return SetupResult(
            success=True,
            project_path=self.project_path,
            credentials_path=credentials_path
        )
    
    def _build_step_list(
        self, config: SetupConfig
    ) -> List[Tuple[str, Callable[[SetupConfig], Optional[Path]]]]:
        """Build list of steps to execute based on config."""
        
        # Always include scaffold and validate
        steps: List[Tuple[str, Callable]] = [
            ("Scaffolding structure", self._scaffold),
            ("Validating structure", self._validate),
        ]
        
        # Venv and deps (unless skipped)
        if not config.skip_venv:
            steps.append(("Creating virtualenv", self._setup_venv))
            steps.append(("Installing dependencies", self._install_deps))
        
        # Quick mode stops here
        if config.quick:
            return steps
        
        # DB operations
        if not config.skip_migrations:
            steps.append(("Running migrations", self._migrate))
        
        if not config.skip_seed:
            steps.append(("Seeding homepage", self._seed_content))
        
        if not config.skip_superuser:
            steps.append(("Creating superuser", self._create_superuser))
        
        # Server (only if requested)
        if config.run_server:
            steps.append(("Starting server", self._start_server))
        
        return steps
    
    def _show_progress(self, step: int, total: int, message: str, status: str) -> None:
        """Display progress indicator."""
        OutputFormatter.progress(step, total, message, status)
    
    def _setup_venv(self, config: SetupConfig) -> None:
        """Create virtualenv."""
        self.venv_manager.create(self.project_path)
    
    def _install_deps(self, config: SetupConfig) -> None:
        """Install dependencies."""
        self.deps_manager.install(self.project_path)
    
    def _migrate(self, config: SetupConfig) -> None:
        """Run database migrations."""
        executor = DjangoCommandExecutor(self.project_path, self.mode)
        db_manager = DatabaseManager(executor)
        db_manager.migrate()
    
    def _seed_content(self, config: SetupConfig) -> None:
        """Seed homepage content."""
        executor = DjangoCommandExecutor(self.project_path, self.mode)
        seeder = ContentSeeder(executor)
        seeder.seed_homepage(preset=config.seed_preset)
    
    def _create_superuser(self, config: SetupConfig) -> Path:
        """Create superuser and return credentials path."""
        executor = DjangoCommandExecutor(self.project_path, self.mode)
        auth_manager = SuperuserManager(executor, self.project_path)
        result = auth_manager.create(
            username=config.superuser_username,
            email=config.superuser_email,
            password=config.superuser_password
        )
        return result.credentials_path
    
    def _scaffold(self, config: SetupConfig) -> None:
        """Scaffold project structure."""
        # Implementation: copy boilerplate, rename files, etc.
        # This is existing logic to be integrated
        pass
    
    def _validate(self, config: SetupConfig) -> None:
        """Validate project structure."""
        # Implementation: check required files exist, etc.
        # This is existing logic to be integrated
        pass
    
    def _start_server(self, config: SetupConfig) -> None:
        """Start development server in background."""
        python = self.venv_manager.get_python_executable(self.project_path)
        
        # Start server as background process
        subprocess.Popen(
            [str(python), "manage.py", "runserver", f"127.0.0.1:{config.port}"],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
```
