from odoo import api, fields, models


class CustomStarter(models.Model):
    _name = "custom.starter"
    _description = "Custom Starter Record"
    _order = "name"

    name = fields.Char(string="Nomi", required=True)
    description = fields.Text(string="Tavsif")
    active = fields.Boolean(string="Faol", default=True)
    sequence = fields.Integer(string="Tartib", default=10)
