# Deploy Runbook (Fresh VPS)

**Purpose:** Deploy a new SUM client site from bare VPS to production-ready.  
**Reference:** [`docs/dev/deploy/vps-golden-path.md`](../dev/deploy/vps-golden-path.md)

---

## Prerequisites

Before starting:

- [ ] VPS provisioned (Ubuntu 22.04+)
- [ ] Root or sudo access
- [ ] SSH keys configured
- [ ] Domain DNS pointed to VPS IP
- [ ] Client project repository ready (scaffolded via `sum init` or existing)
- [ ] Database credentials generated (strong password)

---

## Pre-Deploy Checklist

### 1. Baseline packages

```bash
sudo apt update
sudo apt install -y \
  ca-certificates curl git \
  python3 python3-venv python3-pip build-essential \
  libpq-dev postgresql postgresql-contrib postgresql-client \
  redis-server \
  ufw
```

**Stop if:** package installation fails.

---

### 2. Install Caddy

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

**Verify:**

```bash
caddy version
```

**Stop if:** Caddy not installed.

---

### 3. Create deploy user

```bash
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy
```

---

### 4. Firewall (UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status verbose
```

**Expected:** Firewall enabled, ports 22/80/443 allowed.

---

### 5. Postgres setup

```bash
sudo -u postgres psql
```

**In psql:**

```sql
CREATE USER sum_site_user WITH PASSWORD 'REPLACE_WITH_STRONG_PASSWORD';
CREATE DATABASE sum_site_db OWNER sum_site_user;
\q
```

**Verify connectivity:**

```bash
psql "postgresql://sum_site_user:REPLACE_WITH_STRONG_PASSWORD@127.0.0.1:5432/sum_site_db" -c "SELECT 1;"
```

**Stop if:** Connection fails.

---

### 6. Redis setup

```bash
sudo systemctl enable --now redis-server
redis-cli ping
```

**Expected:** `PONG`

**Stop if:** Redis not running.

**Security check:**

```bash
sudo netstat -tlnp | grep 6379
```

**Expected:** `127.0.0.1:6379` and `::1:6379` (NOT `0.0.0.0`)

**Stop if:** Redis exposed publicly.

---

## Site Deployment

### 7. Set site variables

```bash
export SITE_SLUG="acme-kitchens"
export DEPLOY_USER="deploy"
export DOMAIN="example.com"
```

---

### 8. Create site directories

```bash
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/backups"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/static"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/srv/sum/${SITE_SLUG}/media"
sudo install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/var/log/sum/${SITE_SLUG}"
```

---

### 9. Create virtualenv

```bash
sudo -u "$DEPLOY_USER" python3 -m venv "/srv/sum/${SITE_SLUG}/venv"
```

---

### 10. Clone client repository

```bash
sudo -u "$DEPLOY_USER" git clone <CLIENT_REPO_URL> "/srv/sum/${SITE_SLUG}/app"
```

**Replace `<CLIENT_REPO_URL>`** with actual repository URL.

---

### 11. Create .env file

```bash
sudo -u "$DEPLOY_USER" nano "/srv/sum/${SITE_SLUG}/.env"
```

**Minimum .env contents:**

```bash
DJANGO_SETTINGS_MODULE=<project_module>.settings.production
DJANGO_SECRET_KEY=<GENERATE_STRONG_SECRET>
ALLOWED_HOSTS=example.com,www.example.com

DJANGO_DB_NAME=sum_site_db
DJANGO_DB_USER=sum_site_user
DJANGO_DB_PASSWORD=<STRONG_PASSWORD>
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=5432

DJANGO_STATIC_ROOT=/srv/sum/<site_slug>/static
DJANGO_MEDIA_ROOT=/srv/sum/<site_slug>/media

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

SITE_DOMAIN=example.com
```

**Secure .env:**

```bash
sudo chmod 600 "/srv/sum/${SITE_SLUG}/.env"
```

**Stop if:** .env file missing or incorrect.

---

### 12. Install systemd services

**Copy and customize templates:**

From `infrastructure/systemd/`:

- `sum-site-gunicorn.service.template`
- `sum-site-gunicorn.socket.template` (optional)
- `sum-site-celery.service.template` (optional, only if using Celery)

**Replace placeholders:**

- `__SITE_SLUG__` → actual site slug
- `__DEPLOY_USER__` → `deploy`
- `__PROJECT_MODULE__` → Django project module name

**Install gunicorn service:**

```bash
sudo cp infrastructure/systemd/sum-site-gunicorn.service.template \
  /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service
