# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class ProduitPriceList(models.Model):
    _inherit = "product.pricelist"

    price_list_sah_id = fields.Char(string='Id Prix SAH')


class Tarifs(models.Model):

    _inherit = "product.pricelist.item"

    price_sah_id = fields.Char(string="ID Prix SAH")

    @api.model_create_multi
    def create(self,vals):
        res = super(Tarifs,self).create(vals)
        headers = self.env['authentication.sah'].establish_connection()
        if res.product_tmpl_id and res.pricelist_id:
            price_list_id = str(res.pricelist_id.price_list_sah_id)
            url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
            product_id =  res.product_tmpl_id
            _logger.info('============================= %s',res.date_start)
            date_start = res.date_start
            dt = datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
            date_start = dt.isoformat(timespec='microseconds') + "+02:00"

            values ={
                "ProductId": product_id.produit_sah_id,
                "TwoLetterISOCode": "FR",
                "PriceExclTax": product_id.list_price,
                "PriceInclTax": product_id.list_price * (product_id.taxes_id.amount/100),
                "ProductCost": product_id.standard_price,
                "RolePrices": [
                    {
                    "CustomerRoleId": 1,
                    "Quantity": int(res.min_quantity),
                    "NewPriceExclTax": res.fixed_price ,
                    #"NewPriceInclTax": res.fixed_price * (product_id.taxes_id.amount/100),
                    "StartDate": date_start or False,
                    # "EndDate": res.date_end,
                    # "CombinationId": 1
                    },
                ]   
            }
            response = requests.put(url, json=values, headers=headers)
            if response.status_code == 200:
                data = response.json()
                res.price_sah_id =  data['RolePrices'][0]['Id']
                _logger.info('=============================== %s ==== %s', res.price_sah_id,data )
            else:
                _logger.info('=============================== %s',response.text)
        
        return res


    """def write(self,vals):
        price_list_id = str(self.pricelist_id.price_list_sah_id)
        url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
        values ={
                "ProductId": product_id.produit_sah_id,
                "BrandTaxRate": 2.1,
                "BrandTaxName": "sample string 3",
                "TwoLetterISOCode": "FR",
                "PriceExclTax": 1.1,
                "PriceInclTax": 1.1,
                "ProductCost": 5.1,
                "EcoTax": 6.1,
                "RolePrices": [
                    {
                    # "Id": 1,
                    "CustomerRoleId": 1,
                    "Quantity": 2,
                    "NewPriceExclTax": 1.1,
                    "NewPriceInclTax": 1.1,
                    "StartDate": "2024-10-21T18:04:14.6234241+02:00",
                    "EndDate": "2024-10-21T18:04:14.6234241+02:00",
                    "CombinationId": 1
                    },
                ]   
            }
        requests.put(url, headers=headers, json=values)
        res = super(Tarifs,self).write(vals)
        return res"""
