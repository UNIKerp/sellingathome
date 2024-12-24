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

from PIL import Image
from io import BytesIO

class ProduitSelligHome(models.Model):
    _inherit = "product.template"

    produit_sah_id = fields.Integer("ID produit SAH",copy=False, help="l'ID du produit dans SAH")
    default_list_price = fields.Many2one('product.pricelist', string='Liste de prix par défaut')
    long_sah = fields.Float("Longueur Produit SAH", help="Longueur du produit dans SAH")
    haut_sah = fields.Float("Hauteur Produit SAH", help="Hauteur du produit dans SAH")
    unitcapacity = fields.Char("Capacité Unitaire SAH", help="Capacité de l'unitaire du produit dans SAH")
    availableOnHostMinisites = fields.Boolean("Disponible Minisites hôtes SAH", help="Disponible de minisites hôtes dans SAH")
    discountEndDate = fields.Datetime("Date Fin SAH", help="Date de fin dans SAH")
    discountStartDate = fields.Datetime("Date debut SAH", help="Date de début dans SAH")
    discountBadgeIsActive = fields.Boolean("BadgeEst Actif", help="Le badge de réduction est actif dans SAH")

    _sql_constraints = [
        ('produit_sah_id_uniq', 'unique (produit_sah_id)', "ID du produit SAH exists deja !"), ]

    # création des articles venant de l'api dans odoo
    def create_article_sah_odoo(self):
        headers = self.env['authentication.sah'].establish_connection()
        url_produit = "https://demoapi.sellingathome.com/v1/Products"
        
        post_response_produit = requests.get(url_produit, headers=headers, timeout=120)
        
        if post_response_produit.status_code == 200:
            response_data_produit = post_response_produit.json()
            _logger.info("Produits récupérés depuis l'API SAH")
            
            # Parcourir la liste des produits de l'API
            for produit_api in response_data_produit:
                sah_id = produit_api['Id']
                reference = produit_api['Reference']
                name = produit_api['ProductLangs'][0]['Name'] if produit_api.get('ProductLangs') else 'Sans nom'
                description = produit_api['ProductLangs'][0]['Description'] if produit_api.get('ProductLangs') else ''
                price = produit_api['Prices'][0]['PriceExclTax'] if produit_api.get('Prices') else 0.0
                barcode = produit_api.get('Barcode', False)
                weight = produit_api.get('Weight', 0.0)
                type_sah = produit_api.get('InventoryMethod')

                existing_product = self.env['product.template'].search([('produit_sah_id', '=', sah_id)], limit=1)
                
                if not existing_product:
                    if not barcode:
                        barcode = False

                    if barcode:
                        product_with_same_barcode = self.env['product.template'].search([('barcode', '=', barcode)], limit=1)
                        if product_with_same_barcode:
                            _logger.warning(f"Code-barres {barcode} déjà attribué au produit {product_with_same_barcode.name}. Ignoré pour {name}.")
                            barcode = False

                    # Créer le produit dans Odoo
                    new_product = self.env['product.template'].create({
                        'name': name,
                        'default_code': reference,
                        'list_price': price,
                        'description_sale': description,
                        'barcode': barcode,
                        'weight': weight,
                        'produit_sah_id': sah_id,
                        'is_storable' : True if type_sah == 1 else False
                    })

                    # Créer un élément de liste de prix associé
                    # price_list = self.env['product.pricelist'].search([('price_list_sah_id', '=', None)], limit=1)
                    # if price_list:
                    #     price_list = self.env['product.pricelist'].create({
                    #         'name': 'SAH Liste de Prix',
                    #         'currency_id': self.env.user.company_id.currency_id.id
                    #     })
                    
                    # self.env['product.pricelist.item'].create({
                    #     'pricelist_id': price_list.id,
                    #     'product_tmpl_id': new_product.id,
                    #     'fixed_price': price,
                    # })
                    # _logger.info(f"Liste de prix ajoutée pour le produit : {name} (ID SAH: {sah_id})")

                    _logger.info(f"Produit créé dans Odoo : {name} (ID SAH: {sah_id})")
                else:
                    _logger.info(f"Produit déjà existant dans Odoo : {name} (ID SAH: {sah_id})")
        else:
            _logger.error(f"Erreur lors de la récupération des produits depuis l'API SAH : {post_response_produit.status_code}")

    def update_aticle_sah(self):
        headers = self.env['authentication.sah'].establish_connection()
        url_produit = "https://demoapi.sellingathome.com/v1/Products"
        get_response_produit = requests.get(url_produit, headers=headers)
        if get_response_produit.status_code == 200:
            response_data_produit = get_response_produit.json()
            for identifiant in response_data_produit:
                identite_api = identifiant['Id']

                product_odoo = self.env['product.template'].search([('produit_sah_id', '=', identite_api)], limit=1)
                if product_odoo:
                    self.update_produit_dans_sah(product_odoo, headers)
                else:
                    _logger.warning(f"Produit avec ID {identite_api} non trouvé dans Odoo, création possible.")

        else:
            _logger.error(f"Erreur lors de la récupération des produits depuis l'API SAH : {get_response_produit.status_code}")

    # Met à jour les informations d'un produit sur l'API SAH avec les données d'Odoo
    def update_produit_dans_sah(self, product, headers):
        _logger.info("======================= Debut de mise à jour de l'Article")
        id_categ = ''
        # Si le produit a une catégorie, récupérer ou créer la catégorie dans l'API
        if product.categ_id:
            url_categ = "https://demoapi.sellingathome.com/v1/Categories"
            post_response_categ = requests.get(url_categ, headers=headers)
            
            if post_response_categ.status_code == 200:
                response_data_categ = post_response_categ.json()
                categ_parent = response_data_categ[0]['Id']
                j = 0
                
                # Parcourir les catégories et comparer les noms
                for c in response_data_categ:
                    CategoryLangs = c['CategoryLangs']
                    for cc in CategoryLangs:
                        nom_cat = cc['Name']
                        
                        # Remplacer res.categ_id.name par product.categ_id.name
                        if product.categ_id.name == nom_cat:
                            id_categ = c['Id']
                            j += 1
                
                # Si aucune catégorie correspondante n'est trouvée, en créer une nouvelle
                if j == 0:
                    create_category = {
                        "Reference": product.categ_id.name,
                        "ParentCategoryId": categ_parent,
                        "IsPublished": True,
                        "CategoryLangs": [
                            {
                                "Name": product.categ_id.name,
                                "Description": 'None',
                                "ISOValue": "fr",
                            },
                        ],
                    }
                    
                    post_response_categ_create = requests.post(url_categ, json=create_category, headers=headers)
                    
                    if post_response_categ_create.status_code == 200:
                        categ = post_response_categ_create.json()
                        id_categ = categ['Id']
            else:
                _logger.info(f"Erreur {post_response_categ.status_code}: {post_response_categ.text}")

        # Gestion des images du produit
        # product_photos = []
        # if product.product_template_image_ids:
        #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #     if not base_url:
        #         _logger.error("Base URL is not configured in Odoo. Check 'web.base.url' parameter.")
        #         return
            
        #     for index, image in enumerate(product.product_template_image_ids):
        #         try:
        #             # Créer une pièce jointe publique pour chaque image
        #             attachment = self.env['ir.attachment'].create({
        #                 'name': f'product_image_{product.id}.png',
        #                 'type': 'binary',
        #                 'datas': image.image_1920, 
        #                 'res_model': 'product.template',
        #                 'res_id': product.id,
        #                 'mimetype': 'image/png', 
        #                 'public': True,
        #             })

        #             # Vérifier que l'attachement est créé
        #             if attachment:
        #                 product_image_url = f'{base_url}/web/content/{attachment.id}/{attachment.name}'
        #                 product_photos.append({
        #                     "Link": product_image_url,
        #                     "ProductId": product.id,
        #                     "IsDefault": index == 0,
        #                     "DisplayOrder": index + 1
        #                 })
        #                 _logger.info(f"Image URL generated: {product_image_url}")
        #             else:
        #                 _logger.error("Failed to create attachment for product image.")
        #         except Exception as e:
        #             _logger.error(f"Error while processing product image: {e}")

        # _logger.info("######################## Product Photos ###########################")
        # _logger.info(product_photos)

        # # Si aucune image n'a été ajoutée
        # if not product_photos:
        #     _logger.warning("No product photos were generated for the product.")
        
        # Si le produit a un produit_sah_id, mettre à jour le produit dans l'API
        if product.produit_sah_id:
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{product.produit_sah_id}"
            
            # Préparer les données à envoyer à l'API (basées sur les informations dans Odoo)
            update_data = {
                "ProductType": 5,
                "Reference": product.default_code,
                "Prices": [
                    {
                        "Id": product.produit_sah_id,
                        "BrandTaxRate": 2.1,
                        "BrandTaxName": product.name,
                        "TwoLetterISOCode": "FR",
                        "PriceExclTax": product.list_price,
                        "PriceInclTax": product.list_price * (1 + product.taxes_id.amount / 100),
                        "ProductCost": product.standard_price,
                        "EcoTax": 8.1
                    }
                ],
                "Barcode": product.barcode,
                "Weight": product.weight,
                "IsPublished": True,
                "InventoryMethod": 1 if product.is_storable == True else 0,
                'ProductLangs': [
                    {
                        'Name': product.name, 
                        'Description': product.description_sale, 
                        'ISOValue': 'fr'
                    }
                ],
                "Categories": [
                    {
                        "Id": id_categ,
                    }
                ],
                "ProductPhotos": product_photos,
                "Combinations": [
                    {
                        "ProductAttributes": [
                            {
                                "AttributeId": value.attribute_id.id,
                                "Attribute": value.attribute_id.name,
                                "Value": value.name,
                                "WeightAdjustement": product.weight,
                                "ProductAttributeLangs": [
                                    {
                                        "Name": value.attribute_id.name,
                                        "Value": value.name,
                                        "ISOValue": 'fr'
                                    }
                                ]
                            }
                            for value in line.value_ids
                        ]
                    }
                    for line in product.attribute_line_ids if line.value_ids
                ]
            }
            
            put_response_produit = requests.put(url_produit, json=update_data, headers=headers)
            
            if put_response_produit.status_code == 200:
                _logger.info(f"Article {product.name} mis à jour avec succès sur l'API SAH")
            else:
                _logger.error(f"Erreur lors de la mise à jour de l'article {product.name} sur l'API SAH : {put_response_produit.status_code}")

        _logger.info("======================= Fin de mise à jour de l'Article")

    def creation_produit_odoo_sah(self,objet,is_published,type,allow_out_of_stock_order,sale_ok,is_storable,categ_id,
                                    discountStartDate,discountEndDate,default_code,id,name,list_price,taxes_id,
                                    standard_price,barcode,weight,long_sah,haut_sah,availableOnHostMinisites,
                                    description,accessory_product_ids,attribute_line_ids,product_photos):
        _logger.info("$$$$$$$$$$$ Creating Product in SellingAtHome...")
        _logger.info(product_photos)
        headers = self.env['authentication.sah'].establish_connection()
        est_publie = bool(is_published)
        virtual = type == 'service'
        rupture_stock = bool(allow_out_of_stock_order)
        is_sale = bool(sale_ok)
        id_categ = ''
        categ_parent =''
        suivi_stock = 1 if is_storable == True else 0
        if categ_id:
            url_categ = "https://demoapi.sellingathome.com/v1/Categories"
            post_response_categ = requests.get(url_categ, headers=headers)
            
            if post_response_categ.status_code == 200:
                response_data_categ = post_response_categ.json()
                categ_parent = response_data_categ[0]['Id']
                j=0
                for c in response_data_categ:
                    CategoryLangs = c['CategoryLangs']
                    for cc in CategoryLangs :
                        nom_cat = cc['Name']
                        if categ_id.name==nom_cat:
                            id_categ = c['Id']
                            j+=1
                if j==0:
                    create_category = {
                        "Reference": categ_id.name,
                        "ParentCategoryId": categ_parent,
                        "IsPublished": True,
                        "CategoryLangs": [
                            {
                                "Name": categ_id.name,
                                "Description": 'None',
                                "ISOValue": "fr",
                            },
                        ],
                    }
                    post_response_categ_create = requests.post(url_categ, json=create_category, headers=headers)
                    if post_response_categ_create.status_code == 200:
                        categ = post_response_categ_create.json()
                        id_categ = categ['Id']
            else:
                _logger.info(f"Error {post_response_categ.status_code}: {post_response_categ.text}")

            url = "https://demoapi.sellingathome.com/v1/Products"   

            discount_start_date = discountStartDate
            discount_end_date = discountEndDate
            user_timezone = self.env.user.tz or 'UTC'

            if discount_start_date:
                discount_start_date_utc = pytz.timezone(user_timezone).localize(discount_start_date).astimezone(pytz.UTC)
                discount_start_date_iso = discount_start_date_utc.isoformat()
            else:
                discount_start_date_iso = None

            if discount_end_date:
                discount_end_date_utc = pytz.timezone(user_timezone).localize(discount_end_date).astimezone(pytz.UTC)
                discount_end_date_iso = discount_end_date_utc.isoformat()
            else:
                discount_end_date_iso = None

            product_data = {
                "ProductType": 5,
                "Reference": default_code,
                "Prices": [
                    {
                        "ProductId": id,
                        "BrandTaxRate": 2.1,
                        "BrandTaxName": name,
                        "TwoLetterISOCode": "FR",
                        "PriceExclTax": list_price,
                        "PriceInclTax": list_price * (taxes_id.amount/100),
                        "ProductCost": standard_price,
                        "EcoTax": 8.1
                    }
                ],
                # "RemoteId": "sample string 2",
                # "RemoteReference": "sample string 3",
                "Barcode": barcode,
                "Weight": weight,
                "Length": long_sah,
                # "Width": 1.1,
                "Height": haut_sah,
                "IsPublished": est_publie,
                "IsVirtual": virtual,
                "UncommissionedProduct": is_sale,
                "InventoryMethod": suivi_stock,
                # "LowStockQuantity": 1,
                "AllowOutOfStockOrders": rupture_stock,
                "AvailableOnSellerMinisites": availableOnHostMinisites,
                "DiscountEndDate": discount_end_date_iso,
                "DiscountStartDate": discount_start_date_iso,
                'ProductLangs': [
                    {'Name': name,
                    'Description': description, 
                    'ISOValue': 'fr',
                    }
                ],
                "Categories": [
                    {
                    "Id": id_categ,
                    },
                ],

                "ProductPhotos": product_photos,

                "ProductRelatedProducts": [
                    {
                        "ProductId": id,
                        "ProductRemoteId": str(related_product.id),
                        "ProductReference": related_product.default_code,
                        "IsDeleted": False
                    } for related_product in accessory_product_ids
                ],
                "Combinations": [
                    {
                        "ProductAttributes": [
                            {
                                "AttributeId": value.attribute_id.id,
                                "Attribute": value.attribute_id.name,
                                "Value": value.name,
                                "WeightAdjustement": weight,
                                "ProductAttributeLangs": [
                                    {
                                        "Name": value.attribute_id.name,
                                        "Value": value.name,
                                        "ISOValue": 'fr'
                                    }
                                ]
                            }
                            for value in line.value_ids
                        ]
                    }
                    for line in attribute_line_ids if line.value_ids
                ]
            }
            post_response = requests.post(url, json=product_data, headers=headers)
            if post_response.status_code == 200:
                response_data = post_response.json()
                product_id = response_data.get('Id')
                objet.produit_sah_id = product_id

    @api.model
    def create(self, vals):
        res = super(ProduitSelligHome, self).create(vals)
        # Récupérer les images depuis product_template_image_ids
        product_photos = []
        if res.product_template_image_ids:
            for index, image in enumerate(res.product_template_image_ids):
                # Créer une pièce jointe publique pour chaque image
                attachment = self.env['ir.attachment'].create({
                    'name': f'product_image_{res.id}.png',
                    'type': 'binary',
                    'datas': image.image_1920, 
                    'res_model': 'product.template',
                    'res_id': res.id,
                    'mimetype': 'image/png', 
                    'public': True,
                })
                # Générer l'URL de l'image
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                product_image_url = f'{base_url}/web/content/{attachment.id}/{attachment.name}'
                _logger.info("##################### product_image_url ############################")
                _logger.info(product_image_url)
                product_photos.append({
                    "Link": product_image_url,
                    "ProductId": res.id,
                    "IsDefault": index == 0,
                    "DisplayOrder": index + 1
                })
        _logger.info("*************************** product_photos *************************")
        _logger.info(product_photos)

        if res :
            job_kwargs = {
                'description': 'Création produit Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).creation_produit_odoo_sah(res,res.is_published,res.type,res.allow_out_of_stock_order,res.sale_ok,res.is_storable,res.categ_id,
                                    res.discountStartDate,res.discountEndDate,res.default_code,res.id,res.name,res.list_price,res.taxes_id,
                                    res.standard_price,res.barcode,res.weight,res.long_sah,res.haut_sah,res.availableOnHostMinisites,
                                    res.description,res.accessory_product_ids,res.attribute_line_ids,product_photos)
        return res


    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        rec = super(ProduitSelligHome, self).write(vals)
        if vals:
            job_kwargs = {
                'description': 'Mise à jour du produit dans SAH',
            }
            self.with_delay(**job_kwargs).update_produit_dans_sah(self, headers)

            ### Modification stock
            job_kwargs2 = {
                'description': 'Mise à jour du stock produit',
            }
            self.with_delay(**job_kwargs2).maj_des_stocks(self.is_storable,self.produit_sah_id,self.default_code,self.qty_available,self.virtual_available)
        return rec

    def maj_des_stocks(self,is_storable,produit_sah_id,default_code,qty_available,virtual_available):
        headers = self.env['authentication.sah'].establish_connection()
        if is_storable == True:
            url2 = 'https://demoapi.sellingathome.com/v1/Stocks'
            values = {
                "ProductId": produit_sah_id,
                "ProductReference": default_code,
                "StockQuantity": int(qty_available),
                "StockQuantityComing":int(virtual_available),
                "AllowOutOfStockOrders": True
                
            }
            requests.put(url2, headers=headers, json=values)
          


    def _export_stock_produit(self):
        headers = self.env['authentication.sah'].establish_connection()
        active_ids = self.env.context.get('active_ids')
        for active_id in active_ids:
            product_id = self.env['product.template'].search([('id','=',active_id)])
            job_kwargs2 = {
                'description': 'Export stock',
            }
            self.with_delay(**job_kwargs2).maj_des_stocks(product_id.is_storable,product_id.produit_sah_id,product_id.default_code,product_id.qty_available,product_id.virtual_available)
        
        

    def _export_datas_produit(self):
        headers = self.env['authentication.sah'].establish_connection()
        active_ids = self.env.context.get('active_ids')
        for active_id in active_ids:
            product_id = self.env['product.template'].search([('id','=',active_id)])
            job_kwargs = {
                    'description': 'Export  produit',
            }
            self.with_delay(**job_kwargs).update_produit_dans_sah(product_id, headers)