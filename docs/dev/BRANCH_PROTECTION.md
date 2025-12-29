# Branch Protection Rules

This document defines protection rules for each branch level in our 5-tier model.

---

## Protection Philosophy

**Stricter as you go up:**
- Task branches → minimal (agent workspace)
- Feature branches → require CI
- Release branches → require CI + Claude review
- Develop → require CI + Claude + audit
- Main → strictest, all gates

**Key principle:** Protection exists to catch mistakes at the right level, not to slow down work.

---

## Branch Rules by Level

### `main` — Production

**Purpose:** Tagged releases only. Always deployable.

| Rule | Setting |
|------|---------|
| Require PR | ✅ Yes |
| Required approvals | 2 |
| Dismiss stale reviews | ✅ Yes |
| Require review from CODEOWNERS | ✅ Yes |
| Require status checks | ✅ Yes |
| Required checks | `ci`, `release-audit` |
| Require branches up to date | ✅ Yes |
| Require conversation resolution | ✅ Yes |
| Require signed commits | ✅ Optional |
| Allow force push | ❌ No |
| Allow deletions | ❌ No |

**Who can merge:** Repository admins only

---

### `develop` — Integration

**Purpose:** Stable integration of completed versions. Should always be deployable.

| Rule | Setting |
|------|---------|
| Require PR | ✅ Yes |
| Required approvals | 1 |
| Dismiss stale reviews | ✅ Yes |
| Require status checks | ✅ Yes |
| Required checks | `ci`, `release-audit` |
| Require branches up to date | ✅ Yes |
| Require conversation resolution | ✅ Yes |
| Allow force push | ❌ No |
| Allow deletions | ❌ No |

**Who can merge:** Maintainers

---

### `release/*` — Version Integration

**Purpose:** Collects features for a specific version.

| Rule | Setting |
|------|---------|
| Require PR | ✅ Yes |
| Required approvals | 1 |
| Dismiss stale reviews | ✅ Yes |
| Require status checks | ✅ Yes |
| Required checks | `ci`, `claude-review` |
| Require branches up to date | ❌ No (parallel features) |
| Require conversation resolution | ✅ Yes |
| Allow force push | ❌ No |
| Allow deletions | ✅ Yes (after version ships) |

**Who can merge:** Maintainers

---

### `feature/*` — Feature Integration

**Purpose:** Collects tasks for a specific feature/component.

| Rule | Setting |
|------|---------|
| Require PR | ✅ Yes |
| Required approvals | 0 (Claude review sufficient) |
| Require status checks | ✅ Yes |
| Required checks | `ci`, `claude-review` |
| Require branches up to date | ❌ No (parallel tasks) |
| Require conversation resolution | ✅ Yes |
| Allow force push | ❌ No |
| Allow deletions | ✅ Yes (after feature merged) |

**Who can merge:** Maintainers, Agents (via automation)

---

### `task/*`, `fix/*`, `feat/*` — Work Branches

**Purpose:** Active development by agents/developers.

| Rule | Setting |
|------|---------|
| Require PR | ✅ Yes (to merge) |
| Required approvals | 0 |
| Require status checks | ✅ Yes |
| Required checks | `ci` |
| Require branches up to date | ❌ No |
| Allow force push | ✅ Yes (for rebasing) |
| Allow deletions | ✅ Yes |

**Who can merge:** Anyone (but PR targets feature branch, not develop)

---

## Required Status Checks

### `ci` (All branches)

**Required check context:** `ci`

This is the *single gate check* produced by `.github/workflows/ci.yml` (job name `ci`).

- For code-changing PRs, the workflow runs lint + the full test suite slices.
- For docs/CI-only PRs, the workflow **short-circuits** (skips lint/tests) but still reports `ci` as ✅ passing.

**Important:** Do **not** require individual job checks like `lint`, `test-full`, etc. Those jobs are intentionally skipped on docs/CI-only PRs to avoid burning runners.

Standard CI pipeline (when code changes):
```yaml
- make lint           # ruff, djlint
- make test-templates # fast fail template ordering
- make test           # pytest
- make test-cli
- make test-themes
```

**Docs/CI-only scope (fast-path):**
- `docs/**`
- `**/*.md`, `**/*.mdx` (markdown anywhere in the repo)
- `.github/**`, `.agent/**`, `.claude/**`
- `AGENTS.md`, `CLAUDE.md`, `README.md`

### `claude-review` (Feature branches and above)

Claude's strategic review must not request changes:
- Submits GitHub review via `gh pr review`
- APPROVE → check passes
- REQUEST CHANGES → check fails (blocks merge)
- COMMENT → check passes (advisory only)

