# -*- coding: utf-8 -*-
{
    'name': "Conekta",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com. This module depends on
        External dependensies of Conekta. To install this dependency run on you system
        pip install conekta==1.0.1""",

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
    'depends': ['base','payment','account'],
    'external_dependencies' : {"python": ["conekta"]},

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_conekta_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_acquirer_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'images': ['static/description/Logo-Conekta.jpg'],
    'installable': True,
    #'post_init_hook': 'create_missing_journal_for_acquirers',
}