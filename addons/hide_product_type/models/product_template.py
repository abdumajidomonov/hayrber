from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        required=False,
    )
