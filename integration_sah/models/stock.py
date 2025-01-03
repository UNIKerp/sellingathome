# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import io
import logging
import lxml
import random
import re
import requests
import threading
import werkzeug.urls
from ast import literal_eval
from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from werkzeug.urls import url_join
from PIL import Image, UnidentifiedImageError

from odoo import api, fields, models, tools, _
from odoo.addons.base_import.models.base_import import ImportValidationError
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)

class StockPickingSAH(models.Model):
    _inherit = "stock.picking" 

    @api.model
    def create(self, vals):
        res = super(StockPickingSAH, self).create(vals)
        if res.origin:
            sale_order = self.env['sale.order'].search([('name', '=', res.origin)], limit=1)
            if sale_order and sale_order.vdi:
                    group_vdi = self.env['gestion.vdi'].search([('contact_vdi_ids', 'in', [sale_order.vdi.id])], limit=1)
                    if group_vdi:
                        res.partner_id = group_vdi.adresse_livraison
        return res


    def button_validate(self):
        res = super(StockPickingSAH,self).button_validate()
        if res:
            job_kwargs2 = {
                'description': 'Mise à jour du stock produit',
            }
            self.with_delay(**job_kwargs2).maj_des_stocks(self.move_ids_without_package)
        return res
    
    def maj_des_stocks(self,move_ids_without_package):
        if  move_ids_without_package:
            for line in move_ids_without_package:
                if line.product_id.product_tmpl_id.is_storable == True:
                    qty_available = line.product_id.product_tmpl_id.qty_available
                    virtual_available = line.product_id.product_tmpl_id.virtual_available
                    url = 'https://demoapi.sellingathome.com/v1/Stocks'
                    headers = self.env['authentication.sah'].establish_connection()
                    values = {
                        "ProductId":   line.product_id.product_tmpl_id.produit_sah_id,
                        "ProductReference":  line.product_id.product_tmpl_id.default_code,
                        "StockQuantity": int(qty_available),
                        "StockQuantityComing":int(virtual_available),
                        "AllowOutOfStockOrders": True
                        
                    }
                    requests.put(url, headers=headers, json=values)
                   

class StockSAH(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.model
    def create(self,vals):
        res = super(StockSAH,self).create(vals)
        if res:
            job_kwargs2 = {
                'description': 'Mise à jour du stock produit',
            }
            object_id = self.env.context.get('active_id')
            self.with_delay(**job_kwargs2).maj_des_stocks(object_id,res.new_quantity) 
        return res

    def maj_des_stocks(self,object_id,new_quantity):
        if object_id:
            produit = self.env['product.template'].search([('id','=',object_id),('is_storable','=',True)])
            if new_quantity and produit:
                url = 'https://demoapi.sellingathome.com/v1/Stocks'
                headers = self.env['authentication.sah'].establish_connection()
                if headers:
                    values = {
                        "ProductId":  produit.produit_sah_id,
                        "ProductReference": produit.default_code,
                        "StockQuantity": int(new_quantity),
                        "StockQuantityComing":int(produit.virtual_available),
                        "AllowOutOfStockOrders": True
                    }
                    requests.put(url, headers=headers, json=values)
                    


class StockQuant(models.Model):

    _inherit = "stock.quant"

    @api.model
    def create(self,vals):
        res = super(StockQuant,self).create(vals)
        if res:
            job_kwargs2 = {
                'description': f'Mise à jour du stock produit',
            }
            self.with_delay(**job_kwargs2).maj_des_stocks(res.product_tmpl_id,res.inventory_quantity_auto_apply)
        return res


    def write(self,vals):
        res = super(StockQuant,self).write(vals)
        if vals:
            job_kwargs2 = {
                'description': 'Mise à jour du stock produit',
            }
            self.with_delay(**job_kwargs2).maj_des_stocks(self.product_tmpl_id,self.inventory_quantity_auto_apply)
        return res

    def maj_des_stocks(self,product_tmpl_id,inventory_quantity_auto_apply):
        if  product_tmpl_id.is_storable:
            url = 'https://demoapi.sellingathome.com/v1/Stocks'
            headers = self.env['authentication.sah'].establish_connection()
            if headers:
                values = {
                    "ProductId": product_tmpl_id.produit_sah_id,
                    "ProductReference": product_tmpl_id.default_code,
                    "StockQuantity": int(inventory_quantity_auto_apply),
                    "StockQuantityComing":int(product_tmpl_id.virtual_available),  
                    "AllowOutOfStockOrders": True
                }
                requests.put(url, headers=headers, json=values)
                