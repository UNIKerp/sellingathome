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
            for line in self.move_ids_without_package:
                if line.product_id.product_tmpl_id.is_storable == True:
                    qty_available = line.product_id.product_tmpl_id.qty_available
                    virtual_available = line.product_id.product_tmpl_id.virtual_available
                    url = 'https://demoapi.sellingathome.com/v1/Stocks'
                    headers = self.env['authentication.sah'].establish_connection()
                    values = {
                        "ProductId":   line.product_id.product_tmpl_id.produit_sah_id,
                        "ProductReference":  line.product_id.product_tmpl_id.default_code,
                        "StockQuantity": int(qty_available),
                        "StockQuantityComing":int(virtual_available),
                        "ProductCombinationStocks": [
                            {
                            "ProductCombinationId": line.product_id.product_tmpl_id.produit_sah_id,
                            "ProductCombinationBarcode": "sample string 1",
                            "ProductCombinationSku": "sample string 2",
                            "ProductCombinationRemoteId": 1,
                            "StockQuantity": 1,
                            "StockQuantityComing": 1,
                            "StockQuantityComingAt": "2024-10-22T13:46:02.7937593+02:00",
                            "SellerStockQuantity": 1,
                            "AllowOutOfStockOrders": True
                            }
                        ],
                        "AllowOutOfStockOrders": True
                        
                    }
                    response = requests.put(url, headers=headers, json=values)
                    if response.status_code == 200:
                        _logger.info('=====================%s',response.json())  
                    else:
                        _logger.info('=====================%s',response.text)
        return res

class StockSAH(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.model
    def create(self,vals):
        res = super(StockSAH,self).create(vals)
        object_id = self.env.context.get('active_id')
        if object_id:
            produit = self.env['product.template'].search([('id','=',object_id),('is_storable','=',True)])
            if res.new_quantity and produit:
                url = 'https://demoapi.sellingathome.com/v1/Stocks'
                headers = self.env['authentication.sah'].establish_connection()
                if headers:
                    values = {
                        "ProductId":  produit.produit_sah_id,
                        "ProductReference": produit.default_code,
                        "StockQuantity": int(res.new_quantity),
                        "StockQuantityComing":int(produit.virtual_available),  
                        "ProductCombinationStocks": [
                            {
                            "ProductCombinationId": produit.produit_sah_id,
                            "ProductCombinationBarcode": "sample string 1",
                            "ProductCombinationSku": "sample string 2",
                            "ProductCombinationRemoteId": 1,
                            "StockQuantity": 1,
                            "StockQuantityComing": 1,
                            "StockQuantityComingAt": "2024-10-22T13:46:02.7937593+02:00",
                            "SellerStockQuantity": 1,
                            "AllowOutOfStockOrders": True
                            }
                        ],
                        "AllowOutOfStockOrders": True
                    }
                    response = requests.put(url, headers=headers, json=values)
                    if response.status_code == 200:
                        print(response.json())  
                    else:
                        print(f"Erreur {response.status_code}: {response.text}")
        return res

            