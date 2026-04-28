#!/usr/bin/env python3
"""
GitHub Webhook Listener — Odoo Auto-Deploy
==========================================
GitHub'dan push event'ini eshitadi, HMAC imzosini tekshiradi va
deploy.sh skriptini ishga tushiradi.

Konfiguratsiya muhit o'zgaruvchilari orqali:
    WEBHOOK_SECRET   — GitHub webhook'da ko'rsatilgan sir (majburiy)
    WEBHOOK_PORT     — tinglovchi port (default: 9000)
    REPO_DIR         — loyiha papkasi (default: /opt/odoo-vps)
    DEPLOY_BRANCH    — deploy bo'ladigan branch (default: main)

Faqat standart kutubxonalardan foydalanadi — qo'shimcha o'rnatish kerak emas.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = logging.getLogger("odoo-webhook")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

SECRET = os.environ.get("WEBHOOK_SECRET", "").encode()
PORT = int(os.environ.get("WEBHOOK_PORT", "9000"))
REPO_DIR = os.environ.get("REPO_DIR", "/opt/odoo-vps")
EXISTING_ODOO_DIR = os.environ.get("EXISTING_ODOO_DIR", "/root/odoo")
BRANCH = os.environ.get("DEPLOY_BRANCH", "main")
DEPLOY_SCRIPT = os.path.join(REPO_DIR, "deploy", "deploy.sh")


def verify_signature(payload: bytes, signature_header: str | None) -> bool:
    """GitHub HMAC-SHA256 imzosini tekshiradi (X-Hub-Signature-256 sarlavhasi)."""
    if not SECRET:
        LOG.error("WEBHOOK_SECRET o'rnatilmagan — barcha so'rovlar rad etiladi")
        return False
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = signature_header.split("=", 1)[1]
    mac = hmac.new(SECRET, msg=payload, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, expected)


def run_deploy() -> tuple[int, str]:
    """deploy.sh ni ishga tushirish."""
    if not os.path.isfile(DEPLOY_SCRIPT):
        return 127, f"Deploy skripti topilmadi: {DEPLOY_SCRIPT}"
    try:
        result = subprocess.run(
            ["/bin/bash", DEPLOY_SCRIPT],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=900,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode, out
    except subprocess.TimeoutExpired:
        return 124, "Deploy 15 daqiqada tugamadi (timeout)"
    except Exception as exc:
        return 1, f"Deploy xatosi: {exc}"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        LOG.info("%s - %s", self.address_string(), format % args)

    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, {
                "status": "ok",
                "branch": BRANCH,
                "repo": REPO_DIR,
                "odoo": EXISTING_ODOO_DIR,
            })
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length) if length > 0 else b""
        signature = self.headers.get("X-Hub-Signature-256")
        event = self.headers.get("X-GitHub-Event", "unknown")

        if not verify_signature(payload, signature):
            LOG.warning("Imzo noto'g'ri yoki yo'q (event=%s)", event)
            self._send(401, {"error": "invalid signature"})
            return

        if event == "ping":
            self._send(200, {"msg": "pong"})
            return

        if event != "push":
            self._send(200, {"msg": f"event ignored: {event}"})
            return

        try:
            body = json.loads(payload)
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid json"})
            return

        ref = body.get("ref", "")
        expected_ref = f"refs/heads/{BRANCH}"
        if ref != expected_ref:
            LOG.info("Push %s ga (kutilgan: %s) — o'tkazib yuborilmoqda", ref, expected_ref)
            self._send(200, {"msg": f"branch ignored: {ref}"})
            return

        LOG.info("Deploy boshlandi: %s -> %s", body.get("after", "?")[:8], BRANCH)
        code, output = run_deploy()
        LOG.info("Deploy tugadi: exit=%d", code)
        if code != 0:
            LOG.error("Deploy log:\n%s", output[-2000:])
        self._send(200 if code == 0 else 500, {"exit": code, "log_tail": output[-1500:]})


def main() -> int:
    if not SECRET:
        LOG.critical("WEBHOOK_SECRET o'rnatilmagan. Chiqilmoqda.")
        return 2
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    LOG.info("Webhook tinglovchi: 0.0.0.0:%d (branch=%s, repo=%s)", PORT, BRANCH, REPO_DIR)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("To'xtatilmoqda...")
        server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
