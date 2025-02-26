# -*- coding: utf-8 -*-
import logging
import requests

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class StockPickingSAH(models.Model):
    _inherit = "stock.picking" 

    url_tracking = fields.Char(string="URL Tracking", help="URL de suivi")

    # @api.model
    # def create(self, vals):
    #     res = super(StockPickingSAH, self).create(vals)
    #     if res.sale_id and res.sale_id.vdi:
    #         _logger.info("@@@@@11111111111")
    #         group_vdi = self.env['gestion.vdi'].search([('contact_vdi_ids', 'in', [res.sale_id.vdi.id])], limit=1)
    #         if group_vdi:
    #             _logger.info("@@@@@33333333333")
    #             res.partner_id = group_vdi.adresse_livraison.id
    #     return res


    def button_validate(self):
        res = super(StockPickingSAH,self).button_validate()
        if res:
            job_kwargs2 = {
                'description': 'Mise à jour du stock produit',
            }
            self.with_delay(**job_kwargs2).maj_des_stocks(self.move_ids_without_package)
            if self.sale_id:
                job_kwargs = {
                    'description': 'Mise à jour etat de la commande en expédié dans SAH',
                }
                self.with_delay(**job_kwargs).update_state_order(self.sale_id)
        return res
        
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
                        "TrackingUrl": self.url_tracking
                    }
                    requests.put(url_status_order, json=datas, headers=headers)

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
                