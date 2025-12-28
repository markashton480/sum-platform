# SSH Key Strategy for VPS Deployment

Single-operator SSH key management for SUM platform deployments. This document
assumes a manual process for v0.6.0 and keeps deploy access scoped to the
`deploy` user.

## Overview

- One key per operator (not per site).
- Key auth only; password auth disabled after verification.
- Root SSH disabled; use `sudo` via the `deploy` user.

## Key generation (ed25519 preferred)

Generate the key locally on the operator machine (use a dedicated filename to
avoid clobbering defaults):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/sum-deploy -C "deploy@<operator-domain>"
```

Suggested defaults:

- Location: `~/.ssh/sum-deploy`
- Passphrase: required for operator laptops

## Key distribution

1. Copy the public key to the server (temporary password auth may be enabled
   for first access):

```bash
ssh-copy-id -i ~/.ssh/sum-deploy.pub deploy@<vps-ip>
```

2. Verify the key works:

```bash
ssh -i ~/.ssh/sum-deploy deploy@<vps-ip> "echo connected"
```

3. Confirm permissions on the server:

```bash
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

## Security baseline

- Disable password authentication after key access is verified:
  - `PasswordAuthentication no`
- Disable root SSH login:
  - `PermitRootLogin no`
- Keep your current SSH session open, and verify a new login works before
  closing it.
- Reload sshd after changes (restart if reload does not pick up config
  updates):

```bash
sudo systemctl reload ssh
sudo systemctl restart ssh
```

Optional but recommended:

- Enable fail2ban for basic SSH abuse protection.
- Restrict SSH to known IPs via firewall rules if feasible.

## Key rotation and access audit

- Rotate keys annually, or immediately on personnel change.
- Review `/home/deploy/.ssh/authorized_keys` during audits.
- Remove unused keys promptly.

## Secrets handling (adjacent guidance)

- Database passwords: generate per site and store in a password manager.
- Django secret key: generate per site and store in `.env` (never in git).
- Do not store private keys in repos or shared cloud drives.

## Integration with deploy.sh

- `deploy.sh` assumes SSH key auth is already working.
- Test access before running deployments:

```bash
ssh deploy@<vps-ip> "echo connected"
```
