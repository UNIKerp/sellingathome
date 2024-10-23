# -*- coding: utf-8 -*-
from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class vendeur(models.Model):
    _inherit = "res.partner"


    def recuperation_vendeurs_sah_vers_odoo(self):
        headers = self.env['authentication.sah'].establish_connection()
        url = 'https://demoapi.sellingathome.com/v1/Sellers'

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            datas = response.json()
            for data in datas:
                contact = self.env['res.partner'].search([('id_client_sah','=',data['Id'])])
                if contact:
                    vals = {
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
                        'company_name':data['CompanyName'],
                        'lang':data['Language']['ISOValue'],
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
                    }
                    _logger.info('============== Maj des données des vendeurs %s  ===========',vals)
                    contact.write(vals)
        else:
            _logger.info('Erreurrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr: %s', response.text)