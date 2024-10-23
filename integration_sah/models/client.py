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
    

    def get_client_sah(self):
        print("#####################")
        
        headers_client = self.env['authentication.sah'].establish_connection()

        url_client = "https://demoapi.sellingathome.com/v1/Customers"

        response2 = requests.get(url_client, headers=headers_client)
        
        if response2.status_code == 200:
            # Récupérer les données au format JSON
            clients_data = response2.json()  # Cela convertit la réponse en JSON
            
            print("########################",clients_data)
            for clients_sah in clients_data:
                
                print("########################",clients_sah['Id'])
                client_odoo = self.env['res.partner'].search([('id_client_sah','=',clients_sah['Id'])])
                if not client_odoo:
                    if clients_sah['CompanyName']:
                        campany = self.create({
                            'company_type':'company',
                            'name' :clients_sah['CompanyName'],
                        })
                        if clients_sah['CountryIso']:
                            pays = self.env['res.country'].search([('code','=',clients_sah['CountryIso'])])
                        self.create({
                            'id_client_sah':clients_sah['Id'],
                            #'':clients_sah['Gender'],
                            'name':clients_sah['Firstname']+'  '+clients_sah['Lastname'],
                            'email':clients_sah['Email'],
                            'phone':clients_sah['Phone'],
                            'mobile':clients_sah['MobilePhone'],
                            #'':clients_sah['Roles'],
                            'ref':clients_sah['CustomerReference'],
                            'parent_id':campany.name,
                            #'':clients_sah['CompanyIdentificationNumber'],
                            'vat':clients_sah['CompanyVAT'],
                            #'':clients_sah['TaxExempt'],
                            'street':clients_sah['StreetAddress'],
                            'street2':clients_sah['StreetAddress2'],
                            'zip':clients_sah['Postcode'],
                            'city':clients_sah['City'],
                            'country_id':pays.id,
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
                        if clients_sah['CountryIso']:
                            pays = self.env['res.country'].search([('code','=',clients_sah['CountryIso'])])
                        self.create({
                            'id_client_sah':clients_sah['Id'],
                            #'':clients_sah['Gender'],
                            'name':clients_sah['Firstname']+'  '+clients_sah['Lastname'],
                            'email':clients_sah['Email'],
                            'phone':clients_sah['Phone'],
                            'mobile':clients_sah['MobilePhone'],
                            #'':clients_sah['Roles'],
                            'ref':clients_sah['CustomerReference'],
                            #'':clients_sah['CompanyIdentificationNumber'],
                            'vat':clients_sah['CompanyVAT'],
                            #'':clients_sah['TaxExempt'],
                            'street':clients_sah['StreetAddress'],
                            'street2':clients_sah['StreetAddress2'],
                            'zip':clients_sah['Postcode'],
                            'city':clients_sah['City'],
                            'country_id':pays.id,
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
            # 
            print("************************", json.dumps(clients_data, indent=4))  # Formatage pour un affichage lisible

            return clients_data  # Vous pouvez également retourner les données pour un usage ultérieur
        else:
            print('Erreur lors de la récupération des clients:', response2.text)
            return None  # Retourne None en cas d'erreur


   
