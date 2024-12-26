# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
from datetime import date
_logger = logging.getLogger(__name__)


class MethodePaiement(models.Model):
    _name = "methode.paiement.sah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "gestion des methodes de paiement"

    name = fields.Char(string='Nom', copy=False)
    value = fields.Integer(copy=False)
    is_confirme = fields.Boolean(string='Est confirmé',help="Le paiement est confirmé")
    
    _sql_constraints = [
        ('value_uniq', 'unique (value)', "value SAH exists deja!"), ]
   
 

     