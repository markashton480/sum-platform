# TEST-016A: Stabilize local black runs (eliminate “hang” on cli/tests)

## Branch

- [x] Checkout/create branch: fix/TEST-016A-black-local-hang
- [x] Verify: git branch --show-current

## Objective

Local verification has repeatedly been blocked by black appearing to hang (especially when checking cli/tests). This task diagnoses the root cause and makes make lint reliably complete locally without weakening formatting enforcement or changing CI behaviour unexpectedly.

## Acceptance Criteria

- [x] make lint completes locally without hanging (black step finishes) on a typical dev run.
- [x] black --check cli/tests completes locally without hanging.
- [x] CI remains green (at minimum: lint + test slices still succeed).
- [x] Root cause and remediation are documented in the follow-up report, including black version and the specific trigger (file, directory, symlink, generated tree, version bug, etc.).

## Steps

1. Confirm branch is correct: git branch --show-current
2. Capture tool versions in the follow-up notes:

   - python --version
   - black --version (or python -m black --version)

3. Reproduce the issue locally:

   - Run make lint and note whether/where black stalls.
   - Run black --check cli/tests directly to confirm the minimal repro.

4. Identify whether the stall is “file discovery” vs “formatting one file”:

   - Run black with verbose output on cli/tests to see the last file processed.
   - If it still stalls, run black against individual files in cli/tests to isolate a single problematic file (if any).

5. Check for environmental/tree triggers under cli/tests:

   - Look for symlinks (potential loops).
   - Look for large generated/untracked directories containing many .py files (even if gitignored), which black may still traverse.

6. Apply the smallest safe fix that makes black deterministic:

   - If the cause is black traversing generated trees: update black configuration (extend-exclude) and/or adjust make lint to format/check tracked + non-ignored python files via git ls-files to avoid scanning ignored/generated outputs.
   - If the cause is a black version bug: pin to a known-good version (or upgrade) in the dev dependencies, with a short note why.

7. Verify end-to-end:

   - make lint
   - make test
   - make test-cli
   - make test-themes
   - make test-templates

## Documentation

- [x] Create docs/dev/Tasks/TEST/TEST-016A_followup.md with:

  - Summary of changes made
  - Files modified/created
  - Root cause analysis (what specifically caused the hang)
  - Tool versions (python, black)
  - Test results and command outputs (what was run and what passed)

## Commit & Push

- [ ] Stage changes: git add -A
- [ ] Commit: fix(TEST-016A): stabilize local black runs

  - Include BOTH docs/dev/Tasks/TEST/TEST-016A.md AND docs/dev/Tasks/TEST/TEST-016A_followup.md

- [ ] Push: git push origin fix/TEST-016A-black-local-hang

## Verification

- [ ] Run git status --porcelain
- [ ] Expected: empty (clean) OR only intentional untracked files (documented in followup)

## Recommended Agent

| Criteria      | Selection                                                                                            |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| **Model**     | GPT-5.1 Codex Max                                                                                    |
| **Thinking**  | Standard                                                                                             |
| **Rationale** | Tooling/debug task with some uncertainty; needs careful local reproduction and minimal, safe change. |
