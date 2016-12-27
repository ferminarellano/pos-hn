# -*- coding: utf-8 -*-
from odoo import http

# class PosHn(http.Controller):
#     @http.route('/pos_hn/pos_hn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_hn/pos_hn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_hn.listing', {
#             'root': '/pos_hn/pos_hn',
#             'objects': http.request.env['pos_hn.pos_hn'].search([]),
#         })

#     @http.route('/pos_hn/pos_hn/objects/<model("pos_hn.pos_hn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_hn.object', {
#             'object': obj
#         })