### `claude-docs-review` (Docs changes)

Claude's documentation coherence review.

- Triggered when a PR changes documentation files (matching the docs scope above).
- Posts a structured comment with:
  - contradictions/inconsistencies vs existing docs
  - suggested follow-on doc updates to keep terminology uniform
  - clarity/quality issues, missing steps, broken links, etc.

This is **advisory by default** (not required for merge). If you later decide to require it,
ensure the workflow always reports a status check (even when no docs changed) before adding it as a required check.

### `release-audit` (Develop and main only)

Full scope audit comparing PR against Version Declaration:
- Verifies commit/line count within tolerance
- Checks for undeclared features
- Validates all declared work orders complete

---

## GitHub Settings Configuration

### To configure in GitHub UI:

**Settings → Branches → Add branch protection rule**

For each branch pattern (`main`, `develop`, `release/*`, `feature/*`):

1. **Branch name pattern:** Enter pattern (e.g., `release/*`)

2. **Protect matching branches:**
   - ☑️ Require a pull request before merging
   - ☑️ Require approvals (set number)
   - ☑️ Dismiss stale pull request approvals when new commits are pushed
   - ☑️ Require status checks to pass before merging
     - Search and add: `ci`, `claude-review`, etc.
   - ☑️ Require conversation resolution before merging

3. **Rules applied to everyone including administrators:**
   - For `main`: ☑️ Yes
   - For others: ☐ No (allows admin override)

4. **Allow force pushes:**
   - For task/fix/feat: ☑️ Yes
   - For others: ☐ No

5. **Allow deletions:**
   - For main/develop: ☐ No
   - For others: ☑️ Yes

---

## Rulesets (Alternative to Branch Protection)

GitHub Rulesets provide more flexibility. If using rulesets:

```yaml
# Example ruleset configuration
name: Production Protection
target: branch
enforcement: active
conditions:
  ref_name:
    include: ["refs/heads/main"]
rules:
  - type: pull_request
    parameters:
      required_approving_review_count: 2
      dismiss_stale_reviews_on_push: true
      require_code_owner_review: true
  - type: required_status_checks
    parameters:
      required_status_checks:
        - context: ci
        - context: release-audit
      strict_required_status_checks_policy: true
  - type: non_fast_forward
```

---

## Code Scanning & Quality Gates

### Enable in Settings → Code security and analysis:

| Tool | Purpose | Branches |
|------|---------|----------|
| **Dependabot alerts** | Vulnerable dependencies | All |
| **Dependabot security updates** | Auto-fix vulnerabilities | All |
| **Code scanning (CodeQL)** | Security vulnerabilities | PRs to main/develop |
| **Secret scanning** | Exposed credentials | All |

### CodeQL Configuration

Create `.github/workflows/codeql.yml`:

```yaml
name: CodeQL

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python, javascript
      - uses: github/codeql-action/analyze@v3
```

### Require Code Scanning Results

In branch protection, add as required check:
- `CodeQL` (blocks if high/critical vulnerabilities found)

---

## Coverage Requirements (Optional)

If using coverage reporting (e.g., Codecov):

```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 2%
    patch:
      default:
        target: 80%
```

Add `codecov/project` and `codecov/patch` as required checks for feature branches and above.

---

## Summary Matrix

| Branch | Approvals | CI | Claude | Docs Review | Audit | CodeQL | Force Push |
|--------|-----------|-----|--------|------------|-------|--------|------------|
| `main` | 2 | ✅ | — | ✅ (advisory) | ✅ | ✅ | ❌ |
| `develop` | 1 | ✅ | — | ✅ (advisory) | ✅ | ✅ | ❌ |
| `release/*` | 1 | ✅ | ✅ | ✅ (advisory) | — | ✅ | ❌ |
| `feature/*` | 0 | ✅ | ✅ | ✅ (advisory) | — | — | ❌ |
| `task/*` | 0 | ✅ | — | ✅ (advisory) | — | — | ✅ |

**Docs/CI-only changes:** CI runs in fast-path mode; `ci` still reports success,
but lint/test jobs are skipped.

---

## CODEOWNERS

Create `.github/CODEOWNERS` for required reviews on sensitive paths:

```
# Default owner
* @markashton480

# Core models require explicit review
/core/sum_core/models/ @markashton480

# Migrations require explicit review
/core/sum_core/migrations/ @markashton480

# Settings require explicit review
/core/config/settings/ @markashton480

# CI/CD changes require explicit review
/.github/ @markashton480
```

This ensures changes to critical paths require human review even if other checks pass.
