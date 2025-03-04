# -*- coding: utf-8 -*-
# from odoo.http import request

from odoo import api, fields, models


class ConfigSAH(models.Model):

    _inherit = "res.company"

    token_sah = fields.Char(string="Token",copy=False)
    secret_key_sah = fields.Char(string="Secret Key",copy=False)
    url_commande = fields.Char(string='URL commande SAH', copy=False, default='https://demoapi.sellingathome.com/v1/Orders')
    date_debut = fields.Datetime(string="Date de debut",copy=False)
    date_fin = fields.Datetime(string="Date de Fin",copy=False)