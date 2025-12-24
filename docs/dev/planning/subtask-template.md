# Subtask Template

**Title Format:** `GH-XXX: <Short Deliverable Description>`

---

## Parent Work Order
<!-- Link to the parent WO if this is part of a larger effort -->

Part of: #YYY (WO: Description)

---

## Deliverable
<!-- What exactly will be delivered? Be specific and concrete -->

This subtask will deliver:


---

## Boundaries
<!-- Critical: what should and should NOT be touched -->

### Do
<!-- What this subtask should change/create -->

- 
- 

### Do NOT
<!-- What this subtask must NOT touch to avoid conflicts -->

- ❌ Do not modify `file-x.ts` - owned by #ZZZ
- ❌ Do not change shared config in `config/` - handled separately
- 

---

## Acceptance Criteria
<!-- Clear, testable conditions that define "done" -->

- [ ] 
- [ ] 
- [ ] 

---

## Test Commands
<!-- Specific commands that must be run to verify this work -->

```bash
# Run these commands to verify the deliverable

# Example:
make test
npm run test:unit
sum check
```

**Expected Results:**
<!-- What success looks like -->

```
# Output should show:
- All tests passing
- No new warnings
- Feature X working as expected
```

---

## Files/Paths Expected to Change
<!-- Best-effort list of what will be modified -->

```
src/component/feature.ts
src/component/feature.test.ts
docs/component-guide.md
```

**Note:** This is a best-effort estimate. Actual changes may vary slightly.

---

## Dependencies
<!-- Other subtasks or issues this depends on -->

**Depends On:**
- [ ] #XXX must be merged first (reason)

**Blocks:**
- #YYY is waiting for this (reason)

---

## Implementation Notes
<!-- Technical guidance, constraints, or approach suggestions -->

### Approach
<!-- Suggested implementation approach -->


### Constraints
<!-- Technical or architectural constraints to respect -->

- 
- 

### References
<!-- Links to relevant docs, prior art, or examples -->

- 

---

## Risk Assessment
<!-- Risk level specific to this subtask -->

**Risk Level:** [Low / Med / High]

**Why:**


---

## Labels Checklist
<!-- Ensure these are applied to this issue -->

- [ ] `type:task` (or `type:bug` if fixing a defect)
- [ ] `agent:*` (who is assigned to do this)
- [ ] `component:*` (which component/area)
- [ ] `risk:*` (low/med/high)
- [ ] `model:*` (which model is planned to do this)
- [ ] Milestone: `vX.Y.Z`

---

## Project Fields Checklist
<!-- Ensure these are set in GitHub Projects -->

- [ ] **Agent:** (assigned)
- [ ] **Model Planned:** (selected)
- [ ] **Component:** (selected)
- [ ] **Change Type:** [feat / fix / chore / refactor / docs]
- [ ] **Risk:** (selected)
- [ ] **Release:** `vX.Y.Z`
- [ ] **Status:** Todo

---

## Definition of Done (DoD) Checklist
<!-- This subtask is only "Done" when ALL of these are complete -->

- [ ] All acceptance criteria met
- [ ] Test commands specified above have been run and passed
- [ ] PR is merged to `main` (or explicitly approved to defer merge)
- [ ] **Model Used** field is set in Project
- [ ] Matching `model:*` label is applied
- [ ] Any necessary docs/notes are captured
- [ ] Parent WO is updated with completion status

---

## Notes
<!-- Any additional context, gotchas, or important information -->