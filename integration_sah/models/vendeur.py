# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class vendeur(models.Model):
    _inherit = "res.users"


    def recuperation_veudeurs_sah_vers_odoo(self):
        print("UUUUUUUUUUUUUUUUUUuu")