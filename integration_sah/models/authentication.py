# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests

_logger = logging.getLogger(__name__)


class AuthenticaionSAH(models.Model):
    _name = "authentication.sah"
    _description = "Authentication sellingathome"

    
    def establish_connection(self,url):
        token = self.env['ir.config_parameter'].sudo().get_param('integration_sah.token')
        secret_key = self.env['ir.config_parameter'].sudo().get_param('integration_sah.secret_key')

        headers = {
            "token": token,
            "SECRET_KEY": secret_key
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            _logger.info("Erreur connexion")

   