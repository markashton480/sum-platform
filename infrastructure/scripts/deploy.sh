#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  deploy.sh --site-slug <slug> [--ref <git-ref>] [--no-restart] [--domain <domain>]

Expected server layout:
  /srv/sum/<slug>/app/   (git checkout of the client site)
  /srv/sum/<slug>/venv/  (python venv)
  /srv/sum/<slug>/.env   (env vars: DJANGO_SETTINGS_MODULE, DB creds, etc)
  /srv/sum/<slug>/static (collectstatic target; via DJANGO_STATIC_ROOT)
  /srv/sum/<slug>/media  (upload target; via DJANGO_MEDIA_ROOT)

Notes:
  - This script is designed to be re-run safely.
  - It reads secrets from /srv/sum/<slug>/.env (not from git).
EOF
}

log() { printf '[deploy] %s\n' "$*" >&2; }
die() { printf '[deploy] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG="${SITE_SLUG:-}"
REF=""
NO_RESTART="false"
DOMAIN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    --ref) REF="${2:-}"; shift 2 ;;
    --no-restart) NO_RESTART="true"; shift ;;
    --domain) DOMAIN="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required (or set SITE_SLUG env var)"

BASE_DIR="/srv/sum/${SITE_SLUG}"
APP_DIR="${BASE_DIR}/app"
VENV_DIR="${BASE_DIR}/venv"
ENV_FILE="${BASE_DIR}/.env"
LOCK_FILE="${BASE_DIR}/deploy.lock"

[[ -d "$APP_DIR" ]] || die "App dir not found: $APP_DIR"
[[ -f "$ENV_FILE" ]] || die "Env file not found: $ENV_FILE"

mkdir -p "$BASE_DIR"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  die "Another deploy appears to be running (lock: $LOCK_FILE)"
fi

log "Loading env: $ENV_FILE"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# If caller didn't provide, try to use env:
DOMAIN="${DOMAIN:-${SITE_DOMAIN:-${DEPLOY_DOMAIN:-}}}"

log "Ensuring venv: $VENV_DIR"
if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi

PY="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

log "Updating pip tooling"
"$PY" -m pip install --upgrade pip setuptools wheel >/dev/null

log "Updating code in: $APP_DIR"
cd "$APP_DIR"

if [[ -n "$(git status --porcelain)" ]]; then
  die "Git working tree is dirty; refuse to deploy. Fix in $APP_DIR"
fi

git fetch --all --tags --prune

if [[ -n "$REF" ]]; then
  log "Checking out ref: $REF"
  git checkout --force "$REF"
else
  log "Pulling current branch (ff-only)"
  git pull --ff-only
fi

log "Installing requirements"
if [[ -f "requirements.txt" ]]; then
  "$PIP" install -r requirements.txt
else
  die "requirements.txt not found in $APP_DIR"
fi

log "Running migrations"
"$PY" manage.py migrate --noinput

log "Collecting static"
"$PY" manage.py collectstatic --noinput

GUNICORN_SERVICE="sum-${SITE_SLUG}-gunicorn.service"
CELERY_SERVICE="sum-${SITE_SLUG}-celery.service"

if [[ "$NO_RESTART" != "true" ]]; then
  log "Restarting systemd service: $GUNICORN_SERVICE"
  sudo systemctl restart "$GUNICORN_SERVICE"

  if sudo systemctl list-unit-files "$CELERY_SERVICE" >/dev/null 2>&1; then
    if sudo systemctl is-enabled "$CELERY_SERVICE" >/dev/null 2>&1; then
      log "Restarting (enabled) service: $CELERY_SERVICE"
      sudo systemctl restart "$CELERY_SERVICE"
    else
      log "Celery unit exists but is not enabled; skipping restart: $CELERY_SERVICE"
    fi
  fi
else
  log "--no-restart set; skipping systemd restart"
fi

if [[ -n "$DOMAIN" ]]; then
  log "Smoke check: https://${DOMAIN}/health/"
  curl -fsS "https://${DOMAIN}/health/" >/dev/null
  log "Health OK"

  log "Optional: https://${DOMAIN}/sitemap.xml"
  if curl -fsS "https://${DOMAIN}/sitemap.xml" >/dev/null; then
    log "Sitemap OK"
  else
    log "Sitemap check failed (non-blocking)"
  fi
else
  log "DOMAIN not provided (use --domain or set SITE_DOMAIN in .env); skipping smoke check"
fi

cat <<EOF

Deploy complete.

Next steps / debugging:
  - Logs: sudo journalctl -u ${GUNICORN_SERVICE} -f --no-pager
  - Health: https://${DOMAIN:-<domain>}/health/
EOF
