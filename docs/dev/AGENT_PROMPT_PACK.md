# Agent Prompt Pack: Version Planning → VD/WO/TASK → GH Issue Creation

This file contains copy/paste prompts you can use with agents to go from idea → implementation plan → repo markdown → GitHub issues (with sub-task links).

---

## Prompt 0 — Inputs you should provide to the agent

Paste this “context block” before any of the prompts below:

```text
REPO: <owner>/<repo>
DEFAULT_BRANCHES: develop, main
NEXT_VERSION: <e.g. 0.7.0 or "decide">
IDEA:
<describe the feature/problem, why it matters>

CONSTRAINTS:
- <timebox, compatibility, must-not-break, etc.>

NON-NEGOTIABLES:
- Must follow issue hierarchy: VD → WO → TASK/FIX
- Must follow deterministic branch mapping and slug rules
- WOs must be sub-tasks of VD; TASK/FIX must be sub-tasks of WOs
- Planning artifacts must be committed to release/<version> under: planning/releases/<version>/
```

---

## Prompt 1 — Version Planner (Idea → Implementation Plan → WO/TASK breakdown)

Use this to produce the complete plan and a structured breakdown.

```text
You are the Version Planner.

Using the provided IDEA + constraints, produce:
1) An IMPLEMENTATION_PLAN.md in markdown.
2) A structured work breakdown as JSON with:
   - version (string)
   - vd_title (string without prefix)
   - statement_of_intent (is / is_not)
   - work_orders[] each with:
       - title (without prefix)
       - slug (derived from title using slug rules)
       - objective[]
       - in_scope[]
       - out_of_scope[]
       - tasks[] each with:
           - type ("TASK" or "FIX")
           - title (without prefix)
           - slug (derived from title using slug rules)
           - deliverable (1–3 bullets)
           - do[] / do_not[]
           - acceptance_criteria[]
           - test_commands[] (default: make lint, make test unless overridden)

Rules:
- Prefer fewer WOs with clear feature boundaries.
- Ensure each TASK/FIX is atomic enough for one agent to complete.
- Call out risks and open questions explicitly in the implementation plan.
- Do NOT include GitHub issue numbers yet; use placeholders only.
Output format:
- First: IMPLEMENTATION_PLAN.md content in a fenced code block.
- Then: JSON breakdown in a fenced code block.
```

---

## Prompt 2 — Ticket Writer (JSON plan → VD/WO/TASK markdown files)

Use this after Prompt 1. It converts the JSON into the actual ticket bodies.

```text
You are the Ticket Writer.

Input: the JSON breakdown from the Version Planner.

Generate the repo planning markdown files under:
planning/releases/<version>/

Files to output:
- planning/releases/<version>/VD.md
- planning/releases/<version>/WO/<work-order-slug>.md (one per WO)
- planning/releases/<version>/WO/<work-order-slug>/TASK/<task-slug>.md (one per TASK/FIX)

Rules:
- Use the existing templates for VD, WO, and TASK/FIX as the structure.
- Replace <version>, <title>, etc. with real values.
- For parent issue numbers, use placeholders:
  - VD issue: #TBD
  - WO parent VD: #TBD
  - TASK parent WO: #TBD
- Include the deterministic branch names in each file based on slug rules.
- Keep each TASK/FIX deliverable + acceptance criteria very concrete.

Output format:
For each file:
1) A header line: FILE: <path>
2) Then the full markdown content in a fenced code block.
```

---

## Prompt 3 — Git Scaffold (create release branch + write files + commit)

Use this after Prompt 2 if your agent can run shell commands; otherwise use it to get a command list.

```text
You are the Git Scaffold agent.

Given:
- version number
- the list of FILE paths + contents produced by Ticket Writer

Produce an exact sequence of shell commands to:
1) Create `release/<version>` from `develop` (if it does not exist).
2) Create the directories under planning/releases/<version>/.
3) Write each file content to disk.
4) `git add`, commit with message: "chore(plan): scaffold <version> plan", and push.

Assume a Unix shell and that git remote is `origin`.
Do not invent extra steps.
```

---

## Prompt 4 — GH Issue Creator + Sub-task linker (repo markdown → GH issues)

Use this once the markdown files exist on `release/<version>`.

```text
You are the GitHub Issue Creator.

Goal: create GitHub issues from the planning markdown files and link them with the `gh sub-task` extension.

Constraints:
- Create issues in this order: VD → WOs → TASK/FIX
- After creating each issue, capture the created issue number.
- Update the markdown files in planning/releases/<version>/ to replace #TBD placeholders with real issue numbers.
- Link hierarchy using `gh sub-task`:
  - each WO is a sub-task of the VD
  - each TASK/FIX is a sub-task of its WO

Deliver:
1) A command sequence using `gh issue create` (prefer --title + --body-file).
2) A mapping file content (JSON) you will write to:
   planning/releases/<version>/issue-map.json
   with keys: vd, work_orders[], tasks[] including issue numbers.
3) Commands to update markdown files and commit:
   "chore(plan): link <version> issues"

Important:
- If you do not know the exact `gh sub-task` syntax, emit a clearly marked placeholder command
  and show what parent/child issue numbers should be inserted.
```

---

## Prompt 5 — Plan QA (validate the plan before execution)

Use this after issues exist.

```text
You are the Plan QA agent.

Given:
- VD issue body
- WO issue bodies
- TASK/FIX issue bodies
- the issue-map.json

Check for:
- Missing acceptance criteria
- Tasks that are too large / not atomic
- Missing parent links
- Branch names not matching slug rules
- Scope creep (items that contradict VD "IS NOT")

Output:
- A checklist of fixes (grouped by VD, WO, TASK)
- Suggested edits (exact markdown diffs where possible)
```
