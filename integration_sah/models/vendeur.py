# -*- coding: utf-8 -*-
from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class vendeur(models.Model):
    _inherit = "res.users"

    id_vendeur_sah = fields.Char(string='Id vendeur SAH')
    type_revendeur = fields.Selection([
        ('vendeur_domicile', 'VENDEUR À DOMICILE INDÉPENDANT'),
        ('vdi', 'VDI INSCRIT AU RCS'),
        ('auto_entrepreneur', 'AUTO-ENTREPRENEUR'),
        ('agent_commercial', 'AGENT COMMERCIAL')
    ], string='Type Revendeur')

    _sql_constraints = [
        ('id_vendeur_sah_unique', 'unique(id_vendeur_sah)', 'Le champ "Id vendeur SAH" doit être unique.'),
    ]
    def get_update_client_sah(self):
        headers_client = self.env['authentication.sah'].establish_connection()
        url_client = "https://demoapi.sellingathome.com/v1/Customers"
        response2 = requests.get(url_client, headers=headers_client)
        if response2.status_code == 200:
            clients_data = response2.json()
            for clients_sah in clients_data:
                client_odoo = self.env['res.partner'].search(['|',('id_client_sah','=',clients_sah['Id']),('email','=',clients_sah['Email'])])
                vendeur_id = self.env['res.users'].search([('id_vendeur_sah','=',clients_sah['SellerId'])])
                campany = self.create({ 'company_type':'company','name' :clients_sah['CompanyName']}).id if clients_sah['CompanyName'] else None
                pays = self.env['res.country'].search([('code','=',clients_sah['CountryIso'])]).id if clients_sah['CountryIso'] else None
                if not client_odoo:
                    self.create({
                        'id_client_sah':clients_sah['Id'],
                        'user_id':vendeur_id.id or False,
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
                    client_odoo.write({
                        'id_client_sah':clients_sah['Id'],
                        'user_id':vendeur_id.id or False,
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

   
    def recuperation_vendeurs_sah_vers_odoo(self):
        headers = self.env['authentication.sah'].establish_connection()
        url = 'https://demoapi.sellingathome.com/v1/Sellers'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            datas = response.json()
            for data in datas:
                print('PPPPPPPPP',data)
                pays=self.env['res.country'].search([('code','=',data['CountryIso'])])
                contact = self.env['res.users'].search([('login','=',data['Email'])])
                active_lang = self.env['res.lang'].search([('iso_code','=',data['Language']['ISOValue'])], limit=1)
                if active_lang:
                    active_lang.write({
                        'active':True
                    })
                if contact:
                    type_revendeur = (
                        'vdi' if data['CompanyStatus'] == 15 else
                        'agent_commercial' if data['CompanyStatus'] == 30 else
                        'auto_entrepreneur' if data['CompanyStatus'] == 20 else
                        'vendeur_domicile' if data['CompanyStatus'] == 10 else
                        None
                    )
                    _logger.info('@@@@@@@@ssssssssssss %s',data['Email'])
                    contact.write({
                        'id_vendeur_sah':data['Id'],
                        'phone':data['Phone'],
                        'type_revendeur':type_revendeur,
                        'name':data['FirstName']+' '+data['LastName'],
                        'mobile':data['MobilePhone'],
                        'street':data['StreetAddress'],
                        'street2':data['StreetAddress2'],
                        'zip':data['Postcode'],
                        'city':data['City'],
                        'partner_latitude':data['Latitude'],
                        'partner_longitude':data['Longitude'],
                        'company_name':data['CompanyName'],
                        'country_id':pays.id if pays else None,
                        'lang':active_lang.code,
                        'vat':data['CompanyVAT'],
                        'email': data['Email'],
                        # 'ImageUrl':data[''],
                        # 'Status':data[''],
                        # 'StatusForever':data[''],
                        # 'CandidacyId':data[''],
                        # 'EmailIsFlagged':data[''],
                        # 'Birthdate':data[''],
                        # 'BirthPlace':data[''],
                        # 'ParentSeller':data[''],
                        # 'AnimatorSeller':data[''],
                        # 'CustomerAccount':data[''],
                        # 'NationalIdentificationNumber':data[''],
                        # 'IdentityCardNumber':data[''],
                        # 'Nationality':data[''],
                        # 'CompanyStatus':data[''],
                        # 'CompanyIdentificationNumber':data[''],
                        # 'SocialContributionsType':data[''],
                        # 'StartContractDate':data[''],
                        # 'EndContractDate':data[''],
                        # 'StartActivityDate':data[''],
                        # 'RemoteStatus':data[''],
                        # 'CreateCustomerAccount':data[''],
                        # 'Brand':data[''],
                        # 'Roles':data[''],
                        # 'AdditionalInformations':data[''],
                        # 'AccountBankCode':data[''],
                        # 'AccountWicketCode':data[''],
                        # 'AccountNumber':data[''],
                        # 'AccountKey':data[''],
                        # 'AccountIban'('id_vendeur_sah','=',data['Id']),:data[''],
                        # 'AccountSwiftCode':data[''],
                        # 'BankName':data[''],
                        # 'BankingDomiciliation':data[''],
                        # 'BankAccountOwner':data[''],
                        # 'GdprAccepted':data[''],
                        # 'AuthorizeSellerDeliveryModeOnEcommerce':data[''],
                        # 'GdprLastAcceptedDate':data[''],
                        # 'Photo':data[''],
                        # 'TimeZone':data[''],
                        # 'Signature':data[''],
                        # 'MiniSiteUrl':data[''],
                        # 'MiniSiteUsername':data[''],
                        # 'MiniSiteIsActive':data[''],
                    })
                else:
                    type_revendeur = (
                        'vdi' if data['CompanyStatus'] == 15 else
                        'agent_commercial' if data['CompanyStatus'] == 30 else
                        'auto_entrepreneur' if data['CompanyStatus'] == 20 else
                        'vendeur_domicile' if data['CompanyStatus'] == 10 else
                        None
                    )
       
                    contact.create({
                    'id_vendeur_sah':data['Id'],
                    'name':data['FirstName']+' '+data['LastName'],
                    'login':data['Email'],
                    'type_revendeur':type_revendeur,
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                    'phone':data['Phone'],
                    'mobile':data['MobilePhone'],
                    'street':data['StreetAddress'],
                    'street2':data['StreetAddress2'],
                    'zip':data['Postcode'],
                    'city':data['City'],
                    'partner_latitude':data['Latitude'],
                    'partner_longitude':data['Longitude'],
                    'company_name':data['CompanyName'],
                    'country_id':pays.id if pays else None,
                    'lang':active_lang.code,
                    'vat':data['CompanyVAT'],
                    'email': data['Email'],
                    # 'ImageUrl':data[''],
                    # 'Status':data[''],
                    # 'StatusForever':data[''],
                    # 'CandidacyId':data[''],
                    # 'EmailIsFlagged':data[''],
                    # 'Birthdate':data[''],
                    # 'BirthPlace':data[''],
                    # 'ParentSeller':data[''],
                    # 'AnimatorSeller':data[''],
                    # 'CustomerAccount':data[''],
                    # 'NationalIdentificationNumber':data[''],
                    # 'IdentityCardNumber':data[''],
                    # 'Nationality':data[''],
                    # 'CompanyStatus':data[''],
                    # 'CompanyIdentificationNumber':data[''],
                    # 'SocialContributionsType':data[''],
                    # 'StartContractDate':data[''],
                    # 'EndContractDate':data[''],
                    # 'StartActivityDate':data[''],
                    # 'RemoteStatus':data[''],
                    # 'CreateCustomerAccount':data[''],
                    # 'Brand':data[''],
                    # 'Roles':data[''],
                    # 'AdditionalInformations':data[''],
                    # 'AccountBankCode':data[''],
                    # 'AccountWicketCode':data[''],
                    # 'AccountNumber':data[''],
                    # 'AccountKey':data[''],
                    # 'AccountIban':data[''],
                    # 'AccountSwiftCode':data[''],
                    # 'BankName':data[''],
                    # 'BankingDomiciliation':data[''],
                    # 'BankAccountOwner':data[''],
                    # 'GdprAccepted':data[''],
                    # 'AuthorizeSellerDeliveryModeOnEcommerce':data[''],
                    # 'GdprLastAcceptedDate':data[''],
                    # 'Photo':data[''],
                    # 'TimeZone':data[''],
                    # 'Signature':data[''],, limit=1, limit=1
                    # 'MiniSiteUrl':data[''],
                    # 'MiniSiteUsername':data[''],
                    # 'MiniSiteIsActive':data[''],
                })

        else:
            _logger.info("==================================Erreur: %s ==========================",  response.text)