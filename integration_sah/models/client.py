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


    id_client_sah = fields.Integer("ID client SAH",copy=False, help="l'ID du client dans SAH")
    id_vendeur_sah = fields.Integer(string='ID vendeur SAH',copy=False, help="l'ID du vendeur dans SAH")
    type_revendeur = fields.Selection([
        ('vendeur_domicile', 'VENDEUR À DOMICILE INDÉPENDANT'),
        ('vdi', 'VDI INSCRIT AU RCS'),
        ('auto_entrepreneur', 'AUTO-ENTREPRENEUR'),
        ('agent_commercial', 'AGENT COMMERCIAL')
    ], string='Type Revendeur' , help="Type de revendeur SAH")
    vdi_id = fields.Many2one('res.partner',string="VDI", help="VDI ratacher au contact")
    client_sah=fields.Selection([('client','CLIENT'),('vdi','VDI')], string="Type Client" , help="si c'est un client ou un vdi")
    ref_sah = fields.Char('')
   
    companyIdentificationNumber = fields.Char(string="Numéro d'identification de l'entreprise cliente",help="Numéro d'identification de l'entreprise cliente")
    sellerId = fields.Integer(string="Identifiant du vendeur principal du client",help="Identifiant du vendeur principal du client")
    hostedMeeting = fields.Boolean(string="A déjà accueilli une réunion",help="A déjà accueilli une réunion")
    participedMeeting = fields.Boolean(string="A déjà participé à une réunion",help="A déjà participé à une réunion")
    hasOrdered = fields.Boolean(string='A déjà commandé',help='A déjà commandé')
    consent = fields.Boolean(string='Consentement du client',help='Consentement du client')
    ConsentDt = fields.Boolean(string="date du Consentement du client",help="date du Consentement du client")
    CustomQuestionAnswers = fields.Char(string='Réponses en question',help="Réponses en question")
    
    # Les champs du du vendeur
    status = fields.Char(string='Nom du statut',help='Nom du statut')
    statut_pour_toujours = fields.Char(string="Statut permanent",help='Statut permanent')
    isActive = fields.Boolean(string='Vendeur Actif',help='Vendeur Actif')
    candidacyId =fields.Integer(string="ID de candidature",help='ID de candidature')
    emailIsFlagged = fields.Boolean(string="État de l'e-mail du vendeur",help="État de l'e-mail du vendeur")
    birthdate = fields.Date(string="Date de naissance du vendeur",help="Date de naissance du vendeur")
    birthPlace = fields.Char(string="Lieu de naissance du vendeur",help="Lieu de naissance du vendeur")
    parentSeller = fields.Integer(string="Vendeur parent rattaché au vendeur",help="Vendeur parent rattaché au vendeur")
    animatorSeller = fields.Integer(string="Vendeur Animateur",help="Vendeur Animateur")
    customerAccount = fields.Integer(string="ID de compte client du vendeur",help="ID de compte client du vendeur")
    nationalIdentificationNumber = fields.Char(string="Numéro d'identification national du vendeur",help="Numéro d'identification national du vendeur")
    identityCardNumber = fields.Char(string="Numéro de carte d'identité du vendeur",help="Numéro de carte d'identité du vendeur")
    nationalite =fields.Char(string="Nationalité du vendeur",help="Nationalité du vendeur")
    miniSiteIsActive = fields.Boolean(string='Le mini-site est actif',help="Le mini-site est actif")
    miniSiteUsername = fields.Char(string="Nom d'utilisateur du minisite",help="Nom d'utilisateur du minisite")
    miniSiteUrl = fields.Char(string='URL du mini-site',help=" URL du mini-site")
    signature = fields.Char(string='Signature du vendeur',help="Signature du vendeur")
    # timeZone = fields.Many2one('time.zone', string='vendeur TimeZone',help="vendeur TimeZone")
    photo = fields.Char(string='URL de la photo du vendeur',help="URL de la photo du vendeur")
    gdprLastAcceptedDate = fields.Date(string='Date de la dernière acceptation du RGPD',help="Date de la dernière acceptation du RGPD")
    authorizeSellerDeliveryModeOnEcommerce = fields.Boolean(string='Autoriser le mode de livraison du vendeur sur le commerce électronique',hel="Autoriser le mode de livraison du vendeur sur le commerce électronique")
    gdprAccepted = fields.Boolean(string='Accepté par le RGPD',help="Accepté par le RGPD")
    bankAccountOwner = fields.Char(string='Titulaire du compte bancaire',help="Titulaire du compte bancaire")
    bankingDomiciliation = fields.Char(string='Domiciliation bancaire',help="Domiciliation bancaire")
    bankName = fields.Char(string='Nom de la banque',help="Nom de la banque")
    accountSwiftCode = fields.Char(string='Code Swift du compte',help="Code Swift du compte")
    accountIban = fields.Char(string='Compte Iban',help='Compte Iban')
    accountKey = fields.Char(string='Clé de compte',help="Clé de compte")
    accountNumber = fields.Char(string='Numéro de compte',help="Numéro de compte")
    accountWicketCode = fields.Char(string='Code de guichet de compte',help="Code de guichet de compte")
    accountBankCode = fields.Char(string='Code bancaire du compte',help="Code bancaire du compte")
    additionalInformations = fields.Text(string='Informations complémentaires du vendeur',help="Informations complémentaires du vendeur")
    brand = fields.Integer(string='Marque attachée au vendeur',help="Marque attachée au vendeur")
    createCustomerAccount = fields.Boolean(string='Créer un compte client pour le vendeur',help="Créer un compte client pour le vendeur")
    remoteStatus = fields.Boolean(string='Le mini-site est actif',help="Le mini-site est actif")
    startActivityDate = fields.Date(string='Date de début du contrat du vendeur',help="Date de début du contrat du vendeur")
    endContractDate = fields.Date(string='Date de fin du contrat du vendeur',help="Date de fin du contrat du vendeur")
    startContractDate = fields.Boolean(string='Le mini-site est actif',help="Le mini-site est actif")
    socialContributionsType = fields.Integer(string='Type de cotisations sociales du vendeur',help='Type de cotisations sociales du vendeur')
    companyRCSNumber = fields.Char(string='Numéro RCS de la société vendeuse',help="Numéro RCS de la société vendeuse")
    companyVAT = fields.Char(string='TVA de la société vendeuse',help="TVA de la société vendeuse")
    companyIdentificationNumbervendeur= fields.Char(string="Numéro d'identification de l'entreprise du vendeur",help="Numéro d'identification de l'entreprise du vendeur")

    _sql_constraints = [
        ('id_client_sah_uniq', 'unique (id_client_sah)', "ID client SAH already exists !"),
        ('ref_sah_unique', 'unique(ref_sah)', 'Le champ Reference SAH doit être unique !'),
        ]
    
    def copy(self, default=None):
        default = dict(default or {})
        default['ref_sah'] = ''
        default['id_client_sah'] = 0
        default['id_vendeur_sah'] = 0
        # Appeler la méthode copy du parent pour créer la copie avec les valeurs par défaut
        return super(ClientSAH, self).copy(default)
    
    # Fonction maj des donnéés de SAH 
    def _update_infos_customers_and_sellers_and_commandes(self):
        job_kwargs_customers = {
            "description": "Mise à jour et création de nouveaux clients s'ils existent de SAH vers Odoo",
        }
        job_kwargs_sellers = {
            "description": "Mise à jour et création de nouveaux vendeurs s'ils existent de SAH vers Odoo",
        }
        job_kwargs_commandes = {
            "description": "Mise à jour et création de nouveaux commandes s'ils existent de SAH vers Odoo",
        }
        self.with_delay(**job_kwargs_sellers).recuperation_vendeurs_sah_vers_odoo()
        self.with_delay(**job_kwargs_customers).get_update_client_sah()
        self.env['sale.order'].with_delay(**job_kwargs_commandes).get_commande()
        
    def get_update_client_sah(self):
        _logger.info("======================= Debut de mise à jour des clients")
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
                monsieur=self.env['res.partner.title'].search([('id','=',3)])
                mademaselle=self.env['res.partner.title'].search([('id','=',1)])
                madame=self.env['res.partner.title'].search([('id','=',2)])
                gender = (
                        monsieur.id if clients_sah['Gender'] == 0 else
                        mademaselle.id if clients_sah['Gender'] == 1 else
                        madame.id if clients_sah['Gender'] == 2 else
                        None
                    )
                if not client_odoo:
                    parent = self.create({
                        'id_client_sah':clients_sah['Id'],
                        'vdi_id':vendeur_id.id or False,
                        'client_sah':'client',
                        'ref_sah':ref_sah,
                        'title':gender,
                        'sellerId':clients_sah['SellerId'],
                        'name':clients_sah['Firstname']+'  '+clients_sah['Lastname'],
                        'email':clients_sah['Email'],
                        'phone':clients_sah['Phone'],
                        'mobile':clients_sah['MobilePhone'],
                        'ref':clients_sah['CustomerReference'],
                        'parent_id':campany,
                        'companyIdentificationNumber':clients_sah['CompanyIdentificationNumber'],
                        'vat':clients_sah['CompanyVAT'],
                        'street':clients_sah['StreetAddress'],
                        'street2':clients_sah['StreetAddress2']+','+clients_sah['StreetAddress3'] if clients_sah['StreetAddress3']!="" else clients_sah['StreetAddress2'],
                        'zip':clients_sah['Postcode'],
                        'city':clients_sah['City'],
                        'country_id':pays,
                        'partner_latitude':clients_sah['Latitude'],
                        'partner_longitude':clients_sah['Longitude'],
                        'country_code':clients_sah['CountryIso'],
                        'hostedMeeting':clients_sah['HostedMeeting'],
                        'participedMeeting':clients_sah['ParticipedMeeting'],
                        'participedMeeting':clients_sah['HasOrdered'],
                        'consent':clients_sah['Consent'],
                        'ConsentDt':clients_sah['ConsentDt'],
                        'CustomQuestionAnswers':clients_sah['CustomQuestionAnswers'],

                        })
                    delivery_address = self.env['res.partner'].create({
                        'name': 'Adresse de livraison' + ' ' + clients_sah['Firstname']+'  '+clients_sah['Lastname'],
                        'street': clients_sah['StreetAddress'],
                        'street2':clients_sah['StreetAddress2']+','+clients_sah['StreetAddress3'] if clients_sah['StreetAddress3']!="" else clients_sah['StreetAddress2'],
                        'city': clients_sah['City'],
                        'zip': clients_sah['Postcode'],
                        'country_id': pays,
                        'type': 'delivery',  
                        'parent_id': parent.id,
                    })
                else:
                    client_odoo.write({
                        'id_client_sah':clients_sah['Id'],
                        'vdi_id':vendeur_id.id or False,
                        'client_sah':'client',
                        'title':gender,
                        'sellerId':clients_sah['SellerId'],
                        'name':clients_sah['Firstname']+'  '+clients_sah['Lastname'],
                        'email':clients_sah['Email'],
                        'phone':clients_sah['Phone'],
                        'mobile':clients_sah['MobilePhone'],
                        'ref':clients_sah['CustomerReference'],
                        'parent_id':campany,
                        'companyIdentificationNumber':clients_sah['CompanyIdentificationNumber'],
                        'vat':clients_sah['CompanyVAT'],
                        'street':clients_sah['StreetAddress'],
                        'street2':clients_sah['StreetAddress2']+','+clients_sah['StreetAddress3'] if clients_sah['StreetAddress3']!="" else clients_sah['StreetAddress2'],
                        'zip':clients_sah['Postcode'],
                        'city':clients_sah['City'],
                        'country_id':pays,
                        'partner_latitude':clients_sah['Latitude'],
                        'partner_longitude':clients_sah['Longitude'],
                        'country_code':clients_sah['CountryIso'],
                        'hostedMeeting':clients_sah['HostedMeeting'],
                        'hostedMeeting':clients_sah['ParticipedMeeting'],
                        'hostedMeeting':clients_sah['HasOrdered'],
                        'consent':clients_sah['Consent'],
                        'ConsentDt':clients_sah['ConsentDt'],
                        'CustomQuestionAnswers':clients_sah['CustomQuestionAnswers'],

                        })
            _logger.info("==================================Résultat: %s ==========================", json.dumps(clients_data, indent=4))
        else:
            _logger.info("==================================Erreur: %s ==========================",  response2.text)
        _logger.info("======================= Fin de mise à jour des Clients")

    def recuperation_vendeurs_sah_vers_odoo(self):
        _logger.info("======================= Debut de mise à jour des vendeurs")
        headers = self.env['authentication.sah'].establish_connection()
        url = 'https://demoapi.sellingathome.com/v1/Sellers'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            datas = response.json()
            for data in datas:
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
                monsieur=self.env['res.partner.title'].search([('id','=',3)])
                mademaselle=self.env['res.partner.title'].search([('id','=',1)])
                madame=self.env['res.partner.title'].search([('id','=',2)])
                gender = (
                        monsieur.id if data['Gender'] == 0 else
                        mademaselle.id if data['Gender'] == 1 else
                        madame.id if data['Gender'] == 2 else None
                    )
                if contact:
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
                        'email': data['Email'],
                        'isActive':data['IsActive'],
                        'title':gender,
                        'status':data['Status'],
                        'statut_pour_toujours':data['StatusForever'],
                        'candidacyId':data['CandidacyId'],
                        'emailIsFlagged':data['EmailIsFlagged'],
                        'birthdate':data['Birthdate'],
                        'birthPlace':data['BirthPlace'],
                        'parentSeller':data['ParentSeller'],
                        'animatorSeller':data['AnimatorSeller'],
                        'customerAccount':data['CustomerAccount'],
                        'nationalIdentificationNumber':data['NationalIdentificationNumber'],
                        'identityCardNumber':data['IdentityCardNumber'],
                        'nationalite':data['Nationality'],
                        'companyIdentificationNumber':data['CompanyIdentificationNumber'],
                        'socialContributionsType':data['SocialContributionsType'],
                        'startContractDate':data['StartContractDate'],
                        'endContractDate':data['EndContractDate'],
                        'startActivityDate':data['StartActivityDate'],
                        'remoteStatus':data['RemoteStatus'],
                        'createCustomerAccount':data['CreateCustomerAccount'],
                        'brand':data['Brand'],
                        'additionalInformations':data['AdditionalInformations'],
                        'accountBankCode':data['AccountBankCode'],
                        'accountWicketCode':data['AccountWicketCode'],
                        'accountNumber':data['AccountNumber'],
                        'accountKey':data['AccountKey'],
                        'accountIban':data['AccountIban'],
                        'accountSwiftCode':data['AccountSwiftCode'],
                        'bankName':data['BankName'],
                        'bankingDomiciliation':data['BankingDomiciliation'],
                        'bankAccountOwner':data['BankAccountOwner'],
                        'gdprAccepted':data['GdprAccepted'],
                        'authorizeSellerDeliveryModeOnEcommerce':data['AuthorizeSellerDeliveryModeOnEcommerce'],
                        'gdprLastAcceptedDate':data['GdprLastAcceptedDate'],
                        'photo':data['Photo'],
                        'companyIdentificationNumbervendeur':data['CompanyIdentificationNumber'],
                        'signature':data['Signature'],
                        'miniSiteUrl':data['MiniSiteUrl'],
                        'miniSiteUsername':data['MiniSiteUsername'],
                        'miniSiteIsActive':data['MiniSiteIsActive'],
                        'companyRCSNumber':data['CompanyRCSNumber'],
                        'companyVAT':data['CompanyVAT'],
                    })
                else:
       
                    parent = contact.create({
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
                        'email': data['Email'],
                        'status':data['Status'],
                        'statut_pour_toujours':data['StatusForever'],
                        'candidacyId':data['CandidacyId'],
                        'emailIsFlagged':data['EmailIsFlagged'],
                        'birthdate':data['Birthdate'],
                        'birthPlace':data['BirthPlace'],
                        'parentSeller':data['ParentSeller'],
                        'animatorSeller':data['AnimatorSeller'],
                        'customerAccount':data['CustomerAccount'],
                        'nationalIdentificationNumber':data['NationalIdentificationNumber'],
                        'identityCardNumber':data['IdentityCardNumber'],
                        'nationalite':data['Nationality'],
                        # 'CompanyStatus':data[''],
                        'companyIdentificationNumber':data['CompanyIdentificationNumber'],
                        'socialContributionsType':data['SocialContributionsType'],
                        'startContractDate':data['StartContractDate'],
                        'endContractDate':data['EndContractDate'],
                        'startActivityDate':data['StartActivityDate'],
                        'remoteStatus':data['RemoteStatus'],
                        'createCustomerAccount':data['CreateCustomerAccount'],
                        'brand':data['Brand'],
                        'additionalInformations':data['AdditionalInformations'],
                        'accountBankCode':data['AccountBankCode'],
                        'accountWicketCode':data['AccountWicketCode'],
                        'accountNumber':data['AccountNumber'],
                        'accountKey':data['AccountKey'],
                        'accountIban':data['AccountIban'],
                        'accountSwiftCode':data['AccountSwiftCode'],
                        'bankName':data['BankName'],
                        'bankingDomiciliation':data['BankingDomiciliation'],
                        'bankAccountOwner':data['BankAccountOwner'],
                        'gdprAccepted':data['GdprAccepted'],
                        'authorizeSellerDeliveryModeOnEcommerce':data['AuthorizeSellerDeliveryModeOnEcommerce'],
                        'gdprLastAcceptedDate':data['GdprLastAcceptedDate'],
                        'photo':data['Photo'],
                        'signature':data['Signature'],
                        'miniSiteUrl':data['MiniSiteUrl'],
                        'miniSiteUsername':data['MiniSiteUsername'],
                        'miniSiteIsActive':data['MiniSiteIsActive'],
                        'companyRCSNumber':data['CompanyRCSNumber'],
                        'companyVAT':data['CompanyVAT'],
                        'companyIdentificationNumbervendeur':data['CompanyIdentificationNumber'],
                        'isActive':data['IsActive'],
                })
                delivery_address = self.env['res.partner'].create({
                    'name': 'Adresse de livraison' + ' '+  data['FirstName']+' '+data['LastName'],
                    'street': data['StreetAddress'],
                    'street2':data['StreetAddress2'],
                    'city': data['City'],
                    'zip': data['Postcode'],
                    'country_id': pays.id if pays else None,
                    'type': 'delivery',  
                    'parent_id': parent.id,
                })

        else:
            _logger.info("==================================Erreur: %s ==========================",  response.text)
            
        _logger.info("======================= Fin de mise à jour des vendeurs")
