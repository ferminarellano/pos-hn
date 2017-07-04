# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cai(models.Model):
	_name = "poshn.cai"

	codigo_cai = fields.Char(string="CAI", help="Ingrese su Código de Autorización de Impresión en este campo. Este saldrá automaticamente en su factura", size=37)
	fecha_limite_emision = fields.Date(string="Fecha limite emision", help="Ingrese la fecha limite de emisión para su código CAI")
	punto_emision = fields.Char(string="Punto de Emisión", size=3, default="000", help="Ingrese el punto de emisión que aparecera en su secuencia de factura. (000)")
	establecimiento = fields.Char(string="Establecimiento", size=3, default="001", help="Ingrese el establecimiento que aparecera en su secuencia de factura. (001)")
	tipo_documento = fields.Char(string="Tipo de Documento", size=2, default="01", help="Ingrese el tipo de documento que aparecera en su secuencia de factura. (01)")
	rango_autorizado_desde = fields.Float(digits=(8,0), string="Rango autorizado (desde)", help="Ingrese el rango de facturación autorizado por la DEI.")
	rango_autorizado_hasta = fields.Float(digits=(8,0), string="Rango autorizado (hasta)")
	activo = fields.Boolean(string="Activo")
	
	@api.one
	def compute_sequence(self):	
		self.env['ir.sequence'].create({
			'name':self.codigo_cai+'/'+str(int(self.rango_autorizado_desde))+'-'+str(int(self.rango_autorizado_hasta)),
			'code': 'regimen.dei',
			'implementation':'no_gap', 
			'padding':8, 
			'number_increment':1,
			'number_next_actual': int(self.rango_autorizado_desde),
			'regimen_aplicado':True,
			'punto_emision':self.punto_emision,
			'establecimiento':self.establecimiento,
			'tipo_documento':self.tipo_documento,
			'rango_desde':int(self.rango_autorizado_desde),
			'rango_hasta':int(self.rango_autorizado_hasta)
		})

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
	default_client = fields.Many2one(comodel_name = "res.partner", domain="[('customer','=',True)]", string="Cliente por Defecto")
	cai = fields.Many2one(comodel_name="poshn.cai", string="CAI")
	
class pos_order(models.Model):
	_name = 'pos.order'
	_inherit = 'pos.order'
	
	def _force_picking_done(self, picking):
		self.ensure_one()
		picking.action_confirm()
		picking.force_assign()
		self.set_pack_operation_lot(picking)
		if not any([(x.product_id.tracking not in ['none','serial']) for x in picking.pack_operation_ids]):
			picking.action_done()
	
	
