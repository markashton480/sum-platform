# GH Project Operating Guide (SUM Platform)

**Purpose:** A lightweight, auditable way to run parallel work across multiple agents/models while keeping merges, releases, and verification predictable.

This process assumes:
- `main` is always stable and shippable (no direct commits).
- Every change is traceable to a GitHub Issue.
- Releases are cut from `main` using the release checklist and verified.

---

## 1) Core concepts

### 1.1 Milestones = Release trains
We use GitHub **Milestones** as release containers. Milestone names match release tags:

- `v0.6.2` (patch train)
- `v0.7.0` (minor train)

**Rule:** If it’s meant to ship in the next release, it must be in that Milestone.

### 1.2 Work Orders = Parent coordination issues
A **Work Order (WO)** is a parent Issue used to coordinate parallel work that could otherwise collide. It defines:
- the outcome
- boundaries / ownership
- merge order
- verification focus

A WO contains **subtasks** as separate Issues (child tickets), assigned to agents/models.

### 1.3 Subtasks = Atomic deliverables
A subtask should be small enough that:
- one agent can complete it end-to-end
- it touches a limited set of files/areas
- it can be reviewed/merged independently

### 1.4 Project board = Live execution view
GitHub Projects (v2) is the “what’s happening now” view:
- work status
- who is doing it
- which model did it
- which release it’s for
- where conflicts/risk might be brewing

---

## 2) Required GitHub configuration

### 2.1 Labels (recommended minimum set)
**Type**
- `type:work-order`
- `type:task`
- `type:bug`
- `type:release`

**Ownership**
- `agent:codex-a`, `agent:codex-b`, `agent:codex-c`, `agent:claude`, `agent:human`

**Model tracking**
- `model:codex-5.1-max`
- `model:codex-5.2-extra-high`
- `model:claude`
- `model:human`
- `model:other`

**Risk**
- `risk:low`, `risk:med`, `risk:high`

**Component**
- `component:core`, `component:cli`, `component:boilerplate`, `component:infra`, `component:docs`

### 2.2 Project fields (v2)
Add these fields to the Project:

**Execution**
- `Status` (Todo / Queue / In Progress / Holding / Done)
- `Agent` (single select)
- `Model Planned` (single select)
- `Model Used` (single select)

**Change clarity**
- `Component` (single select)
- `Change Type` (single select: feat / fix / chore / refactor / docs)
- `Risk` (single select: Low / Med / High)
- `Release` (text or iteration; usually mirrors Milestone, e.g. `v0.7.0`)

> Note: Labels make model visible directly on the issue. Project fields make it filterable/trackable at scale.

---

## 3) Work intake: how a new piece of work is created

### 3.1 Decide: single issue vs Work Order
Use a **single Issue** when:
- one person/agent can do it
- low collision risk
- limited scope and files

Use a **Work Order** when:
- multiple agents will work in parallel
- multiple components are involved
- risk of merge conflicts is non-trivial
- you need a planned merge order

### 3.2 Work Order template
Create a parent Issue titled:

**`WO: <Outcome> (vX.Y.Z)`**

**WO body should include:**
- **Objective:** what “done” means (2–5 bullets)
- **Scope boundaries:** which areas are in/out
- **Affected paths:** directories/files likely touched
- **Subtasks:** links to child issues (see 3.3)
- **Merge plan:** order + who merges + dependency notes
- **Verification focus:** smoke + any delta checks

Apply labels:
- `type:work-order`
- relevant `component:*` and `risk:*`
- assign Milestone `vX.Y.Z`

Set Project fields:
- `Release = vX.Y.Z`
- `Risk`, `Component` (if clear at WO level)

### 3.3 Create subtasks (child Issues)
Create child Issues titled:

**`<ticket-id>: <short deliverable>`**  
Example: `GH-123: Add leads status transitions`

Each subtask must include:
- **Deliverable**
- **Boundaries** (“do not touch X”; “only change Y”)
- **Acceptance criteria**
- **Test commands to run**
- **Files/paths expected to change** (best-effort)

Apply labels:
- `type:task` (or `type:bug`)
- `agent:*` (who you intend to do it)
- `component:*`
- `risk:*` (optional but useful)
- Milestone `vX.Y.Z`

Set Project fields:
- `Agent = …`
- `Model Planned = …`
- `Component / Change Type / Risk`
- `Release = vX.Y.Z`

---

## 4) Parallelism rules (how we avoid merge hell)

### 4.1 One agent, one slice
Do not assign two agents to change the same “hot area” in the same train unless you explicitly plan the merge order.

