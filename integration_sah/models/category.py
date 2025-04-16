# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
_logger = logging.getLogger(__name__)


class ClientSAH(models.Model):
    _inherit = "product.public.category"
    _description = "client de SAH"

    category_sah_id = fields.Integer(string="ID Catégorie SAH")

    def ajout_category_sah_odoo(self):
        headers = self.env['authentication.sah'].establish_connection()
        url = "https://demoapi.sellingathome.com/v1/Categories"
        response = requests.get(url, headers=headers, timeout=120)

        if response.status_code != 200:
            _logger.error("Erreur lors de la récupération des catégories SAH : %s", response.text)
            return

        datas = response.json()
        category_model = self.env['product.public.category']
        category_map = {} 
    
        for data in datas:
            sah_id = data.get('Id')
            if not sah_id:
                continue

            existing_categ = category_model.search([('category_sah_id', '=', sah_id)], limit=1)
            if not existing_categ and  data.get('Reference'):
                new_categ = category_model.create({
                    'name': data.get('Reference'),
                    'category_sah_id': sah_id,
                })
                category_map[sah_id] = new_categ
            else:
                category_map[sah_id] = existing_categ

     
        for data in datas:
            sah_id = data.get('Id')
            parent_id = data.get('ParentCategoryId')

            if sah_id and parent_id:
                current_categ = category_map.get(sah_id)
                parent_categ = category_map.get(parent_id)

                if current_categ and parent_categ and current_categ.parent_id != parent_categ:
                    current_categ.write({'parent_id': parent_categ.id})


    def ajout_stock_sah_odoo(self):
        products = self.env['product.template'].search([('produit_sah_id','!=',0),('is_storable', '=', True)])
        if products:
            for product in products:
                headers = self.env['authentication.sah'].establish_connection()
                url_produit = f"https://demoapi.sellingathome.com/v1/Stocks?productId={product.produit_sah_id}"
                response = requests.get(url_produit, headers=headers, timeout=120)
                if response.status_code == 200:
                    location = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
                    datas =  response.json()
                    if location and datas.get('StockQuantity') > 0:
                        upload = {
                            'product_id': product.product_variant_id.id,
                            'location_id': location.id,
                            'quantity': int(datas.get('StockQuantity'))
                        }
                        stock_quants_data = self.env['stock.quant'].create(upload)
                        product.product_variant_id._compute_quantities()
                        _logger.info(f'✅ =========================== {len(stock_quants_data)} lignes de stock créées =====================')

                    logging.info(f'================================ {product.name}')


       
    def ajout_nommenclature_sah_odoo(self):
        products = self.env['product.template'].search([('produit_sah_id','!=',0)])
        if products:
            for product in products:
                headers = self.env['authentication.sah'].establish_connection()
                url_produit = f"https://demoapi.sellingathome.com/v1/Products/{product.produit_sah_id}"
                response = requests.get(url_produit, headers=headers, timeout=120)
                if response.status_code == 200:
                    logging.info(f'================================ {response.json()}')
                    data = response.json()
                    if data.get('AttachedProducts'):
                        upload = {
                            'product_tmpl_id':product.id,
                            'type':'phantom'
                        }
                        nommencalture = self.env['mrp.bom'].create(upload)
                        for bom in  data.get('AttachedProducts'):
                            upload2 = {
                                'bom_id':nommencalture.id,
                                'product_tmpl_id':product.id,
                                'product_id':product.product_variant_id.id,
                                'product_qty':bom.get('Quantity')
                            }
                            line = self.env['mrp.bom.line'].create(upload2)

                            logging.info('============================= %s',line)



    def ajout_liste_prix_produit_sah_odoo(self):
        products = self.env['product.template'].search([('produit_sah_id','!=',0)])
        if products:
            for product in products:
                headers = self.env['authentication.sah'].establish_connection()
                url_produit = f"https://demoapi.sellingathome.com/v1/Prices?productid={product.produit_sah_id}"
                response = requests.get(url_produit, headers=headers, timeout=120)
                if response.status_code == 200:
                    logging.info(f'================================ {response.json()}')
                    datas = response.json()
                    for data in datas:
                        code = data.get('Country').get('TwoLetterISOCode')
                        country = self.env['res.country'].search([('code','=',code)])
                        pricelist_id = self.env['product.pricelist'].search([('name','=',data.get('BrandTaxName'))], limit=1)
                        if not pricelist_id:
                            upload = {
                                'price_list_sah_id':data.get('Id'),
                                'country_id':country.id if country else False,
                                'name':data.get('BrandTaxName'),
                            }
                            pricelist_id = self.env['product.pricelist'].create(upload)
                        if data.get('RolePrices'):
                            logging.info('################################ %s',data.get('RolePrices'))
                            for role in data.get('RolePrices'):
                                start_raw = role.get('StartDate')
                                end_raw = role.get('EndDate')

                                if isinstance(start_raw, str):
                                    start_date = datetime.fromisoformat(start_raw).date()
                                else:
                                    start_date = start_raw.date() if hasattr(start_raw, 'date') else False

                                if isinstance(end_raw, str):
                                    end_date = datetime.fromisoformat(end_raw).date()
                                else:
                                    end_date = end_raw.date() if hasattr(end_raw, 'date') else False
                                upload2 = {
                                    'product_tmpl_id':product.id,
                                    'min_quantity': role.get('Quantity'),
                                    'fixed_price':role.get('NewPriceExclTax'),
                                    'date_start':start_date,
                                    'date_end':end_date,
                                    'pricelist_id':pricelist_id.id,
                                    'price_sah_id':role.get('Id'),
                                }
                                price = self.env['product.pricelist.item'].create(upload2)
                                logging.info('===============================price %s',price)
                        else:
                            upload2 = {
                                'product_tmpl_id':product.id,
                                'min_quantity': 1,
                                'fixed_price':data.get('PriceExclTax'),
                                'pricelist_id':pricelist_id.id,
                                'price_sah_id':role.get('Id'),
                            }
                            price = self.env['product.pricelist.item'].create(upload2)
                            logging.info('=============================== %s',price)

