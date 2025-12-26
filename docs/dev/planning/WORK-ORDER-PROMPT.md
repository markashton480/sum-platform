---
description: "Create GitHub issues from a Work Order markdown file"
argument-hint: "<path/to/workorder.md>"
allowed-tools: "Bash(gh:*),Bash(cat:*),View"
---

# Create Work Order Issues

Read the file: $1

If subtasks aren't in this file, check other files in the same directory or `docs/planning/`.

Create a GitHub issue for the Work Order with label `type:work-order` and `component:<component>`.

Then create an issue for each subtask with label `type:task` and `component:<component>`.

Each subtask body should start with `Part of: #<WO-number>`.

Use the content from the file. Don't summarize or rewrite it.

## Link Subtasks

After creating all issues, link them as sub-issues:

```bash
gh extension install github/gh-sub-issue 2>/dev/null || true
gh sub-issue add <WO-number> <subtask-number>
```

Repeat for each subtask.

See `PROJECT-PLANNING-GUIDELINES.md` for more details.
