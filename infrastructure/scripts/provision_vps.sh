#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  cat <<'EOF'
Usage:
  provision_vps.sh --site-slug <slug> --deploy-user <user> [--install-packages]

This is an OPTIONAL helper. It is intentionally conservative and explicit.
It prepares baseline directories and (optionally) installs packages.

It does NOT:
  - Configure Postgres roles/dbs
  - Configure Caddy site files/domains
  - Install systemd unit files

Run as root (or with sudo).
EOF
}

log() { printf '[provision_vps] %s\n' "$*" >&2; }
die() { printf '[provision_vps] ERROR: %s\n' "$*" >&2; exit 1; }

SITE_SLUG=""
DEPLOY_USER=""
INSTALL_PACKAGES="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-slug) SITE_SLUG="${2:-}"; shift 2 ;;
    --deploy-user) DEPLOY_USER="${2:-}"; shift 2 ;;
    --install-packages) INSTALL_PACKAGES="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$SITE_SLUG" ]] || die "--site-slug is required"
[[ -n "$DEPLOY_USER" ]] || die "--deploy-user is required"

if [[ "$(id -u)" -ne 0 ]]; then
  die "Run as root (or via sudo)"
fi

if [[ "$INSTALL_PACKAGES" == "true" ]]; then
  log "Installing baseline packages (apt)"
  apt-get update -y
  apt-get install -y \
    ca-certificates \
    curl \
    git \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    libpq-dev \
    postgresql-client \
    ufw

  # Caddy official repo install (idempotent)
  if ! command -v caddy >/dev/null 2>&1; then
    log "Installing Caddy"
    apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update -y
    apt-get install -y caddy
  fi
fi

log "Ensuring deploy user exists: $DEPLOY_USER"
if ! id "$DEPLOY_USER" >/dev/null 2>&1; then
  useradd --create-home --shell /bin/bash "$DEPLOY_USER"
fi

log "Creating site directories"
BASE_DIR="/srv/sum/${SITE_SLUG}"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "$BASE_DIR"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "${BASE_DIR}/backups"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "${BASE_DIR}/static"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "${BASE_DIR}/media"

log "Ensuring log directory exists"
install -d -m 0755 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/var/log/sum/${SITE_SLUG}"

log "UFW baseline (SSH + HTTP/HTTPS)"
ufw allow OpenSSH || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true

cat <<EOF

Provisioning helper complete.

Next (manual):
  - Postgres: create role/db; set password; test psql connection
  - Place /srv/sum/${SITE_SLUG}/.env (chmod 600)
  - Clone app into ${BASE_DIR}/app
  - Install systemd unit(s) and Caddy site file
EOF
