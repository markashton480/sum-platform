---
name: Work Order
about: Parent coordination issue for a feature (groups TASK/FIX tickets)
title: "WO: <feature title>"
labels: ["type:work-order"]
projects: ["markashton480/12"]
---

# Work Order: <feature title>

## Parent

**Version Declaration:** #NNN — VD: <version> - <vd title>

## Branch

| Branch | Created From & PR Target |
|---|---|
| `feature/<work-order-slug>` | `release/<version>` |

> **Branch name rule:** slugify the WO title (after `WO:`).
>
> Example: `WO: Blog Upgrades` → `feature/blog-upgrades`

```bash
# Always branch from the release branch
git checkout release/<version>
git pull origin release/<version>

# Create (or update) the feature branch
git checkout -b feature/<work-order-slug>
git push -u origin feature/<work-order-slug>
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

### Out of Scope

-

---

## Subtasks

Create TASK/FIX issues under this WO.

| # | Ticket | Branch | Status |
|---|---|---|---|
| 1 | #XXX: TASK: <title> | `task/<task-slug>` | 🔲 |
| 2 | #YYY: FIX: <title> | `fix/<task-slug>` | 🔲 |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Verification

After each task PR is merged into the feature branch:

```bash
git checkout feature/<work-order-slug>
git pull origin feature/<work-order-slug>
make lint && make test
```

Before opening the feature PR to the release branch:

```bash
git checkout feature/<work-order-slug>
git pull origin feature/<work-order-slug>
make lint && make test
```

---

## Definition of Done

- [ ] All TASK/FIX PRs squash-merged into `feature/<work-order-slug>`
- [ ] `make lint && make test` passes on the feature branch
- [ ] Feature PR opened: `feature/<work-order-slug>` → `release/<version>`
