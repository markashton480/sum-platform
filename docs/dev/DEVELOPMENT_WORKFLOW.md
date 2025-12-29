# SUM Platform: Development Workflow

This document explains the complete development workflow for SUM Platform: **issue hierarchy**, **branch strategy**, and the flow from planning through release.

---

## Overview

We use a **three-level issue hierarchy** and a matching **three-level branch hierarchy**:

- **Version Declaration (VD)** → version boundary + release branch
- **Work Order (WO)** → feature boundary + feature branch
- **Task Ticket (TASK/FIX)** → atomic work + task/fix branch

The goal is to make branching fully deterministic so agents **do not ask** which branch to use.

---

## Issue Hierarchy

```
Version Declaration (VD)
├── Work Order (WO)
│   ├── Task (TASK)
│   └── Fix (FIX)
└── Work Order (WO)
    ├── Task (TASK)
    └── Fix (FIX)
```

### Level 1: Version Declaration (VD)

**Purpose:** Declares what a version contains and its boundaries.

**Title format:**
- `VD: <version> - <title>`

Example:
- `VD: 0.6.0 - Blog Upgrades`

**Maps to branch:** `release/<version>` (e.g. `release/0.6.0`)

---

### Level 2: Work Order (WO)

**Purpose:** A feature or component delivered within a single version.

**Title format:**
- `WO: <feature title>`

Example:
- `WO: Blog Upgrades`

**Maps to branch:** `feature/<work-order-slug>` (e.g. `feature/blog-upgrades`)

**Required in body:**
- Parent VD reference (issue number)

---

### Level 3: Task Tickets (TASK / FIX)

**Purpose:** One atomic unit of work that one agent can complete.

**Title format:**
- `TASK: <short deliverable>`
- `FIX: <bug / regression>`

Examples:
- `TASK: Add category filtering`
- `FIX: Fix the fucking blog`

**Maps to branch:**
- `task/<task-slug>` for TASK issues
- `fix/<task-slug>` for FIX issues

**Required in body:**
- Parent WO reference (issue number)

---

## Branch Hierarchy

Branches mirror the issue hierarchy:

```
main                           Production, tagged releases
  ↑ PR (squash)
develop                        Stable integration, always deployable
  ↑ PR (squash)
release/<version>              Version integration (maps to VD)
  ↑ PR (merge --no-ff)
feature/<work-order-slug>      Feature integration (maps to WO)
  ↑ PR (squash)
task/<task-slug>  OR  fix/<task-slug>   Task work (maps to TASK/FIX)
```

### Naming Rules

- **No trailing slash** (Git branches cannot end with `/`).
- Use **slugified** names for `feature/*`, `task/*`, `fix/*`.

**Slug rules:**
- lower-case
- spaces → `-`
- remove punctuation (keep letters/numbers/hyphens)
- collapse multiple `-`
- trim leading/trailing `-`

Examples:
- `WO: Blog Upgrades` → `feature/blog-upgrades`
- `TASK: Fix the fucking blog` → `task/fix-the-fucking-blog`

---

## PR Targeting Rules

| Your Branch | PR Target |
|------------|-----------|
| `task/*` | `feature/<work-order-slug>` |
| `fix/*` *(in release)* | `feature/<work-order-slug>` |
| `fix/*` *(bypass)* | `develop`, `main`, or `release/*` |
| `docs/*` *(bypass)* | `develop`, `main`, or `release/*` |
| `feature/*` | `release/<version>` |
| `release/*` | `develop` |
| `develop` | `main` |

> **Bypass branches** (`docs/*`, `fix/*` targeting develop/main) require a `## Bypass Justification` section in the PR body.

---

## Merge Strategy

| From → To | Strategy | Why |
|-----------|----------|-----|
| `task/*` / `fix/*` → `feature/*` | Squash | One clean commit per task. |
| `feature/*` → `release/*` | Merge `--no-ff` | Preserve feature boundary. |
| `release/*` → `develop` | Squash | One commit per version. |
| `develop` → `main` | Squash | Clean prod history. |

---

## Execution Flow

### Phase 1: Planning (human)

1. Create a **Version Declaration** issue (`VD: <version> - <title>`)
2. Create the **release branch** from `develop`: `release/<version>`
3. Create **Work Order** issues under the VD
4. Create **Task/Fix** issues under each WO

> Optional: create each `feature/*` branch when the WO is created.
> If not, the **first task** under that WO will create it (see agent flow).

---

### Phase 2: Execution (agent)

Agents are invoked via the GH Issue prompt (e.g. `/gh-issue 123`).

**Agent responsibilities for TASK/FIX issues:**

1. Load the TASK/FIX issue
2. Find the parent WO
3. Find the parent VD (from the WO)
4. Resolve branch names deterministically
5. Ensure `release/<version>` is up to date
6. Ensure `feature/<work-order-slug>` exists (create if missing) and is up to date
7. Create `task/*` or `fix/*` from the feature branch
8. Open a draft PR targeting the feature branch
9. Implement, test, update PR
10. Do **not** merge

---

### Phase 3: Review & Integration (human)

- TASK/FIX PRs are **squash merged** into the feature branch
- When a WO is complete, the feature branch is merged into the release branch with **`--no-ff`**
- When a version is complete, the release branch is **squash merged** into `develop`
- When ready to ship, `develop` is **squash merged** into `main`

---

## Troubleshooting

### Agent can’t resolve branches

Make sure the issue templates are followed:

- TASK/FIX issue body references its parent WO
- WO body references its parent VD
- VD title contains the version string

### Feature branch missing

That’s OK: the first TASK/FIX under a WO is allowed to create the feature branch from the release branch.
