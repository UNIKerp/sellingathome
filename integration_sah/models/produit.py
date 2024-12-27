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

    # url_image = fields.Char("URL image", help="Url de l'image")

    _sql_constraints = [
        ('produit_sah_id_uniq', 'unique (produit_sah_id)', "ID du produit SAH exists deja !"), ]

    """ Création des produits de SAH dans Odoo """
    def create_article_sah_odoo(self):
        headers = self.env['authentication.sah'].establish_connection()
        url_produit = "https://demoapi.sellingathome.com/v1/Products"
        post_response_produit = requests.get(url_produit, headers=headers, timeout=120)
        if post_response_produit.status_code == 200:
            response_data_produit = post_response_produit.json()
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
                    self.env['product.template'].create({
                        'name': name,
                        'default_code': reference,
                        'list_price': price,
                        'description_sale': description,
                        'barcode': barcode,
                        'weight': weight,
                        'produit_sah_id': sah_id,
                        'is_storable' : True if type_sah == 1 else False
                    })
                    _logger.info(f"Le produit {name} est  crée avec succés")
        else:
            _logger.error(f"Connexion à l'api : {post_response_produit.status_code}")

    

    """ Mise à jour d'un produit de Odoo => SAH """ 
    def update_produit_dans_sah(self, product, headers):
        if product.produit_sah_id:
            id_categ = ''
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
                    
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{product.produit_sah_id}"
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

    
    #
    """ Creation d'un produit de Odoo => SAH """
    def creation_produit_odoo_sah(self,product_id):
        headers = self.env['authentication.sah'].establish_connection()
        est_publie = bool(product_id.is_published)
        virtual = type == 'service'
        rupture_stock = bool(product_id.allow_out_of_stock_order)
        is_sale = bool(product_id.sale_ok)
        id_categ = ''
        categ_parent =''
        suivi_stock = 1 if product_id.is_storable == True else 0
    
        if product_id.categ_id and not product_id.produit_sah_id:
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
                        if product_id.categ_id.name==nom_cat:
                            id_categ = c['Id']
                            j+=1
                if j==0:
                    create_category = {
                        "Reference": product_id.categ_id.name,
                        "ParentCategoryId": categ_parent,
                        "IsPublished": True,
                        "CategoryLangs": [
                            {
                                "Name": product_id.categ_id.name,
                                "Description": 'None',
                                "ISOValue": "fr",
                            },
                        ],
                    }
                    post_response_categ_create = requests.post(url_categ, json=create_category, headers=headers)
                    if post_response_categ_create.status_code == 200:
                        categ = post_response_categ_create.json()
                        id_categ = categ['Id']
        

        url = "https://demoapi.sellingathome.com/v1/Products"   
        discount_start_date = product_id.discountStartDate
        discount_end_date = product_id.discountEndDate
        user_timezone = self.env.user.tz or 'UTC'
        if discount_start_date:
            discount_start_date = pytz.timezone(user_timezone).localize(discount_start_date).astimezone(pytz.UTC)
            discount_start_date = discount_start_date.isoformat()
        else:
            discount_start_date = None
        if discount_end_date:
            discount_end_date = pytz.timezone(user_timezone).localize(discount_end_date).astimezone(pytz.UTC)
            discount_end_date = discount_end_date.isoformat()
        else:
            discount_end_date = None

        product_data = {
            "ProductType": 5,
            "Reference": product_id.default_code,
            "Prices": [
                {
                    # "ProductId": id,
                    "BrandTaxRate": 2.1,
                    "BrandTaxName": product_id.name,
                    "TwoLetterISOCode": "FR",
                    "PriceExclTax": product_id.list_price,
                    "PriceInclTax": product_id.list_price * (product_id.taxes_id.amount/100),
                    "ProductCost": product_id.standard_price,
                    "EcoTax": 8.1
                }
            ],
            "Barcode": product_id.barcode,
            "Weight": product_id.weight,
            "Length": product_id.long_sah,
            "Height": product_id.haut_sah,
            "IsPublished": est_publie,
            "IsVirtual": virtual,
            "UncommissionedProduct": is_sale,
            "InventoryMethod": suivi_stock,
            "AllowOutOfStockOrders": rupture_stock,
            "AvailableOnSellerMinisites": product_id.availableOnHostMinisites,
            "DiscountEndDate": discount_start_date,
            "DiscountStartDate": discount_start_date,
            'ProductLangs': [
                {'Name': product_id.name,
                'Description': product_id.description, 
                'ISOValue': 'fr',
                }
            ],
            "Categories": [
                {
                "Id": id_categ,
                },
            ],

            # "ProductPhotos": product_photos if product_photos else [],

            "ProductRelatedProducts": [
                {
                    # "ProductId": id,
                    "ProductRemoteId": str(related_product.id),
                    "ProductReference": related_product.default_code,
                    "IsDeleted": False
                } for related_product in product_id.accessory_product_ids
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
                for line in product_id.attribute_line_ids if line.value_ids
            ]
        }
        
        post_response = requests.post(url, json=product_data, headers=headers)
        if post_response.status_code == 200:
            response_data = post_response.json()
            _logger.info("========== Création avec sucés du produit ; %s ==========",response_data)
            product_id.produit_sah_id = int(response_data.get('Id'))
            _logger.info('========== ID SAH DU PRODUIT  %s ==========',product_id.produit_sah_id)

    """ Redéfiniton de la fonction création du produit """
    @api.model
    def create(self, vals):
        res = super(ProduitSelligHome, self).create(vals)
        if res:
            job_kwargs = {
                'description': 'Création produit Odoo vers SAH',
            }
            self.with_delay(**job_kwargs).creation_produit_odoo_sah(res)

        return res


    # def write(self, vals):
    #     headers = self.env['authentication.sah'].establish_connection()
    #     rec = super(ProduitSelligHome, self).write(vals)
    #     if vals and self.produit_sah_id:
    #         job_kwargs = {
    #             'description': 'Mise à jour du produit dans SAH',
    #         }
    #         self.with_delay(**job_kwargs).update_produit_dans_sah(self, headers)

    #         ### Modification stock
    #         job_kwargs2 = {
    #             'description': 'Mise à jour du stock produit',
    #         }
    #         self.with_delay(**job_kwargs2).maj_des_stocks(self.is_storable,self.produit_sah_id,self.default_code,self.qty_available,self.virtual_available)
    #     return rec

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
          

    def maj_des_photos_produits(self,product_id):
        # product_photos = []
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # if product_id.product_template_image_ids:
        #     for image in product_id.product_template_image_ids:
        #         attachment = self.env['ir.attachment'].create({
        #             'name': f'product_image_{product_id.id}.png',
        #             'type': 'binary',
        #             'datas': image.image_1920, 
        #             'res_model': 'product.template',
        #             'res_id': product_id.id,
        #             'mimetype': 'image/png', 
        #             'public': True,
        #         })
        #         product_image_url = f'{base_url}/web/content/{attachment.id}/{attachment.name}'
        #         product_photos.append({
        #             "Link": product_image_url,
        #         })
        # if product_id.image_1920:
        #     attachment_img = self.env['ir.attachment'].create({
        #         'name': f'product_image_{product_id.id}.png',
        #         'type': 'binary',
        #         'datas': product_id.image_1920, 
        #         'res_model': 'product.template',
        #         'res_id': product_id.id,
        #         'mimetype': 'image/png', 
        #         'public': True,
        #     })
        #     product_image_1920 = f'{base_url}/web/content/{attachment_img.id}/{attachment_img.name}'
        #     product_photos.append({
        #         "Link": product_image_1920,
        #     })
        # _logger.info('=================================== %s',product_photos)
        # product_photos = {
        #     "Prices": [
        #         {
        #             "Id": product_id.produit_sah_id,
        #             "BrandTaxRate": 2.1,
        #             "BrandTaxName": product_id.name,
        #             "TwoLetterISOCode": "FR",
        #             "PriceExclTax": product_id.list_price,
        #             "PriceInclTax": product_id.list_price * (1 + product_id.taxes_id.amount / 100),
        #             "ProductCost": product_id.standard_price,
        #             "EcoTax": 8.1
        #         }
        #     ],
        #     "ProductPhotos": product_photos
        # }
        headers = self.env['authentication.sah'].establish_connection()
        url_produit = f"https://demoapi.sellingathome.com/v1/Products/{product_id.produit_sah_id}"
        response_produit = requests.get(url_produit, headers=headers)
        if response_produit.status_code == 200:
            product_data = response_produit.json()
            _logger.info("Produit data récupérée : %s", product_data)
            
            # Étape 2 : Récupérer les IDs des photos existantes
            product_photos_existing = product_data.get('ProductPhotos', [])
            existing_photo_ids = [photo.get('Id') for photo in product_photos_existing if 'Id' in photo]
            _logger.info("IDs des photos existantes : %s", existing_photo_ids)

            # Étape 3 : Générer les nouvelles URLs des images et associer les IDs
            product_photos_update = []
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

            if product_id.product_template_image_ids:
                for i, image in enumerate(product_id.product_template_image_ids):
                    attachment = self.env['ir.attachment'].create({
                        'name': f'product_image_{product_id.id}_{i}.png',
                        'type': 'binary',
                        'datas': image.image_1920,
                        'res_model': 'product.template',
                        'res_id': product_id.id,
                        'mimetype': 'image/png',
                        'public': True,
                    })
                    product_image_url = f'{base_url}/web/content/{attachment.id}/{attachment.name}'
                    
                    # Utiliser l'ID existant si disponible, sinon laisser None
                    photo_id = existing_photo_ids[i] if i < len(existing_photo_ids) else None
                    product_photos_update.append({
                        "Id": photo_id,
                        "Link": product_image_url,
                    })

            if product_id.image_1920:
                attachment_img = self.env['ir.attachment'].create({
                    'name': f'product_image_{product_id.id}.png',
                    'type': 'binary',
                    'datas': product_id.image_1920,
                    'res_model': 'product.template',
                    'res_id': product_id.id,
                    'mimetype': 'image/png',
                    'public': True,
                })
                product_image_1920 = f'{base_url}/web/content/{attachment_img.id}/{attachment_img.name}'
                
                # Ajouter une photo supplémentaire sans ID (si elle n'existe pas déjà)
                # product_photos_update.append({
                #     "Id": None,
                #     "Link": product_image_1920,
                # })

            _logger.info("Photos à mettre à jour : %s", product_photos_update)

            # Étape 4 : Préparer les données pour l'API
            values = {
                "Prices": [
                    {
                        "Id": product_id.produit_sah_id,
                        "BrandTaxRate": 2.1,
                        "BrandTaxName": product_id.name,
                        "TwoLetterISOCode": "FR",
                        "PriceExclTax": product_id.list_price,
                        "PriceInclTax": product_id.list_price * (1 + product_id.taxes_id.amount / 100),
                        "ProductCost": product_id.standard_price,
                        "EcoTax": 8.1
                    }
                ],
                "ProductPhotos": product_photos_update
            }

            # Étape 5 : Effectuer la mise à jour via l'API
            url_put = f"https://demoapi.sellingathome.com/v1/Products/{product_id.produit_sah_id}"
            response_put = requests.put(url_put, json=values, headers=headers)

            if response_put.status_code == 200:
                _logger.info("Mise à jour des photos réussie : %s", response_put.json())
            else:
                _logger.error("Échec de la mise à jour des photos : %s", response_put.text)
        else:
            _logger.error("Échec de la récupération des données produit : %s", response_produit.text)
            


            # res = response_produit.json()
            # values = {}
            # for elt in res:
            #     if elt['Id'] == product_id.produit_sah_id:
            #         values = elt
            #         break
            # _logger.info('=================================%s',values)
            # for photo in values['ProductPhotos']:
            #     photo["Link"] = "https://unikerp-sellingathome-staging-17258348.dev.odoo.com/web/content/2551/product_image_317.png"
            # _logger.info('================================= aprss%s',values)
            # url_put = f"https://demoapi.sellingathome.com/v1/Products/{product_id.produit_sah_id}"
            # _logger.info('result======================================%s',url_put)
            # result = requests.put(url_put,json=values, headers=headers)
            # _logger.info('================================= result%s',result)



        

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
            self.maj_des_photos_produits(product_id)
            # job_kwargs = {
            #         'description': 'Export  produit',
            # }
            # self.with_delay(**job_kwargs).update_produit_dans_sah(product_id, headers)