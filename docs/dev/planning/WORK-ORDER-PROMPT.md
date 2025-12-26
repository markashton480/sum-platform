---
description: "Create GitHub issues from a Work Order markdown file"
argument-hint: "<path/to/workorder.md>"
allowed-tools: "Bash(gh:*),Bash(cat:*),Bash(grep:*),Bash(sed:*),View"
---

# Create Work Order Issues

**File:** $1

---

## Step 1: Read the Work Order File

```bash
cat "$1"
```

Parse the file to extract:

**From Metadata section:**

- Version (e.g., `v0.7.0`)
- Component (e.g., `forms`) — becomes `component:*` label
- Priority (e.g., `high`) — becomes `priority:*` label

**From main content:**

- Title from `# WO: <title>`
- Description section
- Acceptance Criteria section

**From Subtasks section:**
Each `### <title>` is a subtask with:

- Title
- Description
- Acceptance Criteria
- Boundaries (Do / Do NOT)
- Dependencies

---

## Step 2: Find Version Declaration (Optional)

```bash
VERSION="<extracted version>"
VD_ISSUE=$$(gh issue list --search "Version Declaration $$VERSION in:title" --json number --jq '.[0].number // empty')
```

If found, we'll link the WO to it. If not, continue without.

---

## Step 3: Create the Work Order Issue

```bash
COMPONENT="<extracted component>"
PRIORITY="<extracted priority>"

WO_BODY="Part of: #$$VD_ISSUE (if exists)

## Description

<description from file>

## Acceptance Criteria

<acceptance criteria from file>

## Subtasks

- [ ] <subtask 1 title>
- [ ] <subtask 2 title>
- [ ] <subtask 3 title>
"

WO_NUMBER=$$(gh issue create \
  --title "WO: <title from file>" \
  --body "$$WO_BODY" \
  --label "type:work-order" \
  --label "component:$$COMPONENT" \
  --label "priority:$$PRIORITY" \
  --json number --jq '.number')

echo "✅ Created Work Order: #$$WO_NUMBER"
```

---

## Step 4: Create Each Subtask Issue

For each `### <title>` section under `## Subtasks`:

```bash
SUBTASK_BODY="Part of: #$$WO_NUMBER (WO: <wo title>)

## Description

<description from subtask>

## Acceptance Criteria

<acceptance criteria from subtask>

## Boundaries

### Do
<do items>

### Do NOT
<do not items>

## Dependencies

<dependencies if any>
"

SUBTASK_NUMBER=$$(gh issue create \
  --title "<subtask title>" \
  --body "$$SUBTASK_BODY" \
  --label "type:task" \
  --label "component:$$COMPONENT" \
  --json number --jq '.number')

echo "✅ Created Subtask: #$$SUBTASK_NUMBER - <title>"
```

Repeat for each subtask in the file.

---

## Step 5: Link Subtasks as Sub-Issues

```bash
# Install extension if needed
gh extension list | grep -q "sub-issue" || gh extension install yahsan2/gh-sub-issue

# Link each subtask
gh sub-issue add $$WO_NUMBER $$SUBTASK_NUMBER
```

Repeat for each subtask.

---

## Step 6: Output Summary

```
============================================
✅ Work Order Created Successfully
============================================

Work Order: #<WO_NUMBER> - <title>
  Component: <component>
  Version: <version>

Subtasks:
  #<N1> - <subtask 1>
  #<N2> - <subtask 2>
  #<N3> - <subtask 3>

Next Steps:
1. Create feature branch:
   git checkout release/<version>
   git checkout -b feature/<component>
   git push -u origin feature/<component>

2. Execute tasks:
   /gh-issue <N1>
   /gh-issue <N2>
   ...
============================================
```

---

## File Format Expected

```markdown
# WO: [Feature Name]

## Metadata

- **Version:** v0.7.0
- **Component:** forms
- **Priority:** high

## Description

[What this feature does]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

---

## Subtasks

### Subtask Title 1

**Description:**
What this subtask does.

**Acceptance Criteria:**

- [ ] AC 1
- [ ] AC 2

**Boundaries:**

- Do: X
- Do: Y
- Do NOT: Z

---

### Subtask Title 2

**Description:**
...
```

---

## Error Handling

- File doesn't exist → exit with error
- Missing metadata → warn and use defaults
- WO creation fails → exit before subtasks
- Subtask fails → continue others, report at end
- Sub-issue linking fails → report but don't fail

See `PROJECT-PLANNING-GUIDELINES.md` for more details.
