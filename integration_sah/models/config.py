# -*- coding: utf-8 -*-
# from odoo.http import request

from odoo import api, fields, models


class ConfigSAH(models.TransientModel):

    _inherit = "res.config.settings"


    token = fields.Char(string="Token")
    secret_key = fields.Char(string="Secret Key")
    
    def set_values(self):
        res = super(ConfigSAH, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('integration_sah.token', self.token)
        self.env['ir.config_parameter'].sudo().set_param('integration_sah.secret_key', self.secret_key)
        return res

    @api.model
    def get_values(self):
        res = super(ConfigSAH, self).get_values()
        res.update(
            token = self.env['ir.config_parameter'].sudo().get_param('integration_sah.token') or False ,
            secret_key = self.env['ir.config_parameter'].sudo().get_param('integration_sah.secret_key') or False ,
        )
        return res
    