# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
from datetime import date
_logger = logging.getLogger(__name__)


class MethodePaiement(models.Model):
    _name = "methode.paiement.sah"
    _description = "Gestion des methodes de paiement sah"

    name = fields.Char(string='Nom',required=True, copy=False)
    code = fields.Char(string='Code',required=True, copy=False)
    value = fields.Integer( copy=False)
    is_confirme = fields.Boolean(string='Confirmer Commande',help="Si les commandes rattachées sont automatiquement confirmées.")
    
    _sql_constraints = [
        ('code_uniq', 'unique (code)', "Ce code existe déjà !")]


class ModeLivraison(models.Model):
    _name = "mode.livraison.sah"
    _description = "Gestion des Modes de livraison SAH"

    name = fields.Char(string='Nom',required=True, copy=False)
    desciption = fields.Char(string='Description')
    value = fields.Integer( string='Valeur' , copy=False , required=True)
    delivery_carrier_id = fields.Many2one('delivery.carrier',string="Mode de livraison",help='le Modes de livraison correspondant dans odoo')

    _sql_constraints = [
        ('value_uniq', 'unique (value)', "Cette Valeur existe déjà!")]
 


class TaxSah(models.Model):
    _name = "tax.sah"
    _description = "Gestion des taxes de SAH"

    name = fields.Char(string='Nom',required=True, copy=False)
    amount = fields.Float( string='Montant', required=True, copy=False)
    amount_tax_id = fields.Many2one('account.tax',string="Tax rattacher",help='la tax correspondant dans odoo', copy=False)

    _sql_constraints = [
        ('amount_uniq', 'unique (amount,amount_tax_id)', "Cette taxe a déjà été configurée !")]