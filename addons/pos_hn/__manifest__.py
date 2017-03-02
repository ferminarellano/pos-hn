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
    'depends': ['point_of_sale'],
    'data': [
		'report/ventas_por_categoria/ventas_por_categoria.xml',
		'wizard/ventas_por_categoria/ventas_por_categoria_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
        'data.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'qweb':['static/src/xml/custom.xml']
}
