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

    def button_validate(self):
        res = super(StockPickingSAH,self).button_validate()
        if self.move_ids_without_package:
            for line in self.move_ids_without_package:
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
                    }
                    response = requests.put(url, headers=headers, json=values)
                    if response.status_code == 200:
                        _logger.info('=====================%s',response.json())  
                    else:
                        _logger.info('=====================%s',response.text)
        return res

class StockSAH(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.model
    def create(self,vals):
        res = super(StockSAH,self).create(vals)
        object_id = self.env.context.get('active_id')
        if object_id:
            produit = self.env['product.template'].search([('id','=',object_id),('is_storable','=',True)])
            if res.new_quantity and produit:
                url = 'https://demoapi.sellingathome.com/v1/Stocks'
                headers = self.env['authentication.sah'].establish_connection()
                if headers:
                    values = {
                        "ProductId":  produit.produit_sah_id,
                        "ProductReference": produit.default_code,
                        "StockQuantity": int(res.new_quantity),
                        "StockQuantityComing":int(produit.virtual_available),
                    }
                    response = requests.put(url, headers=headers, json=values)
                    if response.status_code == 200:
                        print(response.json())  
                    else:
                        print(f"Erreur {response.status_code}: {response.text}")
        return res

            