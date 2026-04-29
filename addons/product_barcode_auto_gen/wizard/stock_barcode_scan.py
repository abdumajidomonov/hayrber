from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockBarcodeScanLine(models.TransientModel):
    _name = 'stock.barcode.scan.line'
    _description = 'Barcode Scan Line'

    wizard_id = fields.Many2one('stock.barcode.scan', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Mahsulot', required=True)
    qty = fields.Float(string='Miqdor', default=1.0)
    price_unit = fields.Float(string='Narxi')
    uom_id = fields.Many2one('uom.uom', string="O'lchov", related='product_id.uom_id')


class StockBarcodeScan(models.TransientModel):
    _name = 'stock.barcode.scan'
    _description = 'Barcode Scanning Station'

    barcode = fields.Char(string='Barkodni skanerlang', help="Skanerni shu erga bosing")

    operation_type = fields.Selection([
        ('in', 'Kirdi (Qabul qilish)'),
        ('out', 'Chiqdi (Sotuv/Berish)')
    ], string='Amal turi', default='in', required=True)

    process_type = fields.Selection([
        ('raw', 'Xomashyo'),
        ('finished', 'Tayyor mahsulot')
    ], string='Jarayon turi', default='raw', required=True)

    should_print = fields.Boolean(string='Tasdiqlangach barkodni chop etish', default=False)

    location_id = fields.Many2one('stock.location', string='Qayerdan', domain=[('usage', '=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', string='Qayerga', domain=[('usage', '=', 'internal')])

    line_ids = fields.One2many('stock.barcode.scan.line', 'wizard_id', string='Skanerlanган mahsulotlar')
    last_scan_info = fields.Char(string='Oxirgi skaner', readonly=True)

    @api.onchange('process_type', 'operation_type')
    def _onchange_process_locations(self):
        raw_loc = self.env.ref('product_barcode_auto_gen.location_raw_materials', raise_if_not_found=False)
        finished_loc = self.env.ref('product_barcode_auto_gen.location_finished_goods', raise_if_not_found=False)
        supplier_loc = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
        customer_loc = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)

        if self.operation_type == 'in':
            self.location_id = supplier_loc.id if supplier_loc else False
            if self.process_type == 'raw':
                self.location_dest_id = raw_loc.id if raw_loc else False
            else:
                self.location_dest_id = finished_loc.id if finished_loc else False
        else:
            self.location_dest_id = customer_loc.id if customer_loc else False
            if self.process_type == 'raw':
                self.location_id = raw_loc.id if raw_loc else False
            else:
                self.location_id = finished_loc.id if finished_loc else False

    @api.onchange('barcode')
    def _onchange_barcode(self):
        if not self.barcode:
            return
        product = self.env['product.product'].search([('barcode', '=', self.barcode)], limit=1)
        if not product:
            barcode_val = self.barcode
            self.barcode = False
            return {'warning': {'title': _('Topilmadi'), 'message': _('Barkod topilmadi: %s') % barcode_val}}

        existing = next((l for l in self.line_ids if l.product_id.id == product.id), None)
        if existing:
            existing.qty += 1
        else:
            self.line_ids = [(0, 0, {
                'product_id': product.id,
                'qty': 1.0,
                'price_unit': product.standard_price,
            })]
        self.last_scan_info = _("✓ %s qo'shildi") % product.name
        self.barcode = False

    def _find_picking_type(self):
        code = 'incoming' if self.operation_type == 'in' else 'outgoing'
        company = self.env.company
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', code), ('warehouse_id.company_id', '=', company.id)],
            limit=1,
        )
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', code)], limit=1)
        if not picking_type:
            raise UserError(_("'%s' turidagi picking type topilmadi.") % code)
        return picking_type

    def action_apply(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Hech narsa skanerlanmagan! Avval mahsulotlarni skanerlang."))
        if not self.location_id or not self.location_dest_id:
            raise UserError(_("Omborlar tanlanmagan!"))
        if self.location_id == self.location_dest_id:
            raise UserError(_("'Qayerdan' va 'Qayerga' omborlari bir xil bo'lmasligi kerak."))

        picking_type = self._find_picking_type()
        product_names = ', '.join(l.product_id.name for l in self.line_ids)
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'origin': _('Barkod (%s)') % self.process_type,
        })

        for line in self.line_ids:
            move = self.env['stock.move'].create({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'price_unit': line.price_unit,
                'description_picking': line.product_id.name,
            })

        picking.action_confirm()
        picking.action_assign()

        for move in picking.move_ids:
            matched_line = next((l for l in self.line_ids if l.product_id.id == move.product_id.id), None)
            if not matched_line:
                continue
            if not move.move_line_ids:
                self.env['stock.move.line'].create({
                    'move_id': move.id,
                    'picking_id': picking.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'quantity': matched_line.qty,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                })
            else:
                for ml in move.move_line_ids:
                    ml.quantity = matched_line.qty
        picking.move_ids.picked = True

        if self.should_print:
            product_ids = self.line_ids.mapped('product_id').ids
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.barcode.wizard.final',
                'view_mode': 'form',
                'target': 'new',
                'context': {'active_model': 'product.product', 'active_ids': product_ids},
            }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Muvaffaqiyatli'),
                'message': _('%d mahsulot — Transfer: %s (Tasdiqlash kutilmoqda)') % (len(self.line_ids), picking.name),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
