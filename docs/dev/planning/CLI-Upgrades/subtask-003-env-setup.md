# Subtask

**Title:** `CLI-003: Environment Setup Modules (venv.py, deps.py)`

---

## Parent

**Work Order:** #WO-CLI-V2 — CLI v2 Enhanced Architecture (v2.0.0)

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-v2/003-env-setup` | `feature/cli-v2` |

```bash
git checkout feature/cli-v2
git pull origin feature/cli-v2
git checkout -b feature/cli-v2/003-env-setup
git push -u origin feature/cli-v2/003-env-setup
```

---

## Deliverable

This subtask will deliver:

- `cli/sum/setup/__init__.py` — Package initialization
- `cli/sum/setup/venv.py` — VenvManager class for virtualenv operations
- `cli/sum/setup/deps.py` — DependencyManager class for pip operations
- `cli/tests/test_venv.py` — Unit tests for virtualenv management
- `cli/tests/test_deps.py` — Unit tests for dependency installation

---

## Boundaries

### Do

- Implement `VenvManager` class with:
  - `create(project_path)` — create `.venv` if not exists (idempotent)
  - `get_python_executable(project_path)` — return path to venv Python
  - `is_activated()` — check if currently in a virtualenv
  - `exists(project_path)` — check if `.venv` directory exists
- Implement `DependencyManager` class with:
  - `install(project_path)` — run `pip install -r requirements.txt`
  - `verify(project_path)` — check if key packages are installed
- Use `VenvError` and `DependencyError` exceptions from #CLI-001
- Ensure all operations are idempotent (safe to re-run)
- Use type hints throughout

### Do NOT

- ❌ Do not implement DatabaseManager — owned by #CLI-004
- ❌ Do not implement SuperuserManager — owned by #CLI-004
- ❌ Do not implement SetupOrchestrator — owned by #CLI-006
- ❌ Do not modify command files

---

## Acceptance Criteria

- [ ] `VenvManager().create(path)` creates `.venv` directory using `python -m venv`
- [ ] `VenvManager().create(path)` returns existing venv path if already exists (idempotent)
- [ ] `VenvManager().get_python_executable(path)` returns `path/.venv/bin/python`
- [ ] `VenvManager().is_activated()` correctly detects virtualenv activation state
- [ ] `DependencyManager().install(path)` runs pip install using venv's pip
- [ ] `DependencyManager().install(path)` raises `DependencyError` on failure
- [ ] `DependencyManager().verify(path)` checks for key packages (django, wagtail)
- [ ] All operations log progress using `OutputFormatter` from #CLI-001
- [ ] Unit tests include mocked subprocess calls
- [ ] Integration test creates real venv in temp directory
- [ ] `make lint && make test` passes

---

## Test Commands

```bash
make lint
make test

# Specific tests
python -m pytest tests/test_venv.py -v
python -m pytest tests/test_deps.py -v
```

---

## Files Expected to Change

```
cli/sum/setup/__init__.py          # New
cli/sum/setup/venv.py              # New
cli/sum/setup/deps.py              # New
cli/tests/test_venv.py             # New
cli/tests/test_deps.py             # New
```

---

## Dependencies

**Depends On:**
- [ ] #CLI-001 must be merged first (provides exceptions, OutputFormatter)
- [ ] #CLI-002 must be merged first (provides ExecutionMode context)

**Blocks:**
- #CLI-006 Seeding & Orchestrator is waiting for this

---

## Risk

**Level:** Low

**Why:**
- Standard Python venv module is well-documented
- pip operations are straightforward subprocess calls
- No Django or database interaction
- Idempotent design reduces risk of corruption

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
feat(cli): add virtualenv and dependency management modules

- Add VenvManager for creating and managing .venv directories
- Add DependencyManager for pip install operations
- Ensure idempotent operations (safe to re-run)
- Add comprehensive unit tests with subprocess mocking

Closes #CLI-003
```

---

## Implementation Notes

### VenvManager

```python
from pathlib import Path
import subprocess
import sys
import logging

from sum.exceptions import VenvError

logger = logging.getLogger(__name__)

class VenvManager:
    """Manages Python virtual environments."""
    
    def create(self, project_path: Path) -> Path:
        """Create .venv if it doesn't exist."""
        venv_path = project_path / ".venv"
        
        if venv_path.exists():
            logger.info(f"Virtualenv already exists: {venv_path}")
            return venv_path
        
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise VenvError(f"Failed to create virtualenv: {e.stderr}")
        
        return venv_path
    
    def get_python_executable(self, project_path: Path) -> Path:
        """Get path to virtualenv Python."""
        return project_path / ".venv" / "bin" / "python"
    
    def is_activated(self) -> bool:
        """Check if we're in a virtualenv."""
        return sys.prefix != sys.base_prefix
    
    def exists(self, project_path: Path) -> bool:
        """Check if virtualenv exists."""
        return (project_path / ".venv").is_dir()
```

### DependencyManager

```python
from pathlib import Path
import subprocess

from sum.exceptions import DependencyError
from sum.setup.venv import VenvManager

class DependencyManager:
    """Manages Python package dependencies."""
    
    def __init__(self):
        self.venv_manager = VenvManager()
    
    def install(self, project_path: Path) -> None:
        """Install dependencies from requirements.txt."""
        requirements = project_path / "requirements.txt"
        
        if not requirements.exists():
            raise DependencyError(f"requirements.txt not found: {requirements}")
        
        python = self.venv_manager.get_python_executable(project_path)
        
        try:
            subprocess.run(
                [str(python), "-m", "pip", "install", "-r", str(requirements)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise DependencyError(f"pip install failed: {e.stderr}")
    
    def verify(self, project_path: Path) -> bool:
        """Verify key packages are installed."""
        python = self.venv_manager.get_python_executable(project_path)
        
        for package in ["django", "wagtail"]:
            result = subprocess.run(
                [str(python), "-c", f"import {package}"],
                capture_output=True
            )
            if result.returncode != 0:
                return False
        
        return True
```
