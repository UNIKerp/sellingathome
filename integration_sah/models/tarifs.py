# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests

class Tarifs(models.Model):

    _inherit = "product.pricelist"

    @api.model
    def create(self,vals):
        res = super(Tarifs,self).create(vals)
        url = 'https://demoapi.sellingathome.com/v1/Prices'
        headers = self.env['authentication.sah'].establish_connection()
        values={
            "ProductId": 118556,
            "BrandTaxRate": 2.1,
            "BrandTaxName": "prix 1 test",
            "TwoLetterISOCode": "fr",
            # "PriceExclTax": 200,
            # "PriceInclTax": 250,
            # "ProductCost": 150,
            # "EcoTax": 6.1,
            "IsDefault": True,
            # "RolePrices": [
            #     {
            #     # "CustomerRoleId": 1,
            #     "Quantity": elt.min_quantity,
            #     # "NewPriceExclTax": 1.1,
            #     # "NewPriceInclTax": 1.1,
            #     "StartDate":elt.date_start,
            #     "EndDate": elt.end_start,
            #     # "CombinationId": 1yy
            #     }
            #     for elt in res.item_ids
            # ]
        }
        response = requests.post(url, headers=headers, json=values)
        if response.status_code == 200:
            print(response.json())  
        else:
            print(f"Erreur {response.status_code}: {response.text}")
        return res
