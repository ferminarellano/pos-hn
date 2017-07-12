# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.exceptions import ValidationError

class cai(models.Model):
	_name = "poshn.cai"

	codigo_cai = fields.Char(string="Código de Autorización de Impresión", help="Ingrese su Código de Autorización de Impresión en este campo. Este saldrá automaticamente en su factura", size=37, required=True)
	fecha_limite_emision = fields.Date(string="Fecha limite emision", help="Ingrese la fecha limite de emisión para su código CAI", required=True)
	punto_emision = fields.Char(string="Punto de Emisión", size=3, default="000", help="Ingrese el punto de emisión que aparecera en su secuencia de factura. (000)", required=True)
	establecimiento = fields.Char(string="Establecimiento", size=3, default="001", help="Ingrese el establecimiento que aparecera en su secuencia de factura. (001)", required=True)
	tipo_documento = fields.Char(string="Tipo de Documento", size=2, default="01", help="Ingrese el tipo de documento que aparecera en su secuencia de factura. (01)", required=True)
	rango_autorizado_desde = fields.Integer(string="Rango autorizado (desde)", help="Ingrese el rango de facturación autorizado por la DEI.", required=True)
	rango_autorizado_hasta = fields.Integer(string="Rango autorizado (hasta)", required=True)
	activo = fields.Boolean(string="Activo")
	sequence = fields.Integer(default=1)
	
	@api.one
	@api.constrains('codigo_cai')
	def _validar_cai(self):
		if not self.codigo_cai or len(self.codigo_cai) != 37:
			raise ValidationError("El CAI ingresado no es válido. Debe de contener 37 caractéres incluyendo los guiones. Siga el siguiente formato XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX-XX")
			
	@api.one
	@api.constrains('punto_emision')
	def _validar_punto_emision(self):
		if not self.punto_emision or len(self.punto_emision) != 3:
			raise ValidationError("El punto de emisión es un código numerico compuesto de 3 digitos. Ejemplo: 000")
			
	@api.one
	@api.constrains('establecimiento')
	def _validar_establecimiento(self):
		if not self.establecimiento or len(self.establecimiento) != 3:
			raise ValidationError("El establecimiento es un código numerico compuesto de 3 digitos. Ejemplo: 000")
			
	@api.one
	@api.constrains('tipo_documento')
	def _validar_tipo_documento(self):
		if not self.tipo_documento or len(self.tipo_documento) != 2:
			raise ValidationError("El tipo de documento es un código numerico compuesto de 2 digitos. Ejemplo: 01")
	
	# Revisar si la enumeración ingresada no entra en conflicto con alguna ingresada previamente. 
	# Las enumeraciones no deben de entrelazarse ya que en ese caso existirían dos documentos (facturas, recibos)
	# con el mismo numero de factura. 
	@api.one
	@api.constrains('codigo_cai','punto_emision','establecimiento','tipo_documento','rango_autorizado_desde','rango_autorizado_hasta')
	def _validar_znumeracion(self):
		numeraciones = self.search([('codigo_cai','=',self.codigo_cai), ('id','!=',self.id)])

		for num in numeraciones:
			if num.punto_emision == self.punto_emision and num.establecimiento == self.establecimiento and num.tipo_documento == self.tipo_documento:
				rango_x = range(num.rango_autorizado_desde, num.rango_autorizado_hasta+1)
				rango_y = range(self.rango_autorizado_desde, self.rango_autorizado_hasta+1)
				set_x = set(rango_x)
				inter = set_x.intersection(rango_y)
				
				if len(inter) != 0:
					raise ValidationError("Numeración no valida. Verifique que el rango autorizado no este en conflicto con otro ingresado anteriormente. Se repiten los siguientes numeros:"+str(inter))
	
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
	cai_ids = fields.Many2many(comodel_name="poshn.cai", string="CAI")
	
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
	
	
