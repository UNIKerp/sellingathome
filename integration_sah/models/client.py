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
    id_vendeur_sah = fields.Integer(string='ID vendeur SAH', help="l'ID du vendeur dans SAH")
    type_revendeur = fields.Selection([
        ('vendeur_domicile', 'VENDEUR À DOMICILE INDÉPENDANT'),
        ('vdi', 'VDI INSCRIT AU RCS'),
        ('auto_entrepreneur', 'AUTO-ENTREPRENEUR'),
        ('agent_commercial', 'AGENT COMMERCIAL')
    ], string='Type Revendeur' , help="Type de revendeur SAH")
    vdi_id = fields.Many2one('res.partner',string="VDI", help="VDI ratacher au contact")
    client_sah=fields.Selection([('client','CLIENT'),('vdi','VDI')], string="Type Client" , help="si c'est un client ou un vdi")
    ref_sah = fields.Char('')
    _sql_constraints = [
        ('id_client_sah_uniq', 'unique (id_client_sah)', "ID client SAH already exists !"),
        ('ref_sah_unique', 'unique(ref_sah)', 'Le champ Reference SAH doit être unique !'),
        ]


    def get_update_client_sah(self):
        headers_client = self.env['authentication.sah'].establish_connection()
        url_client = "https://demoapi.sellingathome.com/v1/Customers"
        response2 = requests.get(url_client, headers=headers_client)
        if response2.status_code == 200:
            clients_data = response2.json()
            for clients_sah in clients_data:
                # client_odoo = self.env['res.partner'].search(['|',('id_client_sah','=',clients_sah['Id']),('email','=',clients_sah['Email'])])
                client_odoo = self.env['res.partner'].search([('id_client_sah','=',clients_sah['Id'])])
                ref_vendeur = 'V'+str(clients_sah['SellerId'])
                ref_sah ='C'+str(clients_sah['Id'])
                vendeur_id = self.env['res.partner'].search([('ref_sah','=',ref_vendeur)])
                campany = self.create({ 'company_type':'company','name' :clients_sah['CompanyName']}).id if clients_sah['CompanyName'] else None
                pays = self.env['res.country'].search([('code','=',clients_sah['CountryIso'])]).id if clients_sah['CountryIso'] else None
                if not client_odoo:
                    self.create({
                        'id_client_sah':clients_sah['Id'],
                        'vdi_id':vendeur_id.id or False,
                        'client_sah':'client',
                        'ref_sah':ref_sah,
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
                        'vdi_id':vendeur_id.id or False,
                        'client_sah':'client',
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
                ref_sah= 'V'+str(data['Id'])
                pays=self.env['res.country'].search([('code','=',data['CountryIso'])])
                contact = self.env['res.partner'].search([('ref_sah','=',ref_sah)])
                active_lang = self.env['res.lang'].search([('iso_code','=',data['Language']['ISOValue'])], limit=1)
                if active_lang:
                    active_lang.write({
                        'active':True
                    })
                type_revendeur = (
                        'vdi' if data['CompanyStatus'] == 15 else
                        'agent_commercial' if data['CompanyStatus'] == 30 else
                        'auto_entrepreneur' if data['CompanyStatus'] == 20 else
                        'vendeur_domicile' if data['CompanyStatus'] == 10 else
                        None
                    )
                if contact:
                    
                    _logger.info('@@@@@@@@ssssssssssss %s',data['Email'])
                    contact.write({
                        'client_sah':'vdi',
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
       
                    contact.create({
                    'id_vendeur_sah':data['Id'],
                    'client_sah':'vdi',
                    'ref_sah':ref_sah,
                    'name':data['FirstName']+' '+data['LastName'],
                    'type_revendeur':type_revendeur,
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