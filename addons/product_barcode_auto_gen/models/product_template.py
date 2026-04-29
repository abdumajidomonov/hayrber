from odoo import models, api


def _next_barcode(env, fallback_id):
    seq = env['ir.sequence'].next_by_code('product.barcode')
    return seq or f"PROD{fallback_id}"


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        for product in products:
            if not product.barcode:
                product.barcode = _next_barcode(self.env, product.id)
        return products


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        for product in products:
            if not product.barcode:
                if product.product_tmpl_id.barcode:
                    product.barcode = product.product_tmpl_id.barcode
                else:
                    product.barcode = _next_barcode(self.env, product.product_tmpl_id.id)
        return products
