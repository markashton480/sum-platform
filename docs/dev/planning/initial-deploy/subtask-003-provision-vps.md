# Subtask Template

**Title:** `GH-XXX: Provision staging VPS for Sage & Stone`

---

## Parent

**Work Order:** #YYY — Initial Sage & Stone Deployment (v0.6.0)

---

## Branch

| Branch | Target |
| ------ | ------ |
| N/A    | N/A    |

**Note:** This is a manual operations task. No code changes required.

---

## Deliverable

This subtask will deliver:

- Ubuntu 22.04+ VPS provisioned (DigitalOcean, Linode, Vultr, or similar)
- Baseline packages installed per vps-golden-path.md
- Deploy user created with SSH key access
- Firewall configured (UFW)
- PostgreSQL installed and database created
- Redis installed and verified
- Caddy installed

---

## Boundaries

### Do

- Provision VPS from provider of choice
- Follow `infrastructure/docs/vps-golden-path.md` sections 1-6
- Use `infrastructure/scripts/provision_vps.sh` if helpful
- Document VPS details in secure location (IP, provider, access)
- Verify SSH access as deploy user

### Do NOT

- ❌ Do not deploy the site yet — that's subtask #4
- ❌ Do not configure systemd services yet
- ❌ Do not configure Caddy site config yet
- ❌ Do not store VPS credentials in git

---

## Acceptance Criteria

- [ ] VPS accessible via SSH as deploy user
- [ ] `python3 --version` returns 3.10+
- [ ] `redis-cli ping` returns PONG
- [ ] PostgreSQL database exists and is accessible
- [ ] `caddy version` returns valid version
- [ ] `ufw status` shows ports 22, 80, 443 allowed
- [ ] DNS for `sage-and-stone.lintel.site` points to VPS IP

---

## Test Commands

Run these on the VPS after provisioning:

```bash
# As deploy user
ssh deploy@<VPS_IP>

# Verify Python
python3 --version

# Verify Redis
redis-cli ping

# Verify Postgres (replace with actual credentials)
psql "postgresql://sage_stone_user:PASSWORD@127.0.0.1:5432/sage_stone_db" -c "SELECT 1;"

# Verify Caddy
caddy version

# Verify firewall
sudo ufw status verbose

# Verify Redis is localhost-only
sudo netstat -tlnp | grep 6379
```

---

## Files Expected to Change

No files in repository. VPS configuration only.

**Document in secure location (password manager or private notes):**
- VPS IP address
- VPS provider and region
- Database credentials
- Deploy user SSH key fingerprint

---

## Dependencies

**Depends On:**

- [ ] Subtask #2 (SSH strategy) should be documented before provisioning

**Blocks:**

- Subtask #4 (Deploy Sage & Stone) requires VPS ready

---

## Risk

**Level:** Medium

**Why:**
- Manual process with many steps
- First-time execution (no muscle memory yet)
- Potential for misconfiguration

**Mitigation:**
- Follow vps-golden-path.md step by step
- Verify each section before proceeding
- Test SSH access early to catch key issues

---

## Labels

- [ ] `type:task`
- [ ] `agent:human`
- [ ] `component:infra`
- [ ] `risk:med`
- [ ] Milestone: `v0.6.0`

---

## Project Fields

- [ ] Agent: human
- [ ] Model Planned: human
- [ ] Component: infra
- [ ] Change Type: chore
- [ ] Risk: med
- [ ] Release: `v0.6.0`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] VPS accessible and baseline verified
- [ ] DNS pointing to VPS
- [ ] Credentials stored securely (not in git)
- [ ] Parent Work Order updated

---

## Checklist (from vps-golden-path.md)

### Section 1: VPS Prerequisites
- [ ] VPS created (Ubuntu 22.04+)
- [ ] Baseline packages installed
- [ ] Redis installed and running
- [ ] Caddy installed

### Section 2: Deploy User + Hardening
- [ ] Deploy user created
- [ ] SSH key added to authorized_keys
- [ ] Password auth disabled (optional for initial setup)

### Section 3: Firewall
- [ ] UFW enabled
- [ ] Ports 22, 80, 443 allowed

### Section 4: PostgreSQL
- [ ] Database user created
- [ ] Database created
- [ ] Connectivity verified

### Section 5: Directory Layout
- [ ] `/srv/sum/sage-and-stone/` created
- [ ] Subdirectories created (backups, static, media)
- [ ] `/var/log/sum/sage-and-stone/` created

### Section 6: Environment
- [ ] `.env` file created at `/srv/sum/sage-and-stone/.env`
- [ ] Permissions set to 600

### DNS
- [ ] `sage-and-stone.lintel.site` A record points to VPS IP
- [ ] DNS propagated (verify with `dig sage-and-stone.lintel.site`)
