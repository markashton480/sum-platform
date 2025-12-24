# THEME-026: Add Codex “preflight” slash prompt + repo preflight script

## Branch
- [ ] Checkout/create: `chore/THEME-026-codex-preflight`
- [ ] Verify: `git branch --show-current`

## Context
We keep hitting avoidable merge/test drama because agents sometimes start work on branches that are behind `origin/develop` (especially across worktrees), then later collide with generated theme assets (`themes/theme_a/static/theme_a/css/main.css` + `.build_fingerprint`) and/or fail CI safety checks.

We want a **repeatable “preflight” ritual** that Codex can run at the start of *every* ticket:
- Confirm clean working tree
- Fetch + confirm branch base is current
- Rebase onto `origin/develop` (or stop with a clear message if unsafe)
- Print next actions / guardrails (esp. around generated CSS + fingerprint)

Codex CLI supports custom “slash commands” via **custom prompts** stored in `~/.codex/prompts/` and invoked as `/prompts:<name>`.

## Objective
Create a repo-owned preflight script + documentation, and provide a copy/pasteable Codex prompt file that Mark can install locally (and share with other devs) so every ticket can start with `/prompts:sum-preflight`.

## Key Files
- `scripts/codex_preflight.sh` – new repo script that performs the actual checks/actions
- `Makefile` – add `make preflight` wrapper to standardise usage
- `docs/dev/codex/README.md` (create if missing) – how to install/use the Codex prompt and the preflight script
- `docs/dev/codex/prompts/sum-preflight.md` – **versioned template** for the Codex prompt file (developers copy to `~/.codex/prompts/`)

## Acceptance Criteria
- [ ] Running `make preflight`:
  - [ ] fails fast if there are uncommitted changes (with a clear remediation message)
  - [ ] fetches `origin`
  - [ ] confirms the branch can be rebased onto `origin/develop` safely
  - [ ] performs `git rebase origin/develop` when behind (non-interactive; stops on conflicts)
  - [ ] prints a short “what next” summary (run tests, rebuild theme CSS if required, etc.)
- [ ] `docs/dev/codex/README.md` clearly explains how to install and invoke `/prompts:sum-preflight`
- [ ] Prompt template exists at `docs/dev/codex/prompts/sum-preflight.md` with YAML front matter metadata
- [ ] Tests pass per `test-strategy-post-mvp-v1.md`
- [ ] No regressions in existing functionality

## Steps
1. **Create repo preflight script**
   - Add `scripts/codex_preflight.sh` (bash).
   - Requirements for the script:
     - `set -euo pipefail`
     - Determine repo root via `git rev-parse --show-toplevel`
     - Refuse to run if `git status --porcelain` is non-empty (print list + advise commit/stash)
     - `git fetch origin`
     - Ensure `origin/develop` exists; if not, print helpful error
     - Detect relationship to `origin/develop` (ahead/behind/diverged)
     - If behind: run `git rebase origin/develop`
     - If diverged: abort with message (“manual intervention required: rebase may rewrite remote history”)
     - If already up-to-date: print confirmation and exit 0
     - Print a final checklist including:
       - “Run relevant tests”
       - “If you changed theme templates/tailwind inputs, rebuild theme CSS + fingerprint before pushing”
       - “If you hit conflicts in generated CSS/fingerprint: resolve by regenerating, not hand-merging”

2. **Add Makefile entrypoint**
   - Add a target:
     - `preflight:` → runs `./scripts/codex_preflight.sh`
   - Optional: allow `BASE=origin/develop` override later, but default is fine.

3. **Add Codex prompt template (versioned in repo)**
   - Create: `docs/dev/codex/prompts/sum-preflight.md`
   - Include YAML front matter:
     - `description: SUM preflight: sync branch to origin/develop + print theme build checklist`
     - `argument-hint: [TICKET_ID=<THEME-###>]`
   - Body should:
     - Ask Codex to run `make preflight`
     - Then show `/diff`
     - Then print “ready to start $TICKET_ID” and remind about generated theme assets policy.

4. **Documentation**
   - Create/update `docs/dev/codex/README.md` explaining:
     - How Codex CLI custom prompts work (must live in `~/.codex/prompts/`)
     - Install steps:
       - `mkdir -p ~/.codex/prompts`
       - `cp docs/dev/codex/prompts/sum-preflight.md ~/.codex/prompts/sum-preflight.md`
       - Restart Codex CLI session
     - Usage:
       - `/prompts:sum-preflight TICKET_ID=THEME-0XX`
     - Team note: prompt file is local-only; repo contains the “blessed template” to copy from.

## Testing Requirements
- [ ] Run: `make test`
- [ ] Expected: all tests pass (green)
- [ ] Manual smoke:
  - [ ] On a clean branch: `make preflight` prints “up to date” and exits 0
  - [ ] With an intentional local change (dirty tree): `make preflight` exits non-zero and tells you what’s dirty
  - [ ] On a branch behind develop: `make preflight` rebases and exits 0 (or stops cleanly on conflicts)

## Documentation Updates
Update if changes affect:
- [ ] `WIRING-INVENTORY.md` (only if you add new “standard workflow” worth capturing globally)
- [ ] `test-strategy-post-mvp-v1.md` (only if you change recommended dev workflow materially)

## Deliverables
- [ ] Create `THEME-026_followup.md` (same directory as this ticket) containing:
  - Summary of changes
  - Files modified/created
  - Test results
  - Decisions made / blockers hit
  - Doc updates made (if any)

## Commit & Push
- [ ] Stage: `git add -A`
- [ ] Commit: `chore(THEME-026): add Codex preflight script + prompt template`
  - **Must include both** `THEME-026.md` AND `THEME-026_followup.md`
- [ ] Push: `git push origin chore/THEME-026-codex-preflight`

## Verification
- [ ] `git status --porcelain` → empty or documented untracked only

---

## Recommended Agent
- **Criteria:** Scripts + docs, low risk, needs careful bash ergonomics
- **Selection:** GPT-5.1 Mini
- **Thinking:** Low
- **Rationale:** Cost-effective; straightforward changes; minimal architectural risk
