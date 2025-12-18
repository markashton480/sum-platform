# CM-M6-QA-01 — QA Tooling Investigation Report

## Executive Summary

The investigation confirmed a systemic failure in the QA tooling signal. While `make lint` reports success, it is effectively a "no-op" for several critical checks due to configuration errors and intentional suppression. This state has existed since the initial repository baseline but became a risk during Milestone 6-A as the codebase grew.

---

## 1. Black (Formatter) Audit

### Observed Behaviour

`black --check core cli tests` reports:

> “No Python files are present to be formatted. Nothing to do 😴”

### Root Cause

In `pyproject.toml`, the configuration uses a literal string for the `include` regex:

```toml
include = '\\.pyi?$'
```

In TOML, single-quoted strings (`'...'`) are literal. The double backslash `\\` is not unescaped, meaning Black is searching for the literal characters `\`, `\`, followed by `.py`. No files match this pattern.

### Intent vs Reality

- **Intent**: Ensure all `.py` and `.pyi` files in the specified directories are formatted.
- **Reality**: Zero files are checked.

### Risk Assessment

- **Medium**: Codebases can drift into inconsistent styles, making diffs harder to read and potentially masking logic changes.

---

## 2. Isort (Import Sorting) Audit

### Observed Behaviour

`isort --check-only core cli tests` reports:

> “Skipped 40 files”

### Root Cause

Configuration in `pyproject.toml` explicitly skips migrations and virtual environments:

```toml
skip_glob = ["*/migrations/*", "*/venv/*", "*/.venv/*"]
```

Manual verification (`isort --verbose`) confirms that the 40 skipped files are primarily Django migrations and `__pycache__` directories.

### Intent vs Reality

- **Intent**: Skip auto-generated files (migrations) to avoid unnecessary diffs.
- **Reality**: Matching intent, but the high skip count (relative to ~200 source files) created suspicion of over-exclusion.

### Risk Assessment

- **Low**: Skipping migrations is standard practice. No evidence of core logic files being skipped was found.

---

## 3. Mypy (Type Checker) Audit

### Observed Behaviour

`make lint` passes even when `mypy` finds 32 errors in 18 files.

### Root Cause

The `Makefile` explicitly suppresses Mypy failures:

```makefile
lint:
    ...
    mypy core cli tests --exclude '^clients/' || true
```

The `|| true` ensures the command always returns an exit code of 0.

### Intent vs Reality

- **Intent**: Likely introduced as a temporary measure to allow CI to pass while type hints were being incrementally added.
- **Reality**: Mypy has ceased to function as a "gate," allowing type regressions to accumulate.

### Risk Assessment

- **High**: 32 active errors exist in the codebase. Type safety is not being enforced, increasing the likelihood of runtime `AttributeError` or `TypeError` surfacing in production.

---

## 4. Ruff (Linter) Audit

### Observed Behaviour

`ruff check .` appears to run but manual verbose checks show it only checks a handful of files in some contexts, or relies on defaults instead of the root `pyproject.toml`.

### Root Cause

The presence of `core/pyproject.toml` and `cli/pyproject.toml` (without `[tool.ruff]` sections) causes Ruff to treat these as separate project roots. When recursing, Ruff hits these files and stops looking for the root `pyproject.toml`. It then falls back to default settings for those directories, which may differ from the project’s intended ruleset.

### Intent vs Reality

- **Intent**: Unified linting across the monorepo via the root `pyproject.toml`.
- **Reality**: Fragmented linting where sub-packages may be uses defaults or skipped entirely depending on command invocation.

### Risk Assessment

- **Medium**: Inconsistent linting rules across the platform can lead to "clean" code in one package being flagged in another, and potential bypass of project-specific rules.

---

## 5. Makefile & Signal Audit

### Observed Behaviour

`make lint` provides a false "Green" signal.

### Root Cause

A combination of:

1.  **Black** finding no files to check (0).
2.  **Mypy** failures being piped to `true` (0).
3.  **Isort** finding no issues in the few files it doesn't skip (0).
4.  **Ruff** potentially using default/loose settings in sub-packages.

### Intent vs Reality

- **Intent**: Provide a quality gate for releases and PRs.
- **Reality**: `make lint` is effectively a no-op that masks 32+ type errors and avoids checking formatting.

### Risk Assessment

- **Critical**: The "Tooling Contract" is broken. Developers and CI systems are blind to QA failures.

---

## Historical Trace Summary

- **Introduction**: These configurations (`|| true`, Black regex, Isort skips) were all introduced in the **initial baseline commits** (circa Dec 8, 2025, e.g., `a210b6b`).
- **Evolution**: They were never "fixed" as the project transitioned from a skeleton to a production-ready platform.
- **Visibility**: The issue was "discovered" now because recent work on Milestone 6-A expected a high level of QA rigor that the baseline was not actually providing.

---

## Appendices

### Relevant Commit SHAs

- `a210b6b4aa264c07b1e8dbb7fc83749530b9eecd`: Initial `Makefile` and `pyproject.toml` with the faulty configurations.

### Tool References

- [Black Documentation on include/exclude](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#include-and-exclude)
- [Ruff Documentation on Configuration Discovery](https://docs.astral.sh/ruff/configuration/#config-discovery)
