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
    
    def recuperation_vendeurs_sah_vers_odoo(self):
        headers = self.env['authentication.sah'].establish_connection()
        url = 'https://demoapi.sellingathome.com/v1/Sellers'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            datas = response.json()
            for data in datas:
                pays=self.env['res.country'].search([('code','=',data['CountryIso'])])
                contact = self.env['res.users'].search([('login','=',data['Email'])])
                if contact:
                    type_revendeur = (
                        'vdi' if data['CompanyStatus'] == 15 else
                        'agent_commercial' if data['CompanyStatus'] == 30 else
                        'auto_entrepreneur' if data['CompanyStatus'] == 20 else
                        'vendeur_domicile' if data['CompanyStatus'] == 10 else
                        None
                    )
                    
                    contact.write({
                        'id_vendeur_sah':data['Id'],
                        'phone':data['Phone'],
                        'type_revendeur':type_revendeur,
                        'mobile':data['MobilePhone'],
                        'street':data['StreetAddress'],
                        'street2':data['StreetAddress2'],
                        'zip':data['Postcode'],
                        'city':data['City'],
                        'partner_latitude':data['Latitude'],
                        'partner_longitude':data['Longitude'],
                        'company_name':data['CompanyName'],
                        'country_id':pays.id if pays else None,
                        'lang':data['Language']['ISOValue']+'_'+data['Language']['ISOValue'].upper(),
                        'vat':data['CompanyVAT'],
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
                    print('RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR',data['Language']['ISOValue'])
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
                    'name':data['FirstName']+''+data['LastName'],
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
                    'lang':data['Language']['ISOValue']+'_'+data['Language']['ISOValue'].upper(),
                    'vat':data['CompanyVAT'],
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
                    # 'Signature':data[''],
                    # 'MiniSiteUrl':data[''],
                    # 'MiniSiteUsername':data[''],
                    # 'MiniSiteIsActive':data[''],
                })

        else:
            _logger.info("==================================Erreur: %s ==========================",  response2.text)