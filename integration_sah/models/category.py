# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime,date
_logger = logging.getLogger(__name__)


class ClientSAH(models.Model):
    _inherit = "product.public.category"
    _description = "client de SAH"

    category_sah_id = fields.Integer(string="ID Catégorie SAH")

    
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
                barcode = produit_api.get('Barcode', '')
                weight = produit_api.get('Weight', 0.0)
                type_sah = produit_api.get('InventoryMethod')

                # Ajout des tax
                list_prices = produit_api['Prices']
                if list_prices:
                    for line in list_prices:
                        if line['BrandTaxRate'] > 0:
                            tax_sah = self.env['tax.sah'].search([('amount','=',line['BrandTaxRate'])])
                            if not tax_sah:
                                self.env['tax.sah'].create({
                                    'name':f'Taxe {line['BrandTaxRate']}%',
                                    'amount':line['BrandTaxRate']
                                })
                #
                
                existing_product = self.env['product.template'].search([('produit_sah_id', '=', sah_id)], limit=1)
                
                if not existing_product:
                    if barcode and self.env['product.template'].search([('barcode', '=', barcode)]):
                        _logger.warning(f"Code-barres déjà utilisé : {barcode} pour le produit {name}")
                        barcode = None
                    
                    product_data = {
                        'name': name,
                        'default_code': reference,
                        'list_price': price,
                        'description_sale': description,
                        'weight': weight,
                        'produit_sah_id': sah_id,
                        'is_storable': True if type_sah == 1 else False,
                    }
                    
                    if barcode:
                        product_data['barcode'] = barcode
                    
                    self.env['product.template'].create(product_data)
                    _logger.info(f"Le produit {name} est créé avec succès")
        else:
            _logger.error(f"Connexion à l'API échouée : {post_response_produit.status_code}")


    # def  update_article_AttachedProducts_sah_odoo(self):
    #     article_ids = self.env['product.template'].search([('produit_sah_id','!=',None)])
        
    #     headers = self.env['authentication.sah'].establish_connection()
    #     for article in article_ids:
    #         _logger.info('============ produit_sah_id =============== %s',article.produit_sah_id)
    #         url_produit = f"https://demoapi.sellingathome.com/v1/Products/{article.produit_sah_id}"

    #         get_response_produit = requests.get(url_produit,headers=headers)
    #         if get_response_produit.status_code == 200:

    #             response_data_produit = get_response_produit.json()
                
    #             if response_data_produit['ProductType'] == 20:
    #                 combo_ids = []
    #                 ProductComponents = response_data_produit['ProductComponents']
    #                 if ProductComponents:
    #                     for p in ProductComponents[0]:
    #                         for c in p['ProductComponentProducts']:
    #                             p_id = self.env['product.template'].search([('produit_sah_id','=',c['ProductId'])])
    #                             if p_id:
    #                                 comb_id = self.env['product.combo'].search([('name','=',p['Name'])],limit=1)
    #                                 if comb_id:
    #                                     self.env['product.combo.item'].create({
    #                                         'combo_id':comb_id.id,
    #                                         'product_id':p_id.product_variant_id.id
    #                                     })
    #                                 else:
    #                                     comb = self.env['product.combo'].create({
    #                                         'name':p['Name'],
    #                                         'combo_ids':[{'product_id':p_id.product_variant_id.id}]
    #                                     })
    #                                     if comb :
    #                                         combo_ids.append(comb.id)
    #                 _logger.info('00000000 ProductComponents 1111111 %s',ProductComponents)
    #                 article.sudo().write({'type':'combo','combo_ids':combo_ids})

    def update_article_AttachedProducts_sah_odoo(self):
        article_ids = self.env['product.template'].search([('produit_sah_id', '!=', None)])
        headers = self.env['authentication.sah'].establish_connection()

        for article in article_ids:
            _logger.info('============ produit_sah_id =============== %s', article.produit_sah_id)

            url_produit = f"https://demoapi.sellingathome.com/v1/Products/{article.produit_sah_id}"
            get_response_produit = requests.get(url_produit, headers=headers)

            if get_response_produit.status_code != 200:
                _logger.warning('Échec de récupération du produit SAH ID %s', article.produit_sah_id)
                continue

            response_data_produit = get_response_produit.json()
            if response_data_produit.get('ProductType') != 20:
                continue

            combo_ids = []
            product_components = response_data_produit.get('ProductComponents', [])
            if product_components:
                for component in product_components:
                    for c in component.get('ProductComponentProducts', []):
                        p_id = self.env['product.template'].search([('produit_sah_id', '=', c['ProductId'])], limit=1)
                        if not p_id:
                            _logger.warning("Produit avec SAH ID %s non trouvé dans Odoo", c['ProductId'])
                            continue

                        combo_name = component.get('Name')
                        comb_id = self.env['product.combo'].search([('name', '=', combo_name)], limit=1)

                        if comb_id:
                            j=0
                            for c in comb_id.combo_item_ids:
                                if c.product_id.id == p_id.product_variant_id.id:
                                    j +=1
                            if j==0:
                                self.env['product.combo.item'].create({
                                    'combo_id': comb_id.id,
                                    'product_id': p_id.product_variant_id.id
                                })
                        else:
                            comb = self.env['product.combo'].create({
                                'name': combo_name,
                            })
                            self.env['product.combo.item'].create({
                                'combo_id': comb.id,
                                'product_id': p_id.product_variant_id.id
                            })
                            combo_ids.append(comb.id)

            _logger.info('ProductComponents récupérés pour produit ID %s : %s', article.produit_sah_id, product_components)
            article.sudo().write({
                'type': 'combo',
                'combo_ids': [(6, 0, combo_ids)]
            })

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
        headers = self.env['authentication.sah'].establish_connection()
        url_produit = f"https://demoapi.sellingathome.com/v1/Products"
       
        response = requests.get(url_produit, headers=headers, timeout=120)
        if response.status_code == 200:
            datas = response.json()
            for data in datas:
                product = self.env['product.template'].search([('produit_sah_id','=',data.get('Id'))])
                if product:
                    if data.get('AttachedProducts'):
                        upload = {
                            'product_tmpl_id':product.id,
                            'type':'phantom'
                        }
                        nommencalture = self.env['mrp.bom'].create(upload)

                        for bom in  data.get('AttachedProducts'):
                            _logger.info('================================ %s',bom)
                            product_rattache = self.env['product.template'].search([('produit_sah_id','!=',bom.get('ProductId'))],limit=1)
                            line = self.env['mrp.bom.line'].search([('bom_id','=',nommencalture.id),('product_id','=',product_rattache.product_variant_id.id)])
                            if not line:
                                if product_rattache:
                                    upload2 = {
                                        'bom_id':nommencalture.id,
                                        'product_tmpl_id':product_rattache.id,
                                        'product_id':product_rattache.product_variant_id.id,
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

