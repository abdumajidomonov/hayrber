from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    issue_barcode_ids = fields.One2many(
        'stock.issue.barcode', 'picking_id', string='Chiqim Barcodelari'
    )
    issue_barcode_count = fields.Integer(
        compute='_compute_issue_barcode_count',
        string='Barcode soni'
    )

    @api.depends('issue_barcode_ids')
    def _compute_issue_barcode_count(self):
        for rec in self:
            rec.issue_barcode_count = len(rec.issue_barcode_ids)

    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            if picking.picking_type_code in ('outgoing', 'internal') and not picking.issue_barcode_ids:
                picking._generate_issue_barcodes()
        return res

    def _generate_issue_barcodes(self):
        IrSequence = self.env['ir.sequence']
        now = fields.Datetime.now()
        vals_list = []
        for move in self.move_ids.filtered(lambda m: m.state == 'done'):
            qty = sum(ml.quantity for ml in move.move_line_ids)
            if not qty:
                continue
            barcode_val = IrSequence.next_by_code('product.issue.barcode') or f"BC{self.id}{move.id}"
            vals_list.append({
                'barcode': barcode_val,
                'picking_id': self.id,
                'product_id': move.product_id.id,
                'product_qty': qty,
                'uom_id': move.product_uom.id,
                'issue_date': now,
            })
        if vals_list:
            self.env['stock.issue.barcode'].create(vals_list)

    def action_print_issue_barcodes(self):
        self.ensure_one()
        return self.env.ref(
            'product_barcode_auto_gen.action_report_issue_barcode'
        ).report_action(self.issue_barcode_ids)

    def action_view_issue_barcodes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chiqim Barcodelari',
            'res_model': 'stock.issue.barcode',
            'view_mode': 'list,form',
            'domain': [('picking_id', '=', self.id)],
            'context': {'default_picking_id': self.id},
        }
