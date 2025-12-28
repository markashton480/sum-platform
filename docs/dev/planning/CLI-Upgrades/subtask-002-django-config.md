# Subtask

**Title:** `CLI-002: Django Execution & Config (django.py, SetupConfig)`

---

## Parent

**Work Order:** #WO-CLI-V2 — CLI v2 Enhanced Architecture (v2.0.0)

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-v2/002-django-config` | `feature/cli-v2` |

```bash
git checkout feature/cli-v2
git pull origin feature/cli-v2
git checkout -b feature/cli-v2/002-django-config
git push -u origin feature/cli-v2/002-django-config
```

---

## Deliverable

This subtask will deliver:

- `cli/sum/utils/django.py` — DjangoCommandExecutor class for running manage.py commands
- `cli/sum/config.py` — SetupConfig dataclass for orchestration configuration
- `cli/tests/test_django.py` — Unit tests for Django command execution
- `cli/tests/test_config.py` — Unit tests for SetupConfig

---

## Boundaries

### Do

- Implement `DjangoCommandExecutor` class with `run_command()` method
- **Always use project's `.venv/bin/python`** for Django commands (mode does NOT affect interpreter choice)
- Handle PYTHONPATH injection for monorepo mode (add sum_core to path) — **append to existing PYTHONPATH, don't replace**
- Use `find_monorepo_root()` from #CLI-001 to resolve `core/` path
- Support environment variable passing to subprocess
- Support `check=True/False` for error handling control
- Implement `_get_python_executable()` that returns project venv Python (raise `VenvError` if missing)
- Implement `SetupConfig` dataclass with all operation flags
- Implement `SetupConfig.from_cli_args()` class method
- Note: `--full` and `--quick` are mutually exclusive (enforce in SetupConfig validation)
- Use type hints throughout
- Use `ExecutionMode` from #CLI-001

### Do NOT

- ❌ Do not implement VenvManager — owned by #CLI-003
- ❌ Do not implement DatabaseManager — owned by #CLI-004
- ❌ Do not implement SuperuserManager — owned by #CLI-004
- ❌ Do not modify command files (init.py, check.py, run.py)

---

## Acceptance Criteria

- [ ] `DjangoCommandExecutor(project_path, mode)` initializes correctly
- [ ] `executor.run_command(["migrate", "--noinput"])` runs Django command via subprocess
- [ ] Django commands **always** use `.venv/bin/python` regardless of mode
- [ ] `VenvError` is raised if `.venv/bin/python` doesn't exist
- [ ] Monorepo mode appends `core/` to PYTHONPATH (does not replace existing PYTHONPATH)
- [ ] Custom environment variables can be passed to commands
- [ ] `SetupConfig` has all flags: `full`, `quick`, `ci`, `no_prompt`, `skip_venv`, `skip_migrations`, `skip_seed`, `skip_superuser`, `run_server`, `port`
- [ ] `SetupConfig` has credential fields: `superuser_username`, `superuser_email`, `superuser_password`
- [ ] `SetupConfig` validates that `full` and `quick` are mutually exclusive
- [ ] `SetupConfig.from_cli_args(**kwargs)` creates config from CLI arguments
- [ ] Unit tests cover happy path and error scenarios
- [ ] `make lint && make test` passes

---

## Test Commands

```bash
make lint
make test

# Specific tests
python -m pytest tests/test_django.py -v
python -m pytest tests/test_config.py -v
```

---

## Files Expected to Change

```
cli/sum/utils/__init__.py          # Modified: add django exports
cli/sum/utils/django.py            # New
cli/sum/config.py                  # New
cli/tests/test_django.py           # New
cli/tests/test_config.py           # New
```

---

## Dependencies

**Depends On:**
- [ ] #CLI-001 must be merged first (provides ExecutionMode, exceptions)

**Blocks:**
- #CLI-003 Environment Setup Modules is waiting for this
- #CLI-004 Database & Auth Modules is waiting for this

---

## Risk

**Level:** Medium

**Why:**
- Mode detection affects Python executable resolution
- PYTHONPATH manipulation must be correct for imports to work
- Subprocess execution has platform-specific considerations
- Critical foundation for all setup modules

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
feat(cli): add Django command executor and SetupConfig

- Add DjangoCommandExecutor for running manage.py commands
- Handle PYTHONPATH injection for monorepo mode
- Support environment variable passing to subprocesses
- Add SetupConfig dataclass with all CLI flags and credentials
- Add from_cli_args() factory method for CLI integration

Closes #CLI-002
```

---

## Implementation Notes

### DjangoCommandExecutor

```python
from pathlib import Path
from typing import Dict, List, Optional
import os
import subprocess

from sum.exceptions import VenvError
from sum.utils.environment import ExecutionMode, find_monorepo_root


class DjangoCommandExecutor:
    """Executes Django management commands."""
    
    def __init__(self, project_path: Path, mode: ExecutionMode):
        self.project_path = project_path
        self.mode = mode
    
    def run_command(
        self,
        command: List[str],
        env: Optional[Dict[str, str]] = None,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a Django management command."""
        python = self._get_python_executable()
        full_command = [str(python), "manage.py"] + command
        
        command_env = os.environ.copy()
        
        # In monorepo mode, APPEND core/ to PYTHONPATH (don't replace)
        if self.mode == ExecutionMode.MONOREPO:
            core_path = self._get_core_path()
            existing = command_env.get('PYTHONPATH', '')
            if existing:
                command_env['PYTHONPATH'] = f"{core_path}{os.pathsep}{existing}"
            else:
                command_env['PYTHONPATH'] = str(core_path)
        
        if env:
            command_env.update(env)
        
        return subprocess.run(
            full_command,
            cwd=self.project_path,
            env=command_env,
            capture_output=True,
            text=True,
            check=check
        )
    
    def _get_python_executable(self) -> Path:
        """Get project venv Python executable.
        
        Always uses project's .venv - mode does NOT affect interpreter choice.
        """
        venv_python = self.project_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            raise VenvError(
                f"Virtualenv not found at {self.project_path / '.venv'}. "
                "Run 'sum init --full' or create manually with 'python -m venv .venv'"
            )
        return venv_python
    
    def _get_core_path(self) -> Path:
        """Get path to sum_core for PYTHONPATH (monorepo mode only)."""
        repo_root = find_monorepo_root(self.project_path)
        if repo_root:
            return repo_root / "core"
        raise ValueError("Cannot determine core path - not in monorepo")
```

### SetupConfig

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class SetupConfig:
    """Configuration for setup orchestration."""
    
    # Operation flags
    full: bool = False
    quick: bool = False
    ci: bool = False
    no_prompt: bool = False
    
    # Skip flags
    skip_venv: bool = False
    skip_migrations: bool = False
    skip_seed: bool = False
    skip_superuser: bool = False
    
    # Runtime options
    run_server: bool = False
    port: int = 8000
    
    # Superuser credentials
    superuser_username: str = "admin"
    superuser_email: str = "admin@example.com"
    superuser_password: str = "admin"
    
    # Content options
    seed_preset: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.full and self.quick:
            raise ValueError("--full and --quick are mutually exclusive")
        
        # CI mode implies no_prompt
        if self.ci:
            self.no_prompt = True
    
    @classmethod
    def from_cli_args(cls, **kwargs) -> 'SetupConfig':
        """Create config from CLI arguments."""
        return cls(**kwargs)
```
