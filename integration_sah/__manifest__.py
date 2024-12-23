# -*- coding: utf-8 -*-
{
    'name': "Integration Selling at home",
    'version': '18.0.2.0.0',
    'depends': ["stock","contacts",'sale_management','point_of_sale','website_sale','queue_job'],
    "author":"Unikerp",
    "website" : "www.unikerp.com",
    'description': """ Integration sellingathome et odoo """,
    'application': True,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/config.xml',
        'views/product.xml',
        'views/sale.xml',
        'views/client.xml',
        'views/crons.xml',
        'views/gestion_vdi.xml',
    ],
    'images':['static/description/icon.png',],
}
