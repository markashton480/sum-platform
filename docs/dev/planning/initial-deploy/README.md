# Initial Sage & Stone Deployment - Work Order

**Version:** v0.6.0
**Status:** Planning
**Target:** Deploy Sage & Stone to `sage-and-stone.lintel.site`

## Overview

This Work Order covers the first deployment of a SUM platform consumer site (Sage & Stone) to a staging VPS. This is the final step of M6 and establishes the deploy/upgrade practice loop.

## Files

| File | Description |
|------|-------------|
| `work-order.md` | Parent Work Order defining objectives and scope |
| `subtask-001-docs-consolidation.md` | Move vps-golden-path.md to infrastructure/docs/ |
| `subtask-002-ssh-strategy.md` | Document SSH key management approach |
| `subtask-003-provision-vps.md` | Manual VPS provisioning checklist |
| `subtask-004-deploy-sage-stone.md` | Deploy site to VPS checklist |
| `subtask-005-smoke-tests.md` | Smoke tests and tracking updates |
| `create-issues.sh` | Script to create GitHub issues |

## Dependencies

```
Subtask 1 (Docs) ──┐
                   ├──► Subtask 3 (VPS) ──► Subtask 4 (Deploy) ──► Subtask 5 (Smoke Tests)
Subtask 2 (SSH) ───┘
```

- Subtasks 1 & 2 can run in parallel (both are documentation)
- Subtask 3 requires SSH strategy documented
- Subtask 4 requires VPS provisioned
- Subtask 5 requires deployment complete

## Creating GitHub Issues

Run the script to create all issues with proper linking:

```bash
chmod +x docs/dev/planning/initial-deploy/create-issues.sh
./docs/dev/planning/initial-deploy/create-issues.sh
```

**Prerequisites:**
- `gh` CLI installed and authenticated
- Access to create issues in markashton480/sum-platform

## Key Documentation

- **Golden Path:** `infrastructure/docs/vps-golden-path.md` (after consolidation)
- **Deploy Runbook:** `docs/ops-pack/deploy-runbook.md`
- **Smoke Tests:** `docs/ops-pack/smoke-tests.md`
- **Loop Sites Matrix:** `docs/ops-pack/loop-sites-matrix.md`

## Success Criteria

1. Documentation consolidated and coherent
2. VPS provisioned with all baseline services
3. Sage & Stone accessible at `https://sage-and-stone.lintel.site/`
4. Health endpoint returns HTTP 200
5. Initial backup created
6. Loop sites matrix updated
7. Any issues documented in what-broke-last-time.md
