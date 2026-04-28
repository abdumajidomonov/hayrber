#!/usr/bin/env bash
# VPS uchun bir martalik o'rnatish skripti.
# Ishlatish (root sifatida):
#   curl -fsSL https://raw.githubusercontent.com/<USER>/<REPO>/main/deploy/setup.sh | bash -s -- <REPO_URL>
# Yoki:
#   git clone <REPO_URL> /opt/odoo-vps && cd /opt/odoo-vps && bash deploy/setup.sh
set -euo pipefail

REPO_URL="${1:-${REPO_URL:-}}"
REPO_DIR="${REPO_DIR:-/opt/odoo-vps}"
BRANCH="${DEPLOY_BRANCH:-main}"

log() { echo -e "\033[1;32m[setup]\033[0m $*"; }
err() { echo -e "\033[1;31m[setup]\033[0m $*" >&2; }

if [ "$EUID" -ne 0 ]; then
  err "Bu skriptni root sifatida ishga tushiring (sudo)."
  exit 1
fi

# === 1. Tizim paketlari ===
log "Tizim paketlari yangilanmoqda..."
apt-get update -y
apt-get install -y --no-install-recommends \
  ca-certificates curl git python3 ufw

# === 2. Docker ===
if ! command -v docker >/dev/null 2>&1; then
  log "Docker o'rnatilmoqda..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
else
  log "Docker allaqachon o'rnatilgan ($(docker --version))"
fi

# === 3. Repo'ni klon qilish ===
if [ -d "$REPO_DIR/.git" ]; then
  log "Repo allaqachon mavjud: $REPO_DIR — pull qilinmoqda"
  git -C "$REPO_DIR" fetch origin "$BRANCH"
  git -C "$REPO_DIR" reset --hard "origin/$BRANCH"
else
  if [ -z "$REPO_URL" ]; then
    err "REPO_URL berilmagan. Foydalanish: bash setup.sh https://github.com/USER/REPO.git"
    exit 1
  fi
  log "Repo klonlanmoqda: $REPO_URL -> $REPO_DIR"
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

# === 4. .env fayli ===
if [ ! -f .env ]; then
  log ".env yaratilmoqda — qiymatlarni keyin tahrirlang!"
  cp .env.example .env
  WEBHOOK_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 32)
  DB_PASSWORD=$(openssl rand -hex 24 2>/dev/null || head -c 24 /dev/urandom | xxd -p -c 24)
  sed -i "s|^WEBHOOK_SECRET=.*|WEBHOOK_SECRET=$WEBHOOK_SECRET|" .env
  sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|" .env
  log "Yaratilgan WEBHOOK_SECRET (GitHub'da kerak bo'ladi):"
  echo "  $WEBHOOK_SECRET"
fi

# === 5. Skriptlarni executable qilish ===
chmod +x deploy/deploy.sh deploy/webhook.py 2>/dev/null || true

# === 6. Systemd unit ===
log "Webhook xizmati o'rnatilmoqda..."
cp deploy/odoo-webhook.service /etc/systemd/system/odoo-webhook.service
systemctl daemon-reload
systemctl enable --now odoo-webhook.service

# === 7. Firewall (port ochish) ===
WEBHOOK_PORT=$(grep -E '^WEBHOOK_PORT=' .env | cut -d= -f2)
ODOO_PORT=$(grep -E '^ODOO_PORT=' .env | cut -d= -f2)
WEBHOOK_PORT="${WEBHOOK_PORT:-9000}"
ODOO_PORT="${ODOO_PORT:-8069}"

if command -v ufw >/dev/null 2>&1; then
  log "UFW: portlar ochilmoqda (22, $ODOO_PORT, $WEBHOOK_PORT)"
  ufw allow 22/tcp >/dev/null
  ufw allow "${ODOO_PORT}/tcp" >/dev/null
  ufw allow "${WEBHOOK_PORT}/tcp" >/dev/null
fi

# === 8. Birinchi marta Odoo ishga tushirish ===
log "Odoo + Postgres ishga tushirilmoqda..."
docker compose pull
docker compose up -d

# === 9. Yakuniy ma'lumot ===
IP=$(curl -fsS https://api.ipify.org 2>/dev/null || hostname -I | awk '{print $1}')
cat <<EOF

============================================================
✅ O'rnatish tugadi!

Odoo:           http://${IP}:${ODOO_PORT}
Webhook health: http://${IP}:${WEBHOOK_PORT}/health

Keyingi qadamlar:
  1. GitHub repo'ga o'ting: Settings → Webhooks → Add webhook
     Payload URL:  http://${IP}:${WEBHOOK_PORT}/
     Content type: application/json
     Secret:       (yuqorida ko'rsatilgan WEBHOOK_SECRET)
     Event:        Just the push event
  2. Odoo'ga kiring va master parolni o'rnating.
  3. Endi har push avtomatik deploy bo'ladi.

Loglarni ko'rish:
  systemctl status odoo-webhook
  journalctl -fu odoo-webhook
  docker compose logs -f odoo
============================================================
EOF
