from odoo import models, api, fields
import requests
import json
from datetime import date


class ProduitSelligHome(models.Model):
    _inherit = "product.template"

    produit_sah_id = fields.Integer("ID Selling Home")


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
            res.produit_sah_id = product_id
            pricelist_id = self.env['product.price_list'].search([],limit=1)
            self.env['product.pricelist.item'].create({
                'pricelist_id': pricelist_id.id,
                'product_tmpl_id': res.id,
                'fixed_price': res.list_price,
                'min_quantity': 1,
                'date_start': date.today(),
                'date_end':  date.today(),
                # 'price_sah_id' : response_data.Prices[0]['Id']
            })
        else:
            print(f"Error {post_response.status_code}: {post_response.text}")
        return res

    def write(self, vals):
        product_id = self.produit_sah_id
        if product_id :
            url = f"https://demoapi.sellingathome.com/v1/Products/{product_id}"
            headers = self.env['authentication.sah'].establish_connection()

            product_data = {
                "ProductType": 5,
                "Reference": self.default_code,
                "Prices": [
                    {
                        "Id": product_id,
                        "BrandTaxRate": 2.1,
                        "BrandTaxName": self.name,
                        "TwoLetterISOCode": "FR",
                        "PriceExclTax": self.list_price,
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

            post_response = requests.put(url, json=product_data, headers=headers)
            if post_response.status_code == 200:
                print("Product created successfully:", post_response.json())
            else:
                print(f"Error {post_response.status_code}: {post_response.text}")

            res = super(ProduitSelligHome, self).write(vals)
            return res