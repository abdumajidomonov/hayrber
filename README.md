# Hayrber Odoo — Auto-Deploy

VPS'da allaqachon ishlayotgan Odoo 19 setup'iga **GitHub auto-deploy** qo'shish.

```
[Lokal] -- git push --> [GitHub] -- webhook --> [VPS]
                                                  │
                                       git pull + rsync addons
                                                  │
                                          Odoo restart
```

## Mavjud VPS arxitekturasi

| Komponent | Versiya | Joy |
|-----------|---------|-----|
| Odoo | 19.0 | `odoo-web-1` container |
| PostgreSQL | 16 | `odoo-db-1` container |
| Nginx | latest | `odoo-nginx-1` (HTTPS proxy) |
| Certbot | latest | `odoo-certbot-1` (SSL renew) |
| Domain | `erp.hayrber.org` | Let's Encrypt SSL |
| Compose dir | `/root/odoo/` | docker-compose.yml |
| Custom addons | `/root/odoo/addons/` | mounted as `/mnt/extra-addons` |

## Repository tarkibi

```
hayrber/
├── README.md                      ← bu fayl
├── addons/                        ← yangi custom modullaringiz shu yerga
│   └── README.md
└── deploy/
    ├── setup.sh                   ← VPS bir martalik integration
    ├── deploy.sh                  ← har push'da chaqiriladi (rsync + restart)
    ├── webhook.py                 ← GitHub webhook listener
    └── odoo-webhook.service       ← systemd unit
```

## 🚀 O'rnatish

### 1. VPS'ga ulaning va bitta buyruqni bajaring

```bash
ssh root@213.199.44.110

curl -fsSL https://raw.githubusercontent.com/abdumajidomonov/hayrber/main/deploy/setup.sh \
  | bash -s -- https://github.com/abdumajidomonov/hayrber.git
```

Skript:
- ✅ Mavjud `/root/odoo/` ni backup qiladi (`/root/odoo-backup-YYYYMMDD-HHMMSS`)
- ✅ Repo'ni `/opt/odoo-vps/` ga klon qiladi
- ✅ `.env` ni xavfsiz parol bilan yaratadi
- ✅ Webhook xizmatini yoqadi (systemd)
- ✅ Firewall'da port 9000 ni ochadi
- ✅ **WEBHOOK_SECRET** ni ekranga chiqaradi

### 2. GitHub webhook ulash

Repo → **Settings → Webhooks → Add webhook**:

| Maydon | Qiymat |
|--------|--------|
| Payload URL | `http://213.199.44.110:9000/` |
| Content type | `application/json` |
| Secret | (skript bergan WEBHOOK_SECRET) |
| Events | Just the push event |

### 3. Test

Lokal kompyuteringizda:

```powershell
# README ga bitta belgi qo'shing
git add . ; git commit -m "test deploy" ; git push
```

10-20 soniya kuting va VPS'da:

```bash
journalctl -u odoo-webhook -n 30 --no-pager
```

`[deploy] tugadi (OK)` yozuvini ko'rishingiz kerak.

## 📦 Yangi modul yaratish

1. Lokal `addons/` papkasida yangi papka yarating: `addons/my_module/`
2. Odoo manifest va kodni yozing (`__manifest__.py`, `__init__.py`, `models/`, va h.k.)
3. `git push`
4. Avtomatik VPS'ga yetib boradi
5. Odoo'da: **Apps** → "Update Apps List" → modulni o'rnating

## 🛠 Foydali buyruqlar (VPS'da)

```bash
# Webhook holati
systemctl status odoo-webhook

# Webhook loglar
journalctl -fu odoo-webhook

# Odoo loglar
cd /root/odoo && docker compose logs -f web

# Qo'lda deploy
cd /opt/odoo-vps && bash deploy/deploy.sh

# Odoo restart
cd /root/odoo && docker compose restart web
```

## ⚠️ Xavfsizlik

- `.env` fayli `.gitignore`'da — hech qachon GitHub'ga yuborilmaydi
- VPS root parolingizni **albatta o'zgartiring** (`passwd`)
- Webhook secret tasodifiy 64 belgili hex (cryptographically secure)
- rsync `--delete` ishlatmaydi — mavjud addonlar himoyalangan
- Backup `/root/odoo-backup-*` joylashgan — eskisini o'chirmasdan turing
