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

                nomenclatures = self.env['mrp.bom'].search([('product_tmpl_id', '=', res.product_tmpl_id.id)])

                aggregated_products = {}
                kit_variante = {}

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

                                kit_variante[product_id] = {
                                    "ProductId": product_id,
                                    "Quantity": int(line.product_qty),
                                    "DisplayOrder": len(kit_variante) + 1,
                                    "Deleted": False,
                                }

                attached_products = list(aggregated_products.values())
                produit_variantes = list(kit_variante.values())

                # Récupération du taux de taxe (évite une erreur si `taxes_id` est vide)
                tax_rate = res.product_tmpl_id.taxes_id.amount if res.product_tmpl_id.taxes_id else 0

                # Structure de base des données envoyées
                datas = {
                    "Prices": [
                        {
                            "Id": res.product_tmpl_id.produit_sah_id,
                            "BrandTaxRate": 2.1,
                            "BrandTaxName": res.product_tmpl_id.name,
                            "TwoLetterISOCode": "FR",
                            "PriceExclTax": res.product_tmpl_id.list_price,
                            "PriceInclTax": res.product_tmpl_id.list_price * (1 + tax_rate / 100),
                            "ProductCost": res.product_tmpl_id.standard_price,
                            "EcoTax": 8.1
                        }
                    ]
                }

                # Ajout des éléments en fonction du type de produit
                if res.product_tmpl_id.type == 'normal':
                    datas["AttachedProducts"] = attached_products
                elif res.product_tmpl_id.type == 'phantom':
                    datas["ProductComponentProducts"] = produit_variantes

                # Envoi de la mise à jour vers SellingAtHome
                response = requests.put(url_produit, json=datas, headers=headers)

                return response
    
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



  