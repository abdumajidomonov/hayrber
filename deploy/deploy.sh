#!/usr/bin/env bash
# Auto-deploy skripti — webhook tomonidan chaqiriladi.
# 1. GitHub'dan oxirgi o'zgarishlarni tortadi
# 2. addons papkasini /root/odoo/addons/ ga rsync qiladi (qo'shadi/yangilaydi, o'chirmaydi)
# 3. Agar addons o'zgargan bo'lsa, Odoo'ni restart qiladi
set -euo pipefail

REPO_DIR="${REPO_DIR:-/opt/odoo-vps}"
EXISTING_ODOO_DIR="${EXISTING_ODOO_DIR:-/root/odoo}"
ODOO_ADDONS="${ODOO_ADDONS:-$EXISTING_ODOO_DIR/addons}"
BRANCH="${DEPLOY_BRANCH:-main}"

cd "$REPO_DIR"

echo "[deploy] $(date -Is) — boshlandi (branch=$BRANCH)"

# Pull latest
PREV_HEAD=$(git rev-parse HEAD)
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"
NEW_HEAD=$(git rev-parse HEAD)

if [ "$PREV_HEAD" = "$NEW_HEAD" ]; then
  echo "[deploy] hech narsa o'zgarmagan ($NEW_HEAD)"
fi

# Sync addons (qo'shadi/yangilaydi, mavjudni o'chirmaydi)
if [ -d "$REPO_DIR/addons" ] && [ -d "$ODOO_ADDONS" ]; then
  echo "[deploy] addons rsync: $REPO_DIR/addons/ -> $ODOO_ADDONS/"
  rsync -av \
    --exclude="README.md" \
    --exclude=".gitkeep" \
    "$REPO_DIR/addons/" \
    "$ODOO_ADDONS/"
  # Permissions to match other addons
  chmod -R a+rX "$ODOO_ADDONS" 2>/dev/null || true
fi

# Odoo restart agar addons o'zgargan bo'lsa
ADDONS_CHANGED=$(git diff --name-only "$PREV_HEAD" "$NEW_HEAD" -- addons/ 2>/dev/null || true)
if [ -n "$ADDONS_CHANGED" ] || [ "$PREV_HEAD" = "$NEW_HEAD" ]; then
  if [ -n "$ADDONS_CHANGED" ]; then
    echo "[deploy] addons o'zgardi:"
    echo "$ADDONS_CHANGED" | sed 's|^|         |'
    echo "[deploy] Odoo restart qilinmoqda..."
    cd "$EXISTING_ODOO_DIR"
    docker compose restart web
    echo "[deploy] Odoo restart tugadi"
  fi
fi

echo "[deploy] $(date -Is) — tugadi (OK)"
