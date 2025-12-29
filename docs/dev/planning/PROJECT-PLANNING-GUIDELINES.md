# Project Planning Guidelines

> **Coordinate parallel work** across multiple agents while keeping merges, releases, and verification predictable.

**Git Model:** See [`docs/dev/GIT_STRATEGY.md`](../GIT_STRATEGY.md) for the 5-tier branch model.

---

## 1) Issue Hierarchy

```
Milestone: v0.7.0
│
├── Version Declaration: v0.7.0              ←→  release/0.7.0
│   │
│   ├── WO: Dynamic Forms                    ←→  feature/forms
│   │   ├── GH-101: FormDefinition snippet   ←→  feature/forms/001-definition
│   │   ├── GH-102: Field blocks             ←→  feature/forms/002-fields
│   │   └── GH-103: Dynamic form block       ←→  feature/forms/003-block
│   │
│   └── WO: Blog System                      ←→  feature/blog
│       ├── GH-104: Category snippet         ←→  feature/blog/001-category
│       └── GH-105: Blog pages               ←→  feature/blog/002-pages
```

### Issue Types

| Type | Purpose | Branch | PR Target |
|------|---------|--------|-----------|
| **Version Declaration** | Scope + intent for a release | `release/X.Y.0` | `develop` |
| **Work Order (WO)** | Coordinate a feature | `feature/<scope>` | `release/X.Y.0` |
| **Subtask** | Atomic deliverable | `feature/<scope>/<seq>-<slug>` | `feature/<scope>` |

### When to Use What

**Single subtask:** One agent, limited scope, low collision risk.

**Work Order + subtasks:** Multiple agents, multiple files, merge order matters.

**Version Declaration:** Always — one per milestone, defines what ships.

---

## 2) GitHub Configuration

### Labels

| Category | Labels |
|----------|--------|
| **Type** | `type:version-declaration`, `type:work-order`, `type:task`, `type:bug` |
| **Agent** | `agent:codex-a`, `agent:codex-b`, `agent:claude`, `agent:human` |
| **Model** | `model:o3`, `model:claude-sonnet`, `model:claude-opus`, `model:human` |
| **Risk** | `risk:low`, `risk:med`, `risk:high` |
| **Component** | `component:core`, `component:cli`, `component:boilerplate`, `component:themes`, `component:docs` |

### Project Fields

| Field | Type | Purpose |
|-------|------|---------|
| Status | Select | Todo / In Progress / Review / Done |
| Agent | Select | Who is assigned |
| Model Planned | Select | Intended model |
| Model Used | Select | Actual model (set on completion) |
| Component | Select | Which area |
| Change Type | Select | feat / fix / chore / refactor / docs |
| Risk | Select | Low / Med / High |
| Release | Text | Version (e.g., `v0.7.0`) |

---

## 3) Starting a Version

### 3.1 Create Milestone + Version Declaration

```bash
# 1. Create milestone in GitHub: v0.7.0

# 2. Create Version Declaration issue using template
#    Title: "Version Declaration: v0.7.0"
#    Labels: type:version-declaration
#    Milestone: v0.7.0

# 3. Create release branch
git checkout develop
git pull origin develop
git checkout -b release/0.7.0
git push -u origin release/0.7.0
```

### 3.2 Create Work Orders

For each feature in the Version Declaration:

```bash
# 1. Create Work Order issue using template
#    Title: "WO: Dynamic Form System (v0.7.0)"
#    Labels: type:work-order, component:*, risk:*
#    Milestone: v0.7.0

# 2. Create feature branch
git checkout release/0.7.0
git checkout -b feature/forms
git push -u origin feature/forms
```

### 3.3 Create Subtasks

For each task in the Work Order:

```bash
# 1. Create subtask issue using template
#    Title: "GH-101: Add FormDefinition snippet"
#    Labels: type:task, agent:*, component:*, risk:*
#    Milestone: v0.7.0

# 2. Create task branch
git checkout feature/forms
git checkout -b feature/forms/001-definition
git push -u origin feature/forms/001-definition
```

---

## 4) Executing Work

### Task Workflow

```
1. Check out task branch
2. Implement (satisfy acceptance criteria, stay within boundaries)
3. Run: make lint && make test
4. Commit with conventional message + "Closes #NNN"
5. Push and create PR → feature branch
6. Wait for CI, address feedback
7. PR merged (squash) by reviewer
8. Set Model Used + apply model:* label
```

### Feature Completion

When all subtasks merged to `feature/<scope>`:

```bash
git checkout feature/forms
git pull origin feature/forms
make lint && make test

# Create PR: feature/forms → release/0.7.0
# Merge strategy: --no-ff (preserves feature boundary)
```

### Version Completion

When all features merged to `release/X.Y.0`:

```bash
git checkout release/0.7.0
git pull origin release/0.7.0
make release-check

# Create PR: release/0.7.0 → develop (squash)
# Run release audit before merge
# Then: develop → main → sync → tag
```

---

## 5) Parallelism Rules

### One Agent, One Task

Never assign two agents to the same subtask. Agents can work on different subtasks within the same feature.

### Hot File Ownership

If multiple tasks touch the same files:

1. Declare in Work Order which task owns the hot files
2. Define merge order
3. Later tasks rebase before merging

```markdown
### Merge Order
1. GH-101: Form Definition (owns models.py)
2. GH-102: Field Blocks (depends on 101)
3. GH-103: Dynamic Form Block (depends on 102)
```

### Cross-Feature Dependencies

If features depend on each other:

1. Declare in Version Declaration
2. Merge dependent feature first
3. Rebase other features on release branch

---

## 6) Definition of Done

### Subtask DoD

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied

### Work Order DoD

- [ ] All subtasks Done
- [ ] Feature branch merged to release branch
- [ ] No unresolved conflicts

### Version Declaration DoD

- [ ] All Work Orders Done
- [ ] Release branch merged to develop
- [ ] Develop merged to main
- [ ] Tag created on public repo
- [ ] Verification passes

---

## 7) Model Tracking

### When to Set

| Event | Action |
|-------|--------|
| Task assigned | Set `Model Planned` |
| Task completed | Set `Model Used` + apply `model:*` label |

### Enforcement

A subtask cannot move to Done without:
- `Model Used` field set
- Matching `model:*` label applied

---

## 8) PR Conventions

### Titles

| Level | Format |
|-------|--------|
| Task | `GH-NNN: <summary>` |
| Feature | `feat(<scope>): <summary>` |
| Version | `Release vX.Y.0` |

### Bodies

```markdown
## Summary
- What changed

## Testing
- `make lint` ✓
- `make test` ✓

Closes #NNN
```

---

## 9) Suggested Project Views

| View | Configuration |
|------|---------------|
| **Kanban** | Group by Status, show Agent |
| **By Agent** | Filter Status ≠ Done, group by Agent |
| **By Release** | Filter by Release field |
| **High Risk** | Filter Risk = High OR Status = Holding |

---

## Related Documents

- [`docs/dev/GIT_STRATEGY.md`](../GIT_STRATEGY.md) — Branch model
- [`docs/release/declarations/release-declaration-template.md`](../../release/declarations/release-declaration-template.md) — Version planning
- [`WORK-ORDER-PROMPT.md`](WORK-ORDER-PROMPT.md) — Work order template
- [`GH-ISSUE-PROMPT.md`](GH-ISSUE-PROMPT.md) — Subtask issue template
- [`docs/ops-pack/RELEASE_RUNBOOK.md`](../../ops-pack/RELEASE_RUNBOOK.md) — Release process
