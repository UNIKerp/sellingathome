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
                partner_id = self.env['res.partner'].search([('id_client_sah','=',commande['Customer']['Id'])])
                if not commandes_odoo and partner_id:
                    commandes_odoo.create({
                        "id_order_sh":commande['Id'],
                        "name":commande['OrderRefCode'],
                        "partner_id":partner_id.id,
                        'order_line': [(0, 0, {
                            'product_id': self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])]).id or 1, 
                            'product_uom_qty': elt['Quantity'],
                            'price_unit': elt['UnitPrice'], 
                        }) for elt in commande['Products']] 
                      
                    })
                    delivery_address = self.env['res.partner'].create({
                        'type':"delivery",
                        'name': commande['Lastname'], 
                        'phone': commande['phone'],
                        'mobile': commande['MobilePhone'],
                    })
                   

              
        else:
            print(f"Erreur {response.status_code}: {response.text}")
       



            

