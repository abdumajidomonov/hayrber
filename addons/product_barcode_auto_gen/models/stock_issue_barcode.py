from odoo import models, fields


class StockIssueBarcode(models.Model):
    _name = 'stock.issue.barcode'
    _description = 'Mahsulot Chiqimi Barcodi'
    _rec_name = 'barcode'
    _order = 'issue_date desc'

    barcode = fields.Char('Barcode', required=True, readonly=True, index=True, copy=False)
    picking_id = fields.Many2one('stock.picking', string='Transfer', ondelete='cascade', readonly=True)
    product_id = fields.Many2one('product.product', string='Mahsulot', readonly=True)
    product_qty = fields.Float("Miqdor", readonly=True)
    uom_id = fields.Many2one('uom.uom', string="O'lchov birligi", readonly=True)
    issue_date = fields.Datetime('Berilgan vaqt', readonly=True)
    state = fields.Selection([
        ('active', 'Foydalanilmoqda'),
        ('returned', 'Qaytarilgan'),
        ('lost', "Yo'qolgan"),
    ], string='Holat', default='active')
