from odoo import models, api, fields,_
import requests
import json
from datetime import date
from datetime import datetime
import pytz
import logging
_logger = logging.getLogger(__name__)

class NomenclatureSelligHome(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def create(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(NomenclatureSelligHome, self).create(vals)
        if rec:
            self.creation_nomenclature_produits(rec,headers)
        return rec
    
    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(NomenclatureSelligHome, self).write(vals)
        self.creation_nomenclature_produits(self,headers)
        return rec
    
    def creation_nomenclature_produits(self,res,headers):
        if res.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()
                if res.bom_line_ids:
                    liste_composant = []
                    i = 1
                    for line in res.bom_line_ids:
                        if line.product_id and line.product_id.product_tmpl_id.produit_sah_id:
                            i = i+1
                            attachproducts = {
                                "ProductId": line.product_id.product_tmpl_id.produit_sah_id,  
                                "Quantity": line.product_qty,
                                "DisplayOrder": i,
                                "Deleted": True,
                            }
                            liste_composant.append(attachproducts)

                    datas = {

                            "Prices": [
                                    {
                                        "Id": line.product_id.product_tmpl_id.produit_sah_id,
                                        "BrandTaxRate": 2.1,
                                        "BrandTaxName": line.product_id.product_tmpl_id.name,
                                        "TwoLetterISOCode": "FR",
                                        "PriceExclTax": line.product_id.product_tmpl_id.list_price,
                                        "PriceInclTax": line.product_id.product_tmpl_id.list_price * (1 + line.product_id.product_tmpl_id.taxes_id.amount / 100),
                                        "ProductCost": line.product_id.product_tmpl_id.standard_price,
                                        "EcoTax": 8.1
                                    }
                            ],
                            "AttachedProducts": liste_composant,
                    }
                    response = requests.put(url_produit, json=datas, headers=headers)
                    _logger.info("================================d Résultat final : %s",response.json())

                


