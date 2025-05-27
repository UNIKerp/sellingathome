# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
class ProduitSAH(models.Model):
    _inherit = "product.template"
    is_visibles = fields.Boolean(string='Visible')
class SaleOrderCombo(models.Model):
    _inherit = 'sale.order'

    show_all_products = fields.Boolean(string='Filtre stock', help='Filtre sur les produits qui ont un stock prévisionnel > 0')



    @api.onchange('show_all_products')
    def produit_stock_prévisionnel(self):
        # produits = self.env['product.template'].search([('virtual_available', '>', 0)])
        _logger.info("dougounaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        produits = self.env['product.template'].search([('sale_ok','=',True)])
        if self.show_all_products:
            _logger.info("mogui thie produit yi iffffffffffffffffffffffffffff")
            for produit in produits:
                if produit.virtual_available > 0:
                    produit.is_visibles = True
                else:
                    produit.is_visibles = False
        else:
            if produits:
                _logger.info("mogui thie produit yi elseffffffffffffffffffffffffffff")
                for produit in produits:
                    produit.is_visibles = True