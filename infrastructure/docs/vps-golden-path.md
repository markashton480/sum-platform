# VPS Golden Path Deployment (Ubuntu + Caddy + systemd + Postgres + Redis + backups)

This is the **boring, repeatable "golden path"** for deploying a SUM client site to a single Ubuntu VPS using **Caddy + systemd + Postgres + Redis**.

## Assumptions

- **Ubuntu** 22.04+ (tested target; adjust packages for other versions)
- You deploy **one site per server directory**: `/srv/sum/<site_slug>/...`
- You run Django/Wagtail using **gunicorn** behind **Caddy**
- The client site uses **production settings**: `DJANGO_SETTINGS_MODULE=<project>.settings.production`

## 1) VPS prerequisites

### Packages

Install baseline packages (as root):

```bash
sudo apt update
sudo apt install -y \
  ca-certificates curl git \
  python3 python3-venv python3-pip build-essential \
  libpq-dev postgresql postgresql-contrib postgresql-client \
  redis-server \
  ufw
```

### Why Redis is required

> **Redis is part of the baseline SUM runtime.**
> All production deployments assume Redis is installed, running, and reachable.
> If Redis is unavailable, the runtime is considered broken.

Redis is **required** for the default SUM production stack (not optional):

- **Django cache**: Production settings configure Redis as the default cache backend. The application's performance and stability assumptions rely on this cache being available.
- **Celery broker**: **Celery is an optional feature; Redis is not.** If Celery is enabled, it depends on Redis as the broker, but Redis is required for the baseline runtime regardless of whether Celery is enabled. This maintains the option to enable async tasks without infrastructure changes.
- **Health check dependency**: The `/health/` endpoint treats cache as **critical** by default. **Redis failure results in `/health/` reporting `unhealthy` (HTTP 503).** This reflects a broken baseline runtime, not a degraded feature. If Redis is unavailable, health checks will fail, which will trigger alerting and may prevent deployments.

**Security baseline**: Redis is configured to **only listen on localhost** (`127.0.0.1` and `::1`) and is **not exposed to the internet**. The firewall (UFW) does not allow port 6379 from external sources. This is sufficient security for a single-server deployment. Do not expose Redis publicly; if you need remote access, stop and redesign your architecture.

After installation, verify Redis is running:

```bash
sudo systemctl enable --now redis-server
redis-cli ping  # Should return: PONG
```

### Caddy install (official repo)

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

## 2) Create deploy user + basic hardening

### Deploy user

```bash
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy
```

### SSH hardening (baseline)

- Use SSH keys (disable password login once verified)
- Consider: disable root SSH login
- Full process: `infrastructure/docs/ssh-strategy.md`

Edit `/etc/ssh/sshd_config` carefully, then:

```bash
sudo systemctl reload ssh
```

## 3) Firewall (UFW minimal rules)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status verbose
```

## 4) Postgres setup (DB + user + verify)

Create a DB/user **per site**:

```bash
sudo -u postgres psql
```

In `psql`:

```sql
CREATE USER sum_site_user WITH PASSWORD 'REPLACE_ME_STRONG_PASSWORD';
CREATE DATABASE sum_site_db OWNER sum_site_user;
\q
```

Verify connectivity:

```bash
psql "postgresql://sum_site_user:REPLACE_ME_STRONG_PASSWORD@127.0.0.1:5432/sum_site_db" -c "SELECT 1;"
```

## 5) Server directory layout

Choose a **site slug**, e.g. `acme-kitchens`.

Create directories:

```bash
export SITE_SLUG="acme-kitchens"
export DEPLOY_USER="deploy"

sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/backups"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/static"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/media"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/var/log/sum/${SITE_SLUG}"
```

Create venv:

```bash
sudo -u "$DEPLOY_USER" python3 -m venv "/srv/sum/${SITE_SLUG}/venv"
```

Clone your client repo into `/srv/sum/<slug>/app`:

```bash
sudo -u "$DEPLOY_USER" git clone <YOUR_CLIENT_REPO_URL> "/srv/sum/${SITE_SLUG}/app"
```

## 6) `.env` placement and permissions

Create `/srv/sum/<site_slug>/.env` (owned by deploy user, not in git):

```bash
sudo -u "$DEPLOY_USER" nano "/srv/sum/${SITE_SLUG}/.env"
sudo chmod 600 "/srv/sum/${SITE_SLUG}/.env"
```

Minimum recommended values (adapt to your project module + domain):

```bash
DJANGO_SETTINGS_MODULE=<project_module>.settings.production
DJANGO_SECRET_KEY=<generate-strong-secret>
ALLOWED_HOSTS=example.com,www.example.com

DJANGO_DB_NAME=sum_site_db
DJANGO_DB_USER=sum_site_user
DJANGO_DB_PASSWORD=<strong-password>
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=5432

# Golden-path static/media roots (served by Caddy)
DJANGO_STATIC_ROOT=/srv/sum/<site_slug>/static
DJANGO_MEDIA_ROOT=/srv/sum/<site_slug>/media

# Optional: for deploy script smoke checks
SITE_DOMAIN=example.com

# Redis/Celery (required for default production stack)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 7) systemd units (gunicorn + optional socket + optional celery)

Templates live in this repo:

- `infrastructure/systemd/sum-site-gunicorn.service.template`
- `infrastructure/systemd/sum-site-gunicorn.socket.template`
- `infrastructure/systemd/sum-site-celery.service.template`

### Install gunicorn service

Copy the template to `/etc/systemd/system/` and replace placeholders:

- `__SITE_SLUG__` (e.g. `acme-kitchens`)
- `__DEPLOY_USER__` (e.g. `deploy`)
- `__PROJECT_MODULE__` (your Django project package, e.g. `acme_kitchens`)

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-gunicorn.service.template \
  /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service

