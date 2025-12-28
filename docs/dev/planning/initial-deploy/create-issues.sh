#!/bin/bash
# Create GitHub Issues for Initial Sage & Stone Deployment Work Order
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - Run from repository root
#
# Usage: ./docs/dev/planning/initial-deploy/create-issues.sh

set -e

REPO="markashton480/sum-platform"
MILESTONE="v0.6.0"

echo "Creating Work Order issue..."

WO_BODY=$(cat <<'EOF'
## Parent

**Version Declaration:** #190 (v0.6.0)

## Branch

| Branch                  | Target          |
| ----------------------- | --------------- |
| `feature/initial-deploy` | `release/0.6.0` |

## Objective

- [ ] Consolidate and organize deployment documentation into `/infrastructure/`
- [ ] Establish SSH key strategy and secrets management approach
- [ ] Provision first VPS (sandbox/staging environment)
- [ ] Deploy Sage & Stone site to `sage-and-stone.lintel.site`
- [ ] Complete smoke tests and update operational tracking
- [ ] Document lessons learned in `what-broke-last-time.md`

## Scope

### In Scope

- Documentation consolidation: move `docs/dev/deploy/vps-golden-path.md` to `/infrastructure/docs/`
- Remove empty `docs/dev/deploy/` directory
- SSH key strategy documentation for deploy user access
- VPS provisioning using `provision_vps.sh` and golden path
- First Sage & Stone deployment to staging domain
- Smoke tests per `smoke-tests.md`
- Loop sites matrix update

### Out of Scope

- Production domain setup (uses staging `*.lintel.site` only)
- Automated CI/CD pipeline (manual deploy for M6)
- Celery worker setup (optional, not required for launch)
- Multi-site VPS hosting (single site for initial validation)
- External monitoring setup (future scope)

## Subtasks

| #   | Issue                                           | Branch                               | Status |
| --- | ----------------------------------------------- | ------------------------------------ | ------ |
| 1   | Consolidate deployment documentation            | `feature/initial-deploy/001-docs`    | 🔲     |
| 2   | Document SSH key strategy                       | `feature/initial-deploy/002-ssh`     | 🔲     |
| 3   | Provision staging VPS                           | (manual ops - no branch)             | 🔲     |
| 4   | Deploy Sage & Stone to staging                  | (manual ops - no branch)             | 🔲     |
| 5   | Execute smoke tests and update tracking         | (manual ops - no branch)             | 🔲     |

## Risk

**Level:** Medium

**Factors:**
- First real deployment — process not yet muscle memory
- SSH key management introduces security surface
- VPS provisioning has many manual steps

## Definition of Done

- [ ] All documentation subtasks merged to feature branch
- [ ] VPS provisioned and accessible via SSH
- [ ] Sage & Stone deployed to `sage-and-stone.lintel.site`
- [ ] `/health/` returns HTTP 200
- [ ] Homepage renders correctly
- [ ] Loop sites matrix updated
- [ ] Any issues documented in what-broke-last-time.md
EOF
)

WO_NUMBER=$(gh issue create \
  --repo "$REPO" \
  --title "WO: Initial Sage & Stone Deployment (v0.6.0)" \
  --body "$WO_BODY" \
  --label "type:work-order,component:infrastructure,component:docs,risk:medium" \
  --milestone "$MILESTONE" \
  | grep -oE '[0-9]+$')

echo "Created Work Order: #$WO_NUMBER"

# --- Subtask 1: Docs Consolidation ---
echo "Creating Subtask 1: Docs Consolidation..."

