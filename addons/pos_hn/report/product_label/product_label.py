# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.report import report_sxw

class reporte_product_label(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(reporte_product_label, self).__init__(cr, uid, name, context)
		self.localcontext.update({})
		
class wrapped_reporte_product_label(models.AbstractModel):
	_name = 'report.pos_hn.report_reporte_product_label_tplt'
	_inherit = 'report.abstract_report'
	_template = 'pos_hn.report_reporte_product_label_tplt'
	_wrapped_report_class = reporte_product_label
	
	def render_html(self, ids, data=None):
		return super(wrapped_reporte_product_label, self).render_html(ids, data=data)