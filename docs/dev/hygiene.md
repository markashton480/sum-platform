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

**Rationale:** These directories contain generated code, transient test artifacts, or template placeholders that would cause false-positive lint/mypy errors if processed as standard Python.

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
- **No `types-requests`**: Use modern stubs or `mypy` configuration if needed, but avoid ad-hoc type packages if possible.

---

## Logging in Tests

If you need to test log output where `propagate=False` (e.g. strict logging config), use the `caplog_propagate` fixture:

```python
def test_logging(caplog_propagate):
    with caplog_propagate("my.logger"):
        # run code
    assert "Expected Log" in caplog.text
```
