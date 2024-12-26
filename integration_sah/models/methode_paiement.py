# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
from datetime import date
_logger = logging.getLogger(__name__)


class MethodePaiement(models.Model):
    _name = "methode.paiement.sah"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "gestion des methodes de paiement"

    especes = fields.Char(string='Paiement en espèces',help="Paiement en espèces")
    cheque = fields.Char(string='Paiement par chèque',help="Paiement par chèque")
    cheque_multi = fields.Char(string='Paiement Chèque multiple',help="Paiement Chèque multiple")
    carte_credit = fields.Char(string='Paiement Carte de crédit',help="Paiement Carte de crédit")
    carte_credit_multi = fields.Char(string='Paiement Carte de crédit multiple',help="Paiement Carte de crédit multiple")
    declaratif_carte_credit = fields.Char(string='Paiement déclaratif de carte de crédit',help="Paiement déclaratif de carte de crédit")
    financement = fields.Char(string='Financement des paiements',help="Financement des paiements")
    virement_bancaire = fields.Char(string='Paiement Virement Bancaire',help="Paiement Virement Bancaire")
    separe = fields.Char(string='Paiement séparé',help="Paiement séparé")
    depot_dematerialise = fields.Char(string='Paiement Dépôt Dématérialisé',help="Paiement Dépôt Dématérialisé")
    non_remunere = fields.Char(string='Non rémunéré',help="Non rémunéré")
    avantage_gratuit = fields.Char(string='Avantage (gratuit)',help="Avantage (gratuit)")
    bon_administratif = fields.Char(string='Bon administratif',help="Bon administratif")
    declaratif_livraison = fields.Char(string='Paiement déclaratif à la livraison',help="Paiement déclaratif à la livraison")
    is_confirme = fields.Boolean(string='Est confirmé',help="Le paiement est confirmé")

     