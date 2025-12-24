# Work Order Template

**Title Format:** `WO: <Outcome Description> (vX.Y.Z)`

---

## Objective
<!-- What does "done" mean for this Work Order? List 2-5 clear outcomes -->

- [ ] 
- [ ] 
- [ ] 

---

## Scope Boundaries

### In Scope
<!-- What areas/components ARE included in this work -->

- 
- 

### Out of Scope
<!-- What areas/components are explicitly NOT included -->

- 
- 

---

## Affected Paths
<!-- List directories, files, or modules likely to be touched -->

```
/path/to/component/
/path/to/another/area/
specific-file.ts
```

---

## Subtasks
<!-- Link to child issues - update as they are created -->

- [ ] #XXX - [Subtask description]
- [ ] #YYY - [Subtask description]
- [ ] #ZZZ - [Subtask description]

---

## Merge Plan

### Merge Order
<!-- Define the sequence PRs must be merged to avoid conflicts -->

1. **First:** #XXX - [Reason: foundation work]
2. **Second:** #YYY - [Reason: depends on #XXX]
3. **Third:** #ZZZ - [Reason: integrates both]

### Merge Ownership
<!-- Who is responsible for executing merges and resolving conflicts? -->

- **Primary Merger:** @username or agent-name
- **Backup:** @username or agent-name

### Dependency Notes
<!-- Call out critical dependencies between subtasks -->

- #YYY depends on interface changes from #XXX
- #ZZZ cannot start until #XXX establishes the contract

---

## Verification Focus
<!-- What specifically needs to be checked after all subtasks are merged? -->

### Smoke Tests
<!-- Quick validation that core functionality works -->

```bash
# Command examples
make test
sum init test-project
sum check
```

### Delta Checks
<!-- Specific areas where regression risk is high -->

- [ ] Verify X still works as expected
- [ ] Check Y integration didn't break
- [ ] Confirm Z performance is acceptable

---

## Risk Assessment
<!-- Overall risk level for this Work Order -->

**Risk Level:** [Low / Med / High]

**Risk Factors:**
- 
- 

**Mitigation:**
- 
- 

---

## Labels Checklist
<!-- Ensure these are applied to this issue -->

- [ ] `type:work-order`
- [ ] `component:*` (specify which component)
- [ ] `risk:*` (low/med/high)
- [ ] Milestone: `vX.Y.Z`

---

## Project Fields Checklist
<!-- Ensure these are set in GitHub Projects -->

- [ ] **Release:** `vX.Y.Z`
- [ ] **Component:** (selected)
- [ ] **Risk:** (selected)
- [ ] **Status:** Todo

---

## Notes
<!-- Any additional context, constraints, or important information -->