from odoo import models, api, fields,_
import requests
import json
from datetime import date
from datetime import datetime
import pytz
import logging
import copy
_logger = logging.getLogger(__name__)

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
            # self.env['product.template'].with_delay(**job_kwargs).creation_nomenclature_produits(rec.product_tmpl_id, headers)
            self.with_delay(**job_kwargs).creation_nomenclature_produits(rec, headers)
        return rec
    
    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(NomenclatureSelligHome, self).write(vals)
        job_kwargs = {
            'description': 'Mise a jour des Nommenclatures du produit de Odoo vers SAH',
        }
        # self.env['product.template'].with_delay(**job_kwargs).update_produit_dans_sah(self.product_tmpl_id, headers)
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
                                    "GroupId": 1,
                                    "ProductId": line.product_id.produit_sah_id or 0,
                                    "ProductRemoteId": str(line.product_id.id),
                                    "ProductCombinationId": line.product_id.produit_sah_id or 0,
                                    "Quantity": int(line.product_qty),
                                    "DisplayOrder": idx + 1,
                                    "Deleted": False,
                                } for idx, line in enumerate(res.bom_line_ids)

                            ]
                           
                    }
                    response = requests.put(url_produit, json=datas, headers=headers)

                    if response.status_code == 200:
                        _logger.info("Product nomenclature updated successfully.")
                    else:
                        _logger.error(
                            f"Failed to update product nomenclature. Status code: {response.status_code}, Response: {response.text}"
                        )
                else:
                    _logger.warning("No BOM lines found to attach products.")
                 

                


