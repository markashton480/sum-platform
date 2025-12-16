#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  restore_db.sh --site-slug <slug> --file <path.sql.gz> --i-know-this-will-overwrite [--no-restart]

Restores a gzipped plain-SQL backup created by backup_db.sh into the site's configured DB.

Safety:
  - You must pass --i-know-this-will-overwrite (required)

Requires:
  - /srv/sum/<slug>/.env containing DJANGO_DB_* variables
  - psql available on PATH
EOF
}

log() { printf '[restore_db] %s\n' "$*" >&2; }
die() { printf '[restore_db] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG="${SITE_SLUG:-}"
FILE=""
CONFIRM="false"
NO_RESTART="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    --file) FILE="${2:-}"; shift 2 ;;
    --i-know-this-will-overwrite) CONFIRM="true"; shift ;;
    --no-restart) NO_RESTART="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required (or set SITE_SLUG env var)"
[[ -n "$FILE" ]] || die "--file is required"
[[ -f "$FILE" ]] || die "Backup file not found: $FILE"
[[ "$CONFIRM" == "true" ]] || die "Refusing to run without --i-know-this-will-overwrite"

BASE_DIR="/srv/sum/${SITE_SLUG}"
ENV_FILE="${BASE_DIR}/.env"

[[ -f "$ENV_FILE" ]] || die "Env file not found: $ENV_FILE"

log "Loading env: $ENV_FILE"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${DJANGO_DB_NAME:?DJANGO_DB_NAME missing in .env}"
: "${DJANGO_DB_USER:?DJANGO_DB_USER missing in .env}"
: "${DJANGO_DB_PASSWORD:?DJANGO_DB_PASSWORD missing in .env}"
: "${DJANGO_DB_HOST:?DJANGO_DB_HOST missing in .env}"

DJANGO_DB_PORT="${DJANGO_DB_PORT:-5432}"

GUNICORN_SERVICE="sum-${SITE_SLUG}-gunicorn.service"

if [[ "$NO_RESTART" != "true" ]]; then
  log "Stopping service before restore: $GUNICORN_SERVICE"
  sudo systemctl stop "$GUNICORN_SERVICE" || true
else
  log "--no-restart set; not stopping service (not recommended)"
fi

log "Restoring DB '${DJANGO_DB_NAME}' from: $FILE"
export PGPASSWORD="$DJANGO_DB_PASSWORD"
gunzip -c "$FILE" | psql \
  --host "$DJANGO_DB_HOST" \
  --port "$DJANGO_DB_PORT" \
  --username "$DJANGO_DB_USER" \
  --dbname "$DJANGO_DB_NAME" \
  --set ON_ERROR_STOP=on
unset PGPASSWORD

if [[ "$NO_RESTART" != "true" ]]; then
  log "Starting service: $GUNICORN_SERVICE"
  sudo systemctl start "$GUNICORN_SERVICE"
fi

log "Restore complete"