sudo nano /etc/systemd/system/sum-${SITE_SLUG}-gunicorn.service
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now "sum-${SITE_SLUG}-gunicorn.service"
sudo systemctl status "sum-${SITE_SLUG}-gunicorn.service" --no-pager
```

**Stop if:** Service fails to start.

---

### 13. Configure Caddy

**Edit main Caddyfile:**

```bash
sudo nano /etc/caddy/Caddyfile
```

**Add import directive:**

```
import /etc/caddy/sites-enabled/*.caddy
```

**Create site config:**

```bash
sudo cp infrastructure/caddy/Caddyfile.template \
  /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
sudo nano /etc/caddy/sites-enabled/sum-${SITE_SLUG}.caddy
```

**Replace:**

- `__DOMAIN__` → actual domain
- `__SITE_SLUG__` → site slug

**Add Caddy to www-data group:**

```bash
sudo usermod -aG www-data caddy
```

**Validate and reload:**

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

**Stop if:** Caddy config invalid.

---

### 14. Run deploy script

**Copy deployment scripts:**

```bash
sudo install -d -m 0755 /srv/sum/bin
sudo cp infrastructure/scripts/*.sh /srv/sum/bin/
sudo chmod +x /srv/sum/bin/*.sh
```

**Allow deploy user to restart services (sudoers):**

```bash
sudo visudo
```

**Add:**

```
deploy ALL=NOPASSWD: /bin/systemctl restart sum-*-gunicorn.service, /bin/systemctl start sum-*-gunicorn.service, /bin/systemctl stop sum-*-gunicorn.service
```

**Run deploy:**

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/deploy.sh \
  --site-slug "$SITE_SLUG" \
  --ref vX.Y.Z \
  --domain "$DOMAIN"
```

**Replace `vX.Y.Z`** with actual `sum_core` tag.

**Stop if:** Deploy script fails.

---

## Smoke Tests

### 15. Run smoke tests

Follow [`smoke-tests.md`](smoke-tests.md):

- [ ] `/health/` returns 200 or 503 (degraded ok, unhealthy = stop)
- [ ] Homepage renders
- [ ] Admin login works (if accessible)
- [ ] Redis connectivity verified

**Stop if:** Critical smoke tests fail.

---

## Backup Rehearsal

### 16. Create initial backup

```bash
sudo -u "$DEPLOY_USER" /srv/sum/bin/backup_db.sh --site-slug "$SITE_SLUG"
```

**Verify backup file exists:**

```bash
ls -lh /srv/sum/${SITE_SLUG}/backups/
```

**Stop if:** Backup fails.

---

### 17. (Optional) Test restore

**Only in non-production or during initial setup.**

```bash
# Stop gunicorn
sudo systemctl stop "sum-${SITE_SLUG}-gunicorn.service"

# Restore from backup
sudo -u "$DEPLOY_USER" /srv/sum/bin/restore_db.sh \
  --site-slug "$SITE_SLUG" \
  --file "/srv/sum/${SITE_SLUG}/backups/<backup_file>.sql.gz" \
  --i-know-this-will-overwrite

# Start gunicorn
sudo systemctl start "sum-${SITE_SLUG}-gunicorn.service"

# Verify /health/
curl -i "https://${DOMAIN}/health/"
```

---

## Record Keeping

### 18. Update loop sites matrix

Open [`loop-sites-matrix.md`](loop-sites-matrix.md) and add:

- Site name / slug
- Environment (staging / production)
- Deployed version/tag
- Deploy date
- Outcome: Success / Issues

---

### 19. Log issues (if any)

If anything went wrong during deploy:

Open [`what-broke-last-time.md`](what-broke-last-time.md) and append:

- Site: `<slug>`
- Date: `YYYY-MM-DD`
- Issue: `<brief description>`
- Fix: `<what you did to resolve>`
- Follow-up: `<automation ideas>`

---

## Checklist Summary

- [ ] Baseline packages installed (Postgres, Redis, Caddy, etc.)
- [ ] Deploy user created
- [ ] Firewall configured
- [ ] Database created and verified
- [ ] Redis running and secured (localhost only)
- [ ] Site directories created
- [ ] Virtualenv created
- [ ] Client repo cloned
- [ ] `.env` file created and secured
- [ ] Systemd services installed and running
- [ ] Caddy configured and reloaded
- [ ] Deploy script executed successfully
- [ ] Smoke tests pass
- [ ] Initial backup created
- [ ] Loop sites matrix updated
- [ ] Issues logged (if any)

---

## Next Steps

- Run [`full-verification.md`](full-verification.md) before declaring production-ready
- Set up external uptime monitoring
- Schedule automated backups (cron or systemd timer)
- Document site-specific configuration

---

**END OF RUNBOOK**
