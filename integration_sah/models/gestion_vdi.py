# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
_logger = logging.getLogger(__name__)


class GestionVdi(models.Model):
    _name = "gestion.vdi"
    _description = "gestion vdi"


    contact_vdi_ids = fields.Many2many('res.partner', string='Contacts vdi',required=True, help="Contacts vdi")
    contact_vdi_master = fields.Many2one('res.partner', string='Contact vdi master',required=True, help="Contacts vdi master")
    adresse_livraison = fields.Many2one('res.partner', string='Adresse de livraison',required=True,help="Adresse de livraison")
    