Prefer slicing by:
- directory (`core/` vs `cli/` vs `boilerplate/`)
- vertical feature ownership (one agent owns end-to-end)
- interface ownership (one agent changes the contract; others consume)

### 4.2 Declare “hot files”
If a WO touches hot files (examples):
- dependency pins / lockfiles
- boilerplate templates
- shared settings/config
- central routing / registries

…then the WO must include an explicit merge order and a single owner for those files.

### 4.3 Use Draft PRs early
Agents should open a Draft PR early (after first meaningful commit) to:
- surface collisions early
- anchor discussion + review
- ensure Issues/Project automatically link to PRs

---

## 5) Branching + PR conventions

### 5.1 Branch naming
Branch names follow the operational git policy style:

- `feat/gh-123-leads-status`
- `fix/gh-124-boilerplate-drift`
- `chore/gh-125-ci-timeouts`
- `docs/gh-126-gh-project-guide`

### 5.2 PR naming + linking
PR title:
- `GH-123: <summary>`

PR body must include:
- `Closes #123` (or “Refs #123” if it shouldn’t auto-close)
- test evidence (commands + results)
- any notable risk/rollback notes

### 5.3 Merge discipline
- Only merge when the issue is actually done.
- Prefer `--no-ff` merges for traceability (squash only for tiny, isolated changes).
- If multiple PRs are part of a WO, merge in the planned order.

---

## 6) Model tracking (planned vs used)

### 6.1 When to set fields
- **On assignment:** set `Model Planned`
- **On completion:** set `Model Used` + apply `model:*` label

### 6.2 Why both?
- `Model Planned` shows intent and helps routing work.
- `Model Used` is ground truth for reliability analysis (which models regress, which excel).

### 6.3 “Done” requires Model Used
A subtask cannot be moved to **Done** unless:
- `Model Used` is set
- matching `model:*` label is applied

---

## 7) Definition of Done

### 7.1 Subtask DoD
A subtask is “Done” when:
- acceptance criteria met
- tests specified in the issue have been run and passed
- PR is merged to `main` (or explicitly approved to defer merge)
- `Model Used` set + `model:*` label applied
- any follow-up docs/notes are captured (if needed)

### 7.2 Work Order DoD
A Work Order is “Done” when:
- all child issues are Done (or explicitly cut/deferred)
- merge plan executed without unresolved collisions
- verification focus items are checked
- release train remains coherent (Milestone still true)

---

## 8) Release workflow integration

### 8.1 Release issue per Milestone
Each Milestone must have one parent “Release” issue:

**`Release: vX.Y.Z`**

It owns:
- version selection and gates
- boilerplate pinning
- tagging
- post-tag verification
- record keeping

### 8.2 Gates and verification
Releases must follow the repo’s operational release checklist:
- pre-flight: clean `main`
- run `make release-check`
- update boilerplate pinning to the new tag
- create annotated tag on `main`
- post-tag verify via `sum init` + `sum check`
- update loop-sites matrix and release notes

### 8.3 Deploy/upgrade/rollback linkage (if applicable)
If a release involves deploy/upgrade:
- follow deploy/upgrade runbooks
- do smoke tests immediately after
- know rollback triggers and the rollback path
- record anything surprising in “what broke last time”

---

## 9) Record keeping (non-negotiable)

After each release event and any noteworthy operational incident:
- Update **loop-sites matrix** (what’s running where)
- Append to **what broke last time** (lessons, pitfalls, workarounds)

---

## 10) Suggested Project views

Create saved views in GitHub Projects:
1) **Kanban (Execution)**  
   Group by Status, show Agent + Model Planned/Used

2) **By Agent**  
   Filter `Status != Done`, group by Agent

3) **By Model Used**  
   Group by Model Used, filter last 30–90 days when auditing reliability

4) **By Release (Train)**  
   Filter `Release = vX.Y.Z` (or Milestone view via Issues)

5) **High Risk / Holding**  
   Filter `Risk = High OR Status = Holding` to surface blockers

---

## 11) Optional automation (later)
Once the manual process is stable, consider automation:
- Sync `model:*` labels → `Model Used` field
- Auto-set `Release` field from Milestone
- Auto-move status on PR open/merge

Keep automation minimal and auditable—prefer “help humans do the right thing” over “complex magic”.

---

## Appendix A: Quick start checklist
- [ ] Create/confirm labels (type, agent, component, risk, model)
- [ ] Add Project fields (Agent, Model Planned, Model Used, Component, Change Type, Risk, Release)
- [ ] Adopt WO template and subtask template
- [ ] Enforce DoD: Model Used + label required before Done
- [ ] Ensure a Release issue exists for each Milestone train


