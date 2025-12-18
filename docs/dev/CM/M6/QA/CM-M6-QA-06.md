# Task Ticket: **CM-M6-QA-06 — CI Enforcement + Branch Protection Gate**

**Tag:** QA
**Type:** Corrective Mission
**Owner:** QA / Tooling Engineer
**Priority:** High
**Goal:** Turn CI from “present” into “mandatory” and verify it works end-to-end on GitHub.

## Context

CM-M6-QA-05 created `.github/workflows/ci.yml` to run `make lint` and `make test` on pushes/PRs to `main`, and updated the hygiene doc with the lint/CI contract.

This CM ensures:

1. CI actually runs successfully in GitHub’s environment, and
2. CI becomes a **required merge gate** (so the contract can’t silently drift again).

## Scope

### In scope

1. **Run real CI on GitHub**

   - Ensure the workflow triggers on a PR and reports status checks.
   - Capture evidence: workflow run URL(s) and pass/fail summary.

2. **Enforce CI via branch protection**

   - Configure branch protection rules for `main` so merges require:

     - the CI workflow job to pass (or specific checks, depending on GitHub UI),
     - up-to-date branch before merge (optional but recommended),
     - linear history (optional).

   - If branch protection must be done manually in the GitHub UI, produce a **runbook** with exact clicks/fields so it’s repeatable.

3. **Workflow hardening (small, surgical)**

   - Add `timeout-minutes` to the job (prevents hung runs).
   - Add minimal `permissions:` (read-only) unless you truly need more.
   - Add `workflow_dispatch:` so you can manually run CI when debugging.
   - Review the cleanup step; either:

     - keep it but explain why it’s safe, or
     - replace with a safer approach (e.g., remove only known artifacts, or only untracked artifacts).

### Out of scope

- Adding new test suites (Playwright/Cypress), security scanning, Dependabot, etc. (can be later CMs).

## Constraints / Contract

- CI must continue to run **exactly**:

  - `make lint`
  - `make test`

- CI must not start linting/typechecking `clients/` or `boilerplate/` (those are explicitly out-of-scope per existing contract).
- Every change must be traceable and minimal.

## Plan (Agent execution steps)

1. **Precheck**

   - Confirm current `main` includes CM-M6-QA-05 changes.
   - Create a short-lived branch: `cm/CM-M6-QA-06-ci-enforcement`.

2. **Trigger CI**

   - Open a PR to `main`.
   - Observe CI trigger + result.
   - If CI fails:

     - diagnose root cause from logs,
     - patch workflow minimally (e.g., install OS deps only if needed),
     - re-run until green.

3. **Enforce branch protection**

   - Add a runbook: `docs/dev/hygiene.md` (or a new `docs/dev/ci.md`) section:

     - required check name(s),
     - exact GitHub settings.

   - Apply settings (if agent has permission; if not, document exact steps for Mark to apply).

4. **Harden workflow**

   - Add `timeout-minutes`, `permissions`, `workflow_dispatch`.
   - Re-run CI to confirm still green.

5. **Write CM artefacts**

- Complete a comprehensive work report:
  - `docs/dev/CM/M6/QA/CM-M6-QA-06_followup.md` (work report)

## Acceptance criteria

- A PR to `main` shows CI checks and they pass.
- `main` branch protection requires CI checks to pass before merge (or a documented runbook exists if permissions prevent applying it).
- Workflow includes timeouts + minimal permissions + manual trigger.
- Follow-up report includes:

  - CI run links/screenshots references (URLs),
  - any changes made and why,
  - final “contract status: enforced”.

## Risks / Failure modes to watch

- CI fails due to missing Ubuntu system deps → add minimal `apt-get` step only if proven necessary.
- Check name mismatch prevents branch protection from requiring it → document exact check name(s) from the live run.
- Cleanup step deletes something unexpected → adjust to safer cleanup strategy.

## Definition of done

- CI is not only _working_, it’s **unavoidable** for merges into `main`.
