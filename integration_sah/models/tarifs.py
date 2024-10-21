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

    @api.model
    def create(self,vals):
        res = super(Tarifs,self).create(vals)
        headers = self.env['authentication.sah'].establish_connection()
        if res.product_tmpl_id and res.pricelist_id:
            price_list_id = str(res.pricelist_id.price_list_sah_id)
            _logger.info('===============price_list_id================ %s',price_list_id)
            url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
            product_id =  res.product_tmpl_id
            _logger.info('=============================== %s',product_id.produit_sah_id)
            new_price_excl_tax = 200.0  # ou res.product_tmpl_id.list_price par exemple
            new_price_incl_tax = 200.0  # ou calculer en ajoutant la taxe
            
            # Utiliser la date actuelle pour StartDate et EndDate, ou personnaliser
            start_date = datetime.now().isoformat()
            end_date = datetime.now().isoformat()

            values = {
                "ProductId": product_id.produit_sah_id,
                "TwoLetterISOCode": "FR",
                "RolePrices": [
                    {
                        "CustomerRoleId": 1,
                        "Quantity": 2,
                        "NewPriceExclTax": new_price_excl_tax,
                        "NewPriceInclTax": new_price_incl_tax,
                        "StartDate": start_date,
                        "EndDate": end_date,
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
