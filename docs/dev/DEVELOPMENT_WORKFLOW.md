# SUM Platform: Development Workflow

This document explains the complete development workflow for SUM Platform, including issue hierarchy, branch strategy, and the flow from planning through release.

---

## Overview

We use a **hierarchical system** where GitHub Issues map directly to Git branches. This enables:

- Parallel work by multiple agents without conflicts
- Clear scope boundaries at every level
- Automated auditing to catch scope creep
- Clean git history with logical groupings

---

## Issue Hierarchy

All work is organized into three levels of GitHub Issues:

```
Version Declaration (VD)
├── Work Order (WO)
│   ├── Task
│   ├── Task
│   └── Task
└── Work Order (WO)
    ├── Task
    └── Task
```

### Level 1: Version Declaration (VD)

**Purpose:** Defines what a version will contain and its boundaries.

**Format:**
- Title: `Version Declaration: v0.7.0`
- Labels: `type:version-declaration`
- Milestone: `v0.7.0`

**Contains:**
- Statement of intent (what this version IS and IS NOT)
- List of planned Work Orders
- Expected metrics (approximate commits, lines changed)
- Success criteria

**Example:**
```markdown
# Version Declaration: v0.7.0

## Intent
This version introduces the dynamic form system and blog infrastructure.

## Scope
### IS
- Dynamic form definitions (FormDefinition snippet)
- Form field blocks (text, select, checkbox, etc.)
- Blog category system
- Blog listing and detail pages

### IS NOT
- Form submission handling (v0.8.0)
- Blog comments (v0.9.0)
- Search functionality (backlog)

## Work Orders
- [ ] WO: Dynamic Form System (#100)
- [ ] WO: Blog Infrastructure (#101)

## Expected Metrics
- Commits: ~20-30
- Lines: ~+2,000
- Files: ~25
```

### Level 2: Work Order (WO)

**Purpose:** Defines a feature or component to be built within a version.

**Format:**
- Title: `WO: Dynamic Form System`
- Labels: `type:work-order`, `component:<scope>`
- Parent: Version Declaration (via sub-issue)

**Contains:**
- Feature description
- List of tasks (sub-issues)
- Dependencies on other WOs (if any)
- Acceptance criteria for the feature as a whole

**Critical:** Must have a `component:*` label (e.g., `component:forms`). This determines the feature branch name.

**Example:**
```markdown
# WO: Dynamic Form System

Part of: #90 (Version Declaration: v0.7.0)

## Description
Implement a flexible form definition system that allows forms to be 
defined as Wagtail snippets and rendered dynamically.

## Tasks
- [ ] #111 FormDefinition snippet model
- [ ] #112 Form field blocks (text, select, checkbox)
- [ ] #113 DynamicFormBlock for StreamField
- [ ] #114 Form rendering templates

## Acceptance Criteria
- [ ] Forms can be defined in Wagtail admin
- [ ] Forms render correctly on frontend
- [ ] Field validation works
- [ ] All tasks have passing tests
```

### Level 3: Task

**Purpose:** A single, atomic unit of work that one agent can complete.

**Format:**
- Title: `FormDefinition snippet model`
- Labels: `type:task`, `component:<scope>`
- Parent: Work Order (via sub-issue or "Part of: #NNN" in body)

**Contains:**
- Clear description of what to implement
- Acceptance criteria (specific, testable)
- Boundaries (Do / Do NOT sections)
- Dependencies (blocked by)

**Critical:** Must reference parent WO either via GitHub sub-issue hierarchy or with "Part of: #NNN" in the issue body.

**Example:**
```markdown
# FormDefinition snippet model

Part of: #100 (WO: Dynamic Form System)

## Description
Create the FormDefinition Wagtail snippet that stores form metadata.

## Acceptance Criteria
- [ ] FormDefinition model with name, slug, description fields
- [ ] Registered as Wagtail snippet
- [ ] Admin UI accessible and functional
- [ ] Unit tests for model

## Boundaries

### Do
- Create model in core/sum_core/models/
- Add to admin via snippets
- Write model tests

### Do NOT
- Create form field blocks (Task #112)
- Create rendering templates (Task #114)
- Add to any pages yet
```

---

## Branch Hierarchy

Git branches mirror the issue hierarchy:

```
main                           Production, tagged releases
  ↑ PR (squash)
develop                        Stable integration, always deployable
  ↑ PR (squash)
release/0.7.0                  Version integration (maps to VD)
  ↑ PR (merge --no-ff)
feature/forms                  Feature integration (maps to WO)
  ↑ PR (squash)
task/forms/issue-111-...       Task work (maps to Task)
```

