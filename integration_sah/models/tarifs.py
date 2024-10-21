# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests

class Tarifs(models.Model):

    _inherit = "product.pricelist.item"

    price_sah_id = fields.Char(string="ID Prix SAH")

    @api.model
    def create(self,vals):
        res = super(Tarifs,self).create(vals)
        headers = self.env['authentication.sah'].establish_connection()
        url_add_price = 'https://demoapi.sellingathome.com/v1/Prices'
        if res.product_tmpl_id:
            values = {
                "ProductId": res.product_tmpl_id.product_sah_id,
                "BrandTaxRate": 2.1,
                "BrandTaxName": "sample string 3",
                "TwoLetterISOCode": "FR",
                "PriceExclTax": 1.1,
                "PriceInclTax": 1.1,
                "ProductCost": 5.1,
                "EcoTax": 6.1,
                "IsDefault": true,
            }
            response = requests.get(url_add_price, json=values, headers=headers)
            if response1.status_code == 200:
                data = response.json()
                res.price_sah_id =  str(data.get('Id'))
        
        return res


    def write(self,vals):
        product_id = self.id
        url_edit = f'https://demoapi.sellingathome.com/v1/Prices/{self.price_sah_id}'
        values={
            "ProductId": product_id,
            # "BrandTaxRate": 2.1,
            # "BrandTaxName": "prix 1 test",
            "TwoLetterISOCode": "fr",
            # "PriceExclTax": ,
            # "PriceInclTax":,
            # "ProductCost": 150,
            # "EcoTax": 6.1,
            # "IsDefault": True,
            # "RolePrices":,
        }
        requests.put(url_edit, headers=headers, json=values)
        res = super(Tarifs,self).write(vals)
        return res
