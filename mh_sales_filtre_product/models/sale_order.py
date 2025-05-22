# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class SaleLineSAH(models.Model):
    _inherit = "sale.order.line"
    produit_available_ids = fields.Many2many('product.template', string="Produit dont prévisionel possitif")

        
    @api.onchange('order_id')
    def produit_stock_prévisionnel(self):
        produits = self.env['product.template'].search([('virtual_available', '>', 0)])
        pro = self.env['product.template'].search([])
        tab_produit_ids =[]
        if self.order_id.show_all_products == True:
            if produits:
                for produit in produits:
                    tab_produit_ids.append(produit.id)
            self.produit_available_ids = [(6, 0, tab_produit_ids)]
        else:
            if pro:
                for p in pro:
                    tab_produit_ids.append(p.id)
            self.produit_available_ids = [(6, 0, tab_produit_ids)]

class SaleOrderCombo(models.Model):
    _inherit = 'sale.order'

    show_all_products = fields.Boolean(string='Filtre stock', help='Filtre sur les produits qui ont un stock prévisionnel > 0')