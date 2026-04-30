{
    'name': 'Fix UZS Currency Symbol',
    'version': '19.0.1.0',
    'category': 'Custom',
    'summary': "UZS (O'zbek so'mi) valyuta belgisini to'g'rilaydi: лв → so'm",
    'author': 'Custom',
    'depends': ['base'],
    'data': [
        'data/currency_uzs.xml',
    ],
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'license': 'LGPL-3',
}
