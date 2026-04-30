{
    'name': 'Hide Product Type and Deliveries',
    'version': '19.0.1.2',
    'category': 'Custom',
    'summary': 'Hides Product Type, shows Asl Nomi field under product name',
    'author': 'Custom',
    'depends': ['product', 'stock'],
    'data': [
        'views/product_template_view.xml',
        'views/stock_picking_type_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
