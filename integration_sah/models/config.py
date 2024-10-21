# -*- coding: utf-8 -*-
# from odoo.http import request

from odoo import api, fields, models


class ConfigSAH(models.model):

    _inherit = "res.company"

    token = fields.Char(string="Token")
    secret_key = fields.Char(string="Secret Key")
    