### Branch Types

| Branch | Created From | Purpose | Lifetime |
|--------|--------------|---------|----------|
| `main` | — | Production releases | Permanent |
| `develop` | `main` | Integration of completed versions | Permanent |
| `release/X.Y.0` | `develop` | Version work (one per VD) | Until version ships |
| `feature/<scope>` | `release/X.Y.0` | Feature work (one per WO) | Until WO complete |
| `task/<scope>/issue-N-*` | `feature/<scope>` | Task work (one per task) | Until task complete |

### Why `task/` Instead of `feature/<scope>/`?

Git cannot have both `feature/forms` (a branch) and `feature/forms/001-...` (a sub-branch) simultaneously — they conflict as file paths under `refs/heads/`. 

Task branches use the `task/` prefix to avoid this conflict while still organizing by scope.

### Standalone Branches

For issues without a parent WO (bug fixes, small improvements):

| Type | Base | Branch Pattern |
|------|------|----------------|
| Bug fix | `develop` | `fix/<scope>-issue-N-<slug>` |
| Feature | `develop` | `feat/<scope>-issue-N-<slug>` |

---

## Issue ↔ Branch Mapping

```
ISSUES                                  BRANCHES
────────────────────────────────────────────────────────────

Version Declaration: v0.7.0      ←→     release/0.7.0
│
├── WO: Dynamic Forms            ←→     feature/forms
│   │   (component:forms)
│   │
│   ├── Task #111                ←→     task/forms/issue-111-formdefinition
│   ├── Task #112                ←→     task/forms/issue-112-field-blocks
│   └── Task #113                ←→     task/forms/issue-113-dynamic-form-block
│
└── WO: Blog System              ←→     feature/blog
    │   (component:blog)
    │
    ├── Task #114                ←→     task/blog/issue-114-categories
    └── Task #115                ←→     task/blog/issue-115-blog-pages
```

---

## Execution Flow

### Phase 1: Planning (Human)

1. **Create Version Declaration issue**
   - Define scope, intent, boundaries
   - List planned Work Orders
   - Set expected metrics

2. **Create release branch**
   ```bash
   git checkout develop
   git checkout -b release/0.7.0
   git push -u origin release/0.7.0
   ```

3. **Create Work Order issues** (as sub-issues of VD)
   - Each WO must have `component:*` label
   - List planned tasks

4. **Create feature branches** (one per WO)
   ```bash
   git checkout release/0.7.0
   git checkout -b feature/forms
   git push -u origin feature/forms
   ```

5. **Create Task issues** (as sub-issues of WO)
   - Each task must reference parent WO
   - Define acceptance criteria and boundaries

### Phase 2: Execution (Agent)

Agent receives task via slash command:

```
/gh-issue 111
```

**What the agent does:**

1. **Load issue #111**
   - Extract acceptance criteria, boundaries
   - Find parent reference: "Part of: #100"

2. **Resolve branch hierarchy**
   - Load WO #100 → find `component:forms` label
   - Base branch = `feature/forms`
   - Task branch = `task/forms/issue-111-formdefinition`

3. **Create branch and draft PR**
   - Branch from `feature/forms`
   - Open draft PR targeting `feature/forms`

4. **Implement**
   - Follow acceptance criteria
   - Respect boundaries
   - Add tests

5. **Validate**
   - `make lint` ✓
   - `make test` ✓

6. **Finalize PR**
   - Update description
   - Address review feedback
   - Ensure CI green

7. **Done** — Agent does NOT merge

### Phase 3: Task Review (Human)

1. Review the PR
2. Request changes or approve
3. **Squash merge** into `feature/forms`
4. Delete task branch

### Phase 4: Work Order Completion (Human)

When all tasks for a WO are merged:

1. **Open PR:** `feature/forms` → `release/0.7.0`
2. **Automated audit runs** (medium-level check)
3. Review PR — ensure feature is complete
4. **Merge with `--no-ff`** (preserves feature boundary in history)
5. Delete feature branch

### Phase 5: Version Completion (Human)

When all WOs for a version are merged:

