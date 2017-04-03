# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_product(models.Model):
	_name = 'product.product'
	_inherit = 'product.product'
	
	@api.one
	def compute_barcode(self):
		categoria = self.categ_id.name.upper()[0:2]
		padre = self.categ_id.parent_id and self.categ_id.parent_id.name.upper()[0:2] or ''
		producto = "%06d" % self.id
		
		self.write({'barcode':padre+categoria+producto})

		
