# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
from datetime import date
_logger = logging.getLogger(__name__)


class MethodePaiement(models.Model):
    _name = "methode.paiement.sah"
    _description = "gestion des methodes de paiement sah"

    name = fields.Char(string='Nom',required=True, copy=False)
    code = fields.Char(string='Code',required=True, copy=False)
    value = fields.Integer( copy=False)
    is_confirme = fields.Boolean(string='Confirmer Commande',help="Si les commandes rattachées sont automatiquement confirmées.")
    
    _sql_constraints = [
        ('code_uniq', 'unique (code)', "Ce code exists deja!")]


class ModeLivraison(models.Model):
    _name = "mode.livraison.sah"
    _description = "gestion des Modes de livraison SAH"

    name = fields.Char(string='Nom',required=True, copy=False)
    desciption = fields.Char(string='Description')
    value = fields.Integer( string='Valeur' , copy=False , required=True)
    delivery_carrier_id = fields.Many2one('delivery.carrier',string="Mode de livraison",help='le Modes de livraison correspondant dans odoo')

    _sql_constraints = [
        ('value_uniq', 'unique (value)', "Cette Valeur exists deja!")]
 

     