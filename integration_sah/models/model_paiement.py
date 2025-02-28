# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
from datetime import date
_logger = logging.getLogger(__name__)


class ModelPaiement(models.Model):
    _name = "paiement.sah"
    _description = "Gestion des modèles de paiement"


    name = fields.Char(string='Nom',help="Nom du client")
    methode = fields.Many2one('methode.paiement.sah',string='Méthode de paiement',help="Méthode de paiement")
    montant = fields.Float(string='Montant',help="Montant du paiement")
    numero_transaction = fields.Char(string='Numéro de transaction',help="Numéro de transaction") 
    date_paiement = fields.Datetime(string='Date de paiement',help="Date de paiement") 
    date_echeance = fields.Datetime(string='Date d\'échéance du paiement',help="date d'échéance du paiement") 
    date_validation = fields.Datetime(string='Date de validation du paiement',help="Date de validation du paiement") 
    order_id = fields.Many2one('sale.order',string="Commande",help='le bon de commande')