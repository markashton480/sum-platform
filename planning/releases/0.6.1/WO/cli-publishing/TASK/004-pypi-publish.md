# Task

**Title:** `WO-CLI-004: Publish to PyPI production`

---

## Parent

**Work Order:** WO: CLI v2 Publishing & Distribution (v0.6.1)
**Tracking Issue:** #279

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-publishing/004-pypi-publish` | `feature/cli-publishing` |

```bash
git checkout feature/cli-publishing
git pull origin feature/cli-publishing
git checkout -b feature/cli-publishing/004-pypi-publish
git push -u origin feature/cli-publishing/004-pypi-publish
```

---

## Deliverable

This task will deliver:

- CLI v2.0.0 published to production PyPI
- Verified installation from production PyPI
- Announcement/release notes ready
- GitHub release tag for CLI

---

## Boundaries

### Do

- Build final package (wheel and sdist)
- Upload to production pypi.org
- Verify installation from pypi.org
- Test all basic CLI commands
- Create GitHub release for CLI v2.0.0
- Document the release

### Do NOT

- ❌ Do not modify CLI code
- ❌ Do not change version number (should already be 2.0.0)
- ❌ Do not skip verification steps
- ❌ Do not publish if tests fail

---

## Acceptance Criteria

- [ ] Package uploaded to pypi.org successfully
- [ ] `pip install sum-cli` works
- [ ] `sum --version` returns `2.0.0`
- [ ] `sum init test-project --quick` creates project
- [ ] GitHub release created for CLI v2.0.0
- [ ] Release notes complete

---

## Test Commands

```bash
make lint
make test

# Build and upload to production PyPI
cd cli
python -m build
python -m twine upload dist/*

# Test installation from PyPI
python -m venv test-env
source test-env/bin/activate
pip install sum-cli
sum --version
sum init test-project --quick
ls test-project/
```

---

## Files Expected to Change

```
# No files expected to change in this task
# This is a release/publishing task
```

---

## Dependencies

**Depends On:**
- [ ] WO-CLI-001: Configure PyPI packaging
- [ ] WO-CLI-002: Test on PyPI Test instance
- [ ] WO-CLI-003: Update installation documentation (recommended)

**Blocks:**
- Nothing — this is the final task

---

## Risk

**Level:** Medium

**Why:**
- Production release is permanent (versions can't be reused)
- Users will immediately be affected

**Mitigation:**
- Thorough testing on PyPI Test first
- Verify all functionality before upload
- Have rollback plan (yank if critical issues)

---

## Labels

- [ ] `type:task`
- [ ] `component:cli`
- [ ] `risk:medium`
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
chore(cli): release CLI v2.0.0 to PyPI

- Publish sum-cli 2.0.0 to pypi.org
- Verify installation and functionality
- Create GitHub release

Closes #TBD
```

---

## Pre-Release Checklist

Before publishing:

- [ ] All tests pass (`make lint && make test`)
- [ ] PyPI Test verification completed
- [ ] Documentation updated
- [ ] Version is exactly 2.0.0
- [ ] Changelog updated
- [ ] No uncommitted changes in cli/

## GitHub Release Template

```markdown
# CLI v2.0.0

## Installation

```bash
pip install sum-cli
```

## What's New

- Complete rewrite with enhanced architecture
- New `sum init --full` command for automated project setup
- New `sum run` command with port conflict handling
- Enhanced `sum check` command with additional validations
- Improved error messages and user experience

## Upgrade Notes

If upgrading from v1.x, uninstall the old version first:

```bash
pip uninstall sum-cli
pip install sum-cli
```

## Full Changelog

See CHANGELOG.md for complete details.
```
