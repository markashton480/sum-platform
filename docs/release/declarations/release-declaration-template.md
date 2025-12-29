# Release Declaration: v{VERSION}

> **This document is the source of truth for what this release contains.**
> The release audit agent will verify the PR against this declaration.
> Any deviation is a red flag that must be resolved before merge.

---

## Release Metadata

| Field       | Value                               |
| ----------- | ----------------------------------- |
| **Version** | `v0.X.Y`                            |
| **Type**    | `PATCH` / `MINOR` / `MAJOR`         |
| **Branch**  | `release/v0.X.Y` or `hotfix/v0.X.Y` |
| **Target**  | `main`                              |
| **Date**    | YYYY-MM-DD                          |
| **Author**  | @username                           |

---

## Statement of Intent

### What This Release IS

> _One sentence describing the purpose of this release._

Example: "Fix the sync script to clone to /tmp instead of inside the repo, preventing accidental gitlink commits."

### What This Release IS NOT

> _Explicitly state what is OUT OF SCOPE._

Example: "This release does NOT include any new features, form builders, blog functionality, or template changes."

---

## Expected Scope

### Commits

| Expected Count | Tolerance |
| -------------- | --------- |
| `4`            | ±1        |

> If actual commits exceed tolerance, the release MUST be audited manually.

### Lines Changed

| Expected    | Tolerance |
| ----------- | --------- |
| `+30 / -20` | ±50%      |

> Order of magnitude matters. A patch claiming "+30 lines" that shows "+3,000 lines" is a red flag.

### Files Changed

**Expected files (exhaustive list):**

```
.gitignore
CHANGELOG.md
pyproject.toml
core/pyproject.toml
core/sum_core/__init__.py
boilerplate/requirements.txt
cli/sum_cli/boilerplate/requirements.txt
scripts/sync_to_public.py
docs/ops-pack/RELEASE_RUNBOOK.md
docs/release/agent-prompt.md
```

**Unexpected files (red flags if present):**

```
# Feature code
core/sum_core/blocks/*
core/sum_core/forms/*
core/sum_core/pages/*

# Templates
themes/*/templates/*

# Static assets
themes/*/static/*

# Migrations
*/migrations/*.py

# Tests (unless test-only release)
tests/*
```

---

## Version Checklist

All version references must be consistent:

| File                                       | Field         | Expected Value |
| ------------------------------------------ | ------------- | -------------- |
| `core/pyproject.toml`                      | `version`     | `0.X.Y`        |
| `core/sum_core/__init__.py`                | `__version__` | `0.X.Y`        |
| `pyproject.toml` (root)                    | `version`     | `0.X.Y`        |
| `boilerplate/requirements.txt`             | git tag       | `v0.X.Y`       |
| `cli/sum_cli/boilerplate/requirements.txt` | git tag       | `v0.X.Y`       |
| `CHANGELOG.md`                             | latest entry  | `v0.X.Y`       |

---

## Changelog Entry

**Required content:**

```markdown
## [v0.X.Y] - YYYY-MM-DD

### Changed

- Sync staging now defaults to `/tmp/sum-core-sync` to avoid accidental gitlinks; release docs updated.
```

**Prohibited content:**

- No features (`### Added` section for PATCH releases)
- No breaking changes (`### Breaking` section for PATCH/MINOR releases)
- No unrelated fixes

---

## Pre-Merge Verification

Before requesting merge, verify:

- [ ] PR title matches: `Release v0.X.Y` or `Release v0.X.Y (hotfix)`
- [ ] Branch name matches: `release/v0.X.Y` or `hotfix/v0.X.Y`
- [ ] Commit count within tolerance
- [ ] Lines changed within tolerance
- [ ] All expected files present
- [ ] No unexpected files present
- [ ] All version references consistent
- [ ] Changelog entry matches intent
- [ ] CI passes (`lint-and-test`)

---

## Sign-Off

| Role                     | Name | Date | Approved |
| ------------------------ | ---- | ---- | -------- |
| Author                   |      |      | ☐        |
| Auditor (human or agent) |      |      | ☐        |

---

## Audit Log

_Append audit results here:_

```
[YYYY-MM-DD HH:MM] Audit by: <agent/human>
Result: PASS / FAIL
Notes: <any observations>
```
