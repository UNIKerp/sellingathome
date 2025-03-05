# -*- coding: utf-8 -*-
# from odoo.http import request

from odoo import api, fields, models


class ConfigSAH(models.Model):

    _inherit = "res.company"

    token_sah = fields.Char(string="Token",copy=False)
    secret_key_sah = fields.Char(string="Secret Key",copy=False)
    url_commande = fields.Char(string='URL commande SAH', copy=False, default='https://demoapi.sellingathome.com/v1/Orders')
    date_debut = fields.Date(string="Date de debut")
    date_fin = fields.Date(string="Date de Fin")