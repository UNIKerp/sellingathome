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
    _inherit = "res.partner"
    _description = "client de SAH"


    id_client_sah = fields.Integer("ID client SAH", help="l'ID du client dans SAH")
    
    _sql_constraints = [
        ('id_client_sah_uniq', 'unique (id_client_sah)', "ID client SAH already exists !"), ]


    def get_update_client_sah(self):
        headers_client = self.env['authentication.sah'].establish_connection()
        url_client = "https://demoapi.sellingathome.com/v1/Customers"
        response2 = requests.get(url_client, headers=headers_client)
        if response2.status_code == 200:
            clients_data = response2.json()
            for clients_sah in clients_data:
                client_odoo = self.env['res.partner'].search([('id_client_sah','=',clients_sah['Id'])])
                vendeur_id = self.env['res.users'].search([('id_vendeur_sah','=',clients_sah['SellerId'])])
                campany = self.create({ 'company_type':'company','name' :clients_sah['CompanyName'], }).id if clients_sah['CompanyName'] else None
                pays = self.env['res.country'].search([('code','=',clients_sah['CountryIso'])]).id if clients_sah['CountryIso'] else None
                if not client_odoo:
                    self.create({
                        'id_client_sah':clients_sah['Id'],
                        'user_id':vendeur_id,
                        #'':clients_sah['Gender'],
                        #'id_vendeur_sah':clients_sah['SellerId'],
                        'name':clients_sah['Firstname']+'  '+clients_sah['Lastname'],
                        'email':clients_sah['Email'],
                        'phone':clients_sah['Phone'],
                        'mobile':clients_sah['MobilePhone'],
                        #'':clients_sah['Roles'],
                        'ref':clients_sah['CustomerReference'],
                        'parent_id':campany,
                        #'':clients_sah['CompanyIdentificationNumber'],
                        'vat':clients_sah['CompanyVAT'],
                        #'':clients_sah['TaxExempt'],
                        'street':clients_sah['StreetAddress'],
                        'street2':clients_sah['StreetAddress2']+','+clients_sah['StreetAddress3'] if clients_sah['StreetAddress3']!="" else clients_sah['StreetAddress2'],
                        'zip':clients_sah['Postcode'],
                        'city':clients_sah['City'],
                        'country_id':pays,
                        'partner_latitude':clients_sah['Latitude'],
                        'partner_longitude':clients_sah['Longitude'],
                        'country_code':clients_sah['CountryIso'],
                        #'':clients_sah['BrandFields'],
                        #'':clients_sah['SellerId'],
                        #'':clients_sah['HostedMeeting'],
                        #'':clients_sah['ParticipedMeeting'],
                        #'':clients_sah['HasOrdered'],
                        #'':clients_sah['Consent'],
                        #'':clients_sah['ConsentDt'],
                        #'':clients_sah['CustomQuestionAnswers'],

                        })
                else:
                    self.create({
                        'user_id':vendeur_id,
                        #'':clients_sah['Gender'],
                        #'id_vendeur_sah':clients_sah['SellerId'],
                        'email':clients_sah['Email'],
                        'phone':clients_sah['Phone'],
                        'mobile':clients_sah['MobilePhone'],
                        #'':clients_sah['Roles'],
                        'ref':clients_sah['CustomerReference'],
                        'parent_id':campany,
                        #'':clients_sah['CompanyIdentificationNumber'],
                        'vat':clients_sah['CompanyVAT'],
                        #'':clients_sah['TaxExempt'],
                        'street':clients_sah['StreetAddress'],
                        'street2':clients_sah['StreetAddress2']+','+clients_sah['StreetAddress3'] if clients_sah['StreetAddress3']!="" else clients_sah['StreetAddress2'],
                        'zip':clients_sah['Postcode'],
                        'city':clients_sah['City'],
                        'country_id':pays,
                        'partner_latitude':clients_sah['Latitude'],
                        'partner_longitude':clients_sah['Longitude'],
                        'country_code':clients_sah['CountryIso'],
                        #'':clients_sah['BrandFields'],
                        #'':clients_sah['SellerId'],
                        #'':clients_sah['HostedMeeting'],
                        #'':clients_sah['ParticipedMeeting'],
                        #'':clients_sah['HasOrdered'],
                        #'':clients_sah['Consent'],
                        #'':clients_sah['ConsentDt'],
                        #'':clients_sah['CustomQuestionAnswers'],

                        })
            _logger.info("==================================Résultat: %s ==========================", json.dumps(clients_data, indent=4))
        else:
            _logger.info("==================================Erreur: %s ==========================",  response2.text)
