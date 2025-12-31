# Task

**Title:** `WO-CLI-002: Test on PyPI Test instance`

---

## Parent

**Work Order:** WO: CLI v2 Publishing & Distribution (v0.6.1)
**Tracking Issue:** #457

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-publishing/002-pypi-test` | `feature/cli-publishing` |

```bash
git checkout feature/cli-publishing
git pull origin feature/cli-publishing
git checkout -b feature/cli-publishing/002-pypi-test
git push -u origin feature/cli-publishing/002-pypi-test
```

---

## Deliverable

This task will deliver:

- Successful upload to PyPI Test (test.pypi.org)
- Verified installation from PyPI Test
- Documentation of the test process
- Confirmation that package works correctly

---

## Boundaries

### Do

- Build package (wheel and sdist)
- Upload to test.pypi.org using twine
- Install from test.pypi.org in fresh virtualenv
- Verify all commands work correctly
- Document any issues found
- Fix packaging issues if discovered

### Do NOT

- ❌ Do not publish to production PyPI
- ❌ Do not modify CLI functionality
- ❌ Do not change version number
- ❌ Do not skip testing steps

---

## Acceptance Criteria

- [ ] Package uploaded to test.pypi.org successfully
- [ ] `pip install --index-url https://test.pypi.org/simple/ sum-cli` works
- [ ] `sum --version` returns `2.0.0`
- [ ] `sum --help` works correctly
- [ ] Basic `sum init` functionality works
- [ ] No dependency issues during install

---

## Test Commands

```bash
make lint
make test

# Build and upload to test.pypi.org
cd cli
python -m build
python -m twine upload --repository testpypi dist/*

# Test installation from test.pypi.org
python -m venv test-env
source test-env/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ sum-cli
sum --version
sum --help
```

---

## Files Expected to Change

```
# No files expected to change in this task
# This is a testing/verification task
```

---

## Dependencies

**Depends On:**
- [ ] WO-CLI-001: Configure PyPI packaging

**Blocks:**
- WO-CLI-004: Publish to PyPI production

---

## Risk

**Level:** Low

**Why:**
- Test PyPI is for testing, no production impact
- Easy to re-upload with fixes

**Mitigation:**
- Test thoroughly before production upload
- Document any issues found

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
chore(cli): verify CLI package on PyPI Test

- Upload sum-cli 2.0.0 to test.pypi.org
- Verify installation and basic functionality
- Confirm ready for production release

Closes #TBD
```

---

## Implementation Notes

### PyPI Test Credentials

You'll need a PyPI Test account and API token:
1. Create account at https://test.pypi.org
2. Generate API token in account settings
3. Configure in `~/.pypirc` or use `--username __token__`

### Common Issues

- **Dependency not found:** Use `--extra-index-url https://pypi.org/simple/` to get dependencies from real PyPI
- **Version already exists:** Bump micro version for testing (2.0.0.dev1)
- **Invalid metadata:** Check pyproject.toml for required fields
