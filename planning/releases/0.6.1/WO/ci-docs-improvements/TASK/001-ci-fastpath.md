# Task

**Title:** `WO-CI-001: Implement docs-only CI fast-path`

---

## Parent

**Work Order:** #462 (WO: CI & Documentation Enhancements)
**Tracking Issue:** #477
**Related Issue:** #229

---

## Branch

| Branch | Target |
|--------|--------|
| `chore/ci-docs-improvements/001-ci-fastpath` | `chore/ci-docs-improvements` |

```bash
git checkout chore/ci-docs-improvements
git pull origin chore/ci-docs-improvements
git checkout -b chore/ci-docs-improvements/001-ci-fastpath
git push -u origin chore/ci-docs-improvements/001-ci-fastpath
```

---

## Deliverable

This task will deliver:

- CI workflow modification to skip expensive jobs for docs-only PRs
- Path-based job filtering using GitHub Actions path filters
- Reduced CI runtime for documentation changes
- Maintained full CI for code changes

---

## Boundaries

### Do

- Modify `.github/workflows/ci.yml` to add path filtering
- Skip test/lint jobs when only docs/* files changed
- Skip test/lint jobs when only .md files changed
- Keep some basic checks (markdown lint, link check) for docs PRs
- Test the filtering logic on a docs-only PR
- Document the fast-path behavior

### Do NOT

- ❌ Do not skip CI entirely for docs PRs (keep basic checks)
- ❌ Do not modify test logic
- ❌ Do not change deployment workflows
- ❌ Do not affect non-docs PRs

---

## Acceptance Criteria

- [ ] Docs-only PRs skip expensive test jobs
- [ ] Docs-only PRs skip expensive lint jobs
- [ ] Basic markdown checks still run on docs PRs
- [ ] Code changes still run full CI
- [ ] Mixed docs+code PRs run full CI
- [ ] CI workflow documented

---

## Test Commands

```bash
make lint
make test

# Test locally by checking workflow syntax
# actionlint .github/workflows/ci.yml

# Verification: Create docs-only PR and observe CI behavior
```

---

## Files Expected to Change

```
.github/
└── workflows/
    └── ci.yml                  # Modified: add path filtering
```

---

## Dependencies

**Depends On:**
- [ ] None — this is the first task

**Blocks:**
- Nothing — can run in parallel with other tasks

---

## Risk

**Level:** Low

**Why:**
- Standard GitHub Actions pattern
- Easy to test and revert

**Mitigation:**
- Test on feature branch first
- Monitor first few docs PRs after merge

---

## Labels

- [ ] `type:task`
- [ ] `component:ci`
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
chore(ci): implement fast-path for docs-only changes

- Add path filtering to skip expensive jobs for docs PRs
- Keep basic markdown checks for docs changes
- Reduce CI runtime for documentation updates

Closes #229
```

---

## Implementation Notes

### Path Filter Pattern

```yaml
jobs:
  lint:
    if: |
      github.event_name == 'push' ||
      !contains(github.event.pull_request.changed_files, 'only docs')
    # OR use paths-filter action:

  changes:
    runs-on: ubuntu-latest
    outputs:
      code: ${{ steps.filter.outputs.code }}
    steps:
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            code:
              - 'core/**'
              - 'cli/**'
              - 'tests/**'
              - 'themes/**'
              - '*.py'
              - 'pyproject.toml'
            docs:
              - 'docs/**'
              - '*.md'

  test:
    needs: changes
    if: needs.changes.outputs.code == 'true'
    # ... rest of job
```
