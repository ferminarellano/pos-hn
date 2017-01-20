# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cai(models.Model):
	_name = "poshn.cai"

	codigo_cai = fields.Char(string="CAI", help="Ingrese su Código de Autorización de Impresión en este campo. Este saldrá automaticamente en su factura", size=37)
	fecha_limite_emision = fields.Date(string="Fecha limite emision", help="Ingrese la fecha limite de emisión para su código CAI")
	rango_autorizado_desde = fields.Float(digits=(16,0), string="Rango autorizado (desde)", help="Ingrese el rango de facturación autorizado por la DEI.")
	rango_autorizado_hasta = fields.Float(digits=(16,0), string="Rango autorizado (hasta)")
	activo = fields.Boolean(string="Código Activo")

class ir_sequence(models.Model):
	_name = 'ir.sequence'
	_inherit = 'ir.sequence'

	regimen_aplicado = fields.Boolean(string="Activo", default=False, help="Seleccionar para utilizar como prefijo los campos DEI.")
	punto_emision = fields.Char(string="Punto de Emisión", size=64, help="Ingrese el código de punto de emisión que aparecera en su secuencia de factura.")
	establecimiento = fields.Char(string="Establecimiento", size=64, help="Ingrese el código de establecimiento que aparecera en su secuencia de factura.")
	tipo_documento = fields.Char(string="Tipo de Documento", size=64, help="Ingrese el código de tipo de documento que aparecera en su secuencia de factura.")
	rango_desde = fields.Integer(string="Rango autorizado (desde)", help="Ingrese el rango de facturación autorizado por la DEI.")
	rango_hasta = fields.Integer(string="Rango autorizado (hasta)")

	def get_next_char(self, number_next):
		if self.regimen_aplicado == True:
			return  self.punto_emision + "-" + self.establecimiento + "-" + self.tipo_documento + "-" + '%%0%sd' % self.padding % number_next
		else:
			return super(ir_sequence, self).get_next_char(number_next)

class pos_config(models.Model):
	_name = 'pos.config'
	_inherit = 'pos.config'

	sequence_id = fields.Many2one(readonly=False)
