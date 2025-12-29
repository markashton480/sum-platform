---
name: Task / Fix
about: Executable ticket linked to a Work Order
title: "TASK: <title>"
labels: ["type:task"]
projects: ["markashton480/12"]
---

# Ticket: <title>

> Use **TASK** for feature work / chores.
> Use **FIX** for bugs/regressions.
>
> Title must start with either:
> - `TASK:`
> - `FIX:`

## Parent

**Work Order:** #YYY — WO: <feature title>

## Branch

| Branch | Base | PR Target |
|---|---|---|
| `task/<task-slug>` **or** `fix/<task-slug>` | `feature/<work-order-slug>` | `feature/<work-order-slug>` |

> **Branch name rule:** slugify the ticket title (after `TASK:`/`FIX:`).
>
> Example: `TASK: Fix the fucking blog` → `task/fix-the-fucking-blog`

```bash
# Always branch from the feature branch
git checkout feature/<work-order-slug>
git pull origin feature/<work-order-slug>

# Create your task/fix branch
git checkout -b task/<task-slug>   # or: fix/<task-slug>
git push -u origin task/<task-slug>
```

---

## Deliverable

This ticket will deliver:

-

---

## Boundaries

### Do

-

### Do NOT

-

---

## Acceptance Criteria

- [ ]
- [ ]

---

## Test Commands

```bash
make lint
make test
```

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR opened to the feature branch
- [ ] PR body includes `Closes #NNN`
- [ ] Ready for human review (agent does **not** merge)
