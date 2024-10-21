from odoo import models, api, fields
import requests
import json


class ProduitSelligHome(models.Model):
    _inherit = "product.template"


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
            "ProductLangs": [
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
            print("Product created successfully:", post_response.json())
        else:
            print(f"Error {post_response.status_code}: {post_response.text}")

        return res