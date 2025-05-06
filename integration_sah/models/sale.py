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

    
    def action_confirm(self):
        res = super(SaleSAH, self).action_confirm()
        for order in self:
            if order.invoice_status == 'to invoice':
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
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
                    }) for line in order.order_line],
                    'invoice_origin': order.name,
                    'ref': order.client_order_ref,
                    'company_id': order.company_id.id,
                    'user_id': order.user_id.id,
                })
                invoice.action_post()
        return res

  