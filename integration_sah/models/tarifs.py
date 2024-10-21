# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)

class ProduitPriceList(models.Model):
    _inherit = "product.pricelist"

    price_list_sah_id = fields.Char(string='Id Prix SAH')


class Tarifs(models.Model):

    _inherit = "product.pricelist.item"

    price_sah_id = fields.Char(string="ID Prix SAH")

    @api.model
    def create(self,vals):
        res = super(Tarifs,self).create(vals)
        headers = self.env['authentication.sah'].establish_connection()
        if res.product_tmpl_id and res.pricelist_id:
            price_list_id = str(res.pricelist_id.price_list_sah_id)
            url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
            product_id =  res.product_tmpl_id
            _logger.info('=============================== %s',product_id.produit_sah_id)
            values = {
                "ProductId": product_id.produit_sah_id,
                "TwoLetterISOCode": "FR",
                "RolePrices": [
                    {
                    "CustomerRoleId": 1,
                    "Quantity": 2,
                    "NewPriceExclTax":200.0,
                    "NewPriceInclTax": 200.0,
                    "StartDate": "2024-10-21T18:04:14.6234241+02:00",
                    "EndDate": "2024-10-21T18:04:14.6234241+02:00",
                    }
                ]
            }
            response = requests.put(url, json=values, headers=headers)
            if response.status_code == 200:
                data = response.json()
                _logger.info('=============================== %s',data)
                #res.price_sah_id =  str(data.get('Id'))
            else:
                _logger.info('=============================== %s',response.text)
        
        return res


    """def write(self,vals):
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
        return res"""
