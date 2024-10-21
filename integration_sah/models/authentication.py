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

    
    def establish_connection(self,url):
        company = self.env['res.compny'].search([('token','!=',False),('secret_key','!=',False)],limit=1)
        if company:
            headers = {
                "token": company.token,
                "SECRET_KEY": company.secret_key
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                raise ValidationError("Les données fournies ne sont pas valides.")
        else:
            raise UserError("Une erreur est survenue, veuillez vérifier vos paramètres d'accés.")

   