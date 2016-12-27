# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class pos_hn(models.Model):
#     _name = 'pos_hn.pos_hn'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class res_company(models.Model):
	_name = 'res.company'
	_inherit = 'res.company'

	codigo_cai = fields.Char(string="CAI", help="Ingrese su Código de Autorización de Impresión en este campo. Este saldrá automaticamente en su factura", size=64)
	fecha_limite_emision = fields.Date(string="Fecha limite emision", help="Ingrese la fecha limite de emisión para su código CAI")
