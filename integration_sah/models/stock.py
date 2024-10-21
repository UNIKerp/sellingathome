# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests

_logger = logging.getLogger(__name__)


class StockSAH(models.Model):
    _inherit = "product.template"
     
    #  url =""   v/Stocks
    @api.model
    def write(self,vals):
        res = super(StockSAH,self).write(vals)
        if 'qty_available' in vals:
            url = 'https://demoapi.sellingathome.com/v1/Stocks'
            headers = self.env['authentication.sah'].establish_connection()
            values={
                "ProductId": 118557,
                "ProductReference": "sample string 2",
                "StockQuantity": vals.get("user_id"),
                # "SellerId": 1,
                # "SellerRemoteReference": "sample string 3",
                # "SellerStockQuantity": 1,
                # "ProductCombinationStocks": [
                #     {
                #     "ProductCombinationId": 1,
                #     "ProductCombinationBarcode": "sample string 1",
                #     "ProductCombinationSku": "sample string 2",
                #     "ProductCombinationRemoteId": 1,
                #     "StockQuantity": 1,
                #     "StockQuantityComing": 1,
                #     "StockQuantityComingAt": "2024-10-21T13:35:30.8895444+02:00",
                #     "SellerStockQuantity": 1,
                #     "AllowOutOfStockOrders": True
                #     },
                #     {
                #     "ProductCombinationId": 1,
                #     "ProductCombinationBarcode": "sample string 1",
                #     "ProductCombinationSku": "sample string 2",
                #     "ProductCombinationRemoteId": 1,
                #     "StockQuantity": 1,
                #     "StockQuantityComing": 1,
                #     "StockQuantityComingAt": "2024-10-21T13:35:30.8895444+02:00",
                #     "SellerStockQuantity": 1,
                #     "AllowOutOfStockOrders": True
                #     }
                # ],
                # "StockQuantityComing": 1,
                # "StockQuantityComingAt": "2024-10-21T13:35:30.8895444+02:00",
                # "AllowOutOfStockOrders": True
            
            }
            response = requests.put(url, headers=headers, json=values)
            if response.status_code == 200:
                print(response.json())  
            else:
                print(f"Erreur {response.status_code}: {response.text}")
            return res

        