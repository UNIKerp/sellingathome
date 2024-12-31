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
            self.creation_des_api_nsene(rec)
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
                    for line in res.bom_line_ids:
                        if line.product_id:
                            if  line.product_id.product_tmpl_id and  line.product_id.product_tmpl_id.produit_sah_id:
                                datas =  {
                                    "GroupId": res.product_tmpl_id.produit_sah_id,
                                    "ProductId": line.product_id.product_tmpl_id.produit_sah_id,
                                    'ProductRemoteId': None,
                                    'ProductCombinationId': 0,
                                    'Quantity': line.product_qty,
                                    'DisplayOrder': 1,
                                    'Deleted': True
                                }
                                liste_composant.append(datas)
                _logger.info('=============================== Avant : %s',response_data_produit)     
                response_data_produit['AttachedProducts'] = liste_composant
                _logger.info('===============================j Apres : %s',response_data_produit)
                response = requests.put(url_produit, json= response_data_produit, headers=headers)
                _logger.info("================================d Résultat final : %s",response)
    def creation_des_api_nsene(self,rec):
        if rec.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{rec.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()
                datas = {
                    'ProductId': 119741, 
                    'ProductRemoteId': None, 
                    'ProductReference': '00009', 
                    'IsDeleted': None
                }
                response_data_produit['ProductRelatedProducts'] = [datas]
                _logger.info('===============================j Apres : %s',response_data_produit)
                response = requests.put(url_produit, json= response_data_produit, headers=headers)
                _logger.info("================================dd Résultat final : %s",response)

                


