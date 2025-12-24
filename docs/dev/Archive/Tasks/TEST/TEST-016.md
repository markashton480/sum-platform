# TEST-016: CI Safety Gates for CLI and Source Integrity

## Branch

* [ ] Checkout/create branch: chore/TEST-016-ci-safety-gates
* [ ] Verify: git branch --show-current

## Objective

Phase 6 in the post-MVP testing implementation plan is to wire safety and slice checks into CI so regressions are blocked automatically. This task adds a single, reusable “source integrity” gate and runs it after each relevant CI test job (full suite, CLI slice, themes, templates), ensuring tests cannot silently modify or create files inside protected repo paths (especially themes/, boilerplate/, and clients/). This locks in the CLI safety refactor work from Phase 5 by making CI the enforcer. 

## Acceptance Criteria

* [ ] A Make target exists to verify repo source integrity (prefer: make verify-source-intact). 
* [ ] A script exists (or an equivalent Make recipe exists) that fails if, after tests run, any of the protected areas have:

  * tracked file modifications, or
  * non-ignored untracked files created
    Protected scope must include at least: themes/, boilerplate/, clients/, core/, cli/, docs/, infrastructure/, scripts/. 
* [ ] CI runs the source integrity verification after each of these jobs/steps (or their equivalents):

  * full test suite (make test)
  * CLI slice (make test-cli)
  * themes slice (make test-themes)
  * templates slice (make test-templates)
    and fails the workflow if verification fails. 
* [ ] CI still runs the existing slice gates (do not remove prior enforcement work).
* [ ] Local verification passes:

  * make lint
  * make test
  * make test-cli
  * make test-themes
  * make test-templates
  * make verify-source-intact
* [ ] Open PR targets develop (develop-based integration). 

## Steps

1. Verify branch and sync from develop.

   1. git checkout develop
   2. git pull
   3. git checkout -b chore/TEST-016-ci-safety-gates
   4. git branch --show-current 

2. Implement (or confirm existing) local source-integrity gate.

   * If missing, add one of the following (prefer script + Make target):

     * scripts/verify_source_intact.sh (or .py)
     * Makefile target: verify-source-intact
   * The gate should:

     * Assert critical source paths exist (at minimum: themes/theme_a and themes/theme_a/theme.json).
     * Fail if there are tracked diffs after tests (git diff --exit-code).
     * Fail if there are non-ignored untracked files under protected paths (git ls-files --others --exclude-standard …).
   * Keep output actionable: print which files/paths caused failure. 

3. Wire the gate into CI workflow.

   * Update .github/workflows/ci.yml (or the active CI workflow file) to run make verify-source-intact as the final step of each relevant test job:

     * after make test
     * after make test-cli
     * after make test-themes
     * after make test-templates
   * Ensure the verification runs even if earlier steps succeed (standard “final safety check” placement). 

4. Ensure the gate protects CLI output boundaries in practice.

   * Include clients/ in the protected path list so any accidental repo-root client scaffolding is caught immediately. This is a direct enforcement of the CLI safety “writes only under tmp_path / SUM_CLIENT_OUTPUT_PATH” principle. 

5. Run local verification.

   * source .venv/bin/activate
   * make lint
   * make test
   * make test-cli
   * make test-themes
   * make test-templates
   * make verify-source-intact

6. Open a PR into develop.

   * Title: TEST-016: CI safety gates for source integrity
   * Confirm CI runs and the new gate step appears in job logs. 

## Documentation

* [ ] Create TEST-016_followup.md (in the same directory as this task) with:

  * Summary of changes made
  * Files modified/created
  * Any blockers or decisions
  * Test results (commands run + pass/fail)
  * CI notes (job names, confirmation gate ran)

## Commit & Push

* [ ] Stage changes: git add -A
* [ ] Commit: chore(TEST-016): enforce CI source integrity gates

  * Include BOTH TEST-016.md AND docs TEST-016_followup.md
* [ ] Push: git push origin chore/TEST-016-ci-safety-gates

## Verification

* [ ] Run git status --porcelain
* [ ] Expected: empty (clean) OR only intentional untracked files (documented in followup)

## Recommended Agent

| Criteria      | Selection                                                                                     |
| ------------- | --------------------------------------------------------------------------------------------- |
| **Model**     | GPT-5.1 Mini                                                                                  |
| **Thinking**  | Standard                                                                                      |
| **Rationale** | This is CI/Makefile/script plumbing with clear pass/fail criteria and low architectural risk. |
