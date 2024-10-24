# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)

class SaleSAH(models.Model):
    _inherit = "sale.order"

    id_order_sh = fields.Integer(string="ID commande SAH")


    def get_commande(self):
        url_commande = 'https://demoapi.sellingathome.com/v1/Orders'            
        headers = self.env['authentication.sah'].establish_connection()
        response = requests.get(url_commande, headers=headers)
        if response.status_code == 200:
            commandes_sah = response.json()
            for commande in commandes_sah:
                id_order = commande['Id']
                commandes_odoo = self.env['sale.order'].search([('id_order_sh','=',id_order)])
                client_id = self.env['res.partner'].search([('id_client_sah','=',commande['Customer']['Id'])])
                # vendeur_id = self.env['res.users'].search([('id_vendeur_sah','=',commande['Seller']['Id'])])
                if not commandes_odoo and client_id:
                    commandes_odoo.create({
                        "id_order_sh":commande['Id'],
                        "name":commande['OrderRefCode'],
                        "partner_id":client_id.id,
                        "user_id":client_id.user_id,
                        'order_line': [(0, 0, {
                            'product_id': self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])]).id or 1, 
                            'product_uom_qty': elt['Quantity'],
                            'price_unit': elt['UnitPrice'], 
                            'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                        }) for elt in commande['Products']] ,
                        # "partner_shipping_id":delivery_address.id
                      
                    })
                elif commandes_odoo:
                    _logger.info("poooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
                    commandes_odoo.write({
                        "name":commande['OrderRefCode'],
                        "partner_id":client_id.id,
                        "user_id":client_id.user_id,
                        'order_line': [(0, 0, {
                            'product_id': self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])]).id or 1, 
                            'product_uom_qty': elt['Quantity'],
                            'price_unit': elt['UnitPrice'], 
                            'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                        }) for elt in commande['Products']] ,
                    })

        else:
            print(f"Erreur {response.status_code}: {response.text}")
       
            
    def _get_or_create_tax(self, tax_rate):
        # Recherche la taxe par son montant
        tax = self.env['account.tax'].search([('amount', '=', tax_rate)], limit=1)
        
        # Si la taxe n'existe pas, on la crée
        if not tax:
            tax = self.env['account.tax'].create({
                'name': f'Taxe {tax_rate}%',
                'amount': tax_rate,
                # 'type_tax_use': 'sale',  # Ou 'purchase' selon l'utilisation
                # 'price_include': False,  # Si les prix incluent ou non la taxe
            })
        
        return tax.id

