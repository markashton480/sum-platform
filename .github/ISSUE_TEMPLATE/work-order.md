---
name: Work Order
about: Parent coordination issue for grouped tasks
title: `WO: <Feature Description> (vX.Y.Z)`
labels: ["type:work-order"]
projects: ["markashton480/12"]
---

# Work Order Template

**Title:** `WO: <Feature Description> (vX.Y.Z)`

---

## Parent

**Version Declaration:** #NNN (vX.Y.Z)

---

## Branch

| Branch            | Target          |
| ----------------- | --------------- |
| `feature/<scope>` | `release/X.Y.Z` |

```bash
git checkout release/X.Y.Z
git checkout -b feature/<scope>
git push -u origin feature/<scope>
```

---

## Objective

- [ ]
- [ ]
- [ ]

---

## Scope

### In Scope

-
-

### Out of Scope

-
-

---

## Subtasks

| #   | Issue               | Branch                       | Status |
| --- | ------------------- | ---------------------------- | ------ |
| 1   | #XXX: [Description] | `feature/<scope>/001-<slug>` | 🔲     |
| 2   | #YYY: [Description] | `feature/<scope>/002-<slug>` | 🔲     |
| 3   | #ZZZ: [Description] | `feature/<scope>/003-<slug>` | 🔲     |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Merge Plan

### Order

1. **#XXX** — establishes base models
2. **#YYY** — depends on #XXX
3. **#ZZZ** — integrates both

### Hot Files

| File          | Owner | Notes                   |
| ------------- | ----- | ----------------------- |
| `models.py`   | #XXX  | Others import from here |
| `__init__.py` | Last  | Export consolidation    |

---

## Affected Paths

```
core/sum_core/<component>/
themes/theme_a/templates/sum_core/<component>/
tests/<component>/
```

---

## Verification

### After Each Task Merge

```bash
git checkout feature/<scope>
git pull origin feature/<scope>
make lint && make test
```

### Before Feature PR

```bash
git fetch origin
git rebase origin/release/X.Y.Z
make lint && make test
```

---

## Risk

**Level:** Low / Med / High

**Factors:**

-

**Mitigation:**

-

---

## Labels

- [ ] `type:work-order`
- [ ] `component:*`
- [ ] `risk:*`
- [ ] Milestone: `vX.Y.Z`

---

## Definition of Done

- [ ] All subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] Feature branch merged to release branch (PR approved)
- [ ] Version Declaration updated
