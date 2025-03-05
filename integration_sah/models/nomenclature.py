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
        rec = super(NomenclatureSelligHome, self).create(vals)
        if rec.type == 'phantom':
            job_kwargs = {
            'description': 'Ajout des Nommenclatures du produit de Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).creation_nomenclature_produits(rec)
        return rec
    
    def write(self, vals):
        rec = super(NomenclatureSelligHome, self).write(vals)

        if ('type' in vals and vals['type'] == 'phantom') or 'bom_line_ids' in vals:
            job_kwargs = {
                'description': 'Mise a jour des Nommenclatures du produit de Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).creation_nomenclature_produits(self)
        
        return rec

    def creation_nomenclature_produits(self,res):
        if res.product_tmpl_id.produit_sah_id :
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()
                
                aggregated_products = {}
                
                # Récupérer les anciens produits attachés s'ils existent
                old_attached_products = response_data_produit.get('AttachedProducts', [])
                
                # Ajouter les anciens produits à aggregated_products
                for old_product in old_attached_products:
                    product_id = old_product['ProductId']
                    if product_id not in aggregated_products:
                        aggregated_products[product_id] = {
                            "ProductId": product_id,
                            "Quantity": old_product['Quantity'],
                            "DisplayOrder": old_product['DisplayOrder'],
                            "Deleted": False  # Conserver l'état 'Deleted' s'il existe
                        }
                
                # Parcourir les nouvelles lignes de produits
                for line in res.bom_line_ids:
                    product_id = line.product_id.produit_sah_id or 0
                    if product_id:
                        if product_id in aggregated_products:
                            aggregated_products[product_id]['Quantity'] += int(line.product_qty)
                        else:
                            aggregated_products[product_id] = {
                                "ProductId": product_id,
                                "Quantity": int(line.product_qty),
                                "DisplayOrder": len(aggregated_products) + 1,
                                "Deleted": False,
                            }
            
                # Convertir le dictionnaire en liste pour AttachedProducts
                attached_products = list(aggregated_products.values())
                # Préparer les données à envoyer
                datas = {
                    "Prices": response_data_produit['Prices'],
                    "AttachedProducts": attached_products
                }
                
                # Envoyer la requête PUT
                response = requests.put(url_produit, json=datas, headers=headers)

  