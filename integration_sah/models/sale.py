# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
import requests
from datetime import datetime
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaleLineSAH(models.Model):
    _inherit = "sale.order.line"

    id_order_line_sh = fields.Integer(string="ID Line de Commande SAH", copy=False, help="ID Line de Commande dans SAH")

    _sql_constraints = [
        ('id_order_line_sh_uniq', 'unique (id_order_line_sh)', "ID linr de commande SAH exists deja!"), ]
    

class SaleSAH(models.Model):
    _inherit = "sale.order"

    id_order_sh = fields.Integer(string="ID commande SAH", copy=False, help="ID de la Commande dans SAH")
    vdi = fields.Many2one('res.partner',string="Ambassadeur",help='le reveudeur vdi dans SAH')
    methode_paiement_id = fields.Many2one('methode.paiement.sah',string="Moyen de paiement",help='la Methode de paiement')
    paiement_ids = fields.One2many('paiement.sah','order_id',string="Paiement SAH",help='le paiement dans SAH')
    
    _sql_constraints = [
        ('id_order_sh_uniq', 'unique (id_order_sh)', "ID commande SAH exists deja!"), ]

    # Synchronisation des commandes de SAH vers Odoo
    def _synchronisation_commandes_job(self):
        url_commande = 'https://demoapi.sellingathome.com/v1/Orders'           
        headers = self.env['authentication.sah'].establish_connection()
        response = requests.get(url_commande, headers=headers)
        if response.status_code == 200:
            commandes_sah = response.json()
            for commande in commandes_sah:
                id_order = commande['Id']
                commandes_odoo = self.env['sale.order'].search([('id_order_sh','=',id_order)])
                _logger.info('======================================== %s',commandes_odoo)
                if not commandes_odoo:
                    job_kwargs_commandes = {
                        "description": "Mise à jour et création de nouveaux commandes s'ils existent de SAH vers Odoo",
                    }
                    self.with_delay(**job_kwargs_commandes).get_commande(commande)     
    
    def get_commande(self,commande):
        if commande and commande['Status'] not in ['InProgress','Created']:  
            id_order = commande['Id']
            commandes_odoo = self.env['sale.order'].search([('id_order_sh','=',id_order)])
            client_id = self.env['res.partner'].search([('id_client_sah','=',commande['Customer']['Id'])])
            vendeur_id = self.env['res.partner'].search([('id_vendeur_sah','=',commande['Seller']['Id'])])
            Currency = self.env['res.currency'].search([('name','=',commande['Currency'])])
            methode_paiement = commande['PaymentMethod']
            mode_livraison_sah = commande['DeliveryMode']
            methode_paiement_id = None
            mode_livraison_sah_id = None
            
            phone = mobile = street2 = street = zip = city = pays = ''

            if mode_livraison_sah:
                mode_id = self.env['mode.livraison.sah'].search([('value','=',mode_livraison_sah)])
                if mode_id:
                    mode_livraison_sah_id = mode_id
            if methode_paiement:
                methode_paiement = self.env['methode.paiement.sah'].search([('value','=',methode_paiement)])
                if len(methode_paiement) ==1:
                    methode_paiement_id=methode_paiement
            
            adresse_livraison_id = ''
            adresse_livraison_sah = commande['DeliveryAddress']
            if adresse_livraison_sah :
                phone = adresse_livraison_sah.get('Phone')
                mobile = adresse_livraison_sah.get('MobilePhone')
                street = adresse_livraison_sah.get('StreetAddress')
                street2 = (
                    f"{adresse_livraison_sah.get('StreetAddress2', '')}, {adresse_livraison_sah.get('StreetAddress3', '')}".strip(', ')
                    if adresse_livraison_sah.get('StreetAddress2') and adresse_livraison_sah.get('StreetAddress3')
                    else adresse_livraison_sah.get('StreetAddress2')
                )
                zip_code = adresse_livraison_sah.get('Postcode')
                city = adresse_livraison_sah.get('City')
                pays = self.env['res.country'].search([('code', '=', adresse_livraison_sah.get('CountryIso'))]).id if adresse_livraison_sah.get('CountryIso') else None
                # Création d'un domaine de recherche sous forme de liste
                domain = [('type','=','delivery')]
                if phone:
                    domain.append(('phone', '=', phone))
                if mobile:
                    domain.append(('mobile', '=', mobile))
                if street:
                    domain.append(('street', '=', street))
                if street2:
                    domain.append(('street2', '=', street2))
                if zip_code:
                    domain.append(('zip', '=', zip_code))
                if city:
                    domain.append(('city', '=', city))
                if pays:
                    domain.append(('country_id', '=', pays))
                if mode_livraison_sah == 20:
                    if client_id:
                        domain.append(('parent_id', '=', client_id.id))
                elif  mode_livraison_sah == 10:
                    if vendeur_id:
                        domain.append(('parent_id', '=', vendeur_id.id))

                # Recherche de l'adresse avec le domaine construit
                adresse_id = self.env['res.partner'].search(domain,limit=1)
                if adresse_id :
                    adresse_livraison_id = adresse_id
                
            if client_id :
                if not adresse_livraison_id:
                    adresse_livraison_id = self.env['res.partner'].create({
                    'name': 'Adresse de livraison ' + client_id.name,
                    'street': street,
                    'street2':street2,
                    'city': city,
                    'zip': zip,
                    'country_id': pays,
                    'type': 'delivery',  
                    'parent_id': client_id.id,
                })
                if not commandes_odoo :
                    order = commandes_odoo.create({
                        "id_order_sh" : commande['Id'],
                        "name" : commande['OrderRefCode'],
                        "partner_id" : client_id.id,
                        "currency_id" : Currency.id, 
                        "vdi" : vendeur_id.id if vendeur_id else None,
                        "methode_paiement_id" : methode_paiement_id.id if methode_paiement_id else None,
                    })
                    if order:
                        if adresse_livraison_id :
                            order.partner_shipping_id = adresse_livraison_id.id
                        paiement_sah = commande['Payments']
                        if paiement_sah:
                            paiement_vals=[]
                            for p in paiement_sah:
                                mtp = self.env['methode.paiement.sah'].search([('code','=',p['Method'])])
                                self.env['paiement.sah'].sudo().create({
                                    'name':p['Name'],  
                                    'methode': mtp.id if mtp else None,  
                                    'montant': p['Amount'],   
                                    'numero_transaction': p['TransactionNumber'], 
                                    'date_paiement': datetime.strptime(str(p['PaymentAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['PaymentAt']!=None else None,
                                    'date_echeance':datetime.strptime(str(p['DueAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['DueAt']!=None else None,
                                    'date_validation': datetime.strptime(str(p['ValidatedAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['ValidatedAt']!=None else None,
                                    'order_id': order.id,
                                })
                                order.methode_paiement_id = mtp.id if mtp else order.methode_paiement_id
                        
                        for elt in commande['Products']:
                            p=self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])])
                            if p:
                                if self._get_or_create_tax(elt['TaxRate']) :
                                    self.env['sale.order.line'].create({
                                    "id_order_line_sh":elt["Id"],
                                    "name":p.name,
                                    "order_id":order.id,
                                    'product_id':p.product_variant_id.id,
                                    'product_template_id':p.id,
                                    'product_uom_qty': elt['Quantity'],
                                    'price_unit': elt['UnitPrice'], 
                                    'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                                    })
                            else :
                                raise ValidationError("Produit introuvable!")
                        if commande['DeliveryAmount'] != '0.0' and mode_livraison_sah_id and mode_livraison_sah_id.delivery_carrier_id:
                            delivery_carrier = self.env['choose.delivery.carrier'].create({
                                "carrier_id": mode_livraison_sah_id.delivery_carrier_id.id,
                                "order_id":order.id,
                                "partner_id":order.partner_id.id
                                })
                            if delivery_carrier :
                                delivery_carrier.button_confirm()
                                if mode_livraison_sah_id.delivery_carrier_id.product_id:
                                    line = self.env['sale.order.line'].search([( 'order_id','=', order.id),('product_id','=',mode_livraison_sah_id.delivery_carrier_id.product_id.id)], limit=1)
                                    if line:
                                        line.write({
                                        'price_unit': commande['DeliveryAmount'] ,
                                        'tax_id': [(6, 0, [self._get_or_create_tax_delivery(commande['DeliveryAmount'],commande['DeliveryAmountExclTax'])])],
                                    })
                        else :
                            raise ValidationError("Transporteur introuvable!")
                        if order.methode_paiement_id.is_confirme == True:
                            order.action_confirm()
                        
            else:
                _logger.info(" Client introuvable pour la commande ",{commande[Id]})
    
            
    def _get_or_create_tax(self, tax_rate):
        # Recherche la taxe par son montant
        tax = self.env['tax.sah'].search([('amount', '=', tax_rate)], limit=1)
        if tax and tax.amount_tax_id :
            return tax.amount_tax_id.id
        else:
            raise ValidationError("Taxe introuvable!")

    def _get_or_create_tax_delivery(self, deliveryAmount,deliveryAmountExclTax ):
        # Recherche la taxe par son montant
        taux = round((deliveryAmount - deliveryAmountExclTax ) * 100,2)
        _logger.info("gggg%s", taux)
        tax_id = self.env['tax.sah'].search([('amount', '=', taux)], limit=1)
        if tax_id and tax_id.amount_tax_id :
            return tax_id.amount_tax_id.id
        else:
            raise ValidationError("Taxe pour les fraits de livraison introuvable!")

