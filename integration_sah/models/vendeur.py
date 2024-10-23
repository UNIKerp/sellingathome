# -*- coding: utf-8 -*-
from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class vendeur(models.Model):
    _inherit = "res.partner"


    def recuperation_veudeurs_sah_vers_odoo(self):
        headers = self.env['authentication.sah'].establish_connection()
        url = 'https://demoapi.sellingathome.com/v1/Sellers'

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            datas = response.json()
            for data in datas:
                contact = self.env['res.partner'].search([('id_client_sah','=',data['Id'])])
                if contact:
                    contact.write({
                        'id_client_sah':data['Id'],
                        'is_seller':True,
                        'active':data['IsActive'],
                        'name':data['FirstName']+'  '+data['LastName'],
                        'email':data['Email'],
                        'phone':data['Phone'],
                        'mobile':data['MobilePhone'],
                        'street':data['StreetAddress'],
                        'street2':data['StreetAddress2'],
                        'zip':data['Postcode'],
                        'city':data['City'],
                        'partner_latitude':data['Latitude'],
                        'partner_longitude':data['Longitude'],
                        'country_code':data['CountryIso'],
                        'company_name':data['CompanyName'],
                        'lang':data['Language']['ISOValue'],
                    })
                else:
                    contact.create({
                        'id_client_sah':data['Id'],
                        'is_seller':True,
                        'active':data['IsActive'],
                        'name':data['FirstName']+'  '+data['LastName'],
                        'email':data['Email'],
                        'phone':data['Phone'],
                        'mobile':data['MobilePhone'],
                        'street':data['StreetAddress'],
                        'street2':data['StreetAddress2'],
                        'zip':data['Postcode'],
                        'city':data['City'],
                        'partner_latitude':data['Latitude'],
                        'partner_longitude':data['Longitude'],
                        'country_code':data['CountryIso'],
                        'company_name':data['CompanyName'],
                        'lang':data['Language']['ISOValue'],
                        # '':data[''],
                        # '':data[''],
                        # '':data[''],
                        # '':data[''],
                        # '':data[''],
                        # '':data[''],
                        # '':data[''],
                        # '':data[''],
                        # '':data[''],

                    })
            
        else:
            _logger.info('Erreurrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr: %s', response.text)