1. **Open PR:** `release/0.7.0` → `develop`
2. **Automated audit runs** (full release audit)
   - Compares actual vs declared scope
   - Flags deviations (like PR #154 incident)
3. Review audit results
4. **Squash merge** (one commit per version in develop)
5. Delete release branch

### Phase 6: Release (Human)

When ready to ship:

1. **Open PR:** `develop` → `main`
2. Final audit
3. **Squash merge**
4. **Tag release:** `git tag v0.7.0`
5. Sync to public repository
6. Update changelog

---

## Merge Strategies

| From → To | Strategy | Rationale |
|-----------|----------|-----------|
| Task → Feature | Squash | Clean feature history, hide task iterations |
| Feature → Release | Merge `--no-ff` | Preserve feature boundaries in history |
| Release → Develop | Squash | One commit per version |
| Develop → Main | Squash | Clean release history |
| Hotfix → Main | Squash | Minimal footprint |

---

## PR Targeting Rules

| Your Branch | PR Target |
|-------------|-----------|
| `task/<scope>/issue-N-*` | `feature/<scope>` |
| `feature/<scope>` | `release/X.Y.0` |
| `release/X.Y.0` | `develop` |
| `develop` | `main` |
| `fix/<scope>-issue-N-*` | `develop` |
| `feat/<scope>-issue-N-*` | `develop` |
| `hotfix/*` | `main` |

---

## Labels Required

### On Work Orders
- `type:work-order`
- `component:<scope>` — **Critical:** Determines feature branch name

### On Tasks
- `type:task`
- `component:<scope>` — Should match parent WO
- `type:bug` — If this is a bug fix (affects branch prefix)

### On Version Declarations
- `type:version-declaration`

---

## Automated Checks

### Copilot Code Review (automatic)
- Runs on: All PRs
- Checks: Code quality, style, patterns, method-level improvements, test suggestions

### Claude Strategic Review (`claude-code-review.yml`)
- Runs on: Task PRs, Feature PRs
- Checks:
  - PR targeting compliance (correct base branch)
  - Scope alignment with acceptance criteria
  - Boundary compliance ("Do NOT" sections)
  - AI blunder detection (hallucinated imports, fictional APIs)
  - Regression risk assessment
  - Completeness vs acceptance criteria

### Release Audit (`release-audit.yml`)
- Runs on: PRs to `develop` or `main`
- Checks: Full scope verification against Version Declaration
- Catches: Scope creep, unexpected features, metric deviations

---

## Key Principles

1. **Every issue has a branch** — Clear ownership and traceability
2. **Every branch has an issue** — No orphan work
3. **Version Declaration is the contract** — Audit compares against it
4. **Develop is always deployable** — Only complete versions merge in
5. **Agents don't merge** — Human approval required at every level
6. **Scope boundaries are enforced** — "Do NOT" sections are respected

---

## Quick Reference: Agent Task Execution

When an agent receives `/gh-issue <number>`:

```
1. Load issue
2. Find parent WO (from "Part of: #NNN" or sub-issue hierarchy)
3. Get scope from WO's component:* label
4. Base branch = feature/<scope>
5. Create task/scope/issue-N-slug from base
6. Implement, test, PR
7. Target PR at feature/<scope>
8. Do NOT merge
```

---

## Example: Complete Flow

```
# Planning
VD #90: "Version Declaration: v0.7.0"
├── WO #100: "Dynamic Form System" (component:forms)
│   ├── Task #111: "FormDefinition model"
│   └── Task #112: "Field blocks"
└── WO #101: "Blog System" (component:blog)
    └── Task #113: "Blog categories"

# Branches created
release/0.7.0           (from develop)
├── feature/forms       (from release/0.7.0)
└── feature/blog        (from release/0.7.0)

# Agent executes /gh-issue 111
task/forms/issue-111-formdefinition (from feature/forms)
→ PR #150 targets feature/forms

# Task complete
PR #150 squash-merged into feature/forms

# WO complete (all tasks done)
PR #151: feature/forms → release/0.7.0 (merge --no-ff)

# Version complete (all WOs done)
PR #152: release/0.7.0 → develop (squash)
[Release audit passes]

# Release
PR #153: develop → main (squash)
Tag: v0.7.0
```

---

## Troubleshooting

### Agent can't find base branch
- Ensure WO has `component:*` label
- Ensure `feature/<scope>` branch exists
- Check task references parent WO correctly

### Release audit fails
- Compare PR contents against Version Declaration
- Check for undeclared features or excessive scope
- Split into separate version if needed

### Git ref conflict
- Never create `feature/foo` AND `feature/foo/bar`
- Use `task/<scope>/...` for task branches, not `feature/<scope>/...`
