# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)

class StockPickingSAH(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPickingSAH,self).button_validate()
        if self.move_ids_without_package:
            for line self.move_ids_without_package:
                qty_available = line.product_id.product_tmpl_id.qty_available
                qty_available = qty_available+product_uom_qty
                url = 'https://demoapi.sellingathome.com/v1/Stocks'
                headers = self.env['authentication.sah'].establish_connection()
                values = {
                    "ProductId":   line.product_id.product_tmpl_id.produit_sah_id,
                    "ProductReference":  line.product_id.product_tmpl_id.default_code,
                    "StockQuantity": int(qty_available),
                    #"StockQuantityComing":int(produit.virtual_available),
                    }
                    response = requests.put(url, headers=headers, json=values)
                    if response.status_code == 200:
                        print(response.json())  
                    else:
                        print(f"Erreur {response.status_code}: {response.text}")
        return res

class StockSAH(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.model
    def create(self,vals):
        res = super(StockSAH,self).create(vals)
        object_id = self.env.context.get('active_id')
        if object_id:
            produit = self.env['product.template'].search([('id','=',object_id)])
            if res.new_quantity:
                url = 'https://demoapi.sellingathome.com/v1/Stocks'
                headers = self.env['authentication.sah'].establish_connection()
                if headers:
                    values = {
                        "ProductId":  produit.produit_sah_id,
                        "ProductReference": produit.default_code,
                        "StockQuantity": int(res.new_quantity),
                        # "SellerId":produit.seller_ids.partner_id.id,
                        # "SellerRemoteReference":produit.seller_ids.partner_id.ref,
                        "StockQuantityComing":int(produit.virtual_available),
                        
                    
                    }
                    response = requests.put(url, headers=headers, json=values)
                    if response.status_code == 200:
                        print(response.json())  
                    else:
                        print(f"Erreur {response.status_code}: {response.text}")
        return res

            