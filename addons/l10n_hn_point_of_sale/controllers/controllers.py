# -*- coding: utf-8 -*-
from odoo import http

# class L10nHnPointOfSale(http.Controller):
#     @http.route('/l10n_hn_point_of_sale/l10n_hn_point_of_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_hn_point_of_sale/l10n_hn_point_of_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_hn_point_of_sale.listing', {
#             'root': '/l10n_hn_point_of_sale/l10n_hn_point_of_sale',
#             'objects': http.request.env['l10n_hn_point_of_sale.l10n_hn_point_of_sale'].search([]),
#         })

#     @http.route('/l10n_hn_point_of_sale/l10n_hn_point_of_sale/objects/<model("l10n_hn_point_of_sale.l10n_hn_point_of_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_hn_point_of_sale.object', {
#             'object': obj
#         })