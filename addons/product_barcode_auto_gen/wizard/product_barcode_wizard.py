from odoo import models, fields, api

class ProductBarcodeWizardFinal(models.TransientModel):
    _name = 'product.barcode.wizard.final'
    _description = 'Final Barcode Wizard'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')
        if active_ids and active_model:
            if active_model == 'product.template':
                products = self.env['product.product'].search([('product_tmpl_id', 'in', active_ids)])
            elif active_model == 'product.product':
                products = self.env['product.product'].browse(active_ids)
            else: products = []
            lines = [(0, 0, {'product_id': p.id, 'qty': 1}) for p in products if p.exists()]
            if lines: res.update({'line_ids': lines})
        return res

    label_width = fields.Float(string='Kenglik (mm)', default=80.0)
    label_height = fields.Float(string='Balandlik (mm)', default=40.0)
    
    border_thickness = fields.Float(string='Border qalinligi', default=1.0)
    border_color = fields.Char(string='Border rangi', default='#AAAAAA')
    line_color = fields.Char(string='Chiziq rangi', default='#DDDDDD')
    margin = fields.Float(string='Margin (mm)', default=1.0)
    
    padding_top = fields.Float(string='Padding Top (mm)', default=2.0)
    padding_bottom = fields.Float(string='Padding Bottom (mm)', default=2.0)
    padding_left = fields.Float(string='Padding Left (mm)', default=2.0)
    padding_right = fields.Float(string='Padding Right (mm)', default=2.0)
    
    font_size_name = fields.Integer(string='Nom shrifti', default=14)
    name_line_height = fields.Float(string='Nom qator balandligi', default=1.2)
    barcode_height = fields.Integer(string='Barkod balandligi (mm)', default=15)
    font_size_barcode = fields.Integer(string='Barkod raqam shrifti', default=10)
    
    line_ids = fields.One2many('product.barcode.wizard.line.final', 'wizard_id', string='Mahsulotlar')
    preview_html = fields.Html(compute='_compute_preview_html')

    @api.depends('label_width', 'label_height', 'border_thickness', 'border_color', 'line_color', 'margin',
                 'padding_top', 'padding_bottom', 'padding_left', 'padding_right',
                 'font_size_name', 'name_line_height', 'barcode_height', 'font_size_barcode', 'line_ids')
    def _compute_preview_html(self):
        for rec in self:
            sample_name = rec.line_ids[0].product_id.name if rec.line_ids else "MAHSULOT NOMI"
            sample_bc = rec.line_ids[0].product_id.barcode if (rec.line_ids and rec.line_ids[0].product_id.barcode) else "123456789012"
            
            # Border thickness pt da bo'lsa px ga yaqinlashtiramiz preview uchun
            border_style = f"{rec.border_thickness}pt solid {rec.border_color}"
            
            html = f"""
            <div style="background:#f8f9fa; padding:20px; display:flex; justify-content:center; align-items:center;">
                <div style="width:{rec.label_width}mm; height:{rec.label_height}mm; padding:{rec.margin}mm; box-sizing:border-box; display:inline-block; font-size:0; line-height:0;">
                    <div style="width:100%; height:100%; background:white; padding:{rec.padding_top}mm {rec.padding_right}mm {rec.padding_bottom}mm {rec.padding_left}mm; box-sizing:border-box; overflow:hidden;">
                        <table style="width:100%; height:100%; border-collapse:collapse; table-layout:fixed; font-size: 10pt; line-height: normal;">
                            <tr style="height: 25%;">
                                <td style="vertical-align:middle; text-align:center;">
                                    <div style="font-weight:bold; font-size:{rec.font_size_name}pt; color:black; line-height:{rec.name_line_height}; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                                        {sample_name}
                                    </div>
                                </td>
                            </tr>
                            <tr style="height:1pt;">
                                <td style="border-top:0.5pt solid {rec.line_color}; padding:0;"></td>
                            </tr>
                            <tr style="height: 45%;">
                                <td style="vertical-align:middle; text-align:center; padding:2px 0;">
                                    <img src="/report/barcode/?barcode_type=Code128&value={sample_bc}&width=600&height=150" 
                                         style="max-width:100%; height:{rec.barcode_height}mm; display:inline-block; vertical-align:middle;"/>
                                </td>
                            </tr>
                            <tr style="height:1pt;">
                                <td style="border-top:0.5pt solid {rec.line_color}; padding:0;"></td>
                            </tr>
                            <tr style="height: 25%;">
                                <td style="vertical-align:middle; text-align:center;">
                                    <div style="font-size:{rec.font_size_barcode}pt; font-family:monospace; font-weight:bold; color:black;">
                                        {sample_bc}
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>"""
            rec.preview_html = html

    def action_print(self):
        return self.env.ref('product_barcode_auto_gen.action_report_product_barcode_multi_final').report_action(self)

class ProductBarcodeWizardLineFinal(models.TransientModel):
    _name = 'product.barcode.wizard.line.final'
    _description = 'Final Barcode Wizard Line'
    wizard_id = fields.Many2one('product.barcode.wizard.final', ondelete='cascade')
    product_id = fields.Many2one('product.product', required=True)
    qty = fields.Integer(default=1)
