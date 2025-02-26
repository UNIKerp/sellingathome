# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
from datetime import date
_logger = logging.getLogger(__name__)


class MethodePaiement(models.Model):
    _name = "methode.paiement.sah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "gestion des methodes de paiement"

    name = fields.Char(string='Nom',required=True, copy=False)
    code = fields.Char(string='Code',required=True, copy=False)
    value = fields.Integer( copy=False)
    is_confirme = fields.Boolean(string='Confirmer Commande',help="Le paiement est confirmé")
    
    _sql_constraints = [
        ('code_uniq', 'unique (code)', "Ce code exists deja!")]
 

     