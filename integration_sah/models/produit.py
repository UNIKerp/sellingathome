from odoo import models, api, fields,_
import requests
import json
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class ProduitSelligHome(models.Model):
    _inherit = "product.template"

    produit_sah_id = fields.Integer("ID produit SAH")
    default_list_price = fields.Many2one('product.pricelist', string='Liste de prix par défaut')

    

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
                    price_list = self.env['product.pricelist'].search([('price_list_sah_id', '=', None)], limit=1)
                    if price_list:
                        price_list = self.env['product.pricelist'].create({
                            'name': 'SAH Liste de Prix',
                            'currency_id': self.env.user.company_id.currency_id.id
                        })
                    
                    self.env['product.pricelist.item'].create({
                        'pricelist_id': price_list.id,
                        'product_tmpl_id': new_product.id,
                        'fixed_price': price,
                    })
                    _logger.info(f"Liste de prix ajoutée pour le produit : {name} (ID SAH: {sah_id})")

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
        
        # Si le produit a un produit_sah_id, mettre à jour le produit dans l'API
        if product.produit_sah_id:
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{product.produit_sah_id}"
            
            # Préparer les données à envoyer à l'API (basées sur les informations dans Odoo)
            rupture_stock = bool(product.allow_out_of_stock_order)
            est_publie = bool(product.is_published)
            is_sale = bool(product.sale_ok)
            virtual = product.type == 'service'
            des = product.description_ecommerce
            suivi_stock = 1 if product.is_storable == True else 0

            update_data = {
                "ProductType": 5,
                "Reference": product.default_code,
                "AllowOutOfStockOrders": rupture_stock,
                "IsVirtual": virtual,
                "InventoryMethod": suivi_stock,
                "UncommissionedProduct": is_sale,
                "Barcode": product.barcode,
                "Weight": product.weight,
                "IsPublished": est_publie,
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
                "AdditionalInformations": {
                    "description": [des],
                },
                "ProductRelatedProducts": [
                    {
                        "ProductId": product.id,
                        "ProductRemoteId": str(related_product.id),
                        "ProductReference": related_product.default_code,
                        "IsDeleted": False
                    } for related_product in product.accessory_product_ids
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



    @api.model
    def create(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        res = super(ProduitSelligHome, self).create(vals)
        des = res.description_ecommerce 
        est_publie = bool(res.is_published)
        virtual = res.type == 'service'
        rupture_stock = bool(res.allow_out_of_stock_order)
        is_sale = bool(res.sale_ok)
        id_categ = ''
        categ_parent =''
        suivi_stock = 1 if res.is_storable == True else 0
        if res.categ_id:
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
                        if res.categ_id.name==nom_cat:
                            id_categ = c['Id']
                            j+=1
                if j==0:
                    create_category = {
                        "Reference": res.categ_id.name,
                        "ParentCategoryId": categ_parent,
                        "IsPublished": True,
                        "CategoryLangs": [
                            {
                                "Name": res.categ_id.name,
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
            product_data = {
                "ProductType": 5,
                "Reference": res.default_code,
                "Prices": [
                    {
                        "ProductId": res.id,
                        "BrandTaxRate": 2.1,
                        "BrandTaxName": res.name,
                        "TwoLetterISOCode": "FR",
                        "PriceExclTax": res.list_price,
                        "PriceInclTax": res.list_price * (res.taxes_id.amount/100),
                        "ProductCost": res.standard_price,
                        "EcoTax": 8.1
                    }
                ],
                # "RemoteId": "sample string 2",
                # "RemoteReference": "sample string 3",
                "Barcode": res.barcode,
                "Weight": res.weight,
                # "Length": 1.1,
                # "Width": 1.1,
                # "Height": 1.1,
                "IsPublished": est_publie,
                "IsVirtual": virtual,
                "UncommissionedProduct": is_sale,
                "InventoryMethod": suivi_stock,
                # "LowStockQuantity": 1,
                "AllowOutOfStockOrders": rupture_stock,
                # "WarehouseLocation": res.warehouse_id.id or '',
                'ProductLangs': [
                    {'Name': res.name,
                    'Description': res.description, 
                    'ISOValue': 'fr',
                    }
                ],
                "Categories": [
                    {
                    "Id": id_categ,
                    },
                ],
                "AdditionalInformations": {
                    "description": [des],
                },
                "ProductRelatedProducts": [
                    {
                        "ProductId": res.id,
                        "ProductRemoteId": str(related_product.id),
                        "ProductReference": related_product.default_code,
                        "IsDeleted": False
                    } for related_product in res.accessory_product_ids
                ],
                "Combinations": [
                    {
                        "ProductAttributes": [
                            {
                                "AttributeId": value.attribute_id.id,
                                "Attribute": value.attribute_id.name,
                                "Value": value.name,
                                "WeightAdjustement": res.weight,
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
                    for line in res.attribute_line_ids if line.value_ids
                ]
            }

            # Send POST request
            post_response = requests.post(url, json=product_data, headers=headers)
            
            if post_response.status_code == 200:
                response_data = post_response.json()
                product_id = response_data.get('Id')
                res.produit_sah_id = product_id
                default_list_price = self.env['product.pricelist'].create({
                    'name':f'Tarif du produit {res.name}',
                    'price_list_sah_id':response_data['Prices'][0]['Id']
                })
                res.default_list_price = default_list_price.id
            else:
                _logger.info(f"Error {post_response.status_code}: {post_response.text}")
        return res


    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        if vals:
            ### Modification stock
            job_kwargs = {
                'description': 'Mise à jour du produit dans SAH',
            }
            self.with_delay(**job_kwargs).update_produit_dans_sah(self, headers)
            if self.is_storable == True:
                url2 = 'https://demoapi.sellingathome.com/v1/Stocks'
                values = {
                    "ProductId": self.produit_sah_id,
                    "ProductReference": self.default_code,
                    "StockQuantity": int(self.qty_available),
                    "StockQuantityComing":int(self.virtual_available),
                    # "ProductCombinationStocks": [
                    #         {
                    #         "ProductCombinationId": self.produit_sah_id,
                    #         "ProductCombinationBarcode": "sample string 1",
                    #         "ProductCombinationSku": "sample string 2",
                    #         "ProductCombinationRemoteId": 1,
                    #         "StockQuantity": 1,
                    #         "StockQuantityComing": 1,
                    #         "StockQuantityComingAt": "2024-10-22T13:46:02.7937593+02:00",
                    #         "SellerStockQuantity": 1,
                    #         "AllowOutOfStockOrders": True
                    #         }
                    # ],
                    "AllowOutOfStockOrders": True
                    
                }
                response2 = requests.put(url2, headers=headers, json=values)
                if response2.status_code == 200:
                    _logger.info("************************%s",self.virtual_available)  
                else:
                    _logger.info(f"Erreur {response2.status_code}: {response2.text}")
     
                    
            rec = super(ProduitSelligHome, self).write(vals)
            return rec
