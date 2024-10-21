# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests

class Tarifs(models.Model):

    _inherit = "product.pricelist.item"

    price_sah_id = fields.Char(string="ID Prix SAH")

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
        res = super(Tarifs,self).create(vals)
        return res
