# Task

**Title:** `WO-CLI-001: Configure PyPI packaging`

---

## Parent

**Work Order:** WO: CLI v2 Publishing & Distribution (v0.6.1)
**Tracking Issue:** #279

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-publishing/001-pypi-config` | `feature/cli-publishing` |

```bash
git checkout feature/cli-publishing
git pull origin feature/cli-publishing
git checkout -b feature/cli-publishing/001-pypi-config
git push -u origin feature/cli-publishing/001-pypi-config
```

---

## Deliverable

This task will deliver:

- Complete PyPI packaging configuration in `cli/pyproject.toml`
- MANIFEST.in for proper file inclusion
- Build configuration for wheel and sdist
- Version set to 2.0.0
- Proper package metadata (author, license, classifiers)

---

## Boundaries

### Do

- Configure `cli/pyproject.toml` for PyPI publishing
- Add package metadata (name: `sum-cli`, author, license, etc.)
- Set version to 2.0.0 in `cli/sum_cli/__init__.py`
- Create MANIFEST.in for proper file inclusion
- Add Python version classifiers (3.10, 3.11, 3.12)
- Configure entry points for `sum` command
- Test local build with `python -m build`

### Do NOT

- ❌ Do not publish to PyPI in this task
- ❌ Do not modify CLI functionality
- ❌ Do not add new CLI commands
- ❌ Do not change sum-core packaging

---

## Acceptance Criteria

- [ ] `cli/pyproject.toml` has complete PyPI metadata
- [ ] Package name is `sum-cli`
- [ ] Version is `2.0.0`
- [ ] Entry point `sum` is configured
- [ ] `python -m build` creates wheel and sdist successfully
- [ ] Package installs correctly from local wheel
- [ ] `sum --version` returns `2.0.0` after local install

---

## Test Commands

```bash
make lint
make test

# Build package
cd cli
python -m build

# Test local install
python -m venv test-env
source test-env/bin/activate
pip install dist/sum_cli-2.0.0-py3-none-any.whl
sum --version  # should return 2.0.0
```

---

## Files Expected to Change

```
cli/
├── pyproject.toml          # Modified: PyPI metadata
├── MANIFEST.in             # New: package file inclusion
└── sum_cli/
    └── __init__.py         # Modified: version = "2.0.0"
```

---

## Dependencies

**Depends On:**
- [ ] None — this is the first task

**Blocks:**
- WO-CLI-002: Test on PyPI Test instance

---

## Risk

**Level:** Low

**Why:**
- Standard Python packaging patterns
- Local testing verifies configuration

**Mitigation:**
- Test local build and install thoroughly
- Review against PyPI packaging guidelines

---

## Labels

- [ ] `type:task`
- [ ] `component:cli`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

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
feat(cli): configure PyPI packaging for CLI v2.0.0

- Add complete PyPI metadata to pyproject.toml
- Set package name to sum-cli, version 2.0.0
- Configure entry point for sum command
- Add MANIFEST.in for file inclusion
- Verify local build and install works

Closes #TBD
```
