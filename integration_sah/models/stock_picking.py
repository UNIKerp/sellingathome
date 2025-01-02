#-*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        rec = super(StockPicking, self).button_validate()
        if self.sale_id:
            job_kwargs = {
                'description': 'Mise à jour etat de la commande en expédié dans SAH',
            }
            self.with_delay(**job_kwargs).update_state_order(self.sale_id)
        return rec


    def update_state_order(self,sale_id):
        if sale_id.id_order_sh:
            id_commande = sale_id.id_order_sh
            url_commande = f"https://demoapi.sellingathome.com/v1/Orders/{id_commande}"
            headers = self.env['authentication.sah'].establish_connection()
            response = requests.get(url_commande, headers=headers)
            if response.status_code == 200:
                datas = response.json()
                if datas["Status"] == "NotYetShipped":
                    url_status_order = f"https://demoapi.sellingathome.com/v1/OrderStatuses/{id_commande}"  
                    datas = {
                        "OrderId": id_commande,
                        "Status": 3,
                        # "TrackingUrl": ""
                    }
                    response1 = requests.put(url_status_order, json=datas, headers=headers)