# Odoo VPS — Auto-Deploy

Odoo 17 + PostgreSQL + GitHub webhook bilan avtomatik deploy.

```
[Local kod] -- git push --> [GitHub] -- webhook --> [VPS: pull + restart]
```

## Tarkibi

| Yo'l | Tavsif |
|------|--------|
| `docker-compose.yml` | Odoo + Postgres konteynerlari |
| `config/odoo.conf` | Odoo konfiguratsiyasi |
| `addons/custom_starter/` | Boshlang'ich custom modul (namuna) |
| `deploy/webhook.py` | GitHub webhook tinglovchi (Python stdlib) |
| `deploy/deploy.sh` | Pull + restart skripti |
| `deploy/odoo-webhook.service` | Webhook uchun systemd unit |
| `deploy/setup.sh` | VPS bir martalik setup skripti |
| `.env.example` | Muhit o'zgaruvchilari shabloni |

---

## 🚀 To'liq o'rnatish (3 bosqich)

### Bosqich 1 — GitHub repo (1 daqiqa)

1. [github.com/new](https://github.com/new) sahifasiga o'ting
2. Yangi **private repo** yarating (masalan: `odoo-vps`)
3. Repo URL'ni saqlang, masalan: `https://github.com/USERNAME/odoo-vps.git`

### Bosqich 2 — Lokaldan birinchi push

PowerShell'da loyiha papkasida:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial Odoo VPS setup"
git remote add origin https://github.com/USERNAME/odoo-vps.git
git push -u origin main
```

### Bosqich 3 — VPS o'rnatish (5 daqiqa)

VPS'ga SSH bilan kiring:

```bash
ssh root@213.199.44.110
```

Quyidagi buyruqni bajaring (URL'ni o'zingizniki bilan almashtiring):

```bash
curl -fsSL https://raw.githubusercontent.com/USERNAME/odoo-vps/main/deploy/setup.sh \
  | bash -s -- https://github.com/USERNAME/odoo-vps.git
```

Skript:
- Docker o'rnatadi
- Repo'ni `/opt/odoo-vps` ga klon qiladi
- `.env` ni avtomatik yaratadi (xavfsiz parollar bilan)
- Webhook xizmatini yoqadi
- Portlarni firewall'da ochadi
- Odoo + Postgres'ni ishga tushiradi
- Oxirida **WEBHOOK_SECRET** ni ekranga chiqaradi — uni saqlab qoling

### Bosqich 4 — GitHub webhook'ni ulash

Repo'da: **Settings → Webhooks → Add webhook**

| Maydon | Qiymat |
|--------|--------|
| Payload URL | `http://213.199.44.110:9000/` |
| Content type | `application/json` |
| Secret | (Bosqich 3 oxirida ko'rsatilgan) |
| Events | Just the push event |
| Active | ✅ |

**Add webhook** ni bosing. GitHub bir test "ping" yuboradi — webhook'ning yashil ✓ paydo bo'lishi kerak.

### Bosqich 5 — Odoo'ga kirish

Brauzerda: `http://213.199.44.110:8069`

- Database yarating (master parol — `.env` da `admin_passwd` yoki Odoo ichida)
- Admin foydalanuvchini sozlang
- **Apps** menyusiga o'ting → "Update Apps List" → "Custom Starter" modulini topib o'rnating

---

## 📝 Kundalik foydalanish

### Yangi feature qo'shish

```powershell
# Lokalda kodni o'zgartiring (men shu yerda ishlayman)
git add .
git commit -m "Yangi feature qo'shildi"
git push
```

Push'dan 5-15 soniya keyin VPS avtomatik:
1. `git pull` qiladi
2. `docker compose up -d` qiladi
3. Agar `addons/` o'zgargan bo'lsa, Odoo'ni restart qiladi

### Loglarni kuzatish (VPS'da)

```bash
# Webhook listener
journalctl -fu odoo-webhook

# Odoo
cd /opt/odoo-vps && docker compose logs -f odoo

# Postgres
cd /opt/odoo-vps && docker compose logs -f db
```

### Modulni qayta yuklash

Agar XML/Python o'zgarishi UI'ga ko'rinmasa:

```bash
cd /opt/odoo-vps
docker compose exec odoo odoo -u custom_starter -d <DB_NAME> --stop-after-init
docker compose restart odoo
```

---

## 🔒 Xavfsizlik kontrol-ro'yxati

- [ ] **VPS root parolini o'zgartiring** (`passwd`)
- [ ] SSH'ni faqat kalit orqali ishlash uchun sozlang (parolni o'chiring)
- [ ] `.env` faylini hech qachon git'ga yubormang (`.gitignore` da)
- [ ] Webhook'ni `https://` bilan ishlatish uchun reverse proxy (nginx + Let's Encrypt) qo'shing
- [ ] Odoo master parolni `config/odoo.conf` da kuchli qiymatga o'rnating
- [ ] PostgreSQL portini (`5432`) tashqariga ochmang — faqat ichki tarmoqda

---

## 🛠 Tuzatish (Troubleshooting)

| Muammo | Yechim |
|--------|--------|
| Webhook 401 qaytaradi | Secret `.env` va GitHub'da bir xilmi tekshiring |
| `git pull` xato | `cd /opt/odoo-vps && git status` — qo'lda fix |
| Odoo ishlamayapti | `docker compose logs odoo` — xatoni o'qing |
| Port band | `ss -tlnp \| grep 8069` — boshqa servis bormi |
| Disk to'lib qoldi | `docker system prune -a --volumes` |

---

## 🤖 Claude bilan ishlash

Claude (men) bu repo'da:
- ✅ Yangi modul yaratadi (`addons/<name>/`)
- ✅ Mavjud kodni o'zgartiradi
- ✅ Commit + push qiladi
- ❌ VPS'ga to'g'ridan-to'g'ri SSH qilmaydi (xavfsizlik chegarasi)

Server holatini ko'rish uchun, `ssh` bilan kirib log'larni menga nusxa qiling.
