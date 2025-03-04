# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
import requests
from datetime import datetime
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class MappingSAHOdoo(models.Model):
    _name = "commande.sah"
    _description = "Table pour stoker les commandes de SAH dans Odoo"

    name = fields.Char(string='Reference commande SAH',required=True, copy=False)
    job_id = fields.Many2one('queue.job',string="Job",copy=False)
    commande_id = fields.Many2one("sale.order",string="Commande Odoo",copy=False)
    donnes_sah = fields.Json("Données")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    # Synchronisation des commandes de SAH vers Odoo
    def _mapping_commandes_sah_odoo(self):
        url_commande = 'https://demoapi.sellingathome.com/v1/Orders'           
        headers = self.env['authentication.sah'].establish_connection()
        response = requests.get(url_commande, headers=headers)
        if response.status_code == 200:
            commandes_sah = response.json()
            for commande in commandes_sah:
                if commande['Status'] not in ['InProgress','Created','Shipped'] :
                    id_order = commande['Id']
                    commandes_odoo = self.env['sale.order'].search([('id_order_sh','=',id_order)])
                    if not commandes_odoo:
                        job_kwargs_commandes = {
                            "description": "Mise à jour et création de nouveaux commandes s'ils existent de SAH vers Odoo",
                        }
                        self.with_delay(**job_kwargs_commandes).get_commande(commande)     
    
    def get_commande(self,commande):
        if commande and commande['Status'] not in ['InProgress','Created','Shipped']:  
               
            for elt in commande['Products']:
                if elt['TaxRate']:
                    self._get_or_create_tax(elt['TaxRate'])
                        
            if commande['DeliveryAmount'] != '0.0' and mode_livraison_sah_id and mode_livraison_sah_id.delivery_carrier_id:
                self._get_or_create_tax_delivery(commande['DeliveryAmount'],commande['DeliveryAmountExclTax']),
                        
    
            
    def _get_mapping_tax(self, tax_rate):
        # Recherche la taxe par son montant
        tax = self.env['tax.sah'].search([('amount', '=', tax_rate)], limit=1)
        if not tax :
            self.env['tax.sah'].create({
                                    'name':f'Taxe {tax_rate}%',
                                    'amount':tax_rate
                                })

    def _get_mapping_tax_delivery(self, deliveryAmount,deliveryAmountExclTax ):
        # Recherche la taxe par son montant
        taux = round((deliveryAmount - deliveryAmountExclTax ) * 100,1)
        tax_id = self.env['tax.sah'].search([('amount', '=', taux)], limit=1)
        if not tax_id :
            self.env['tax.sah'].create({
                                    'name':f'Taxe {taux}%',
                                    'amount':taux
                                })
