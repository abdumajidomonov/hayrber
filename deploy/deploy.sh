#!/usr/bin/env bash
# Deploy skripti — webhook tomonidan chaqiriladi.
# Git'dan oxirgi o'zgarishlarni tortadi va Odoo'ni qayta ishga tushiradi.
set -euo pipefail

REPO_DIR="${REPO_DIR:-/opt/odoo-vps}"
BRANCH="${DEPLOY_BRANCH:-main}"
COMPOSE="docker compose"

cd "$REPO_DIR"

echo "[deploy] $(date -Is) — boshlandi"
echo "[deploy] git fetch + reset to origin/$BRANCH"
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"
git clean -fd -- addons config

echo "[deploy] docker compose pull"
$COMPOSE pull

echo "[deploy] docker compose up -d"
$COMPOSE up -d --remove-orphans

echo "[deploy] addons yangilanyapti..."
# Agar addons o'zgargan bo'lsa, Odoo'ni yangi modullar bilan yangilash:
CHANGED=$(git diff --name-only HEAD@{1} HEAD -- addons/ 2>/dev/null || true)
if [ -n "$CHANGED" ]; then
  echo "[deploy] addons o'zgardi — Odoo restart"
  $COMPOSE restart odoo
fi

echo "[deploy] $(date -Is) — tugadi (OK)"
