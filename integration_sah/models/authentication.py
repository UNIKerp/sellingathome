# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests

_logger = logging.getLogger(__name__)


class AuthenticaionSAH(models.Model):
    _name = "authentication.sah"
    _description = "Authentication sellingathome"

    
    def establish_connection(self,url):
        headers = {
            "token": "519827d1-1f35-446d-8895-62c5b597c64c",
            "SECRET_KEY": "2915189c-c56c-4b65-8403-4ffd6bd917dc"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            _logger.info("Erreur connexion")

   