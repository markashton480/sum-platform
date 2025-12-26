# Subtask

**Title:** `CLI-001: Foundation Utilities (environment, output, prompts, exceptions)`

---

## Parent

**Work Order:** #WO-CLI-V2 — CLI v2 Enhanced Architecture (v2.0.0)

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-v2/001-foundation-utils` | `feature/cli-v2` |

```bash
git checkout feature/cli-v2
git pull origin feature/cli-v2
git checkout -b feature/cli-v2/001-foundation-utils
git push -u origin feature/cli-v2/001-foundation-utils
```

---

## Deliverable

This subtask will deliver:

- `cli/sum/utils/__init__.py` — Package initialization with exports
- `cli/sum/utils/environment.py` — ExecutionMode enum and mode detection logic
- `cli/sum/utils/output.py` — OutputFormatter class for consistent CLI output
- `cli/sum/utils/prompts.py` — PromptManager class for interactive prompts
- `cli/sum/exceptions.py` — Exception hierarchy (SumCliError, SetupError, etc.)
- `cli/tests/test_environment.py` — Unit tests for mode detection
- `cli/tests/test_output.py` — Unit tests for output formatting
- `cli/tests/test_prompts.py` — Unit tests for prompt handling

---

## Boundaries

### Do

- Implement `ExecutionMode` enum with `MONOREPO` and `STANDALONE` values
- Implement `detect_mode()` function checking for `core/` and `boilerplate/` directories
- Implement `find_monorepo_root()` function that walks upward to find repo root (returns `Path` or `None`)
- Implement `get_clients_dir()` helper that uses monorepo root to resolve clients directory
- Implement `OutputFormatter` with static methods: `progress()`, `success()`, `error()`, `info()`, `summary()`
- Implement `PromptManager` class with `confirm()` and `text()` methods
- Support `no_prompt` and `ci` modes in PromptManager (return defaults without prompting)
- Implement full exception hierarchy: `SumCliError`, `SetupError`, `VenvError`, `DependencyError`, `MigrationError`, `SeedError`, `SuperuserError`
- Use type hints throughout
- Write comprehensive unit tests

### Do NOT

- ❌ Do not implement Django command execution — owned by #CLI-002
- ❌ Do not implement SetupConfig dataclass — owned by #CLI-002
- ❌ Do not implement validation checks — owned by #CLI-008
- ❌ Do not modify any existing command files (init.py, check.py)

---

## Acceptance Criteria

- [ ] `ExecutionMode.MONOREPO` and `ExecutionMode.STANDALONE` enum values exist
- [ ] `detect_mode(path)` correctly identifies monorepo vs standalone based on directory structure
- [ ] `find_monorepo_root(path)` walks upward and returns repo root `Path` or `None` if not found
- [ ] `get_clients_dir(path)` returns `<repo_root>/clients` in monorepo mode
- [ ] `OutputFormatter.progress(step, total, message, status)` prints formatted progress line
- [ ] `OutputFormatter.summary(project_name, data)` prints complete summary box with emojis
- [ ] `PromptManager(no_prompt=True).confirm("Test?")` returns default without prompting
- [ ] `PromptManager(ci=True).text("Name?", default="admin")` returns "admin" without prompting
- [ ] All custom exceptions inherit from `SumCliError`
- [ ] Exception messages are descriptive and actionable
- [ ] All functions have type hints
- [ ] Unit tests achieve >90% coverage for these modules
- [ ] `make lint` passes with no errors
- [ ] `make test` passes

---

## Test Commands

```bash
make lint
make test

# Specific tests
python -m pytest tests/test_environment.py -v
python -m pytest tests/test_output.py -v
python -m pytest tests/test_prompts.py -v
```

---

## Files Expected to Change

```
cli/sum/utils/__init__.py          # New
cli/sum/utils/environment.py       # New
cli/sum/utils/output.py            # New
cli/sum/utils/prompts.py           # New
cli/sum/exceptions.py              # New
cli/tests/test_environment.py      # New
cli/tests/test_output.py           # New
cli/tests/test_prompts.py          # New
```

---

## Dependencies

**Depends On:**
- [ ] None — this is the foundation layer

**Blocks:**
- #CLI-002 Django Execution & Config is waiting for this
- #CLI-003 Environment Setup Modules is waiting for this
- #CLI-004 Database & Auth Modules is waiting for this

---

## Risk

**Level:** Low

**Why:**
- Self-contained utilities with no external dependencies
- Well-defined interfaces from architecture spec
- Standard Python patterns (enums, dataclasses, type hints)
- No interaction with Django or database

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
feat(cli): add foundation utilities for CLI v2

- Add ExecutionMode enum and detect_mode() for monorepo/standalone detection
- Add OutputFormatter with progress, success, error, info, summary methods
- Add PromptManager with confirm/text methods supporting ci/no_prompt modes
- Add exception hierarchy (SumCliError, SetupError, VenvError, etc.)
- Add comprehensive unit tests for all modules

Closes #CLI-001
```

---

## Implementation Notes

### ExecutionMode and Path Resolution

```python
from enum import Enum
from pathlib import Path
from typing import Optional

class ExecutionMode(Enum):
    MONOREPO = "monorepo"
    STANDALONE = "standalone"


def find_monorepo_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """Walk upward to find monorepo root (contains core/ and boilerplate/).
    
    Returns the root Path if found, None otherwise.
    """
    search_path = start_path or Path.cwd()
    
    for parent in [search_path] + list(search_path.parents):
        if (parent / "core").is_dir() and (parent / "boilerplate").is_dir():
            return parent
    
    return None


def detect_mode(path: Optional[Path] = None) -> ExecutionMode:
    """Detect execution mode based on directory structure."""
    if find_monorepo_root(path) is not None:
        return ExecutionMode.MONOREPO
    return ExecutionMode.STANDALONE


def get_clients_dir(start_path: Optional[Path] = None) -> Path:
    """Get the clients directory, resolving from monorepo root if applicable."""
    repo_root = find_monorepo_root(start_path)
    
    if repo_root:
        return repo_root / "clients"
    
    # Standalone mode: assume current directory or raise
    cwd = start_path or Path.cwd()
    if (cwd / "clients").is_dir():
        return cwd / "clients"
    
    raise FileNotFoundError("Cannot locate clients directory")
```

### PromptManager Pattern

```python
from typing import Optional

class PromptManager:
    def __init__(self, no_prompt: bool = False, ci: bool = False):
        self.no_prompt = no_prompt
        self.ci = ci
    
    def confirm(self, message: str, default: bool = True) -> bool:
        if self.no_prompt or self.ci:
            return default
        
        suffix = " (Y/n)" if default else " (y/N)"
        response = input(f"{message}{suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes']
    
    def text(self, message: str, default: Optional[str] = None) -> str:
        if self.no_prompt or self.ci:
            return default or ""
        
        suffix = f" [{default}]" if default else ""
        response = input(f"{message}{suffix}: ").strip()
        
        return response or default or ""
```
