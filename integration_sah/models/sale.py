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
                print('ppppppppppppppppppppppppppppppppppp',commande)
                id_order = commande['Id']
                commandes_odoo = self.env['sale.order'].search([('id_order_sh','=',id_order)])
                partner_id = self.env['res.partner'].search([('id_client_sah','=',commande['Customer']['Id'])])
                _logger.info("maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                _logger.info(commandes_odoo)
                _logger.info("nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
                _logger.info(partner_id)
                _logger.info("partner_idpartner_idpartner_idpartner_idpartner_idpartner_id")
                if not commandes_odoo and partner_id:
                    print("tttttttttttttttttttttttttttttttttttttttt")
                    # delivery_address = self.env['res.partner'].create({
                    #     'type':"delivery",
                    #     'name': commande['FirstName']+'  '+commande['LastName'], 
                    #     'phone': commande['phone'],
                    #     'mobile': commande['MobilePhone'], 
                    #     'street':commande['StreetAddress'],
                    #     'street2':commande['StreetAddress2'],
                    #     'city':commande['City'],

                    # })
                    # print("delivery_addressdelivery_addressdelivery_address",delivery_address)
                    commandes_odoo.create({
                        "id_order_sh":commande['Id'],
                        "name":commande['OrderRefCode'],
                        "partner_id":partner_id.id,
                        'order_line': [(0, 0, {
                            'product_id': self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])]).id or 1, 
                            'product_uom_qty': elt['Quantity'],
                            'price_unit': elt['UnitPrice'], 
                        }) for elt in commande['Products']] ,
                        # "partner_shipping_id":delivery_address.id
                      
                    })
                    _logger.info('mppppppppppppppppppppppppppppppppppppppppppppppppppp')
                    _logger.info(commandes_odoo)
                    break 
        else:
            print(f"Erreur {response.status_code}: {response.text}")
       



            


