from odoo import http
from odoo.http import request


class BarcodeScanController(http.Controller):

    @http.route(
        '/product_barcode_auto_gen/scan_result',
        type='http', auth='user', methods=['GET'], csrf=False
    )
    def scan_result(self, picking_id, pdf_type, **kwargs):
        picking_id = int(picking_id)
        picking = request.env['stock.picking'].browse(picking_id)

        if pdf_type == 'issue':
            # Chiqish: issue barcode PDF
            barcode_ids = ','.join(str(b.id) for b in picking.issue_barcode_ids)
            pdf_url = (
                '/report/pdf/'
                'product_barcode_auto_gen.report_issue_barcode_template/'
                + barcode_ids
            )
            picking_url = f'/odoo/inventory/deliveries/{picking_id}'

        else:
            # Kirish: mahsulot label PDF (wizard orqali)
            product_ids = picking.move_ids.mapped('product_id').ids
            wizard = request.env['product.barcode.wizard.final'].create({
                'line_ids': [(0, 0, {'product_id': p, 'qty': 1}) for p in product_ids]
            })
            pdf_url = (
                '/report/pdf/'
                'product_barcode_auto_gen.report_barcode_final_template/'
                + str(wizard.id)
            )
            picking_url = f'/odoo/inventory/receipts/{picking_id}'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PDF yuklanmoqda...</title>
    <style>
        body {{
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f8f9fa;
            color: #555;
        }}
        .box {{
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="box">
        <h3>&#128196; Barcode PDF yuklanmoqda...</h3>
        <p>Transfer sahifasiga o'tilmoqda, iltimos kuting.</p>
    </div>
    <script>
        // PDF ni yuklab olish
        var a = document.createElement('a');
        a.href = '{pdf_url}';
        a.download = 'barcode.pdf';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();

        // 800ms dan keyin picking formiga o'tish
        setTimeout(function() {{
            window.location.href = '{picking_url}';
        }}, 800);
    </script>
</body>
</html>"""
        return request.make_response(
            html,
            headers=[('Content-Type', 'text/html; charset=utf-8')]
        )
