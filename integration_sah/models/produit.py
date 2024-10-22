from odoo import models, api, fields
import requests
import json
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class ProduitSelligHome(models.Model):
    _inherit = "product.template"

    produit_sah_id = fields.Integer("ID produit SAH")


    @api.model
    def create(self, vals):
        # Create the product record in Odoo
        res = super(ProduitSelligHome, self).create(vals)
        url = "https://demoapi.sellingathome.com/v1/Products"
        headers = self.env['authentication.sah'].establish_connection()

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
            'ProductLangs': [
                {'Name': res.name, 
                'Description': res.description, 
                'ISOValue': 'fr'
                }
            ],
        }


        # Send POST request
        post_response = requests.post(url, json=product_data, headers=headers)

        # Check if the response was successful
        if post_response.status_code == 200:
            response_data = post_response.json()
            product_id = response_data.get('Id')
            _logger.info('=========================== %s',product_id)
            res.produit_sah_id = product_id
            _logger.info('=========================== %s',response_data)
            self.env['product.pricelist'].create({
                'name':f'Tarif du produit {res.name}',
                'price_list_sah_id':response_data['Prices'][0]['Id']
            })
        else:
            print(f"Error {post_response.status_code}: {post_response.text}")
        return res


    def write(self, vals):
        headers = self.env['authentication.sah'].establish_connection()
        if vals:
            ### Modification stock 
            #if vals.get('virtual_available') or vals.get('qty_availaible'):
            _logger.info("========================== %s%s",self.qty_available,self.virtual_available)
            url2 = 'https://demoapi.sellingathome.com/v1/Stocks'
            values = {
                "ProductId":  self.produit_sah_id,
                "ProductReference": self.default_code,
                "StockQuantity": int(self.qty_available),
                "StockQuantityComing":int(self.virtual_available),
            }
            response2 = requests.put(url2, headers=headers, json=values)
            if response2.status_code == 200:
                _logger.info("************************%s",self.virtual_available)  
            else:
                _logger.info(f"Erreur {response2.status_code}: {response2.text}")
            ####
            product_id = self.produit_sah_id
            if product_id :
                url = f"https://demoapi.sellingathome.com/v1/Products/{product_id}"
                

                product_data_upagate = {
                    "ProductType": 5,
                    "Reference": self.default_code,
                    "Prices": [
                        {
                            "Id": product_id,
                            "BrandTaxRate": 2.1,
                            "BrandTaxName": self.name,
                            "TwoLetterISOCode": "FR",
                            "PriceExclTax": self.list_price,
                            "PriceInclTax": self.list_price * (self.taxes_id.amount/100),
                            "ProductCost": self.standard_price,
                            "EcoTax": 8.1
                        }
                    ],
                    'ProductLangs': [
                        {'Name': self.name, 
                        'Description': self.description, 
                        'ISOValue': 'fr'
                        }
                    ],
                }
                    
                put_response = requests.put(url, json=product_data_upagate, headers=headers)
                if put_response.status_code == 200:
                    _logger.info("Product updated successfully:", put_response.json())
                else:
                    _logger.info(f"Error {put_response.status_code}: {put_response.text}")
                    
            rec = super(ProduitSelligHome, self).write(vals)
            return rec