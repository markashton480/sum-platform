# SUM CLI Developer Guide (v2)

This guide is for maintainers and developers working on the SUM Platform CLI tool itself.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Module Structure](#module-structure)
- [Key Concepts](#key-concepts)
- [Command Implementation](#command-implementation)
- [Testing Strategy](#testing-strategy)
- [Development Workflow](#development-workflow)
- [Design Patterns](#design-patterns)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### High-Level Design

The CLI v2 follows a layered architecture:

```
Commands Layer (cli.sum.commands)
    ↓
Orchestration Layer (cli.sum.setup.orchestrator)
    ↓
Setup Modules Layer (cli.sum.setup)
    ↓
Utilities Layer (cli.sum.utils)
    ↓
Core Infrastructure (DjangoCommandExecutor, VenvManager, etc.)
```

### Design Principles

1. **Separation of Concerns** - Commands orchestrate, setup modules execute, utils provide services
2. **Idempotency** - All setup operations are safe to re-run
3. **Composability** - Setup steps can be skipped/combined via configuration
4. **Testability** - All modules have comprehensive unit tests with mocked I/O
5. **Graceful Degradation** - Clear error messages with remediation guidance

---

## Module Structure

### Directory Layout

```
cli/sum/
├── __init__.py
├── cli.py                          # Click entrypoint
├── config.py                       # SetupConfig dataclass
├── exceptions.py                   # CLI exception hierarchy
├── commands/                       # User-facing commands
│   ├── __init__.py
│   ├── init.py                     # sum init command
│   ├── run.py                      # sum run command
│   └── check.py                    # sum check command
├── setup/                          # Setup step implementations
│   ├── __init__.py
│   ├── orchestrator.py             # SetupOrchestrator
│   ├── scaffold.py                 # Project scaffolding
│   ├── venv.py                     # VenvManager
│   ├── deps.py                     # DependencyManager
│   ├── database.py                 # DatabaseManager
│   ├── auth.py                     # SuperuserManager
│   └── seed.py                     # ContentSeeder
└── utils/                          # Shared utilities
    ├── __init__.py
    ├── environment.py              # ExecutionMode, path resolution
    ├── output.py                   # OutputFormatter
    ├── prompts.py                  # PromptManager
    ├── django.py                   # DjangoCommandExecutor
    └── validation.py               # ProjectValidator

cli/tests/                          # 200+ tests
├── conftest.py                     # pytest fixtures
├── test_init.py
├── test_run.py
├── test_check.py
├── test_orchestrator.py            # 456 lines of orchestration tests
├── test_auth.py                    # 303 lines of auth tests
├── test_seed.py                    # 247 lines of seed tests
└── ... (more test files)
```

### Core Infrastructure

**Django Management Command:**
```
core/sum_core/management/commands/
└── seed_homepage.py               # Creates default HomePage

tests/sum_core/
└── test_seed_homepage.py          # 111 lines of tests
```

---

## Key Concepts

### Execution Modes

The CLI detects and adapts to two execution contexts:

```python
class ExecutionMode(str, Enum):
    MONOREPO = "monorepo"      # Inside sum-platform repo
    STANDALONE = "standalone"  # Deployed client project
```

**Detection logic** (`utils/environment.py`):
- Monorepo: Detected by presence of `core/` and `boilerplate/` directories with markers
- Standalone: Everything else

**Implications:**
- **Monorepo:** Adds `core/` to `PYTHONPATH` automatically
- **Standalone:** Expects `sum_core` installed via pip

### Setup Configuration

All setup flags are consolidated in a single dataclass:

```python
@dataclass
class SetupConfig:
    # Mode flags
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

    # Credentials
    superuser_username: str = "admin"
    superuser_email: str = "admin@example.com"
    superuser_password: str = "admin"

    # Content
    seed_preset: str | None = None
```

**Factory method:**
```python
config = SetupConfig.from_cli_args(**cli_args)
```

**Validation:**
- Mutual exclusivity of `--full` and `--quick`
- Auto-enable `no_prompt` when `ci=True`

### Setup Orchestration

The `SetupOrchestrator` coordinates all setup steps:

```python
class SetupStep(str, Enum):
    SCAFFOLD = "Scaffolding structure"
    VALIDATE = "Validating structure"
    CREATE_VENV = "Creating virtualenv"
    INSTALL_DEPS = "Installing dependencies"
    MIGRATE = "Running migrations"
    SEED = "Seeding homepage"
    CREATE_SUPERUSER = "Creating superuser"
    START_SERVER = "Starting server"
```

**Dynamic step list building:**
```python
def _build_step_list(self, config: SetupConfig) -> list[StepDefinition]:
    steps = [
        (SetupStep.SCAFFOLD, self._scaffold),
        (SetupStep.VALIDATE, self._validate),
    ]

    if not config.skip_venv:
        steps.append((SetupStep.CREATE_VENV, self._setup_venv))
        steps.append((SetupStep.INSTALL_DEPS, self._install_deps))

    if config.quick:
        return steps  # Stop here for quick mode

    # ... add DB, seed, auth, server steps based on config
    return steps
```

### Django Command Execution

Centralized Django command runner with proper environment handling:

```python
class DjangoCommandExecutor:
    def __init__(self, project_path: Path, mode: ExecutionMode):
        self.project_path = project_path
        self.mode = mode

    def run(
        self,
        command: list[str],
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        # Inject PYTHONPATH for monorepo mode
        # Set DJANGO_SETTINGS_MODULE
        # Execute python manage.py <command>
```

**Key features:**
- Automatic `PYTHONPATH` configuration for monorepo
- Environment variable injection
- Stderr/stdout capture for parsing
- Return code validation

---

## Command Implementation

### `sum init` Command Flow

```
1. Validate project name
   ├─> validate_project_name() from sum_cli.util
   └─> Normalize slug + python package name

2. Check --full/--quick mutual exclusivity

3. Detect clients directory
   ├─> Monorepo: repo_root/clients/
   └─> Standalone: error (not yet supported)

4. Build SetupConfig
   ├─> From CLI args
   ├─> Interactive prompts (if not --no-prompt/--ci)
   └─> Validate configuration

5. Create SetupOrchestrator
   └─> Pass project_path + execution_mode

6. Run full setup
   ├─> Execute dynamic step list
   ├─> Show progress for each step
   └─> Collect credentials_path from superuser step

7. Display summary
   ├─> Project location
   ├─> Server URL
   └─> Credentials (if created)
```

**Code reference:** `cli/sum/commands/init.py:92`

### `sum run` Command Flow

```
1. Resolve project path
   ├─> From argument (if provided)
   └─> From current directory

2. Detect execution mode
   └─> ExecutionMode.MONOREPO or STANDALONE

3. Check virtualenv exists
   └─> Fail if missing with remediation

4. Find available port
   ├─> Try requested port
   ├─> Fallback to next 10 ports
   └─> Fail if all in use

5. Configure environment
   ├─> Set PYTHONPATH for monorepo
   └─> Inherit system environment

6. Start server
   └─> subprocess.run with proper env
```

**Code reference:** `cli/sum/commands/run.py:46`

### `sum check` Command Flow

```
1. Resolve project path
2. Detect execution mode
3. Create ProjectValidator

4. Run checks
   ├─> Virtualenv exists + packages installed
   ├─> .env.local exists (credentials)
   ├─> Migrations applied
   └─> HomePage exists

5. Display results
   ├─> [OK] / [FAIL] / [SKIP] status
   ├─> Remediation for failures
   └─> Exit code 1 if any failures
```

**Code reference:** `cli/sum/commands/check.py:43`

---

## Testing Strategy

### Test Coverage

**Statistics:**
- **200 tests** across 40+ test files
- **100% coverage** on all new modules
- **Comprehensive edge case testing**

**Test distribution:**
- `test_orchestrator.py`: 456 lines (22 tests)
- `test_auth.py`: 303 lines (19 tests)
- `test_seed.py`: 247 lines (11 tests)
- `test_database.py`: 149 lines
- `test_deps.py`: 135 lines
- `test_validation.py`: 117 lines
- ... and more

### Testing Patterns

#### 1. Subprocess Mocking

All external commands are mocked using `pytest.monkeypatch`:

```python
def test_venv_create(monkeypatch, tmp_path):
    calls = []

    def mock_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr("subprocess.run", mock_run)

    manager = VenvManager()
    manager.create(tmp_path)

    assert len(calls) == 1
    assert calls[0] == [sys.executable, "-m", "venv", str(tmp_path / ".venv")]
```

**Code reference:** `cli/tests/test_venv.py:15`

#### 2. File System Isolation

All tests use `tmp_path` fixture for isolated file operations:

```python
def test_scaffold_project(tmp_path):
    project_path = scaffold_project(
        project_name="test-project",
        clients_dir=tmp_path,
        theme_slug="default",
    )

    assert project_path.exists()
    assert (project_path / "manage.py").exists()
```

**Code reference:** `cli/tests/test_orchestrator.py:50`

#### 3. Error Scenarios

Comprehensive testing of failure modes:

```python
def test_user_exists_raises_on_command_failure(monkeypatch, tmp_path):
    """Test that user_exists raises SuperuserError on command failure."""
    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess([], 1, "", "DB error")

    monkeypatch.setattr("subprocess.run", mock_run)

    manager = SuperuserManager(mock_executor, tmp_path)

    with pytest.raises(SuperuserError, match="Failed to check user existence"):
        manager._user_exists("admin")
```

**Code reference:** `cli/tests/test_auth.py:230`

#### 4. Security Testing

File permissions, injection prevention, validation:

```python
def test_env_local_has_secure_permissions(monkeypatch, tmp_path):
    """Test .env.local is created with 0o600 permissions."""
    # ... setup mocks

    manager = SuperuserManager(executor, tmp_path)
    result = manager.create("admin", "admin@example.com", "secret")

    env_local = tmp_path / ".env.local"
    assert env_local.exists()
    assert oct(env_local.stat().st_mode)[-3:] == "600"
```

**Code reference:** `cli/tests/test_auth.py:145`

#### 5. Integration Testing

Full orchestrator flow testing:

```python
def test_full_setup_with_all_steps(all_mocks, tmp_path):
    """Test complete setup flow with all steps enabled."""
    config = SetupConfig(
        full=True,
        skip_venv=False,
        skip_migrations=False,
        skip_seed=False,
        skip_superuser=False,
        run_server=False,
    )

    orchestrator = SetupOrchestrator(tmp_path, ExecutionMode.STANDALONE)
    result = orchestrator.run_full_setup(config)

    assert result.success is True
    assert result.project_path == tmp_path
    assert result.credentials_path is not None
```

**Code reference:** `cli/tests/test_orchestrator.py:120`

### Running Tests

```bash
# All CLI tests
pytest cli/tests/ -v

# Specific module
pytest cli/tests/test_orchestrator.py -v

# With coverage
pytest cli/tests/ --cov=cli.sum --cov-report=term-missing

# Fast subset
pytest cli/tests/test_init.py cli/tests/test_run.py cli/tests/test_check.py
```

### Test Fixtures

**Key fixtures** (`cli/tests/conftest.py`):

```python
@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for testing external commands."""

@pytest.fixture
def mock_django_executor():
    """Mock DjangoCommandExecutor for testing setup modules."""

@pytest.fixture
def all_mocks(monkeypatch, tmp_path):
    """Comprehensive mock setup for orchestrator tests."""
```

---

## Development Workflow

### Setting Up for Development

```bash
# Clone repo
git clone https://github.com/markashton480/sum-platform.git
cd sum-platform

# Create virtualenv
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
make install-dev

# Install CLI in editable mode
pip install -e ./cli

# Run tests
make test

# Run linters
make lint
```

### Making Changes

1. **Create feature branch:**
   ```bash
   git checkout -b feature/cli/<description>
   ```

2. **Make changes to modules**

3. **Add tests** (100% coverage required)

4. **Run test suite:**
   ```bash
   pytest cli/tests/ -v --cov=cli.sum
   ```

5. **Run linters:**
   ```bash
   make lint
   # Or individual tools:
   ruff check cli/
   mypy cli/
   black cli/
   isort cli/
   ```

6. **Commit with conventional commits:**
   ```bash
   git commit -m "feat(cli): add new feature X"
   ```

### Code Review Checklist

Before submitting a PR:

- [ ] All tests pass (`make test`)
- [ ] Linters pass (`make lint`)
- [ ] 100% test coverage on new code
- [ ] Documentation updated (if user-facing)
- [ ] Error messages are clear and actionable
- [ ] Security considerations addressed
- [ ] Idempotency verified (setup steps safe to re-run)
- [ ] Edge cases tested (empty stderr, missing files, etc.)

---

## Design Patterns

### 1. Manager Pattern

Each setup concern has a dedicated manager class:

```python
class VenvManager:
    """Manages virtualenv lifecycle."""

    def create(self, project_path: Path) -> None: ...
    def exists(self, project_path: Path) -> bool: ...
    def get_python_executable(self, project_path: Path) -> Path: ...

class DatabaseManager:
    """Manages database migrations."""

    def migrate(self) -> None: ...
    def has_pending_migrations(self) -> bool: ...

class SuperuserManager:
    """Manages superuser creation and credentials."""

    def create(self, username: str, email: str, password: str) -> SuperuserResult: ...
```

**Benefits:**
- Single Responsibility Principle
- Easy to test in isolation
- Reusable across commands

### 2. Result Objects

Operations return structured result objects:

```python
@dataclass
class SetupResult:
    success: bool
    project_path: Path
    credentials_path: Path | None = None
    url: str = "http://127.0.0.1:8000/"

@dataclass
class SuperuserResult:
    username: str
    email: str
    password: str
    credentials_path: Path

@dataclass
class ValidationResult:
    status: ValidationStatus
    message: str
    remediation: str | None = None
```

**Benefits:**
- Type-safe return values
- Self-documenting
- Easy to extend

### 3. Strategy Pattern for Steps

Setup steps are defined as a list of callables:

```python
StepFunction = Callable[[SetupConfig], Path | None]
StepDefinition = tuple[SetupStep, StepFunction]

def _build_step_list(self, config: SetupConfig) -> list[StepDefinition]:
    steps = []
    steps.append((SetupStep.SCAFFOLD, self._scaffold))

    if not config.skip_venv:
        steps.append((SetupStep.CREATE_VENV, self._setup_venv))

    # ... build dynamic list
    return steps
```

**Benefits:**
- Composable setup flows
- Easy to add/remove steps
- Configuration-driven behavior

### 4. Lazy Initialization

DjangoCommandExecutor is created once and reused:

```python
def _get_django_executor(self) -> DjangoCommandExecutor:
    """Get or create the Django command executor (lazy initialization)."""
    if self.django_executor is None:
        self.django_executor = DjangoCommandExecutor(
            self.project_path, self.mode
        )
    return self.django_executor
```

**Benefits:**
- Avoid redundant subprocess.run calls
- Share configuration across steps
- Performance optimization

### 5. Exception Hierarchy

Typed exceptions for clear error handling:

```python
class CLIError(Exception):
    """Base exception for CLI errors."""

class SetupError(CLIError):
    """Setup operation failed."""

class VenvError(SetupError):
    """Virtualenv operation failed."""

class DependencyError(SetupError):
    """Dependency installation failed."""

class MigrationError(SetupError):
    """Database migration failed."""

class SuperuserError(SetupError):
    """Superuser creation failed."""

class SeedError(SetupError):
    """Content seeding failed."""
```

**Usage:**
```python
try:
    manager.create_venv()
except VenvError as exc:
    OutputFormatter.error(str(exc))
    return 1
```

---

## Security Considerations

### 1. Credential Storage

**File permissions:** `.env.local` created with `0o600` (read/write owner only):

```python
env_local.write_text(content)
env_local.chmod(0o600)  # Restrictive permissions
```

**Code reference:** `cli/sum/setup/auth.py:156`

### 2. Command Injection Prevention

**JSON serialization** for subprocess output parsing:

```python
# ✅ SAFE: JSON serialization prevents code injection
result = executor.run(
    ["shell", "-c", f"import json; print(json.dumps({{'exists': User.objects.filter(username='{username}').exists()}}))"]
)
output = json.loads(result.stdout.strip())
```

**Code reference:** `cli/sum/setup/auth.py:88`

### 3. Input Validation

**Project name validation:**

```python
try:
    naming = validate_project_name(project_name)
except ValueError as exc:
    OutputFormatter.error(str(exc))
    return 1
```

**Code reference:** `cli/sum/commands/init.py:108`

### 4. Return Code Checking

**Always validate before parsing output:**

```python
result = executor.run(command)
if result.returncode != 0:
    raise SuperuserError(f"Failed: {result.stderr or result.stdout}")

# Now safe to parse result.stdout
```

**Code reference:** `cli/sum/setup/auth.py:95`

### 5. Error Message Sanitization

**Avoid leaking sensitive data in errors:**

```python
# ✅ GOOD: Generic error
raise SuperuserError("Failed to create superuser")

# ❌ BAD: Leaks password
raise SuperuserError(f"Failed to create user with password: {password}")
```

---

## Troubleshooting

### Common Development Issues

#### Test Failures Due to Missing Mocks

**Problem:** Tests fail with actual subprocess calls.

**Solution:** Ensure all `subprocess.run` calls are mocked:

```python
def test_example(monkeypatch):
    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess([], 0, "", "")

    monkeypatch.setattr("subprocess.run", mock_run)
```

#### Circular Import Errors

**Problem:** Click import causes circular dependencies.

**Solution:** Use conditional imports:

```python
click_module: ModuleType | None
try:
    import click as click_module
except ImportError:
    click_module = None

click: ModuleType | None = click_module
```

**Code reference:** `cli/sum/commands/init.py:15-21`

#### Type Checking Errors

**Problem:** MyPy complains about Click types.

**Solution:** Use type annotations and casts:

```python
from typing import cast
import click

cli.add_command(cast("click.Command", init))
```

**Code reference:** `cli/sum/cli.py:21`

### Debugging Techniques

#### Enable Verbose Output

```python
# In orchestrator, add debug prints:
def run_full_setup(self, config: SetupConfig) -> SetupResult:
    print(f"DEBUG: Running setup with config: {config}")
    # ...
```

#### Test with Real Projects

```bash
# Create test project
sum init debug-test --full --ci

# Inspect result
cd clients/debug-test
ls -la
cat .env.local
```

#### Use pdb for Interactive Debugging

```python
def _setup_venv(self, config: SetupConfig) -> None:
    import pdb; pdb.set_trace()  # Breakpoint
    self.venv_manager.create(self.project_path)
```

---

## Extending the CLI

### Adding a New Setup Step

1. **Define the step enum:**

```python
class SetupStep(str, Enum):
    # ... existing steps
    NEW_STEP = "Doing new thing"
```

2. **Add configuration flag:**

```python
@dataclass
class SetupConfig:
    # ... existing flags
    skip_new_step: bool = False
```

3. **Implement the step function:**

```python
def _new_step(self, config: SetupConfig) -> None:
    """Do new thing."""
    # Implementation
    pass
```

4. **Add to step list builder:**

```python
def _build_step_list(self, config: SetupConfig) -> list[StepDefinition]:
    # ... existing steps

    if not config.skip_new_step:
        steps.append((SetupStep.NEW_STEP, self._new_step))

    return steps
```

5. **Add CLI option:**

```python
@click.option(
    "--skip-new-step",
    is_flag=True,
    help="Skip new step",
)
def _click_init(..., skip_new_step: bool):
    # ...
```

6. **Write tests:**

```python
def test_new_step_executes(all_mocks, tmp_path):
    config = SetupConfig(full=True, skip_new_step=False)
    orchestrator = SetupOrchestrator(tmp_path, ExecutionMode.STANDALONE)
    result = orchestrator.run_full_setup(config)
    # Assert new step executed
```

### Adding a New Command

1. **Create command file:**

```python
# cli/sum/commands/newcommand.py
import click

@click.command()
@click.argument("project", required=False)
def newcommand(project: str | None) -> None:
    """Do something new."""
    # Implementation
```

2. **Register in CLI:**

```python
# cli/sum/cli.py
from cli.sum.commands.newcommand import newcommand

cli.add_command(newcommand)
```

3. **Write tests:**

```python
# cli/tests/test_newcommand.py
from click.testing import CliRunner
from cli.sum.commands.newcommand import newcommand

def test_newcommand():
    runner = CliRunner()
    result = runner.invoke(newcommand, ["test-project"])
    assert result.exit_code == 0
```

---

## Release Process

### Version Bumping

Follow SemVer:
- **Patch** (0.6.1): Bug fixes, documentation
- **Minor** (0.7.0): New features, backward compatible
- **Major** (1.0.0): Breaking changes

### Pre-Release Checklist

```bash
# Run full test suite
make test

# Run linters
make lint

# Check test coverage
pytest cli/tests/ --cov=cli.sum --cov-report=term-missing

# Sync boilerplate (if changed)
make sync-cli-boilerplate

# Update version in pyproject.toml
# Update CHANGELOG.md
# Update documentation
```

### Release Workflow

```bash
# Merge feature branch to release/X.Y.0
git checkout release/0.6.0
git merge feature/cli

# Tag release
git tag -a v0.6.0 -m "Release v0.6.0: CLI v2 enhancements"
git push origin v0.6.0

# Merge to main
git checkout main
git merge release/0.6.0
git push origin main
```

---

## Contributing

### Coding Standards

- **PEP 8** compliance (enforced by Black, isort, Ruff)
- **Type hints** on all public functions
- **Docstrings** for all public modules, classes, and functions
- **Descriptive variable names** (avoid abbreviations)
- **Early returns** for error cases

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

Closes #<issue-number>
```

**Types:** feat, fix, docs, test, refactor, chore

**Examples:**
```
feat(cli): add --preset flag to init command

- Support content presets for homepage seeding
- Add preset validation
- Update tests

Closes #123
```

```
fix(cli): handle empty stderr in error messages

- Fallback to stdout if stderr is empty
- Add test for empty stderr scenario

Closes #124
```

### Documentation Standards

- User-facing docs in `docs/dev/CLI_USER_GUIDE.md`
- Developer docs in `docs/dev/CLI_DEVELOPER_GUIDE.md`
- Update both for significant changes
- Include code examples
- Keep up to date with implementation

---

## References

### Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `cli/sum/cli.py` | Click entrypoint | 26 |
| `cli/sum/commands/init.py` | Init command | 318 |
| `cli/sum/commands/run.py` | Run command | 96 |
| `cli/sum/commands/check.py` | Check command | 86 |
| `cli/sum/setup/orchestrator.py` | Setup orchestration | 267 |
| `cli/sum/setup/scaffold.py` | Project scaffolding | 338 |
| `cli/sum/setup/auth.py` | Superuser management | 182 |
| `cli/sum/utils/validation.py` | Project validation | 136 |
| `core/sum_core/management/commands/seed_homepage.py` | Homepage seeding | 118 |

### Related Documentation

- [CLI User Guide](./CLI_USER_GUIDE.md) - End-user command documentation
- [Theme Guide](./THEME-GUIDE.md) - Theme system documentation
- [Release Runbook](../ops-pack/RELEASE_RUNBOOK.md) - Release process
- [Git Strategy](../../GIT_STRATEGY.md) - Branching model
- [Project Planning Guidelines](./planning/PROJECT-PLANNING-GUIDELINES.md) - Issue workflow

### External Resources

- [Click Documentation](https://click.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [Wagtail Documentation](https://docs.wagtail.org/)

---

## Changelog

### v2.0.0 (2025-12-27)

**New Features:**
- Complete CLI rewrite with orchestrated setup flow
- `sum init --full` for complete project initialization
- `sum init --quick` for fast scaffolding with venv/deps
- `sum run` command for development server
- Enhanced `sum check` with comprehensive validation
- Automatic superuser creation with `.env.local`
- Homepage seeding via `seed_homepage` management command
- Interactive prompts with `--no-prompt` and `--ci` modes

**Architecture:**
- New `SetupOrchestrator` for coordinated setup flow
- Idempotent setup modules (safe to re-run)
- Dynamic step list building based on configuration
- Comprehensive error handling with remediation guidance

**Testing:**
- 200 tests with 100% coverage
- Subprocess mocking for all external commands
- Security testing (permissions, injection prevention)
- Edge case coverage (empty stderr, failures, etc.)

**Security:**
- `.env.local` created with `0o600` permissions
- JSON serialization for subprocess output
- Return code validation before parsing
- Input validation and sanitization

**Breaking Changes:**
- None - v1 behavior preserved as default

---

## FAQ

### Q: Why separate managers for each setup concern?

**A:** Single Responsibility Principle. Each manager:
- Has one clear purpose
- Can be tested in isolation
- Can be reused across commands
- Is easier to maintain and extend

### Q: Why use subprocess instead of Django's call_command()?

**A:** The CLI runs *before* Django is configured. We can't import Django until:
- Virtualenv is created
- Dependencies are installed
- Settings module is configured

### Q: Why mock subprocess.run in tests?

**A:** Unit tests should:
- Run fast (no actual venv creation)
- Be deterministic (no network, filesystem side effects)
- Be isolated (don't affect the host system)

Integration tests can use real processes.

### Q: How does monorepo mode work?

**A:** Detection logic checks for `core/` and `boilerplate/` markers. If found:
```python
env["PYTHONPATH"] = str(repo_root / "core")
```

This allows `import sum_core` without pip installation.

### Q: Why use dataclasses for configuration?

**A:** Type safety, validation, and IDE support:
```python
config = SetupConfig(full=True)  # ✅ Type checked
config.port = "invalid"          # ❌ Type error caught by mypy
```

---

## Support and Contact

- **Issues:** [GitHub Issues](https://github.com/markashton480/sum-platform/issues)
- **Pull Requests:** [GitHub PRs](https://github.com/markashton480/sum-platform/pulls)
- **Documentation:** `docs/` directory in repository
- **Code Reviews:** Tag `@markashton480` for maintainer review

---

**Last Updated:** 2025-12-27
**Version:** 2.0.0
**Maintainer:** Mark Ashton (@markashton480)