sudo nano /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service
```

Reload and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-gunicorn.service"
sudo systemctl status "sum-${SITE_SLUG}-gunicorn.service" --no-pager
```

### (Optional) socket activation

If you want socket activation, install the socket unit and uncomment the `Requires=` lines in the service template and switch `ExecStart` to `--bind fd://0`.

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-gunicorn.socket.template \
  /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.socket
sudo nano /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.socket

sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-gunicorn.socket"
```

### (Optional) celery worker

Only enable if you need async tasks day 1.

```bash
sudo cp /path/to/repo/infrastructure/systemd/sum-site-celery.service.template \
  /etc/systemd/system/sum-${SITE_SLUG}-celery.service
sudo nano /etc/systemd/system/sum-${SITE_SLUG}-celery.service

sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-celery.service"
```

## 8) Caddy setup + domain + TLS

Template:

- `infrastructure/caddy/Caddyfile.template`

### Ensure main Caddyfile imports sites-enabled configs

Before installing site configs, ensure the main `/etc/caddy/Caddyfile` imports the sites-enabled directory:

```bash
sudo nano /etc/caddy/Caddyfile
```

Add this import directive at the top (after any global options):

```
import /etc/caddy/sites-enabled/*.caddy
```

Install a site config (replace `__DOMAIN__` and `__SITE_SLUG__`):

```bash
sudo cp /path/to/repo/infrastructure/caddy/Caddyfile.template \
  /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
sudo nano /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
```

Ensure Caddy can connect to the gunicorn socket:

The systemd service creates the socket with group `www-data`, so add the `caddy` user to this group:

```bash
sudo usermod -aG www-data caddy
sudo systemctl restart caddy
```

Validate + reload:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

TLS will be provisioned automatically by Caddy when DNS points at the VPS and ports 80/443 are open.

## 9) First deploy instructions (deploy script)

Scripts live in:

- `infrastructure/scripts/deploy.sh`
- `infrastructure/scripts/backup_db.sh`
- `infrastructure/scripts/restore_db.sh`

On the VPS, copy these scripts into a predictable location (or keep them in the app repo if you vendor them in your client repo):

```bash
sudo install -d -m 0755 /srv/sum/bin
sudo cp /path/to/repo/infrastructure/scripts/*.sh /srv/sum/bin/
sudo chmod +x /srv/sum/bin/*.sh
```

Allow deploy user to restart the specific service(s) without a password (recommended minimal sudoers):

```bash
sudo visudo
```

Add something like:

```
deploy ALL=NOPASSWD: /bin/systemctl restart sum-*-gunicorn.service, /bin/systemctl start sum-*-gunicorn.service, /bin/systemctl stop sum-*-gunicorn.service
```

Run deploy:

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/deploy.sh --site-slug "$SITE_SLUG" --ref vX.Y.Z --domain example.com
```

Smoke check requirements:

- `https://<domain>/health/` returns **HTTP 200** for `ok` or `degraded` (only `unhealthy` is **503**)
- Optional: `https://<domain>/sitemap.xml` returns 200 (logged but non-blocking)

## 10) Upgrade flow (tag pinning discipline)

For the client repo, ensure the `sum_core` dependency is pinned by tag (`SUM_CORE_GIT_REF`) in `requirements.txt` as documented in the boilerplate readme.

Upgrade steps:

- Update `SUM_CORE_GIT_REF` to a new tag in the client `requirements.txt`
- Commit + push
- Deploy with `--ref <tag>` (or deploy main branch if that’s your policy)

Rollback:

- Re-deploy the previous known-good git tag:
  - `deploy.sh --site-slug <slug> --ref vPrev --domain <domain>`

## 11) Backup + restore rehearsal (required)

### Backup

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/backup_db.sh --site-slug "$SITE_SLUG"
```

Output is a gzipped plain SQL file under:

- `/srv/sum/<site_slug>/backups/<site_slug>_db_<UTC_TIMESTAMP>.sql.gz`

### Restore rehearsal

Recommended rehearsal flow:

- Provision a fresh/empty DB for the site (or recreate the DB)
- Stop gunicorn
- Restore
- Start gunicorn
- Verify `/health/`

Restore command (requires explicit confirmation flag):

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/restore_db.sh \
  --site-slug "$SITE_SLUG" \
  --file "/srv/sum/${SITE_SLUG}/backups/<backup_file>.sql.gz" \
  --i-know-this-will-overwrite
```

## 12) Operational sanity: logs + debugging

Gunicorn logs go to journald by default:

```bash
sudo journalctl -u "sum-${SITE_SLUG}-gunicorn.service" -f --no-pager
```

Caddy logs:

```bash
sudo journalctl -u caddy -f --no-pager
```

## 13) Ops smoke checklist

Use this checklist to verify the deployment is healthy:

### Redis

```bash
# Verify Redis is running
sudo systemctl status redis-server

# Test Redis connectivity
redis-cli ping
# Expected output: PONG

# Optional: Check Redis binding (should be localhost only)
sudo netstat -tlnp | grep 6379
# Expected: 127.0.0.1:6379 and ::1:6379 (not 0.0.0.0)
```

### Application health

```bash
# Health endpoint (should return 200 for ok/degraded, 503 only for unhealthy)
curl -i "https://${DOMAIN}/health/"

# Verify site is serving correctly
curl -I "https://${DOMAIN}/"
```

### Service status

```bash
# Gunicorn service
sudo systemctl status "sum-${SITE_SLUG}-gunicorn.service"

# Celery service (if enabled)
sudo systemctl status "sum-${SITE_SLUG}-celery.service" 2>/dev/null || echo "Celery not enabled"

# Caddy
sudo systemctl status caddy
```
