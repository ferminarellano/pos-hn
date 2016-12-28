# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cai(models.Model):
	_name = "poshn.cai"

	codigo_cai = fields.Char(string="CAI", help="Ingrese su Código de Autorización de Impresión en este campo. Este saldrá automaticamente en su factura", size=32)
	fecha_limite_emision = fields.Date(string="Fecha limite emision", help="Ingrese la fecha limite de emisión para su código CAI")
	rango_autorizado_desde = fields.Integer(string="Rango autorizado (desde)", help="Ingrese el rango de facturación autorizado por la DEI.")
	rango_autorizado_hasta = fields.Integer(string="Rango autorizado (hasta)")
	activo = fields.Boolean(string="Código Activo")
