---
name: Task
about: Executable task linked to a Work Order
title: "TASK: <title>"
labels: ["type:task"]
projects: ["markashton480/12"]
---

# **Title:** `TASK: <TASK-ID> <title>`

---

## Parent

**Work Order:** <#WORK-ORDER-ID> - <WORK-ORDER-TITLE>

---

## Branch

| Branch                         | Target            |
| ------------------------------ | ----------------- |
| `feature/<scope>/<seq>-<slug>` | `feature/<scope>` |

```bash
git checkout feature/<scope>
git pull origin feature/<scope>
git checkout -b feature/<scope>/<seq>-<slug>
git push -u origin feature/<scope>/<seq>-<slug>
```

---

# Objective

<Overview of what this task is doing>

---

## Deliverable

This subtask will deliver:

- ***

## Boundaries

### Do

-
-

### Do NOT

- ❌ Do not modify `<file>` — owned by #ZZZ
- ❌ Do not change `<shared-config>` — handled separately

---

## Acceptance Criteria

- [ ]
- [ ]
- [ ]

---

## Test Commands

```bash
make lint
make test

# Or specific tests
python -m pytest tests/<component>/test_<feature>.py -v
```

---

## Files Expected to Change

```
core/sum_core/<component>/<file>.py
tests/<component>/test_<feature>.py
```

---

## Dependencies

**Depends On:**

- [ ] #XXX must be merged first

**Blocks:**

- #ZZZ is waiting for this

---

## Risk

**Level:** Low / Med / High

**Why:**

---

## Labels

- [ ] `type:task`
- [ ] `agent:*`
- [ ] `component:*`
- [ ] `risk:*`
- [ ] Milestone: `vX.Y.Z` <see the VD (Version Declaration)>

---

## Project Fields

- [ ] Agent: (assigned)
- [ ] Model Planned: (selected)
- [ ] Component: (selected)
- [ ] Change Type: feat / fix / chore / refactor / docs
- [ ] Risk: (selected)
- [ ] Release: `vX.Y.Z`

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
<type>(<scope>): <summary>

- Detail 1
- Detail 2

Closes #NNN
```

## PR Description

Use markdown + provide a full work report in the PR description.
