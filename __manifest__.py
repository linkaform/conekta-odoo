# -*- coding: utf-8 -*-
{
    'name': "conekta",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Conectar conekta con la aplicacion
    """,

    'author': "Erick Hillo",
    'website': "linkaform.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Payment',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_conekta_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'installable': True,
}