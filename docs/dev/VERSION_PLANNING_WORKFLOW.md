# SUM Platform: Version Planning Workflow (Idea → Plan → VD → WO → TASK)

This document defines a **repeatable planning workflow** that turns an idea into:

- an **Implementation Plan**
- a **Version Declaration (VD)**
- **Work Orders (WOs)**
- **Task/Fix tickets (TASK/FIX)**
- the required **Git branches**
- matching **markdown artifacts committed to `release/<version>`**
- matching **GitHub Issues linked as sub-tasks**

---

## Why this exists

Execution is already deterministic once a TASK/FIX issue exists.

Planning is the missing bridge from **idea → a complete issue tree** (VD → WO → TASK) plus the matching release branch and repo artifacts.

---

## Inputs

You need at least:

- **Problem / opportunity statement**
- **Constraints** (time, must-keep behaviors, compatibility, etc.)
- **Success criteria**
- **Known risks**
- **Target version** (or “next version” if you decide later)

Optional but helpful:

- Screenshots / logs / user stories
- Prior art / references
- Rough architecture direction (or open questions)

---

## Outputs (artifacts)

### A) Repo artifacts (markdown) on `release/<version>`

Suggested structure (you can rename, but keep it consistent):

```
/planning/releases/<version>/
  IMPLEMENTATION_PLAN.md
  VD.md
  WO/
    <work-order-slug>.md
    <work-order-slug>/
      TASK/
        <task-slug>.md
        <task-slug>.md
```

**Rule:** These markdown docs should be “single source of truth” for the ticket bodies (so GH issues and repo docs don’t diverge).

### B) GitHub artifacts

- 1 VD issue
- N WO issues, each linked as a **sub-task** of the VD
- M TASK/FIX issues, each linked as a **sub-task** of exactly one WO
- Optional: milestones, labels, projects (depending on your GH setup)

### C) Branches

- `release/<version>` (created during planning)
- optional: `feature/<work-order-slug>` branches (created during planning or on the first task)

---

## Definitions and rules

### Issue hierarchy

```
VD (Version Declaration)
└── WO (Work Order)
    └── TASK/FIX (Executable ticket)
```

### Title conventions

- `VD: <version> - <title>`
- `WO: <feature title>`
- `TASK: <short deliverable>`
- `FIX: <bug/regression>`

### Branch mapping

- VD → `release/<version>`
- WO → `feature/<work-order-slug>`
- TASK → `task/<task-slug>`
- FIX → `fix/<task-slug>`

### Slug rules

Use the issue title text after its prefix (`WO:` / `TASK:` / `FIX:`):

- lowercase
- spaces → `-`
- remove punctuation (keep letters/numbers/hyphens)
- collapse multiple `-`
- trim leading/trailing `-`

---

## Planning workflow

### 0) Pre-flight checklist (Definition of Ready)

Before generating tickets, confirm:

- The “what” and “why” are clear enough to implement
- You can name the **version boundary**
- You can identify the **feature boundaries** (WOs)
- You can break work into **atomic tasks** (TASK/FIX) that one agent can complete

If not, create a short “Discovery” WO with 1–3 tasks that produce the missing info.

---

### 1) Create the Implementation Plan (IP)

Create `/planning/releases/<version>/IMPLEMENTATION_PLAN.md` on your local branch.

Minimum IP content:

1. **Problem statement**
2. **Goals / non-goals**
3. **User impact / UX notes**
4. **Technical approach**
5. **Data model / API changes (if any)**
6. **Migration / rollout plan (if any)**
7. **Risks + mitigations**
8. **Work breakdown**:
   - proposed WOs
   - proposed tasks under each WO

> The Implementation Plan is deliberately “pre-ticket” and is allowed to contain open questions.

---

### 2) Decide version and create the `release/<version>` branch

From `develop`:

```bash
git checkout develop
git pull origin develop

git checkout -b release/<version>
git push -u origin release/<version>
```

---

### 3) Add planning markdown artifacts to `release/<version>`

On the `release/<version>` branch:

1. Create the planning directory: `/planning/releases/<version>/...`
2. Create:
   - `VD.md` (based on the VD template)
   - each WO file
   - each TASK/FIX file
3. Use **placeholders** for issue numbers initially:
   - `VD Issue: #TBD`
   - `WO Parent: #TBD`
   - `TASK Parent: #TBD`

Commit:

```bash
git add planning/releases/<version>
git commit -m "chore(plan): add <version> implementation plan and ticket drafts"
git push
```

---

### 4) Create GitHub issues in dependency order

Because parent issue numbers are needed in child bodies:

1. Create the **VD** issue first
2. Create each **WO** issue next (with the VD number filled in)
3. Create each **TASK/FIX** issue last (with the WO number filled in)

For each created issue:

- capture the returned issue number
- update the corresponding markdown file(s) with the real issue numbers
- keep the repo plan aligned with GitHub

---

### 5) Link issues using `gh sub-task`

After issues exist, enforce hierarchy via the `gh sub-task` extension:

- Link every WO as a sub-task of the VD
- Link every TASK/FIX as a sub-task of its WO

> Keep linking **out of** the issue body and **in** GitHub’s sub-task relationships so the hierarchy stays machine-readable.

---

### 6) Optional: pre-create feature branches

If you prefer branches to exist immediately after planning, create each `feature/<work-order-slug>` from the release branch:

```bash
git checkout release/<version>
git pull origin release/<version>

git checkout -b feature/<work-order-slug>
git push -u origin feature/<work-order-slug>
```

---

### 7) Handoff to execution agents

Once the GH issues are created and linked:

- agents should only be invoked on **TASK/FIX** issues
- they can deterministically resolve:
  - parent WO
  - parent VD
  - branch names

---

## Maintenance rules (plan changes)

### Adding new work during the version

If you discover new work mid-version:

1. Decide whether it fits an existing WO
2. If yes, add a new TASK/FIX under that WO
3. If no, create a new WO under the VD (only if it belongs in this version)
4. Update:
   - planning markdown files on `release/<version>`
   - GH issues + sub-task links

### When to bump the version instead

If the change:
- alters the VD “What this version IS / IS NOT”
- or adds significant new scope

…create a new VD instead of expanding the existing one.

---

## Quick QA checks (before starting execution)

- Every WO has exactly one parent VD
- Every TASK/FIX has exactly one parent WO
- Every TASK/FIX has:
  - a single clear deliverable
  - acceptance criteria
  - test commands
- Branch names are derivable from titles and unique
