# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.report import report_sxw

class reporte_ventas_por_categoria(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(reporte_ventas_por_categoria, self).__init__(cr, uid, name, context)
		self.localcontext.update({})
		
class wrapped_reporte_ventas_por_categoria(models.AbstractModel):
	_name = 'report.pos_hn.report_reporte_ventas_por_categoria_tplt'
	_inherit = 'report.abstract_report'
	_template = 'pos_hn.report_reporte_ventas_por_categoria_tplt'
	_wrapped_report_class = reporte_ventas_por_categoria
	
	def render_html(self, ids, data=None):
		return super(wrapped_reporte_ventas_por_categoria, self).render_html(ids, data=data)