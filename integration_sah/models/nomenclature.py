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

    def creation_nomenclature_produits(self, res, headers):
        if res.product_tmpl_id.produit_sah_id:
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()

                # 🔹 Récupérer les nomenclatures du produit
                nomenclatures = self.env['mrp.bom'].search([('product_tmpl_id', '=', res.product_tmpl_id.id)])

                aggregated_products = {}
                product_components = {}

                for bom in nomenclatures:
                    component_id = bom.id  # Identifiant unique pour le composant

                    product_components[component_id] = {
                        "Id": 1060,
                        "Name": bom.product_tmpl_id.name,
                        "ProductId": res.product_tmpl_id.produit_sah_id,  # ID du produit parent
                        "MaxQuantity": 0,
                        "Deleted": False,
                        "RemoteReference": None,
                        "ProductComponentLangs": [{"ISOValue": "fr"}],
                        "ProductComponentProducts": []
                    }

                    for line in bom.bom_line_ids:
                        product_id = line.product_id.produit_sah_id or 0
                        if product_id:
                            if product_id in aggregated_products:
                                aggregated_products[product_id]['Quantity'] += int(line.product_qty)
                            else:
                                aggregated_products[product_id] = {
                                    "ProductId": product_id,
                                    "Quantity": int(line.product_qty),
                                    "DisplayOrder": len(aggregated_products) + 1,
                                    "Deleted": False
                                }

                            # Ajouter ce produit dans `ProductComponentProducts`
                            product_components[component_id]["ProductComponentProducts"].append({
                                "ProductId": product_id,
                                "ProductRemoteId": None,
                                "ProductCombinationId": None,
                                "ProductCombinationBarCode": None,
                                "Quantity": int(line.product_qty),
                                "DisplayOrder": len(product_components[component_id]["ProductComponentProducts"]) + 1,
                                "Deleted": False
                            })

                attached_products = list(aggregated_products.values())
                product_components_list = list(product_components.values())  # Convertir en liste

                # 🔹 Préparer les données pour la requête API
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
                    # "AttachedProducts": attached_products,
                    "ProductComponents": product_components_list
                }

                # 🔹 Envoyer la requête PUT
                response = requests.put(url_produit, json=datas, headers=headers)
                _logger.info(response.status_code, response.json())

    
    """def creation_nomenclature_produits(self,res,headers):
        if res.product_tmpl_id.produit_sah_id :
            headers = self.env['authentication.sah'].establish_connection()
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{res.product_tmpl_id.produit_sah_id}"
            post_response_produit = requests.get(url_produit, headers=headers)
            if post_response_produit.status_code == 200:
                response_data_produit = post_response_produit.json()


                nomenclatures = self.env['mrp.bom'].search([('product_tmpl_id', '=', res.product_tmpl_id.id)])

                aggregated_products = {}

                for bom in nomenclatures:
                    for line in bom.bom_line_ids:
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

                attached_products = list(aggregated_products.values())
                
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
                        "AttachedProducts": attached_products
                        
                }
                response = requests.put(url_produit, json=datas, headers=headers)"""



  