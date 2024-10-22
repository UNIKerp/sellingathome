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
    def create(self, vals):
        res = super(Tarifs, self).create(vals)
        headers = self.env['authentication.sah'].establish_connection()

        if res.product_tmpl_id and res.pricelist_id:
            price_list_id = str(res.pricelist_id.price_list_sah_id)
            url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
            product_id = res.product_tmpl_id
            
            # Log des informations pour déboguer
            _logger.info('============================= ProductId: %s, Date Start: %s, Date End: %s', product_id.produit_sah_id, res.date_start, res.date_end)
            
            start_date = res.date_start.isoformat(timespec='microseconds') + "+02:00" if res.date_start else False
            end_date = res.date_end.isoformat(timespec='microseconds') + "+02:00" if res.date_end else False

            # Calcul du prix TTC en ajoutant la taxe
            price_incl_tax = product_id.list_price * (1 + (product_id.taxes_id.amount / 100)) if product_id.taxes_id else product_id.list_price

            values = {
                "ProductId": product_id.produit_sah_id,
                "TwoLetterISOCode": "FR",
                "PriceExclTax": 1.1,
                "PriceInclTax": 1.1,
                "ProductCost": 1.1,
                "RolePrices": [
                    {
                        "CustomerRoleId": 1,
                        "Quantity": int(res.min_quantity) if res.min_quantity else 1,
                        "NewPriceExclTax": res.fixed_price if res.fixed_price else 0.0,
                        "StartDate": start_date if start_date else False,
                        "EndDate": end_date if end_date else False,
                    },
                ]
            }

            response = requests.put(url, json=values, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                res.price_sah_id = data['RolePrices'][0]['Id']
                _logger.info('=============================== %s', data)
            else:
                _logger.info('=============================== Error Response: %s', response.text)

        return res



    """def write(self,vals):
        headers = self.env['authentication.sah'].establish_connection()
        price_list_id = str(self.pricelist_id.price_list_sah_id)
        url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
        product_id =  self.product_tmpl_id
        start_date = self.date_start.isoformat(timespec='microseconds') + "+02:00"
        end_date = self.date_end.isoformat(timespec='microseconds') + "+02:00"

        values = {
            "ProductId": product_id.produit_sah_id,
            "TwoLetterISOCode": "FR",
            "PriceExclTax": product_id.list_price,
            "PriceInclTax": product_id.list_price * (product_id.taxes_id.amount/100),
            "ProductCost": product_id.standard_price,
            "RolePrices": [
                {
                "CustomerRoleId": 1,
                "Quantity": int(self.min_quantity),
                "NewPriceExclTax": self.fixed_price ,
                #"NewPriceInclTax": self.fixed_price * (product_id.taxes_id.amount/100),
                "StartDate": start_date or False,
                "EndDate": end_date or False,
                # "CombinationId": 1,
                },
            ]   
        }
        response  = requests.put(url, headers=headers, json=values)
        if response.status_code == 200:
            _logger.info('Données modifiées Tarifs %s',response.json())
        res = super(Tarifs,self).write(vals)
        return res"""
