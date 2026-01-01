# Work Order

**Title:** `WO: CLI v2 Publishing & Distribution (v0.6.1)`

---

## Parent

**Version Declaration:** #460 (VD-0.6.1)
**Tracking Issue:** #457

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-publishing` | `release/0.6.1` |

```bash
git checkout release/0.6.1
git checkout -b feature/cli-publishing
git push -u origin feature/cli-publishing
```

---

## Objective

- [ ] Package CLI v2 for PyPI distribution
- [ ] Test installation from PyPI test instance before production release
- [ ] Update installation documentation with pip instructions
- [ ] Verify CLI works correctly in fresh environments
- [ ] Ensure `sum --version` returns 2.0.0

---

## Scope

### In Scope

- PyPI packaging configuration (pyproject.toml, setup.py)
- Build and release workflow for CLI
- Installation testing on PyPI Test
- Documentation updates for pip installation
- Version verification testing

### Out of Scope

- New CLI features or commands
- CLI architecture changes
- sum-core packaging (separate from CLI)

---

## Subtasks

| # | Task | Issue | Branch | Status |
|---|------|-------|--------|--------|
| 1 | WO-CLI-001: Configure PyPI packaging | #467 | `feature/cli-publishing/001-pypi-config` | 🔲 |
| 2 | WO-CLI-002: Test on PyPI Test instance | #468 | `feature/cli-publishing/002-pypi-test` | 🔲 |
| 3 | WO-CLI-003: Update installation documentation | #469 | `feature/cli-publishing/003-docs-update` | 🔲 |
| 4 | WO-CLI-004: Publish to PyPI production | #470 | `feature/cli-publishing/004-pypi-publish` | 🔲 |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Affected Paths

```
cli/
├── pyproject.toml          # Modified: PyPI metadata
├── setup.py                # Modified/New: build configuration
├── MANIFEST.in             # New: package includes
└── sum_cli/
    └── __init__.py         # Modified: version bump

docs/
├── cli.md                  # Modified: installation instructions
└── quickstart.md           # Modified: pip install instructions
```

---

## Verification

### After Each Task Merge

```bash
git checkout feature/cli-publishing
git pull origin feature/cli-publishing
make lint && make test
```

### Before Feature PR

```bash
# Test installation in fresh virtualenv
python -m venv test-env
source test-env/bin/activate
pip install sum-cli  # from PyPI test first
sum --version  # should return 2.0.0
sum init test-project --quick
```

---

## Risk

**Level:** Medium

**Factors:**
- PyPI packaging errors can break user installations
- First-time PyPI publishing has learning curve

**Mitigation:**
- Test on PyPI Test instance before production
- Verify installation in multiple Python versions
- Clear rollback plan if issues discovered

---

## Labels

- [ ] `type:work-order`
- [ ] `component:cli`
- [ ] `risk:medium`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] All subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] CLI v2.0.0 published to PyPI
- [ ] `pip install sum-cli` works in fresh virtualenv
- [ ] `sum --version` returns 2.0.0
- [ ] Documentation updated with pip installation
- [ ] Feature branch merged to release branch
- [ ] Version Declaration updated
