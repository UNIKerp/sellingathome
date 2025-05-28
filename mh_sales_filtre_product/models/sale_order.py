# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
class ProduitSAH(models.Model):
    _inherit = "product.template"
    is_visibles = fields.Boolean(string='Visible')
class SaleOrderCombo(models.Model):
    _inherit = 'sale.order'

    show_all_products = fields.Boolean(string='Filtre stock', help='Filtre sur les produits qui ont un stock prévisionnel > 0',default=False)


    @api.onchange('show_all_products')
    def produit_stock_previsionnel(self):
        _logger.info("Filtrage activé : Affichage uniquement des produits avec stock > 0.")
        """Met à jour la visibilité des produits selon le stock prévisionnel."""
        produits = self.env['product.template'].search([('sale_ok', '=', True)])

        if self.show_all_products == True:
            _logger.info("Filtrage activé : Affichage uniquement des produits avec stock***************************************************** > 0.")
            produits.filtered(lambda p: p.virtual_available > 0).write({'is_visibles': True})
            produits.filtered(lambda p: p.virtual_available <= 0).write({'is_visibles': False})
        else:
            _logger.info("Filtrage désactivé : Tous les produits sont visibles.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@à")
            produits.write({'is_visibles': True})