ST1_BODY=$(cat <<EOF
## Parent

**Work Order:** #$WO_NUMBER — Initial Sage & Stone Deployment (v0.6.0)

## Branch

| Branch                             | Target                   |
| ---------------------------------- | ------------------------ |
| \`feature/initial-deploy/001-docs\`  | \`feature/initial-deploy\` |

## Deliverable

- Move \`docs/dev/deploy/vps-golden-path.md\` to \`infrastructure/docs/vps-golden-path.md\`
- Create \`infrastructure/docs/\` directory if not exists
- Remove empty \`docs/dev/deploy/\` directory
- Update all internal documentation references to the new location

## Acceptance Criteria

- [ ] \`infrastructure/docs/vps-golden-path.md\` exists with identical content
- [ ] \`docs/dev/deploy/\` directory no longer exists
- [ ] \`docs/ops-pack/deploy-runbook.md\` references correct new path
- [ ] \`make lint\` passes

## Risk

**Level:** Low
EOF
)

ST1_NUMBER=$(gh issue create \
  --repo "$REPO" \
  --title "Consolidate deployment documentation into /infrastructure/" \
  --body "$ST1_BODY" \
  --label "type:task,component:docs,component:infrastructure,risk:low" \
  --milestone "$MILESTONE" \
  | grep -oE '[0-9]+$')

echo "Created Subtask 1: #$ST1_NUMBER"

# Link as sub-issue
gh issue develop "$ST1_NUMBER" --repo "$REPO" --issue "$WO_NUMBER" 2>/dev/null || \
  echo "Note: Sub-issue linking may require manual setup or gh-sub-issue extension"

# --- Subtask 2: SSH Strategy ---
echo "Creating Subtask 2: SSH Strategy..."

ST2_BODY=$(cat <<EOF
## Parent

**Work Order:** #$WO_NUMBER — Initial Sage & Stone Deployment (v0.6.0)

## Branch

| Branch                            | Target                   |
| --------------------------------- | ------------------------ |
| \`feature/initial-deploy/002-ssh\`  | \`feature/initial-deploy\` |

## Deliverable

- New document: \`infrastructure/docs/ssh-strategy.md\`
- SSH key management approach for the \`deploy\` user
- Key generation and distribution procedure
- Security baseline (key rotation, access audit)

## Acceptance Criteria

- [ ] \`infrastructure/docs/ssh-strategy.md\` exists
- [ ] Document covers: key generation, distribution, security baseline
- [ ] Cross-reference added to vps-golden-path.md Section 2
- [ ] \`make lint\` passes

## Risk

**Level:** Low
EOF
)

ST2_NUMBER=$(gh issue create \
  --repo "$REPO" \
  --title "Document SSH key strategy for VPS deployment" \
  --body "$ST2_BODY" \
  --label "type:task,component:docs,component:infrastructure,risk:low" \
  --milestone "$MILESTONE" \
  | grep -oE '[0-9]+$')

echo "Created Subtask 2: #$ST2_NUMBER"

# --- Subtask 3: Provision VPS ---
echo "Creating Subtask 3: Provision VPS..."

ST3_BODY=$(cat <<EOF
## Parent

**Work Order:** #$WO_NUMBER — Initial Sage & Stone Deployment (v0.6.0)

## Branch

N/A — Manual operations task

## Deliverable

- Ubuntu 22.04+ VPS provisioned
- Baseline packages installed per vps-golden-path.md
- Deploy user created with SSH key access
- Firewall configured (UFW)
- PostgreSQL installed and database created
- Redis installed and verified
- Caddy installed

## Acceptance Criteria

- [ ] VPS accessible via SSH as deploy user
- [ ] \`python3 --version\` returns 3.10+
- [ ] \`redis-cli ping\` returns PONG
- [ ] PostgreSQL database exists and is accessible
- [ ] \`caddy version\` returns valid version
- [ ] \`ufw status\` shows ports 22, 80, 443 allowed
- [ ] DNS for \`sage-and-stone.lintel.site\` points to VPS IP

## Risk

**Level:** Medium
EOF
)

ST3_NUMBER=$(gh issue create \
  --repo "$REPO" \
  --title "Provision staging VPS for Sage & Stone" \
  --body "$ST3_BODY" \
  --label "type:task,agent:human,component:infrastructure,risk:medium" \
  --milestone "$MILESTONE" \
  | grep -oE '[0-9]+$')

echo "Created Subtask 3: #$ST3_NUMBER"

# --- Subtask 4: Deploy ---
echo "Creating Subtask 4: Deploy Sage & Stone..."

ST4_BODY=$(cat <<EOF
## Parent

**Work Order:** #$WO_NUMBER — Initial Sage & Stone Deployment (v0.6.0)

## Branch

N/A — Manual operations task

## Deliverable

- Sage & Stone client project deployed to VPS
- systemd services configured and running (gunicorn)
- Caddy configured with TLS for \`sage-and-stone.lintel.site\`
- Site accessible via HTTPS

## Acceptance Criteria

- [ ] \`https://sage-and-stone.lintel.site/\` returns HTTP 200
- [ ] \`https://sage-and-stone.lintel.site/health/\` returns HTTP 200
- [ ] Homepage renders with correct theme
- [ ] Static files load (CSS, JS)
- [ ] Gunicorn service is running
- [ ] Caddy is serving TLS (valid certificate)

## Risk

**Level:** Medium
EOF
)

ST4_NUMBER=$(gh issue create \
  --repo "$REPO" \
  --title "Deploy Sage & Stone to staging VPS" \
  --body "$ST4_BODY" \
  --label "type:task,agent:human,component:infrastructure,risk:medium" \
  --milestone "$MILESTONE" \
  | grep -oE '[0-9]+$')

echo "Created Subtask 4: #$ST4_NUMBER"

# --- Subtask 5: Smoke Tests ---
echo "Creating Subtask 5: Smoke Tests..."

ST5_BODY=$(cat <<EOF
## Parent

**Work Order:** #$WO_NUMBER — Initial Sage & Stone Deployment (v0.6.0)

## Branch

N/A — Manual operations task with documentation updates

## Deliverable

- Complete smoke test execution per \`docs/ops-pack/smoke-tests.md\`
- Initial database backup created
- \`docs/ops-pack/loop-sites-matrix.md\` updated with Sage & Stone entry
- Any issues documented in \`docs/ops-pack/what-broke-last-time.md\`

## Acceptance Criteria

- [ ] All smoke tests from smoke-tests.md executed
- [ ] Health endpoint returns HTTP 200
- [ ] Homepage renders correctly
- [ ] Redis connectivity verified
- [ ] Backup file exists at \`/srv/sum/sage-and-stone/backups/\`
- [ ] \`loop-sites-matrix.md\` contains Sage & Stone entry
- [ ] Any deployment issues documented

## Risk

**Level:** Low
EOF
)

ST5_NUMBER=$(gh issue create \
  --repo "$REPO" \
  --title "Execute smoke tests and update operational tracking" \
  --body "$ST5_BODY" \
  --label "type:task,agent:human,component:docs,component:infrastructure,risk:low" \
  --milestone "$MILESTONE" \
  | grep -oE '[0-9]+$')

echo "Created Subtask 5: #$ST5_NUMBER"

# --- Update Work Order with issue numbers ---
echo ""
echo "============================================"
echo "Issues Created Successfully!"
echo "============================================"
echo ""
echo "Work Order:  #$WO_NUMBER"
echo "Subtask 1:   #$ST1_NUMBER (Docs Consolidation)"
echo "Subtask 2:   #$ST2_NUMBER (SSH Strategy)"
echo "Subtask 3:   #$ST3_NUMBER (Provision VPS)"
echo "Subtask 4:   #$ST4_NUMBER (Deploy Sage & Stone)"
echo "Subtask 5:   #$ST5_NUMBER (Smoke Tests)"
echo ""
echo "Next steps:"
echo "1. Update Work Order #$WO_NUMBER subtasks table with issue numbers"
echo "2. Link subtasks as sub-issues (if using GitHub Projects sub-tasks feature)"
echo "   gh issue edit $ST1_NUMBER --add-label 'parent:#$WO_NUMBER'"
echo "   Or use: gh api repos/$REPO/issues/$WO_NUMBER/sub_issues -f sub_issue_id=$ST1_NUMBER"
echo ""
