# Task

**Title:** `WO-CI-002: Configure Claude review permissions`

---

## Parent

**Work Order:** WO: CI & Documentation Enhancements (v0.6.1)
**Tracking Issue:** #225

---

## Branch

| Branch | Target |
|--------|--------|
| `chore/ci-docs-improvements/002-claude-review` | `chore/ci-docs-improvements` |

```bash
git checkout chore/ci-docs-improvements
git pull origin chore/ci-docs-improvements
git checkout -b chore/ci-docs-improvements/002-claude-review
git push -u origin chore/ci-docs-improvements/002-claude-review
```

---

## Deliverable

This task will deliver:

- Claude review workflow configured with proper permissions
- Workflow can submit PR reviews
- Documentation of review workflow usage

---

## Boundaries

### Do

- Configure `.github/workflows/claude-review.yml` with correct permissions
- Add `pull-requests: write` permission
- Test that workflow can submit reviews
- Document the workflow trigger and behavior

### Do NOT

- ❌ Do not modify review logic
- ❌ Do not add new review capabilities
- ❌ Do not change other workflows
- ❌ Do not modify repository settings (just workflow file)

---

## Acceptance Criteria

- [ ] Claude review workflow has `pull-requests: write` permission
- [ ] Workflow can successfully submit reviews on PRs
- [ ] Workflow triggers correctly (on PR open/update)
- [ ] Review comments are posted correctly
- [ ] Documentation updated

---

## Test Commands

```bash
make lint
make test

# Verify workflow syntax
# actionlint .github/workflows/claude-review.yml

# Test: Open a test PR and verify review is submitted
```

---

## Files Expected to Change

```
.github/
└── workflows/
    └── claude-review.yml       # Modified: permissions
```

---

## Dependencies

**Depends On:**
- [ ] None — can run in parallel with other tasks

**Blocks:**
- Nothing

---

## Risk

**Level:** Low

**Why:**
- Simple permission change
- Easy to test and verify

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
chore(ci): enable Claude review workflow to submit reviews

- Add pull-requests: write permission
- Verify review submission works correctly

Closes #225
```

---

## Implementation Notes

### Permission Configuration

```yaml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write  # Required for submitting reviews

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      # ... review steps
```
