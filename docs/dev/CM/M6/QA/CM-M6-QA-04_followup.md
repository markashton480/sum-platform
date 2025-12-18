# CM Task Report: CM-M6-QA-04 — Lint/Typecheck Contract Hardening

## Investigation Results

### 1. Current `make lint` Commands

Before hardening, `make lint` executed:

```makefile
ruff check . --config pyproject.toml
$(if $(MYPY_SOFT),mypy core cli tests --exclude '^clients/' || true,mypy core cli tests --exclude '^clients/')
black --check core cli tests
isort --check-only core cli tests
```

### 2. CI Alignment

No in-repo GitHub Workflows were found. `make lint` remains the authoritative entrance for local and future CI runs.

### 3. Black "No Python files" Mystery

Prior inconsistencies were likely due to Black's discovery logic when mixed with the monorepo structure and lack of explicit `extend-exclude` for `clients/` and `boilerplate/` in `pyproject.toml`. By defining canonical targets and hardening `extend-exclude`, discovery is now deterministic.

### 4. `clients/` Directory Mapping

- `clients/sum_client`: Persistent sample/test client.
- `clients/cli-check-*`: Transient directories created/deleted by `cli/tests/test_cli_init_and_check.py`.
- Both are now explicitly excluded from global linting/typechecking to prevent environmental noise.

## Implementation Summary

### Before vs After Snippets

#### `Makefile`

**Before:**

```makefile
lint:
	ruff check . --config pyproject.toml
	$(if $(MYPY_SOFT),mypy core cli tests --exclude '^clients/' || true,mypy core cli tests --exclude '^clients/')
	black --check core cli tests
	isort --check-only core cli tests
```

**After:**

```makefile
lint: ## Run all linting and typechecking (strict)
	ruff check . --config pyproject.toml
	mypy core cli tests
	black --check core cli tests
	isort --check-only core cli tests
```

#### `pyproject.toml` (Ruff)

**Before:**

```toml
[tool.ruff]
select = [...]
ignore = [...]
```

**After:**

```toml
[tool.ruff]
# ...
[tool.ruff.lint]
select = [...]
ignore = [...]
```

## Lint Contract

- **In Scope:** `core/`, `cli/`, `tests/`
- **Excluded:** `clients/`, `boilerplate/`
- **Rationale:** `clients/` contains generated/transient code that may contain placeholders or temporary state. `boilerplate/` contains template files with intentionally unresolvable placeholders (e.g., `{{ project_name }}`) that trigger lint errors if parsed as standard Python.

## Verification Logs

- `make lint`: **PASS** (deterministic, no warnings)
- `make test`: **PASS** (709 tests)
- **Blocking Check:** Confirmed that `mypy` failure blocks `make lint` with Exit Code 2.

---

_Signed-off by QA / Tooling Engineer_
