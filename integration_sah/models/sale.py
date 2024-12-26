# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from datetime import datetime

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
    methode_paiement_id = fields.Many2one('methode.paiement',string="Methode de paiement",help='la Methode de paiement')
    paiement_id = fields.Many2one('paiement.sah',string="Paiement SAH",help='le paiement dans SAH')
    _sql_constraints = [
        ('id_order_sh_uniq', 'unique (id_order_sh)', "ID commande SAH exists deja!"), ]
    

    def get_commande(self):
        url_commande = 'https://demoapi.sellingathome.com/v1/Orders'            
        headers = self.env['authentication.sah'].establish_connection()
        response = requests.get(url_commande, headers=headers)
        if response.status_code == 200:
            commandes_sah = response.json()
            for commande in commandes_sah:      
                id_order = commande['Id']
                commandes_odoo = self.env['sale.order'].search([('id_order_sh','=',id_order)])
                client_id = self.env['res.partner'].search([('id_client_sah','=',commande['Customer']['Id'])])
                Currency = self.env['res.currency'].search([('name','=',commande['Currency'])])
                # vendeur_id = self.env['res.users'].search([('id_vendeur_sah','=',commande['Seller']['Id'])])

                # Mapping des états SAH aux états Odoo
                state_mapping = {
                    'pending': 'draft',
                    'confirmed': 'sale',
                    'shipped': 'sent',
                    'delivered': 'done'
                }
                order_state_sah = commande.get('Status', 'pending')  # Par défaut 'pending' si l'état n'est pas défini
                _logger.info(order_state_sah)

                if not commandes_odoo and client_id:
                    order = commandes_odoo.create({
                        "id_order_sh":commande['Id'],
                        "name":commande['OrderRefCode'],
                        "partner_id":client_id.id,
                        "currency_id":Currency.id, 
                        "vdi":client_id.vdi_id.id or False,
                        "state": state_mapping.get(order_state_sah, 'draft'),
                    })
                    if order:
                        for elt in commande['Products']:
                            p=self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])])
                            if p:
                                self.env['sale.order.line'].create({
                                "id_order_line_sh":elt["Id"],
                                "name":p.name,
                                "order_id":order.id,
                                'product_id':p.product_variant_id.id,
                                'product_template_id':p.id,
                                'product_uom_qty': elt['Quantity'],
                                'price_unit': elt['UnitPriceExcltax'], 
                                'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                                })

                elif commandes_odoo:
                    commandes_odoo.write({ 
                        "name":commande['OrderRefCode'], 
                        "partner_id":client_id.id, 
                        "currency_id":Currency.id, 
                        "vdi":client_id.vdi_id.id or False,
                        "state": state_mapping.get(order_state_sah, 'draft'),
                    })
                    for elt in commande['Products']:
                        p=self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])])
                        if p:
                            j=0
                            for l in commandes_odoo.order_line:
                                if l.id_order_line_sh==elt["Id"]:
                                    l.write({'product_uom_qty': elt['Quantity'],'price_unit': elt['UnitPriceExcltax'], 'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])] })
                                    j+=1
                            if j==0:
                                self.env['sale.order.line'].create({
                                "id_order_line_sh":elt["Id"],
                                "name":p.name,
                                "order_id":commandes_odoo.id,
                                'product_id':p.product_variant_id.id,
                                'product_template_id':p.id,
                                'product_uom_qty': elt['Quantity'],
                                'price_unit': elt['UnitPriceExcltax'], 
                                'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                                })
        else:
            _logger.info(f"Erreur {response.status_code}: {response.text}")
       
            
    def _get_or_create_tax(self, tax_rate):
        # Recherche la taxe par son montant
        tax = self.env['account.tax'].search([('amount', '=', tax_rate)], limit=1)
        if not tax:
            tax = self.env['account.tax'].create({
                'name': f'Taxe {tax_rate}%',
                'amount': tax_rate,
            })
        
        return tax.id


