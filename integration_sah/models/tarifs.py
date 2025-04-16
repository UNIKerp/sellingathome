# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime
from dateutil import parser

class ProduitPriceList(models.Model):
    _inherit = "product.pricelist"

    price_list_sah_id = fields.Char(string='Id Prix SAH',copy=False,)
    country_id = fields.Many2one('res.country', string="Pays")


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
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(Tarifs, self).create(vals)
        if rec:
            job_kwargs = {
            'description': 'Ajout des RolePrices du produit de Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).creation_role_produits(rec, headers)
        return rec
   
    def write(self,vals):
        result = super(Tarifs, self).write(vals)
        if self.price_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            job_kwargs = {
                'description': 'Mise a jour desRolePricest de Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).mise_role_prices(self, headers)
        return result



    def mise_role_prices(self,objet, headers):
        if objet.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{objet.product_tmpl_id.produit_sah_id}"
            updated_role_prices = []
            if objet.pricelist_id and objet.pricelist_id.item_ids:
                for role in objet.pricelist_id.item_ids:
                    if objet.product_tmpl_id == role.product_tmpl_id:
                        new_role = {
                                "CustomerRoleId": 1,
                                "Quantity": int(role.min_quantity),
                                "NewPriceExclTax": role.fixed_price,
                                "NewPriceInclTax": role.fixed_price * (1 + role.product_tmpl_id.taxes_id.amount / 100) if role.fixed_price else 0.0,
                                "StartDate": role.date_start.isoformat(timespec='microseconds') + "+02:00" if role.date_start else None,
                                "EndDate": role.date_end.isoformat(timespec='microseconds') + "+02:00" if role.date_end else None,
                        }
                        updated_role_prices = updated_role_prices + [new_role]
                datas = {
                    "Prices": [
                        {
                            "Id": objet.product_tmpl_id.produit_sah_id,
                            "BrandTaxRate": 2.1,
                            "BrandTaxName": objet.product_tmpl_id.name,
                            "TwoLetterISOCode": "FR",
                            "PriceExclTax": objet.product_tmpl_id.list_price,
                            "PriceInclTax": objet.product_tmpl_id.list_price * (1 + objet.product_tmpl_id.taxes_id.amount / 100),
                            "ProductCost": objet.product_tmpl_id.standard_price,
                            "EcoTax": 8.1,
                            "RolePrices": updated_role_prices,
                        }
                    ]
                }
                response = requests.put(url_produit, json=datas, headers=headers)

   
                 
    
    def creation_role_produits(self, rec, headers):
        if rec.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{rec.product_tmpl_id.produit_sah_id}"
            
            response = requests.get(url_produit, headers=headers)
            if response.status_code == 200:
                existing_data = response.json()
                existing_role_prices = existing_data.get("Prices", [{}])[0].get("RolePrices", [])
                
                new_role = {
                    "CustomerRoleId": 1,
                    "Quantity": int(rec.min_quantity) if rec.min_quantity else 1,
                    "NewPriceExclTax": rec.fixed_price if rec.fixed_price else 0.0,
                    "NewPriceInclTax": rec.fixed_price * (1 + rec.product_tmpl_id.taxes_id.amount / 100) if rec.fixed_price else 0.0,
                    "StartDate": rec.date_start.isoformat(timespec='microseconds') + "+02:00" if rec.date_start else None,
                    "EndDate": rec.date_end.isoformat(timespec='microseconds') + "+02:00" if rec.date_end else None,
                }
                
                updated_role_prices = existing_role_prices + [new_role]

                datas = {
                    "Prices": [
                        {
                            "Id": rec.product_tmpl_id.produit_sah_id,
                            "BrandTaxRate": 2.1,
                            "BrandTaxName": rec.product_tmpl_id.name,
                            "TwoLetterISOCode": "FR",
                            "PriceExclTax": rec.product_tmpl_id.list_price,
                            "PriceInclTax": rec.product_tmpl_id.list_price * (1 + rec.product_tmpl_id.taxes_id.amount / 100),
                            "ProductCost": rec.product_tmpl_id.standard_price,
                            "EcoTax": 8.1,
                            "RolePrices": updated_role_prices,
                        }
                    ]
                }

                response = requests.put(url_produit, json=datas, headers=headers)
                if response.status_code == 200:
                    datas = response.json()
                    rolesprices = datas['Prices']
                    max_role_price = max(rolesprices[0]['RolePrices'], key=lambda x: x['Id'])
                    id_max = max_role_price['Id']
                    rec.price_sah_id = id_max
                    _logger.info("Creation de la liste de prix avec id  %s", id_max)
                else:
                    _logger.error(f"Erreur lors de la mise à jour du produit sur SAH : {response.status_code}, {response.text}")
            else:
                _logger.error(f"Erreur lors de la récupération du produit sur SAH : {response.status_code}, {response.text}")


                 

                

