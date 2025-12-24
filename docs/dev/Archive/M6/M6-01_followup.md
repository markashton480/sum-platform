## M6-001 Follow-up Report: VPS Golden Path Deployment (Caddy + systemd + Postgres + backups)

### Summary

Implemented the **M6-001 “VPS golden path”** deliverables:

- **Infrastructure templates** for Caddy and systemd under `infrastructure/`
- **Deploy + backup + restore scripts** (fail-fast, idempotent where it matters)
- **Runbook** documenting a fresh Ubuntu VPS setup and first deploy
- **Boilerplate support** for golden-path static/media directories via env overrides

### Key Decisions (and why)

- **Gunicorn behind unix socket**: avoids exposing app ports, works cleanly with systemd + Caddy.
- **Logs to journald**: gunicorn configured to log to stdout/stderr, so `journalctl` is the default operational surface.
- **Static/media served by Caddy**: runbook uses `/srv/sum/<site_slug>/{static,media}`; Django is configured to collect to those via env vars.
- **Redis note**: current boilerplate `settings/production.py` configures Redis cache by default and `/health/` treats cache as **critical**, so Redis is effectively required unless production settings are customized.

### Files Added / Changed

- **Added**: `infrastructure/caddy/Caddyfile.template`
- **Added**: `infrastructure/systemd/`
  - `sum-site-gunicorn.service.template`
  - `sum-site-gunicorn.socket.template` (optional)
  - `sum-site-celery.service.template` (optional)
- **Added**: `infrastructure/scripts/`
  - `deploy.sh`
  - `backup_db.sh`
  - `restore_db.sh`
  - `provision_vps.sh` (optional helper)
- **Added**: `docs/dev/deploy/vps-golden-path.md`
- **Changed**: `boilerplate/project_name/settings/base.py`
- **Changed**: `cli/sum_cli/boilerplate/project_name/settings/base.py`
- **Changed**: `boilerplate/.env.example` (dotfile; updated via terminal edit due to editor ignore)
- **Changed**: `cli/sum_cli/boilerplate/.env.example` (dotfile; updated via terminal edit due to editor ignore)

### How To Use (quick pointers)

- **Runbook**: follow `docs/dev/deploy/vps-golden-path.md` end-to-end on a fresh VPS.
- **Deploy script**:
  - `/srv/sum/bin/deploy.sh --site-slug <slug> --ref <tag> --domain <domain>`
  - Supports `--no-restart` for debugging.
- **Backup script**:
  - `/srv/sum/bin/backup_db.sh --site-slug <slug>`
  - Produces `*.sql.gz` in `/srv/sum/<slug>/backups/`.
- **Restore script**:
  - Requires explicit `--i-know-this-will-overwrite`.

### Acceptance Criteria Checklist (M6-001)

- **Provisioning**: runbook covers packages, deploy user, ssh hardening notes, UFW, Postgres setup and verification.
- **Deploy**: deploy script runs `migrate`, `collectstatic`, restarts gunicorn, and performs health + sitemap smoke checks.
- **Backup/Restore**: scripts create gzipped DB dumps and restore them with a confirmation guard.
- **Operational sanity**: journald logging documented; rollback via git tag deploy is documented.

### Follow-ups / Notes

- If you want Redis to be truly “optional” in production, you’ll need an explicit production setting toggle to use a non-Redis cache backend; the current boilerplate defaults to Redis cache in production.
- `deploy.sh` assumes deploy user can `sudo systemctl restart sum-<slug>-gunicorn.service` (runbook includes minimal sudoers guidance).





