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
            self.creation_nomenclature_produits()
        return res
    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(NomenclatureSelligHome, self).write(vals)
        
        return rec
    
    def creation_nomenclature_produits(self):
        headers = self.env['authentication.sah'].establish_connection()
        url_produit = "https://demoapi.sellingathome.com/v1/Products"
        
        post_response_produit = requests.get(url_produit, headers=headers, timeout=120)
        
        if post_response_produit.status_code == 200:
            response_data_produit = post_response_produit.json()
            print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",response_data_produit)
            data = {
                "Name": "10% sur votre commande",
                "ProductId": 119740,
                "MaxQuantity": 1,
                "Deleted": true,
                "RemoteReference": "sample string 3",
            }
            response = requests.post(url_produit, json=data, headers=headers)

            if response.status_code != 200:
                raise Exception("Erreur lors de la création du produit sur SellingAtHome: %s" % response.text)

            return product


