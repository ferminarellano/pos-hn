# -*- coding: utf-8 -*-
{
    'name': "pos_hn",

    'summary': """
        Localizacion del POS para Honduras""",

    'description': """
        Localización del POS para Honduras, cumpliendo requerimientos de facturación de la DEI para la autoimpresion.
    """,

    'author': "Fermin Arellano",
    'website': "github.com/ferminarellano",
    'category': 'Point Of Sale',
    'version': '0.1',
    'depends': ['point_of_sale','base_action_rule'],
    'data': [
		'report/ventas_por_categoria/ventas_por_categoria.xml',
		'report/pos_order_reprint/pos_order_reprint.xml',
		'report/product_label/product_label.xml',
		'wizard/ventas_por_categoria/ventas_por_categoria_wizard.xml',
		'wizard/product_label/product_label_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
        'data.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'qweb':['static/src/xml/custom.xml']
}
