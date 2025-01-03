# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class ProduitPriceList(models.Model):
    _inherit = "product.pricelist"

    price_list_sah_id = fields.Char(string='Id Prix SAH',copy=False,)


class Tarifs(models.Model):

    _inherit = "product.pricelist.item"

    price_sah_id = fields.Char(string="ID Prix SAH")

    # redéfintion de la fonction _default_pricelist_id
    def _default_pricelist_id(self):
        active_id = self.env.context.get('active_id')
        product_id = self.env['product.template'].search([('id','=',active_id)])
        if product_id and product_id.default_list_price:
            return product_id.default_list_price
        else:
            return self.env['product.pricelist'].search([
                '|', ('company_id', '=', False),
                ('company_id', '=', self.env.company.id)], limit=1)

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        index=True, ondelete='cascade',
        required=True,
        default=_default_pricelist_id)

    @api.model
    def create(self, vals):
        res = super(Tarifs, self).create(vals)
        headers = self.env['authentication.sah'].establish_connection()

        if res.product_tmpl_id and res.pricelist_id:
            price_list_id = str(res.pricelist_id.price_list_sah_id)
            url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
            product_id = res.product_tmpl_id
            start_date = res.date_start.isoformat(timespec='microseconds') + "+02:00" if res.date_start else False
            end_date = res.date_end.isoformat(timespec='microseconds') + "+02:00" if res.date_end else False

            # Calcul du prix TTC en ajoutant la taxe
            price_incl_tax = product_id.list_price * (1 + (product_id.taxes_id.amount / 100)) if product_id.taxes_id else product_id.list_price

            values = {
                "ProductId": product_id.produit_sah_id,
                "TwoLetterISOCode": "FR",
                "PriceExclTax": product_id.list_price,
                "PriceInclTax": price_incl_tax,
                "ProductCost": product_id.standard_price,
                "RolePrices": [
                    {
                        "CustomerRoleId": 1,
                        "Quantity": int(elt.min_quantity) if elt.min_quantity else 1,
                        "NewPriceExclTax": elt.fixed_price if elt.fixed_price else 0.0,
                        "StartDate": start_date if start_date else None,
                        "EndDate": end_date if end_date else None,
                    }
                    for elt in res.pricelist_id.item_ids
                    
                ]
            }
            response = requests.put(url, json=values, headers=headers)
            if response.status_code == 200:
                _logger.info('=============================== %s', response.json())
            else:
                _logger.info('=============================== Error Response: %s', response.text)

        return res


    def write(self, vals):
        res = super(Tarifs, self).write(vals)
        if vals:
            headers = self.env['authentication.sah'].establish_connection()
            price_list_id = str(self.pricelist_id.price_list_sah_id)
            url = f'https://demoapi.sellingathome.com/v1/Prices/{price_list_id}'
            product_id = self.product_tmpl_id
            price_incl_tax = product_id.list_price * (1 + (product_id.taxes_id.amount / 100)) if product_id.taxes_id else product_id.list_price
            values = {
                "ProductId": product_id.produit_sah_id,
                "TwoLetterISOCode": "FR",
                "PriceExclTax": product_id.list_price,
                "PriceInclTax": price_incl_tax,
                "ProductCost": product_id.standard_price,
                "RolePrices": [
                    {
                        "CustomerRoleId": 1,
                        "Quantity": int(elt.min_quantity) if elt.min_quantity else 1,
                        "NewPriceExclTax": elt.fixed_price if elt.fixed_price else 0.0,
                        "StartDate": elt.date_start.isoformat(timespec='microseconds') + "+02:00" if elt.date_start else False,
                        "EndDate": elt.date_end.isoformat(timespec='microseconds') + "+02:00" if elt.date_end  else False,
                    }
                    for elt in self.pricelist_id.item_ids
                ]
            }
            _logger.info('===================================================%s',self.pricelist_id)
            response = requests.put(url, headers=headers, json=values)
            if response.status_code == 200:
                _logger.info('Données modifiées avec succès dans l\'API : %s', response.json())
            else:
                _logger.error('Erreur lors de la modification dans l\'API : %s', response.text)
        return res
