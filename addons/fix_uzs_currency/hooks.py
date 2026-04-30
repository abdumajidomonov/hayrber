def post_init_hook(env):
    # Mahsulot narx maydonidagi kasrni olib tashlash
    for name in ('Product Price', 'Account'):
        rec = env['decimal.precision'].search([('name', '=', name)], limit=1)
        if rec:
            rec.digits = 0
