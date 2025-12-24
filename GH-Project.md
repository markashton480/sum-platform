# GitHub Projects + Issue Workflow (Project 12)

This repository tracks work in GitHub Project **12** (owner: `markashton480`). Work Orders are the parent coordination issues; Tasks are the executable units linked to a Work Order.

## Labels (repo-level)

- **Type:** `type:work-order`, `type:task`, `type:bug`, `type:release`
- **Ownership:** `agent:codex-a`, `agent:codex-b`, `agent:codex-c`, `agent:claude`, `agent:human`
- **Component:** `component:core`, `component:cli`, `component:boilerplate`, `component:infra`, `component:docs`
- **Risk:** `risk:low`, `risk:med`, `risk:high`
- **Model (thinking levels):**
  - Codex 5.1: `model:codex-5.1-low`, `model:codex-5.1-med`, `model:codex-5.1-high`, `model:codex-5.1-extra-high`
  - Codex 5.2: `model:codex-5.2-low`, `model:codex-5.2-med`, `model:codex-5.2-high`, `model:codex-5.2-extra-high`
  - Claude 4.5: `model:claude-4.5-low`, `model:claude-4.5-med`, `model:claude-4.5-high`, `model:claude-4.5-extra-high`
  - Gemini 3: `model:gemini-3-low`, `model:gemini-3-med`, `model:gemini-3-high`, `model:gemini-3-extra-high`
  - Human / other: `model:human`, `model:other`

## Project 12 fields

| Field          | Type           | Options / Usage                                                                                  |
| -------------- | -------------- | ------------------------------------------------------------------------------------------------ |
| Agent          | Single select  | Codex A, Codex B, Codex C, Claude, Human                                                         |
| Component      | Single select  | core, cli, boilerplate, infra, docs                                                              |
| Change Type    | Single select  | feat, fix, chore, refactor, docs                                                                 |
| Risk           | Single select  | Low, Med, High                                                                                   |
| Release        | Text           | Milestone/release tag (informational)                                                            |
| Model Planned  | Single select  | Codex 5.1 (low/med/high/extra-high), Codex 5.2 (low/med/high/extra-high), Claude 4.5 (low/med/high/extra-high), Gemini 3 (low/med/high/extra-high), Human, Other |
| Model Used     | Single select  | Same options as Model Planned                                                                    |

## Usage

- **Work Orders**: use the Work Order template (defaults to `type:work-order` and auto-adds to Project 12). Fill Agent, Component, Change Type, Risk, Release, and Model Planned. Update Model Used when the work ships.
- **Tasks**: create child Task issues from the Task template (defaults to `type:task` and auto-adds to Project 12). Keep fields aligned with the parent Work Order and set Model Planned/Used for the task if it differs.
- **Linkage**: each Task should reference its Work Order. Work Orders should track Task checklist status and merge plan.
- **CLI helpers**:
  - Add an issue to the project: `gh project item-add 12 --owner markashton480 --url <issue-url>`
  - Set a field (requires field/option IDs): `PROJECT_ID=$(gh project view 12 --owner markashton480 --json id --jq .id)` then `gh project field-list 12 --owner markashton480 --format json | jq -r '.fields[] | select(.name==\"Risk\").id'` → `RISK_ID`. Use `gh project item-edit --id <item-id> --project-id \"$PROJECT_ID\" --field-id \"$RISK_ID\" --single-select-option-id <option-id>`
