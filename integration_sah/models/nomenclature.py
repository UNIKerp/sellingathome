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
            # self.test_modification_produits(rec,headers)
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
                _logger.info("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL%s",response_data_produit)
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
                _logger.info('=============================== Apres : %s',response_data_produit)
                response = requests.put(url_produit, json= response_data_produit, headers=headers)
                _logger.info("================================ Résultat final : %s",response)
            
    def test_modification_produits(self,res,headers):
        if res.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            if post_response_produit.status_code == 200:
                response_data_produit_test = post_response_produit.json()
                _logger.info('ggggggggggggggggggggggggggggggggggggggggggggggggggg%s',response_data_produit_test)
                datas =  {
                   'ProductId': 119732, 
                   'ProductRemoteId': None, 
                   'ProductReference': '0001bague', 
                   'IsDeleted': None
                }
                _logger.info('=======================jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj======== Avant : %s',response_data_produit_test)     
                response_data_produit_test['ProductRelatedProducts'] = [datas]
                response = requests.put(url_produit, json= response_data_produit, headers=headers)
                _logger.info("===================kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk============= Résultat final : %s",response)



