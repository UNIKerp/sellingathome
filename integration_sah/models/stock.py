# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests

_logger = logging.getLogger(__name__)


class StockSAH(models.Model):
     _inherit = "stock.warehouse"
     
     url =""

    