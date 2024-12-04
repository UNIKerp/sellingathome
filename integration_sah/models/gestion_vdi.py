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
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "gestion vdi"


    name = fields.Char(string='Nom du groupe',help="Contacts vdi")
    contact_vdi_ids = fields.Many2many('res.partner', string='Contacts vdi',required=True, help="Contacts vdi", domain="[('vdi_id', '!=', False)]")
    contact_vdi_master = fields.Many2one('res.partner', string='Contact vdi master',required=True, help="Contacts vdi master", domain="[('id', 'in', contact_vdi_ids)]")
    adresse_livraison = fields.Many2one('res.partner', string='Adresse de livraison',required=True,help="Adresse de livraison")
    