# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests

_logger = logging.getLogger(__name__)


class StockSAH(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.model
    def create(self,vals):
        print('rrr')
        res = super(StockSAH,self).create(vals)
        object_id = self.env.context.get('active_id')
        produit = self.env['product.template'].search([('id','=',object_id)])
        if res.new_quantity:
            url = 'https://demoapi.sellingathome.com/v1/Stocks'
            headers = self.env['authentication.sah'].establish_connection()
            if headers:
                values={
                    # "ProductId": object_id,
                    "ProductId": 117425,
                    "ProductReference": produit.default_code,
                    "StockQuantity": int(res.new_quantity),
                    "SellerId":produit.seller_ids.partner_id
                
                }
                response = requests.put(url, headers=headers, json=values)
                if response.status_code == 200:
                    print(response.json())  
                else:
                    print(f"Erreur {response.status_code}: {response.text}")
        return res

            