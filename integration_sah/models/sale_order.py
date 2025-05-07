from odoo import models, fields, api

from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrderCombo(models.Model):
    _inherit = 'sale.order'

    def create_order_with_combo(self):
        """
        Crée une commande avec un produit combo et ses produits associés.
        """
        partner_id = 3
        combo_product_id = 93
        # Création de la commande
        order = self.create({
            'partner_id': partner_id,
        })

        # Chargement du produit combo
        combo_product = self.env['product.product'].browse(combo_product_id)

        # Ajout du produit combo à la commande
        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': combo_product.id,
            'product_uom_qty': 1,
            'price_unit': combo_product.list_price,
        })

        # Parcourir les produits associés (ex: champ combo_product_ids Many2many)
        _logger.info("kdddddddddddddddddddddddddddddddddddddddddddd%s",combo_product.combo_ids)
        for associated_product in combo_product.combo_ids:
            self.env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': associated_product.id,
                'price_unit': 0,
                'product_uom_qty': 1,
            })

        return order
