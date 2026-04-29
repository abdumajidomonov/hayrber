# Automatic Product Barcode Generation — Odoo 19 Module

Avtomatik barkod yaratish va tezkor barkod skaner stansiyasi.

---

## 📋 Talablar (Requirements)

- **Odoo 19** server
- `product` va `stock` modullari (standart Inventory app)
- Python 3.10+

---

## 📦 Modul tarkibi (Module contents)

```
product_barcode_auto_gen/
├── __manifest__.py
├── __init__.py
├── data/
│   ├── ir_sequence_data.xml         # Barkod ketma-ketligi (PROD00001...)
│   └── stock_location_data.xml      # Xomashyo/Tayyor mahsulot omborlari
├── models/
│   ├── product_template.py          # Avtomatik barkod yaratish
│   └── barcode_stock_log.py         # Audit log model
├── wizard/
│   ├── product_barcode_wizard.py    # PDF chop etish wizardi
│   ├── product_barcode_wizard_view.xml
│   ├── stock_barcode_scan.py        # Skaner stansiyasi
│   └── stock_barcode_scan_view.xml
├── views/
│   └── barcode_stock_log_views.xml
├── report/
│   └── product_barcode_report.xml   # PDF template
└── security/
    ├── ir.model.access.csv
    └── barcode_security.xml
```

---

## 🚀 O'rnatish (Installation)

### 1-bosqich: ZIP'ni ochish

```bash
cd /root
unzip product_barcode_auto_gen.zip
ls product_barcode_auto_gen/
```

### 2-bosqich: Addons papkasiga ko'chirish

Odoo qayerga o'rnatilganini aniqlang. Eng keng tarqalgan yo'llar:

```bash
# Variantlardan birini ishlating (qaysisi mavjud bo'lsa):
sudo cp -r /root/product_barcode_auto_gen /mnt/extra-addons/
sudo cp -r /root/product_barcode_auto_gen /opt/odoo/custom-addons/
sudo cp -r /root/product_barcode_auto_gen /usr/lib/python3/dist-packages/odoo/addons/

# Egalik huquqi (Odoo foydalanuvchisiga):
sudo chown -R odoo:odoo /mnt/extra-addons/product_barcode_auto_gen
```

> **Topish uchun:** `sudo find / -name "odoo.conf" 2>/dev/null` — `addons_path` yo'lini ko'rsatadi.

### 3-bosqich: `odoo.conf` tekshirish

```bash
sudo cat /etc/odoo/odoo.conf | grep addons_path
```

Natija masalan:
```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
```

Modul shu ro'yxatdagi papkalardan **birida** turishi kerak.

### 4-bosqich: Odoo serverni qayta ishga tushirish

```bash
sudo systemctl restart odoo
# yoki:
sudo service odoo restart
```

Holatni tekshirish:
```bash
sudo systemctl status odoo
sudo tail -f /var/log/odoo/odoo-server.log
```

### 5-bosqich: Modulni o'rnatish

**A) CLI orqali (tavsiya etiladi):**

```bash
# DB nomini o'zgartiring (database_name):
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf \
  -d database_name \
  -i product_barcode_auto_gen \
  --stop-after-init

# Keyin serverni qayta ishga tushiring:
sudo systemctl restart odoo
```

**B) Odoo UI orqali:**

1. Brauzerda Odoo'ga kiring (admin sifatida)
2. **Developer mode** ni yoqing:
   - Settings → Developer Tools → "Activate the developer mode"
3. **Apps** menyusi → **"Update Apps List"** tugmasini bosing
4. Qidiruvda **"Automatic Product Barcode Generation"** ni toping
5. **Install** tugmasini bosing

### 6-bosqich: Tekshirish

O'rnatilgandan keyin:
- ✅ Yuqori menyuda **SKANER (BARCODE)** ko'rinadi
- ✅ Inventory → Configuration → Locations da "Xomashyo Ombori" va "Tayyor Mahsulot Ombori" bor
- ✅ Yangi mahsulot yaratganda barkod avtomatik `PROD00001` formatida qo'yiladi

---

## 🎯 Funksiyalar (Features)

### 1. Avtomatik barkod
Yangi mahsulot yaratilganda `ir.sequence` orqali **PROD00001, PROD00002, ...** ketma-ket barkod beriladi.

### 2. Tezkor skaner stansiyasi
**SKANER (BARCODE) → Tezkor Skanerlash**

- Barkodni o'qish → mahsulot avtomatik topiladi
- Jarayon turi: Xomashyo / Tayyor mahsulot
- Amal turi: Kirdi (qabul) / Chiqdi (sotuv)
- Lokatsiyalar avtomatik tanlanadi
- Tasdiqlangach `stock.picking` yaratiladi va validatsiya qilinadi
- Yashil "toast" xabar chiqadi
- Forma yangidan ochiladi (continuous scanning)

### 3. Audit log
**SKANER (BARCODE) → Barkod Tarixi**

Har bir skaner natijasi yoziladi: sana, mahsulot, miqdor, narxi, amal turi, lokatsiyalar, mas'ul foydalanuvchi.

### 4. PDF chop etish
Mahsulotlar ro'yxatidan **Print → Barkod chop etish**:
- O'lcham, padding, shrift sozlamalari
- Jonli HTML preview
- A4 PDF (bir varaqda ko'p barkod)

---

## 🐛 Muammolarni hal qilish (Troubleshooting)

### Modul Apps ro'yxatida chiqmayapti
```bash
# Addons papkasini tekshiring:
ls -la /mnt/extra-addons/product_barcode_auto_gen/__manifest__.py

# Egalik huquqini tekshiring:
sudo chown -R odoo:odoo /mnt/extra-addons/product_barcode_auto_gen

# Apps List ni qayta yuklang:
# Odoo UI: Apps → Update Apps List
```

### Server log'da xato
```bash
sudo tail -100 /var/log/odoo/odoo-server.log | grep -i error
```

### Modulni qayta o'rnatish (kod o'zgartirgandan keyin)
```bash
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf \
  -d database_name \
  -u product_barcode_auto_gen \
  --stop-after-init
sudo systemctl restart odoo
```

### Menyular ko'rinmayapti
- Foydalanuvchini logout/login qiling
- Brauzer cache: `Ctrl + F5`
- Foydalanuvchi `base.group_user` (Internal User) ekanligini tekshiring

### Barkod sequence ishlamayapti
```bash
# Odoo shell'ga kiring:
sudo -u odoo /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d database_name

# Sequence borligini tekshiring:
>>> env['ir.sequence'].search([('code', '=', 'product.barcode')])
```

---

## 🔧 Texnik ma'lumot

| Xususiyat | Qiymat |
|---|---|
| Odoo versiya | 19.0 |
| Modul versiya | 1.5 |
| License | LGPL-3 |
| Dependencies | `product`, `stock` |
| Application | Yes |

---

## 📞 Yordam

Server log:
```bash
sudo journalctl -u odoo -f
sudo tail -f /var/log/odoo/odoo-server.log
```

Database backup (har doim o'rnatishdan oldin!):
```bash
sudo -u postgres pg_dump database_name > /root/backup_$(date +%F).sql
```
