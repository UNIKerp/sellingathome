from odoo import models, api, fields,_
import requests
import json
from datetime import datetime,date
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
from odoo.exceptions import ValidationError

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
    
    a_synchroniser = fields.Boolean("synchronisé dans SAH ?", help="Si vous voulez synchronisé ce produit dans SAH")
   
    _sql_constraints = [
        ('produit_sah_id_uniq', 'unique (produit_sah_id)', "ID du produit SAH exists déjà !"), ]

    
    #


    def add_category_odoo_sah(self,product):
        if product and product.public_categ_ids:
            list_id_categ = []
            for categ in product.public_categ_ids:
                if categ.category_sah_id:
                    list_id_categ.append(categ.category_sah_id)
                else:
                    headers = self.env['authentication.sah'].establish_connection()
                    url_category = "https://demoapi.sellingathome.com/v1/Categories"
                    datas = {
                        "Reference": categ.name,
                        "ParentCategoryId": categ.parent_id.name if  categ.parent_id else 1,
                    }
                    response = requests.post(url_category,json=datas, headers=headers, timeout=120)
                    if response.status_code == 200:
                        datas = response.json()
                        categ.category_sah_id = datas.get('Id')
                        list_id_categ.append(datas.get('Id'))
            return list_id_categ
               

    

               
    """ Mise à jour d'un produit de Odoo => SAH """ 
    def update_produit_dans_sah(self, product, headers):
        if product.produit_sah_id and product.a_synchroniser==True:
            #Photos
            photos_maj = self.maj_images_du_produit(product)
            _logger.info('=========================== %s',photos_maj)
            #
           
            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{product.produit_sah_id}"

            get_response_produit = requests.get(url_produit,headers=headers)
            if get_response_produit.status_code == 200:

                response_data_produit = get_response_produit.json()
                # Ajout spécifique si c'est un kit (combo)
                type_produit_sah = 5
                product_components = []
                if product.type == 'combo':
                    type_produit_sah = 20
                    for component in product.combo_ids:
                        product_component_products = []
                        for cop in component.combo_item_ids: 
                            component_sah_id = cop.product_id.produit_sah_id
                            if component_sah_id:
                                product_component_products.append({
                                    "ProductId": component_sah_id,
                                    "ProductRemoteId": None,
                                    "ProductCombinationId": None,
                                    "ProductCombinationBarCode": None,
                                    "Quantity": 1,
                                    "DisplayOrder": 0,
                                    "Deleted": False
                                })
                        product_components.append({
                            "Id": component.id,  
                            "Name": component.name,
                            "ProductId": product.produit_sah_id,
                            "MaxQuantity": 0,
                            "Deleted": False,
                            "RemoteReference": None,
                            "ProductComponentLangs": [
                                {"Label": component.name, "ISOValue": "fr"},
                                {"Label": "", "ISOValue": "en"}
                            ],
                            "ProductComponentProducts": product_component_products
                        })
                elif product.type == 'consu':
                    bom_ids = self.env['mrp.bom'].search([('product_tmpl_id','=',product.id)])
                    for bom in bom_ids:
                        if bom.type == 'phantom':
                            type_produit_sah = 10
                            break
                list_id_categ = self.add_category_odoo_sah(product)
                update_data = {
                    "ProductType": type_produit_sah,
                    "Reference": product.default_code,
                    "Prices": response_data_produit['Prices'],
                    "AttachedProducts": response_data_produit['AttachedProducts'],
                    "Barcode": product.barcode if product.barcode else '',
                    "Weight": product.weight,
                    "IsPublished": True,
                    "InventoryMethod": 1 if product.is_storable == True else 0,
                    "ProductPhotos": photos_maj,
                    "ProductComponents": product_components,
                    'ProductLangs': [
                        {
                            'Name': product.name, 
                            'Description': product.description_sale, 
                            'ISOValue': 'fr'
                        }
                    ],
                    "Categories": [
                        {
                            "Id": elt,
                        }for elt in list_id_categ
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
                if not product_components:
                    update_data.pop("ProductComponents", None)
                if type_produit_sah !=5:
                    update_data.pop("Combinations", None)
                put_response_produit = requests.put(url_produit, json=update_data, headers=headers)
                _logger.info(f"========== Article {product.name} Statut SAH {put_response_produit.status_code}==========")
                if put_response_produit.status_code == 200:
                    _logger.info(f"========== Article {product.name} mis à jour avec succès sur l'API SAH ==========")
                else:
                    _logger.error(f"========== Erreur lors de la mise à jour de l'article {product.name} sur l'API SAH : {put_response_produit.text} ==========")


    #
    """ Creation d'un produit de Odoo => SAH """
    def creation_produit_odoo_sah(self,product_id):
        if product_id.a_synchroniser==True:
            headers = self.env['authentication.sah'].establish_connection()
            est_publie = bool(product_id.is_published)
            virtual = type == 'service'
            rupture_stock = bool(product_id.allow_out_of_stock_order)
            is_sale = bool(product_id.sale_ok)
            id_categ = ''
            categ_parent =''
            suivi_stock = 1 if product_id.is_storable == True else 0
            product_photos = self.creation_images_du_produit(product_id)

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

            list_id_categ = self.add_category_odoo_sah(product_id)
            product_data = {
                "ProductType": 5,
                "Reference": product_id.default_code,
                "Prices": [
                    {
                        "BrandTaxRate": self._get_sah_tax(elt) if self._get_sah_tax(elt) else 2.1,
                        "TwoLetterISOCode": "FR",
                        "PriceInclTax": product_id.list_price ,
                        "ProductCost": product_id.standard_price,
                        "EcoTax": 8.1
                    }
                    for elt in product_id.taxes_id if self._get_sah_tax(elt)
                ],

                "Barcode": product_id.barcode if product_id.barcode else '',
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
                    "Id": elt,
                    }for elt in list_id_categ
                ],

                "ProductPhotos":product_photos,

                "ProductRelatedProducts": [
                    {
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
            if not product_photos:
                product_data.pop("ProductPhotos", None)
            if not list_id_categ:
                update_data.pop("Categories", None)

            post_response = requests.post(url, json=product_data, headers=headers)
            if post_response.status_code == 200:
                response_data = post_response.json()
                product_id.produit_sah_id = int(response_data.get('Id'))
                _logger.info('========== creation du produit dans SAH avec succes  %s ==========',product_id.produit_sah_id)
                prices = response_data.get('Prices')
                for price in prices:
                    pays = self.env['res.country'].search([('code', '=', price['TwoLetterISOCode'])], limit=1)
                    pricelist = self.env['product.pricelist'].create({
                        'name': price['BrandTaxName'],
                        'price_list_sah_id': price['Id'],
                        'country_id': pays.id if pays else False,
                        'item_ids': [(0, 0, {
                            'product_tmpl_id': product_id.id,
                            'price':  product_id.list_price,
                        })],
                    })
                    product_id.default_list_price = pricelist.id
                
                        
            else:
                _logger.info('========== Erreur de creation du produit %s ==========',post_response)
    
    def _get_sah_tax(self, tax_id):
        # Recherche la taxe par son montant
        if tax_id :
            tax = self.env['tax.sah'].search([('amount_tax_id', '=', tax_id.id)], limit=1)
            if tax :
                return tax.amount
    """ Redéfiniton de la fonction création du produit """
    # @api.model
    # def create(self, vals):
    #     res = super(ProduitSelligHome, self).create(vals)
    #     if res:
    #         job_kwargs = {
    #             'description': 'Création produit Odoo vers SAH',
    #         }
    #         self.with_delay(**job_kwargs).creation_produit_odoo_sah(res)
    #     return res

    """ Modification d'un produit """
    # def write(self, vals):
    #     headers = self.env['authentication.sah'].establish_connection()
    #     rec = super(ProduitSelligHome, self).write(vals)
    #     for record in self:
    #         if record.a_synchroniser==True or ( 'a_synchroniser' in vals and vals['a_synchroniser']==True):
    #             if vals and record.produit_sah_id:
    #                 job_kwargs = {
    #                     'description': 'Mise à jour du produit dans SAH',
    #                 }
    #                 self.with_delay(**job_kwargs).update_produit_dans_sah(record, headers)

    #                 ### Modification stock
    #                 job_kwargs2 = {
    #                     'description': 'Mise à jour du stock produit',
    #                 }
    #                 self.with_delay(**job_kwargs2).maj_des_stocks(record)
    #     return rec



    def maj_des_stocks(self,product_id):
        headers = self.env['authentication.sah'].establish_connection()
        if product_id.is_storable == True and product_id.a_synchroniser==True:
            url2 = 'https://demoapi.sellingathome.com/v1/Stocks'
            values = {
                "ProductId": product_id.produit_sah_id,
                "ProductReference": product_id.default_code,
                "StockQuantity": int(product_id.qty_available),
                "StockQuantityComing":int(product_id.virtual_available),
                "AllowOutOfStockOrders": True
                
            }
            requests.put(url2, headers=headers, json=values)
          
    

    """ Creation des images du produits """
    def creation_images_du_produit(self, product_id):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        directory = '/home/odoo/src/user/integration_sah/static/description/tmp'
        photos_produit = []
        if product_id.image_1920:
            image_data = base64.b64decode(product_id.image_1920)
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            image_filename = "image_1920.png"
            file_path = os.path.join(directory, image_filename)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            link = f"{base_url}/integration_sah/static/description/tmp/{image_filename}"
           
            photos_produit.append({
                'Link': link,
                'IsDefault': True,
                'Deleted': True
            })
        if product_id.product_template_image_ids:
            i = 0
            for image in product_id.product_template_image_ids:
                image_data = base64.b64decode(image.image_1920)
                i += 1
                if not os.path.exists(directory):
                    os.makedirs(directory)
                image_filename = f"image_supp_{i}.png"
                file_path = os.path.join(directory, image_filename)
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                link = f"{base_url}/integration_sah/static/description/tmp/{image_filename}"
                photos_produit.append({
                    'Link': link,
                    'IsDefault': False,
                    'Deleted': True
                })

        return photos_produit


    """ Mise à jour des images du produits """
    def maj_images_du_produit(self,product_id):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        photos_produit = []
        url = f"https://demoapi.sellingathome.com/v1/Products/{product_id.produit_sah_id}"
        headers = self.env['authentication.sah'].establish_connection()
        response =  requests.get(url, headers=headers)
        if response.status_code == 200:
            playload = response.json()
            photos_produit = self.creation_images_du_produit(product_id)
            for i in range(len(photos_produit)):
                if i < len(playload['ProductPhotos']):
                    # Remplacer les liens existants
                    playload['ProductPhotos'][i]['Link'] = photos_produit[i]['Link']
                else:
                    playload['ProductPhotos'].append(photos_produit[i])
            return playload['ProductPhotos']
        

    def _export_stock_produit(self):
        headers = self.env['authentication.sah'].establish_connection()
        active_ids = self.env.context.get('active_ids')
        for active_id in active_ids:
            product_id = self.env['product.template'].search([('id','=',active_id)])
            job_kwargs2 = {
                'description': 'Export stock',
            }
            self.with_delay(**job_kwargs2).maj_des_stocks(product_id)
        
        

    def _export_datas_produit(self):
        headers = self.env['authentication.sah'].establish_connection()
        active_ids = self.env.context.get('active_ids')
        for active_id in active_ids:
            product_id = self.env['product.template'].search([('id','=',active_id)])
            if product_id.produit_sah_id and product_id.a_synchroniser==True:
                job_kwargs = {
                        'description': ' Mise à jour du produit de odoo vers SAH',
                }
                self.with_delay(**job_kwargs).update_produit_dans_sah(product_id, headers)
            else:
                job_kwargs = {
                    'description': 'Création produit Odoo vers SAH',
                }
                self.with_delay(**job_kwargs).creation_produit_odoo_sah(product_id)