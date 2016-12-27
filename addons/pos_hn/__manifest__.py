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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
