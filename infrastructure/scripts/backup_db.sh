#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  backup_db.sh --site-slug <slug>

Creates a gzipped plain-SQL pg_dump and stores it in:
  /srv/sum/<slug>/backups/

Requires:
  - /srv/sum/<slug>/.env containing DJANGO_DB_* variables
  - pg_dump available on PATH

Output:
  Prints the final backup file path on success.
EOF
}

log() { printf '[backup_db] %s\n' "$*" >&2; }
die() { printf '[backup_db] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG="${SITE_SLUG:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required (or set SITE_SLUG env var)"

BASE_DIR="/srv/sum/${SITE_SLUG}"
ENV_FILE="${BASE_DIR}/.env"
BACKUP_DIR="${BASE_DIR}/backups"

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

mkdir -p "$BACKUP_DIR"
umask 077

ts="$(date -u +%Y%m%dT%H%M%SZ)"
out="${BACKUP_DIR}/${SITE_SLUG}_db_${ts}.sql.gz"

log "Writing backup: $out"

export PGPASSWORD="$DJANGO_DB_PASSWORD"
pg_dump \
  --host "$DJANGO_DB_HOST" \
  --port "$DJANGO_DB_PORT" \
  --username "$DJANGO_DB_USER" \
  --dbname "$DJANGO_DB_NAME" \
  --format=plain \
  --no-owner \
  --no-privileges \
  --clean \
  --if-exists \
| gzip -c > "$out"

unset PGPASSWORD

printf '%s\n' "$out"
