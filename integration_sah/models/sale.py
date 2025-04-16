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

  