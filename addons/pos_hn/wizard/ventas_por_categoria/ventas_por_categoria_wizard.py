# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime, timedelta
 
class sales_category_wizard(models.TransientModel):
	_name = 'sales.category.wizard'
	_description = 'Reporte de Ventas por Categoria'

	fecha_inicio = fields.Date('Fecha inicio', required=True)
	fecha_final = fields.Date('Fecha final', required=True)

	def print_report(self):
		company_name = self.env.user.company_id.name or "NO ENCONTRADO"
		categories_obj = self.env['pos.category'].search([['parent_id','!=',False]]).sorted(key=lambda r: r.parent_id.name)
		
		fecha_inicio_dt = datetime.strptime(self.fecha_inicio + ' 06:00:00.0', '%Y-%m-%d %H:%M:%S.%f')
		fecha_final_dt = datetime.strptime(self.fecha_final + ' 06:00:00.0', '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=1)
		
		orders = self.env['pos.order'].search([['date_order','>',fecha_inicio_dt.strftime('%Y-%m-%d %H:%M:%S.%f')],['date_order','<',fecha_final_dt.strftime('%Y-%m-%d %H:%M:%S.%f')]])
		orders_id = [order.id for order in orders]
		
		order_lines = self.env['pos.order.line'].search([['order_id','in',orders_id]])
		categories = self._process_order_lines(order_lines)
		totales = self._process_total(categories)
		categories = self._calcular_pc_ventas(categories, totales['total_bruto'])
		categories_sorted = self._sort_categories(categories, categories_obj)
		
		data = {
			'company_name': company_name,
			'report_name': self._description,
			'fecha_inicio': datetime.strptime(self.fecha_inicio, '%Y-%m-%d').strftime('%Y/%m/%d'),
			'fecha_final': datetime.strptime(self.fecha_final, '%Y-%m-%d').strftime('%Y/%m/%d'),
			'fecha_actual': (datetime.now() - timedelta(hours=6)).strftime('%Y/%m/%d'),
			'hora_actual': (datetime.now() - timedelta(hours=6)).strftime('%I:%M:%S %p'),
			'usuario': self.env.user.name,
			'categories': categories_sorted,
			'totales': totales
		}	
		return self.env['report'].get_action([], 'pos_hn.report_reporte_ventas_por_categoria_tplt', data=data)
		
	def _sort_categories(self, categories, categories_obj):
		new_list = []
		
		for category_obj in categories_obj:
			category_id = category_obj.id
			
			for category in categories:
				if category_id == category['id']:
					new_list.append(category)
			
		for category in categories:
			if len(category['name']) > 0  and len(category['parent']) == 0:
				new_list.append(category)
				
		for category in categories:
			if len(category['name']) == 0  and len(category['parent']) == 0:
				new_list.append(category)
				
		return new_list
		
	def _process_order_lines(self, order_lines):
		category_data = []
		
		for order_line in order_lines:
			pos_categ = order_line.product_id.product_tmpl_id.pos_categ_id
			
			found = False
			for category in category_data:
				if category['id'] == pos_categ.id:
					found = True
					category['qty'] += order_line.qty
					category['monto_bruto'] += order_line.price_subtotal_incl
					category['descuento'] += order_line.price_subtotal_incl*(float(order_line.discount)/100)
					category['isv'] += order_line.price_subtotal_incl - order_line.price_subtotal
					category['costo'] += order_line.product_id.standard_price
					category['utilidad'] = category['monto_bruto'] - category['isv'] - category['costo'] - category['descuento']
					category['pc_utilidad'] = (category['utilidad']/category['monto_bruto'])*100
					
			if found == False:
				category_data.append({
					'id' : pos_categ.id,
					'name': pos_categ.name or "",
					'parent': pos_categ.parent_id.name or "",
					'qty':order_line.qty,
					'monto_bruto':order_line.price_subtotal_incl,
					'descuento':order_line.price_subtotal_incl*(float(order_line.discount)/100),
					'isv':order_line.price_subtotal_incl - order_line.price_subtotal,
					'costo': order_line.product_id.standard_price,
					'utilidad': order_line.price_subtotal_incl - (order_line.price_subtotal_incl - order_line.price_subtotal) - (order_line.product_id.standard_price) - (order_line.price_subtotal_incl*(float(order_line.discount)/100)),
					'pc_utilidad': ((order_line.price_subtotal_incl - (order_line.price_subtotal_incl - order_line.price_subtotal) - (order_line.product_id.standard_price) - (order_line.price_subtotal_incl*(float(order_line.discount)/100))) / (order_line.price_subtotal_incl))*100,
					'pc_ventas': 0.0
				})
		return category_data
	
	def _calcular_pc_ventas(self, categories, total_ventas_brutas):
		for category in categories:
			category['pc_ventas'] = (category['monto_bruto'] / total_ventas_brutas)*100
			
		return categories
		
	def _process_total(self, categories):
		total_cantidad=0;
		total_bruto=0.0;
		total_descuento=0.0;
		total_isv=0.0;
		total_costo=0.0;
		total_utilidad=0.0;
		total_pc_utilidad=0.0;
		total_pc_ventas=100.00;
		
		for category in categories:
			total_cantidad += category['qty'];
			total_bruto += category['monto_bruto'];
			total_descuento += category['descuento'];
			total_isv += category['isv'];
			total_costo += category['costo'];
			total_utilidad += category['utilidad'];
			
		return {
			'total_cantidad': total_cantidad,
			'total_bruto': total_bruto,
			'total_descuento': total_descuento,
			'total_isv': total_isv,
			'total_costo': total_costo,
			'total_utilidad': total_utilidad,
			'total_pc_utilidad': (total_utilidad/total_bruto)*100,
			'total_pc_ventas': total_pc_ventas
		}
			