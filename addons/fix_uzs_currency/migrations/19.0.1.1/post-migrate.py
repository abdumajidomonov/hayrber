def migrate(cr, version):
    cr.execute("""
        UPDATE decimal_precision
        SET digits = 0
        WHERE name IN ('Product Price', 'Account')
    """)
