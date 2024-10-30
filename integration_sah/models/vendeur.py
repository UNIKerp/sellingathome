# -*- coding: utf-8 -*-
from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

class vendeur(models.Model):
    _inherit = "res.users"

    id_vendeur_sah = fields.Char(string='Id vendeur SAH')
    status = fields.Char(string='Nom du statut')
    Statut_pour_toujours = fields.Char(string="Statut permanent")
    isActive = fields.Boolean(string='Vendeur Actif')
    candidacyId =fields.Integer(string="ID de candidature")
    emailIsFlagged = fields.Boolean(string="État de l'e-mail du vendeur")
    birthdate = fields.Date(string="Date de naissance du vendeur")
    birthPlace = fields.Char(string="Lieu de naissance du vendeur")
    parentSeller = fields.Integer(string="Vendeur parent rattaché au vendeur")
    animatorSeller = fields.Interger(string="Vendeur Animateur")
    customerAccount = fields.Integer(string="ID de compte client du vendeur")
    nationalIdentificationNumber = fields.Char(string="Numéro d'identification national du vendeur")
    identityCardNumber = fields.Char(string="Numéro de carte d'identité du vendeur")
    nationalité =fields.Char(string="Nationalité du vendeur")
    miniSiteIsActive = fields.Boolean(string='Le mini-site est actif')
    miniSiteUsername = fields.Char(string="Nom d'utilisateur du minisite")
    miniSiteUrl = fields.Char(string='URL du mini-site')
    signature = fields.Char(string='Signature du vendeur')
    timeZone = fields.Many2one('time.zone', string='vendeur TimeZone')
    photo = fields.Char(string='URL de la photo du vendeur')
    gdprLastAcceptedDate = fields.Date(string='Date de la dernière acceptation du RGPD')
    authorizeSellerDeliveryModeOnEcommerce = fields.Boolean(string='Autoriser le mode de livraison du vendeur sur le commerce électronique')
    gdprAccepted = fields.Boolean(string='Accepté par le RGPD')
    bankAccountOwner = fields.Char(string='Titulaire du compte bancaire')
    bankingDomiciliation = fields.Char(string='Domiciliation bancaire')
    bankName = fields.Char(string='Nom de la banque')
    accountSwiftCode = fields.Char(string='Code Swift du compte')
    accountIban = fields.Char(string='Compte Iban')
    accountKey = fields.Char(string='Clé de compte')
    accountNumber = fields.Char(string='Numéro de compte')
    accountWicketCode = fields.Char(string='Code de guichet de compte')
    accountBankCode = fields.Char(string='Code bancaire du compte')
    additionalInformations = fields.Text(string='Informations complémentaires du vendeur ')
    brand = fields.Integer(string='Marque attachée au vendeur')
    createCustomerAccount = fields.Boolean(string='Créer un compte client pour le vendeur (vrai ou faux)')
    remoteStatus = fields.Boolean(string='Le mini-site est actif')
    startActivityDate = fields.Date(string='Date de début du contrat du vendeur')
    endContractDate = fields.Date(string='Date de fin du contrat du vendeur')
    startContractDate = fields.Boolean(string='Le mini-site est actif')
    socialContributionsType = fields.Integer(string='Type de cotisations sociales du vendeur')
    companyRCSNumber = fields.Char(string='Numéro RCS de la société vendeuse')
    companyVAT = fields.Char(string='TVA de la société vendeuse')
    companyIdentificationNumber = fields.Char(string="Numéro d'identification de l'entreprise du vendeur")

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