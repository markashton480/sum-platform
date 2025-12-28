# Subtask Template

**Title:** `GH-XXX: Document SSH key strategy for VPS deployment`

---

## Parent

**Work Order:** #YYY — Initial Sage & Stone Deployment (v0.6.0)

---

## Branch

| Branch                            | Target                   |
| --------------------------------- | ------------------------ |
| `feature/initial-deploy/002-ssh`  | `feature/initial-deploy` |

```bash
git checkout feature/initial-deploy
git pull origin feature/initial-deploy
git checkout -b feature/initial-deploy/002-ssh
git push -u origin feature/initial-deploy/002-ssh
```

---

## Deliverable

This subtask will deliver:

- New document: `infrastructure/docs/ssh-strategy.md`
- SSH key management approach for the `deploy` user
- Key generation and distribution procedure
- Security baseline (key rotation, access audit)
- Integration with deploy.sh workflow

---

## Boundaries

### Do

- Create `infrastructure/docs/ssh-strategy.md`
- Document key generation procedure (ed25519 preferred)
- Document how to add authorized_keys to deploy user
- Document security baseline (disable password auth, root SSH)
- Reference from vps-golden-path.md where appropriate (add cross-link)
- Keep it practical — operator-focused, not theoretical

### Do NOT

- ❌ Do not implement automated key management (manual process for now)
- ❌ Do not modify deploy.sh — document assumptions only
- ❌ Do not add CI/CD SSH key handling (future scope)
- ❌ Do not over-engineer — single-operator scenario for v0.6.0

---

## Acceptance Criteria

- [ ] `infrastructure/docs/ssh-strategy.md` exists
- [ ] Document covers: key generation, distribution, security baseline
- [ ] Cross-reference added to vps-golden-path.md Section 2 (SSH hardening)
- [ ] Document is operator-actionable (clear steps, not abstract guidance)
- [ ] `make lint` passes

---

## Test Commands

```bash
make lint

# Verify file exists
test -f infrastructure/docs/ssh-strategy.md && echo "OK" || echo "MISSING"

# Verify cross-reference exists
grep -q "ssh-strategy.md" infrastructure/docs/vps-golden-path.md && echo "OK" || echo "MISSING CROSS-REF"
```

---

## Files Expected to Change

```
infrastructure/docs/ssh-strategy.md         # New file
infrastructure/docs/vps-golden-path.md      # Cross-reference added
```

---

## Dependencies

**Depends On:**

- [ ] Subtask #1 should complete first (so vps-golden-path.md is at new location)

**Blocks:**

- Subtask #3 (VPS provisioning) needs SSH strategy documented

---

## Risk

**Level:** Low

**Why:** Documentation only. No infrastructure changes. Security guidance follows standard practices.

---

## Labels

- [ ] `type:task`
- [ ] `agent:claude`
- [ ] `component:docs`
- [ ] `component:infra`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.0`

---

## Project Fields

- [ ] Agent: claude
- [ ] Model Planned: claude-sonnet
- [ ] Component: docs, infra
- [ ] Change Type: docs
- [ ] Risk: low
- [ ] Release: `v0.6.0`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied
- [ ] Parent Work Order updated

---

## Commit Message

```
docs(infrastructure): add SSH key strategy for VPS deployment

- Document key generation procedure (ed25519)
- Define security baseline (password auth disabled, no root SSH)
- Add cross-reference from vps-golden-path.md

Closes #XXX
```

---

## Suggested Content Outline

```markdown
# SSH Key Strategy for VPS Deployment

## Overview
Single-operator SSH key management for SUM platform deployments.

## Key Generation
- Use ed25519: `ssh-keygen -t ed25519 -C "deploy@lintel.site"`
- Store private key securely (not in repo, not in cloud storage)
- One key per operator (not per site)

## Deploy User Setup
1. Create deploy user (per vps-golden-path.md)
2. Add public key to /home/deploy/.ssh/authorized_keys
3. Set permissions: 700 for .ssh, 600 for authorized_keys

## Security Baseline
- Disable password authentication
- Disable root SSH login
- Use fail2ban (optional, recommended)
- Key rotation: annually or on personnel change

## Secrets Management
- Database passwords: generate per-site, store in password manager
- Django secret key: generate per-site, store in .env (not in repo)
- No secrets in git, ever

## Integration with deploy.sh
- deploy.sh assumes SSH key auth is working
- Test with: `ssh deploy@<vps-ip> "echo connected"`
- Troubleshoot: check permissions, sshd_config, firewall
```
