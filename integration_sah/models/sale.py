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
    vdi = fields.Many2one('res.partner',string="vdi",help='le veudeur dans SAH')
    
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
                if not commandes_odoo and client_id:
                    # p=self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])]).id
                    order = commandes_odoo.create({
                        "id_order_sh":commande['Id'],
                        "name":commande['OrderRefCode'],
                        "partner_id":client_id.id,
                        "currency_id":Currency.id, 
                        "vdi":client_id.vdi_id.id or False
                    })
                    if order:
                        for elt in commande['Products']:
                            if self.get_produit(elt['ProductId'])!=0:
                                self.env['sale.order.line'].create({
                                "id_order_line_sh":elt["Id"],
                                "name":self.get_produit(elt['ProductId']).name,
                                "order_id":order.id,
                                'product_template_id':self.get_produit(elt['ProductId']).id,
                                'product_uom_qty': elt['Quantity'],
                                'price_unit': elt['UnitPriceExcltax'], 
                                'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                                })

                elif commandes_odoo:
                    commandes_odoo.write({ "name":commande['OrderRefCode'], "partner_id":client_id.id, "currency_id":Currency.id, "vdi":client_id.vdi_id.id or False})
                    for elt in commande['Products']:
                        if self.get_produit(elt['ProductId'])!=0:
                            j=0
                            for l in commandes_odoo.order_line:
                                if l.id_order_line_sh==elt["Id"]:
                                    l.write({'product_uom_qty': elt['Quantity'],'price_unit': elt['UnitPriceExcltax'], 'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])] })
                                    j+=1
                            if j==0:
                                self.env['sale.order.line'].create({
                                "id_order_line_sh":elt["Id"],
                                "name":self.get_produit(elt['ProductId']).name,
                                "order_id":commandes_odoo.id,
                                'product_template_id':self.get_produit(elt['ProductId']).id,
                                'product_uom_qty': elt['Quantity'],
                                'price_unit': elt['UnitPriceExcltax'], 
                                'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                                })
        else:
            _logger.info(f"Erreur {response.status_code}: {response.text}")
        _logger.info("======================= Fin de mise à jour des commandes")
       
            
    def _get_or_create_tax(self, tax_rate):
        # Recherche la taxe par son montant
        tax = self.env['account.tax'].search([('amount', '=', tax_rate)], limit=1)
        if not tax:
            tax = self.env['account.tax'].create({
                'name': f'Taxe {tax_rate}%',
                'amount': tax_rate,
            })
        
        return tax.id


    def get_produit(self,ProductId):
        produit = self.env['product.template'].search([('produit_sah_id','=',ProductId)])
        if produit: 
            return produit
        else:
            return 0

