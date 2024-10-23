# -*- coding: utf-8 -*-
{
    'name': "Integration Selling at home",
    'version': '18.0.1.0.0',
    'depends': ["stock"],
    "author":"Unikerp",
    "website" : "www.unikerp.com",
    'description': """ Integration sellingathome et odoo """,
    'application': True,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/config.xml',
        'views/product.xml',
        'views/client.xml',
    ],
}
