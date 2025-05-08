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
    produit_available_ids = fields.Many2many('product.template', string="Produit dont prévisionel possitif")

        
    _sql_constraints = [
        ('id_order_line_sh_uniq', 'unique (id_order_line_sh)', "ID linr de commande SAH exists deja!"), ]
    @api.onchange('order_id')
    def produit_stock_prévisionnel(self):
        produits = self.env['product.template'].search([('virtual_available', '>', 0)])
        if order_id.show_all_products == True:
            tab_produit_ids =[]
            if produits:
                for produit in produits:
                    tab_produit_ids.append(produit.id)
            self.produit_available_ids = tab_produit_ids

    

class SaleSAH(models.Model):
    _inherit = "sale.order"

    id_order_sh = fields.Integer(string="ID commande SAH", copy=False, help="ID de la Commande dans SAH")
    vdi = fields.Many2one('res.partner',string="Ambassadeur",help='le reveudeur vdi dans SAH')
    methode_paiement_id = fields.Many2one('methode.paiement.sah',string="Moyen de paiement",help='la Methode de paiement')
    paiement_ids = fields.One2many('paiement.sah','order_id',string="Paiement SAH",help='le paiement dans SAH')
    
    _sql_constraints = [
        ('id_order_sh_uniq', 'unique (id_order_sh)', "ID commande SAH exists deja!"), ]

    
    def action_confirm(self):
        """
            Redéfinit la méthode action_confirm de sale.order pour automatiser la création et la confirmation de factures.

            Cette méthode est appelée lorsqu'un utilisateur confirme une commande de vente.  Elle effectue les actions suivantes :
            1. Appelle la méthode action_confirm de la classe parente (sale.order) pour exécuter la logique standard de confirmation de commande.
            2. Pour chaque commande dans le self (qui peut contenir plusieurs commandes si l'utilisateur en confirme plusieurs en même temps):
                3. Vérifie si la commande est prête à être facturée (invoice_status == 'to invoice').
                4. Si la commande est prête à être facturée, elle crée une nouvelle facture (account.move) avec les détails de la commande.
                5. Confirme (valide) la facture nouvellement créée.
            6. Retourne le résultat de l'appel à la méthode de la classe parente.
        """    
        res = super(SaleSAH, self).action_confirm()
        # Itère sur chaque commande dans le self.  self peut contenir plusieurs commandes si l'utilisateur
        # sélectionne et confirme plusieurs commandes en même temps dans l'interface utilisateur
        for order in self:
            if order.invoice_status == 'to invoice':
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice', # Définit le type de la facture comme "Facture Client".
                    'partner_id': order.partner_id.id,
                    'currency_id': order.pricelist_id.currency_id.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': line.name,
                        'quantity': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'product_id': line.product_id.id,
                        'tax_ids': [(6, 0, line.tax_id.ids)],
                        'sale_line_ids': [(6, 0, [line.id])],
                    }) for line in order.order_line], # order.order_line est l'ensemble des lignes de la commande
                    'invoice_origin': order.name,
                    'ref': order.client_order_ref,
                    'company_id': order.company_id.id,
                    'user_id': order.user_id.id,
                })
                # Confirme (valide) la facture nouvellement créée.
                invoice.action_post()
        return res

  