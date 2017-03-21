# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.report import report_sxw
from datetime import datetime, timedelta
from itertools import ifilter

class reporte_pos_order_reprint(report_sxw.rml_parse):
	UNIDADES = ('', 'UN ', 'DOS ', 'TRES ', 'CUATRO ', 'CINCO ', 'SEIS ', 'SIETE ', 'OCHO ', 'NUEVE ', 'DIEZ ', 'ONCE ', 'DOCE ', 'TRECE ', 'CATORCE ', 'QUINCE ', 'DIECISEIS ', 'DIECISIETE ', 'DIECIOCHO ', 'DIECINUEVE ', 'VEINTE ')

	DECENAS = ('VENTI', 'TREINTA ', 'CUARENTA ', 'CINCUENTA ', 'SESENTA ', 'SETENTA ', 'OCHENTA ', 'NOVENTA ', 'CIEN ')
	CENTENAS = ( 'CIENTO ', 'DOSCIENTOS ', 'TRESCIENTOS ', 'CUATROCIENTOS ', 'QUINIENTOS ', 'SEISCIENTOS ', 'SETECIENTOS ', 'OCHOCIENTOS ', 'NOVECIENTOS ' ) 
	UNITS = ( ('',''), ('MIL ','MIL '), ('MILLON ','MILLONES '), ('MIL MILLONES ','MIL MILLONES '), ('BILLON ','BILLONES '), ('MIL BILLONES ','MIL BILLONES '), ('TRILLON ','TRILLONES '), ('MIL TRILLONES','MIL TRILLONES'), ('CUATRILLON','CUATRILLONES'), ('MIL CUATRILLONES','MIL CUATRILLONES'), ('QUINTILLON','QUINTILLONES'), ('MIL QUINTILLONES','MIL QUINTILLONES'), ('SEXTILLON','SEXTILLONES'), ('MIL SEXTILLONES','MIL SEXTILLONES'), ('SEPTILLON','SEPTILLONES'), ('MIL SEPTILLONES','MIL SEPTILLONES'), ('OCTILLON','OCTILLONES'), ('MIL OCTILLONES','MIL OCTILLONES'), ('NONILLON','NONILLONES'), ('MIL NONILLONES','MIL NONILLONES'), ('DECILLON','DECILLONES'), ('MIL DECILLONES','MIL DECILLONES'), ('UNDECILLON','UNDECILLONES'), ('MIL UNDECILLONES','MIL UNDECILLONES'), ('DUODECILLON','DUODECILLONES'), ('MIL DUODECILLONES','MIL DUODECILLONES'), )

	MONEDAS = (
		{'country': u'Honduras', 'currency': 'HNL', 'singular': u'LEMPIRA', 'plural': u'LEMPIRAS', 'symbol': u'L', 'decimalsingular':u'CENTAVO','decimalplural':u'CENTAVOS'},
	)

	def __init__(self, cr, uid, name, context):
		super(reporte_pos_order_reprint, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'order_date':self._order_date,
			'money':self._money,
			'get_total_without_tax': self._get_total_without_tax,
			'get_tax_details': self._get_tax_details,
			'get_total_discount': self._get_total_discount,
			'get_payment_lines': self._get_payment_lines,
			'get_change': self._get_change,
			'get_amount_in_words': self._get_amount_in_words,
			'get_fecha_limite_emision': self._get_fecha_limite_emision,
			'to_int': self._to_int
		})
		
	def _to_int(self, amount):
		return int(amount)
		
	def _get_fecha_limite_emision(self, order):
		fecha = order.session_id.config_id.cai.fecha_limite_emision
		return datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y/%m/%d')
		
	def _get_amount_in_words(self, amount):
		return self.to_word(amount, 'HNL')
		
	def _get_change(self, order):
		statement_ids = order.statement_ids.sorted(key=lambda r: r.id)
		change = 0
		
		for payment in statement_ids:
			if payment.amount < 0:
				change = abs(payment.amount)
			
		return self._money(change)
		
	def _get_payment_lines(self, order):
		statement_ids = order.statement_ids.sorted(key=lambda r: r.id)
		payment_lines = []
		
		for payment in statement_ids:
			if payment.amount >= 0:
				payment_lines.append({
					'name': 'Efectivo (HNL)',
					'amount': self._money(payment.amount)
				})
			
		return payment_lines
		
	def _get_total_discount(self, order):
		lines = order.lines
		total_discount = 0
		
		for line in lines:
			total_discount += (line.price_subtotal*(line.discount/100))
		
		return self._money(total_discount)
	
	def _get_tax_details(self, order):
		lines = order.lines
		tax_details = []
		
		for line in lines:
			tax_ids = line.tax_ids
			
			for tax in tax_ids:
				tax_details.append({
					'name': tax.name,
					'amount': self._money(line.price_subtotal*(tax.amount/100))
				})
		return tax_details
		
	def _get_total_without_tax(self, order):
		currency = order.pricelist_id.currency_id
		amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
		return amount_untaxed
		
	def _order_date(self, date):
		return (datetime.strptime(date, '%Y-%m-%d %H:%M:%S')-timedelta(hours=6)).strftime('%Y/%m/%d %I:%M %p')
		
	def _money(self, amount):
		return 'L {:,.2f}'.format(amount)
		
	def hundreds_word(self, number):
		converted = ''
		if not (0 < number < 1000):
			return 'No es posible convertir el numero a letras'

		number_str = str(number).zfill(9)
		cientos = number_str[6:]

		if(cientos):
			if(cientos == '001'):
				converted += 'UN '
			elif(int(cientos) > 0):
				converted += '%s ' % self.__convert_group(cientos)

		return converted.title().strip()

	def __convert_group(self, n):
		output = ''

		if(n == '100'):
			output = "CIEN "
		elif(n[0] != '0'):
			output = self.CENTENAS[int(n[0]) - 1]

		k = int(n[1:])
		if(k <= 20):
			output += self.UNIDADES[k]
		else:
			if((k > 30) & (n[2] != '0')):
				output += '%sY %s' % (self.DECENAS[int(n[1]) - 2], self.UNIDADES[int(n[2])])
			else:
				output += '%s%s' % (self.DECENAS[int(n[1]) - 2], self.UNIDADES[int(n[2])])

		return output

	def to_word(self, number, mi_moneda=None):

		if mi_moneda != None:
			try:
				moneda = ifilter(lambda x: x['currency'] == mi_moneda, self.MONEDAS).next()
				if int(number) == 1:
					entero = moneda['singular']
				else:
					entero = moneda['plural']
					if round(float(number) - int(number), 2) == float(0.01):
						fraccion = moneda['decimalsingular']
					else:
						fraccion = moneda['decimalplural']

			except:
				return "Tipo de moneda inválida"
		else:
			entero = ""
			fraccion = ""

		human_readable = []
		human_readable_decimals = []
		num_decimals ='{:,.2f}'.format(round(number,2)).split('.') #Sólo se aceptan 2 decimales
		num_units = num_decimals[0].split(',')
		num_decimals = num_decimals[1].split(',')
		#print num_units
		for i,n in enumerate(num_units):
			if int(n) != 0:
				words = self.hundreds_word(int(n))
				units = self.UNITS[len(num_units)-i-1][0 if int(n) == 1 else 1]
				human_readable.append([words,units])
		for i,n in enumerate(num_decimals):
			if int(n) != 0:
				words = self.hundreds_word(int(n))
				units = self.UNITS[len(num_decimals)-i-1][0 if int(n) == 1 else 1]
				human_readable_decimals.append([words,units])

		#filtrar MIL MILLONES - MILLONES -> MIL - MILLONES
		for i,item in enumerate(human_readable):
			try:
				if human_readable[i][1].find(human_readable[i+1][1]):
					human_readable[i][1] = human_readable[i][1].replace(human_readable[i+1][1],'')
			except IndexError:
				pass
		human_readable = [item for sublist in human_readable for item in sublist]
		human_readable.append(entero)
		for i,item in enumerate(human_readable_decimals):
			try:
				if human_readable_decimals[i][1].find(human_readable_decimals[i+1][1]):
					human_readable_decimals[i][1] = human_readable_decimals[i][1].replace(human_readable_decimals[i+1][1],'')
			except IndexError:
				pass
		human_readable_decimals = [item for sublist in human_readable_decimals for item in sublist]
		human_readable_decimals.append(fraccion)
		sentence = ' '.join(human_readable).replace('  ',' ').title().strip()
		if sentence[0:len('un mil')] == 'Un Mil':
			sentence = 'Mil' + sentence[len('Un Mil'):]
		if num_decimals != ['00']:
			sentence = sentence + ' con ' + ' '.join(human_readable_decimals).replace('  ',' ').title().strip()
		return sentence
		
class wrapped_reporte_pos_order_reprint(models.AbstractModel):
	_name = 'report.pos_hn.report_reporte_pos_order_reprint_tplt'
	_inherit = 'report.abstract_report'
	_template = 'pos_hn.report_reporte_pos_order_reprint_tplt'
	_wrapped_report_class = reporte_pos_order_reprint
	
	def render_html(self, ids, data=None):
		return super(wrapped_reporte_pos_order_reprint, self).render_html(ids, data=data)