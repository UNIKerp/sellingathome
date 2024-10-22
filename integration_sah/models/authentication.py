# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AuthenticaionSAH(models.Model):
    _name = "authentication.sah"
    _description = "Authentication sellingathome"

    
    def establish_connection(self):
        company = self.env['res.company'].search([('token_sah','!=',False),('secret_key_sah','!=',False)],limit=1)
        if company:
            headers = {
                "token": company.token_sah,
                "SECRET_KEY": company.secret_key_sah,
                "Content-Type": "application/json"
            }
            return headers
   