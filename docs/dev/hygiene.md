# Repository Hygiene Standards

To maintain a deterministic and quiet development environment, please follow these guidelines.

---

## Lint & CI Contract

### Canonical Commands

| Command       | Purpose                               |
| ------------- | ------------------------------------- |
| `make lint`   | Run all linting and type-checking     |
| `make test`   | Run the full test suite with coverage |
| `make format` | Auto-format code (Black + isort)      |

### In-Scope Directories

The following directories are **always** linted and type-checked:

- `core/` — The `sum_core` package (the primary product)
- `cli/` — The `sum` CLI tool
- `tests/` — Test suite

### Out-of-Scope Directories

The following directories are **excluded** from linting, type-checking, and coverage:

- `clients/` — Generated or transient client scaffolds (e.g., `cli-check-*`, `cli-theme-*`)
- `boilerplate/` — Template files with intentionally unresolvable placeholders
- `cli/sum_cli/boilerplate/` — Synced copy of the boilerplate used by the CLI scaffolder

**Rationale:** These directories contain generated code, transient test artifacts, or template placeholders that would cause false-positive lint/typecheck errors if processed as standard Python.

### CI Enforcement

The repository uses GitHub Actions to enforce the lint contract:

- **Workflow file:** `.github/workflows/ci.yml`
- **Triggers:**
  - All pull requests targeting `main`
  - All pushes to `main`
- **Gate behavior:**
  - ❌ PR/push **fails** if `make lint` fails
  - ❌ PR/push **fails** if `make test` fails

CI runs in a clean environment and removes stale artifacts (`.coverage`, `.pytest_cache`, transient scaffold dirs) before each run to avoid flaky failures.

### CI Hardening

The workflow includes the following safety measures:

| Setting             | Value                    | Purpose                             |
| ------------------- | ------------------------ | ----------------------------------- |
| `timeout-minutes`   | 15                       | Prevents hung/runaway jobs          |
| `permissions`       | `contents: read`         | Minimal read-only access            |
| `workflow_dispatch` | enabled                  | Allows manual CI runs for debugging |
| `concurrency`       | cancel-in-progress: true | Cancels superseded runs             |

### Branch Protection (Required Runbook)

To enforce CI as a merge gate, configure branch protection for `main`:

1. Go to **Settings → Branches** in the GitHub repository
2. Click **Add rule** (or edit existing `main` rule)
3. Set **Branch name pattern:** `main`
4. Enable the following:
   - ☑️ **Require a pull request before merging**
   - ☑️ **Require status checks to pass before merging**
     - Search and add: `lint-and-test`
   - ☑️ **Require branches to be up to date before merging** (recommended)
   - ☑️ **Require linear history** (optional, keeps commit graph clean)
5. Click **Create** or **Save changes**

**Check name:** The required status check is named `lint-and-test` (the job name in `ci.yml`).

---

## Verification

Before pushing code, run the standard suite:

```bash
make format  # Auto-format code
make lint    # Check style and types
make test    # Run tests
```

---

## Dependencies

- **No ad-hoc `pip install`**: All dependencies must be declared in `pyproject.toml`.
- **Type stubs**: `types-requests` is included in dev dependencies for pyrefly compatibility.

---

## Logging in Tests

If you need to test log output where `propagate=False` (e.g. strict logging config), use the `caplog_propagate` fixture:

```python
def test_logging(caplog_propagate):
    with caplog_propagate("my.logger"):
        # run code
    assert "Expected Log" in caplog.text
```
