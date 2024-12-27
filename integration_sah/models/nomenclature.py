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
        res = super(NomenclatureSelligHome, self).create(vals)
        if res:
            self.creation_nomenclature_produits(res)
            print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
        return res
    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(NomenclatureSelligHome, self).write(vals)
        
        return rec
    
    def creation_nomenclature_produits(self,res):
        if res.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers, timeout=120)
            _logger.info("IIIIIIIIIIjjjjjjjjjjjjjjjjjjjjjjjIIIIIIIIIIIIII%s",post_response_produit.status_code)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()
                _logger.info("IIIIIIIIIIjjjjjjjjjjjjjjjjjjjjjjjIIIIIIIIIIIIII%s",response_data_produit['AttachedProducts'])
                response_data_produit['AttachedProducts'] = [ {'GroupId': 119741, 'ProductId': 119708, 'ProductRemoteId': None, 'ProductCombinationId': 0, 'Quantity': 2, 'DisplayOrder': 1, 'Deleted': True } ]
       
                _logger.info('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP%s',response_data_produit['AttachedProducts'])

            
                url_produit_modif = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
                # try:
                response = requests.put(url_produit_modif, json= response_data_produit, headers=headers)
                _logger.info("Statut de la réponse : %s, Contenu : %s", response.status_code, response.text)
                # if response.status_code != 200:
                #     raise Exception("Erreur lors de la modification du produit : %s" % response.text)
                # except requests.exceptions.RequestException as e:
                #     _logger.error("Erreur lors de la requête PUT : %s", str(e))
                #     raise
                # return product


