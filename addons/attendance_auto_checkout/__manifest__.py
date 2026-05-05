{
    'name': 'Attendance Auto Checkout',
    'version': '19.0.1.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Har kuni 23:59 da ochiq qolgan davomatlarni 20:00 da yopadi',
    'author': 'Custom',
    'depends': ['hr_attendance'],
    'data': [
        'data/cron.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
