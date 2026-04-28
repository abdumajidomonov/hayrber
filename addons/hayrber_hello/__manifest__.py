{
    "name": "Hayrber Hello (Test)",
    "version": "19.0.1.0.0",
    "summary": "Auto-deploy test moduli — GitHub'dan VPS'ga avtomatik yetib keldi",
    "description": """
Hayrber Hello — Auto-Deploy Test
=================================
Bu modul GitHub'dan VPS'ga avto-deploy ishlayotganini tasdiqlash uchun.
Agar siz buni Odoo'ning **Apps** ro'yxatida ko'rayotgan bo'lsangiz, deploy ishlamoqda! ✅
""",
    "author": "Hayrber",
    "website": "https://erp.hayrber.org",
    "category": "Tools",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "views/hayrber_hello_menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
