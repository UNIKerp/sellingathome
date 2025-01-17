# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime
from dateutil import parser

class ProduitPriceList(models.Model):
    _inherit = "product.pricelist"

    price_list_sah_id = fields.Char(string='Id Prix SAH',copy=False,)
    country_id = fields.Many2one('res.country', string="Pays")


class Tarifs(models.Model):

    _inherit = "product.pricelist.item"

    price_sah_id = fields.Char(string="ID Prix SAH")
   

    # redéfintion de la fonction _default_pricelist_id
    def _default_pricelist_id(self):
        active_id = self.env.context.get('active_id')
        product_id = self.env['product.template'].search([('id','=',active_id)])
        if product_id and product_id.default_list_price:
            return product_id.default_list_price
        else:
            return self.env['product.pricelist'].search([
                '|', ('company_id', '=', False),
                ('company_id', '=', self.env.company.id)], limit=1)

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        index=True, ondelete='cascade',
        required=True,
        default=_default_pricelist_id)

    @api.model
    def create(self, vals):
        res = super(Tarifs, self).create(vals)
        headers = self.env['authentication.sah'].establish_connection()
        job_kwargs = {
                'description': 'Creation liste de prix',
            }
        self.with_delay(**job_kwargs).update_produit_dans_sah(res.product_tmpl_id, headers)
        return res


    def write(self, vals):
        res = super(Tarifs, self).write(vals)
        headers = self.env['authentication.sah'].establish_connection()
        job_kwargs = {
                'description': 'Mise à jour liste de prix',
        }
        self.with_delay(**job_kwargs).update_produit_dans_sah(self.product_tmpl_id, headers)
        return res
