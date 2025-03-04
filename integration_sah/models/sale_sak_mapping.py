# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
import requests
from datetime import datetime
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ConfigAccesSAH(models.Model):
    _name = "acces.sah"
    _description = "Configuration des acces des commandes de SAH"

    url_commande = fields.Char(string='URL commande SAH', copy=False, default='https://demoapi.sellingathome.com/v1/Orders')
    date_debut = fields.Datetime(string="Date de debut",copy=False)
    date_fin = fields.Datetime(string="Date de Fin",copy=False)


class MappingSAHOdoo(models.Model):
    _name = "commande.sah"
    _description = "Table pour stoker les commandes de SAH dans Odoo"

    name = fields.Char(string='Reference commande SAH',required=True, copy=False)
    job_id = fields.Many2one('queue.job',string="Job",copy=False)
    commande_id = fields.Many2one("sale.order",string="Commande Odoo",copy=False)
    donnes_sah = fields.Json("Données")
