# Custom Odoo Addons

Bu papkada GitHub orqali boshqariladigan **Odoo custom modullari** bo'ladi.

## Qanday ishlaydi

```
Lokal kompyuter        GitHub                VPS
─────────────         ────────              ─────────
addons/<modul>  ──>   push   ──>   /opt/odoo-vps/addons/<modul>
                                            │
                                       rsync (qo'shadi/yangilaydi)
                                            ↓
                                   /root/odoo/addons/<modul>
                                            │
                                       Odoo restart
                                            ↓
                                       Modul ishlaydi
```

## Yangi modul qo'shish

1. Bu papkada yangi papka yarating: `addons/my_module/`
2. Odoo modul faylllarini yarating:
   - `__manifest__.py`
   - `__init__.py`
   - `models/`, `views/`, `security/`, va h.k.
3. Commit + push:
   ```powershell
   git add addons/my_module/
   git commit -m "Add my_module"
   git push
   ```
4. 10-15 soniyadan keyin VPS'da modul ko'rinadi
5. Odoo'da: **Apps** → "Update Apps List" → modulni topib o'rnating

## Mavjud VPS addonlari

VPS'da `/root/odoo/addons/` papkasida quyidagi modullar mavjud va **tegilmaydi**:

- `hide_product_type` — custom
- `muk_web_appsbar`, `muk_web_chatter`, `muk_web_colors`, `muk_web_dialog`, `muk_web_enterprise_theme`, `muk_web_group`, `muk_web_refresh` — MUK Web themes
- `product_barcode_auto_gen` — custom

Agar bu modullarni ham GitHub orqali boshqarmoqchi bo'lsangiz, ularni VPS'dan klonlab bu papkaga ko'chirib qo'yishingiz mumkin.

## Muhim eslatma

**rsync `--delete` ishlatmaydi** — bu yerda yo'q bo'lgan modul VPS'dan o'chmaydi. Bu xavfsizlik chorasi.
