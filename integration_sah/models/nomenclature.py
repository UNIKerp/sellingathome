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
    
    def creation_nomenclature_produits(self,product_id,headers):
        if product_id.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{product_id.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers, timeout=120)
            _logger.info("IIIIIIIIIIjjjjjjjjjjjjjjjjjjjjjjjIIIIIIIIIIIIII%s",post_response_produit.status_code)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()
                _logger.info("IIIIIIIIIIjjjjjjjjjjjjjjjjjjjjjjjIIIIIIIIIIIIII%s",response_data_produit['AttachedProducts'])
                # [{'GroupId': 120909, 'ProductId': 119741, 'ProductRemoteId': None, 'ProductCombinationId': 0, 'Quantity': 1, 'DisplayOrder': 1, 'Deleted': False}]
                datas = [
                        {
                        # "GroupId": 1,
                        "ProductId": 120909,
                        # "ProductRemoteId": "sample string 3",
                        # "ProductCombinationId": 4,
                        "Quantity": 2,
                        # "DisplayOrder": 1,
                        # "Deleted": True
                        }
                ]
                _logger.info('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb!! %s',response_data_produit)
                response_data_produit['AttachedProducts'] = datas
                _logger.info('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb %s',response_data_produit)
               
                response = requests.put(url_produit, json= response_data_produit, headers=headers)
                _logger.info("Statut de la réponse : %s, Contenu : %s", response.status_code, response.text)
                if response.status_code != 200:
                   _logger.info('Okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                


