# -*- coding: utf-8 -*-
{
    'name': 'ZRU',

    'description': '''
        Odoo app for the ZRU Platform.
        ''',

    'summary': '''Odoo app for the ZRU Platform''',

    'author': 'ZRU',
    'website': 'https://www.zrupay.com',

    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'eCommerce',
    'version': '17.0.0.4',

    # any module necessary for this one to work correctly
    'depends': ['payment', 'website_sale'],
    'external_dependencies': {'python': ['zru-python']},

    # always loaded
    'data': [
        "views/payment_provider.xml",
        "views/payment_zru_templates.xml",
        "data/payment_zru.xml",
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
}
