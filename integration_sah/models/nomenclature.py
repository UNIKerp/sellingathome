from odoo import models, api, fields,_
import requests
import json
from datetime import date
from datetime import datetime
import os
import base64
from odoo.tools import config
import pytz
import logging
_logger = logging.getLogger(__name__)
import json
from PIL import Image
from io import BytesIO
from dateutil import parser

class NomenclatureSelligHome(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def create(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(NomenclatureSelligHome, self).create(vals)
        if rec:
            job_kwargs = {
            'description': 'Ajout des Nommenclatures du produit de Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).creation_nomenclature_produits(rec, headers)
        return rec
    
    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(NomenclatureSelligHome, self).write(vals)
        job_kwargs = {
            'description': 'Mise a jour des Nommenclatures du produit de Odoo vers SAH',
        }
        self.with_delay(**job_kwargs).creation_nomenclature_produits(self, headers)
        return rec
    
    def creation_nomenclature_produits(self,res,headers):
        if res.product_tmpl_id.produit_sah_id :
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()
                if res.bom_line_ids:
                    datas = {

                            "Prices": [
                                    {
                                        "Id": res.product_tmpl_id.produit_sah_id,
                                        "BrandTaxRate": 2.1,
                                        "BrandTaxName": res.product_tmpl_id.name,
                                        "TwoLetterISOCode": "FR",
                                        "PriceExclTax": res.product_tmpl_id.list_price,
                                        "PriceInclTax": res.product_tmpl_id.list_price * (1 + res.product_tmpl_id.taxes_id.amount / 100),
                                        "ProductCost": res.product_tmpl_id.standard_price,
                                        "EcoTax": 8.1
                                    }
                            ],
                            "AttachedProducts": [
                                {
                                    "ProductId": line.product_id.produit_sah_id or 0,
                                    "Quantity": int(line.product_qty),
                                    "DisplayOrder": idx + 1,
                                    "Deleted": False,
                                } for idx, line in enumerate(res.bom_line_ids)

                            ]
                           
                    }
                    response = requests.put(url_produit, json=datas, headers=headers)


class RolePricesSelligHome(models.Model):
    _inherit = "product.pricelist.item"


    @api.model
    def create(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(RolePricesSelligHome, self).create(vals)
        if rec:
            job_kwargs = {
            'description': 'Ajout des Nommenclatures du produit de Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).creation_role_produits(rec, headers)
        return rec
    
    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(RolePricesSelligHome, self).write(vals)
        job_kwargs = {
            'description': 'Mise a jour des Nommenclatures du produit de Odoo vers SAH',
        }
        self.with_delay(**job_kwargs).creation_role_produits(self, headers)
        return rec
    
    def creation_role_produits(self,rec,headers):
        if rec.product_tmpl_id.produit_sah_id :
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{rec.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()
               
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
                            "EcoTax": 8.1
                            "RolePrices": [
                                {
                                    "CustomerRoleId": 1,
                                    "Quantity": int(rec.min_quantity) if rec.min_quantity else 1,
                                    "NewPriceExclTax": rec.fixed_price if rec.fixed_price else 0.0,
                                    "StartDate": rec.date_start.isoformat(timespec='microseconds') + "+02:00" if rec.date_start else None,
                                    "EndDate": rec.date_end.isoformat(timespec='microseconds') + "+02:00" if rec.date_end else None,
                                }
                            ]
                        }
                    ]
                }
                response = requests.put(url_produit, json=datas, headers=headers)

                 

                


