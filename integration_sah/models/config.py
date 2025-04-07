# -*- coding: utf-8 -*-
# from odoo.http import request

from odoo import api, fields, models


class ConfigSAH(models.Model):

    _inherit = "res.company"

    token_sah = fields.Char(string="Token",copy=False)
    secret_key_sah = fields.Char(string="Secret Key",copy=False)
    date_debut = fields.Date(string="Date de debut")
    date_fin = fields.Date(string="Date de Fin")