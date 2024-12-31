# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from datetime import datetime

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

    def get_orders_with_done_delivery(self):
        id_commande = "233486"
        url_commande = f"https://demoapi.sellingathome.com/v1/Orders/{id_commande}"          
        headers = self.env['authentication.sah'].establish_connection()
        
        # Fetch the order details
        response = requests.get(url_commande, headers=headers)
        if response.status_code == 200:
            com = response.json()
            _logger.info(f"Commande récupérée : {com}")  # Log initial pour vérifier l'état de la commande

            # Vérifiez si 'Payments' est None
            if com.get('Payments') is None:
                _logger.warning("La clé 'Payments' est None avant modification.")

            # Replace 'Payments' with predefined data
            com['Payments'] = [
                {
                    'Name': 'CB déclaratif', 
                    'Method': 'declarativecreditcard', 
                    'Amount': 38.0, 
                    'TransactionNumber': '', 
                    'PaymentAt': '2024-05-30T15:17:49.993464', 
                    'DueAt': '2024-05-30T15:17:49.993464', 
                    'ValidatedAt': '2024-05-30T15:17:49.993464'
                }
            ]

            _logger.info(f"Commande après modification : {com}")  # Log après modification

            # Update the order with modified data
            resp = requests.put(url_commande, json=com, headers=headers)
            if resp.status_code == 200:
                _logger.info(f"Commande {id_commande} mise à jour avec succès : {resp.json()}")
            else:
                _logger.error(f"Erreur lors de la mise à jour de la commande {id_commande}: {resp.status_code} - {resp.text}")
        else:
            _logger.error(f"Erreur lors de la récupération de la commande {id_commande}: {response.status_code} - {response.text}")
        # orders = self.search([('id_order_sh', '!=', False), ('state', '=', 'sale')])
        # _logger.info("Orders found: %s", orders)
        
        # orders_to_update = orders.filtered(lambda order: all(picking.state == 'done' for picking in order.picking_ids))
        # _logger.info("Orders to update (done delivery): %s", orders_to_update)
        # id_commande = "233486"
        # url_commande = f"https://demoapi.sellingathome.com/v1/Orders/{id_commande}"          
        # headers = self.env['authentication.sah'].establish_connection()
        # response = requests.get(url_commande, headers=headers)
        # if response.status_code == 200:
        #     com = response.json()
            
        #     com['Payments'] = [
        #         {
        #             'Name': 'CB déclaratif', 
        #             'Method': 'declarativecreditcard', 
        #             'Amount': 38.0, 
        #             'TransactionNumber': '', 
        #             'PaymentAt': '2024-05-30T15:17:49.993464', 
        #             'DueAt': '2024-05-30T15:17:49.993464', 
        #             'ValidatedAt': '2024-05-30T15:17:49.993464'
        #         }
        #     ]

        #     _logger.info('====================================%s',response.json())
        #     resp = requests.put(url_commande, json=com, headers=headers)
        #     if resp.status_code == 200:
        #         _logger.info(f"Commande {resp.json()} mise à jour avec succès.")
        # for order in orders_to_update:
        #     id_commande = order.id_order_sh
        #     client_id = self.env['res.partner'].search([('id_client_sah', '=', order.partner_id.id_client_sah)], limit=1)
        #     _logger.info("Client found: %s", client_id.name if client_id else "None")
            
        #     if not client_id:
        #         _logger.warning(f"Aucun client trouvé pour la commande {id_commande}.")
        #         continue
            
        #     url_cmd = f"https://demoapi.sellingathome.com/v1/Orders"
        #     post_response_produit = requests.get(url_cmd, headers=headers)
        #     _logger.info('====================================%s',post_response_produit.json())
            
            # try:
            #     post_response_produit = requests.get(url_cmd, headers=headers, timeout=120)

            #     if post_response_produit.status_code == 200:
            #         response_data_produit = post_response_produit.json()
            #         response_data_produit['Status'] = "Validated"
            #         _logger.info('========================================== %s',response_data_produit)
            #         response = requests.put(url_cmd, json=response_data_produit, headers=headers)
            #         if response.status_code == 200:
            #             _logger.info(f"Commande {id_commande} mise à jour avec succès.")
            #             _logger.info("Response from API: %s", response.json())
                

            # except requests.RequestException as e:
            #     _logger.error(f"Erreur de requête pour la commande {id_commande}: {str(e)}")
        
        # return f"{len(orders_to_update)} commandes mises à jour avec succès en Expédié."


    

    def get_commande(self):
        url_commande = 'https://demoapi.sellingathome.com/v1/Orders'           
        headers = self.env['authentication.sah'].establish_connection()
        response = requests.get(url_commande, headers=headers)
        if response.status_code == 200:
            commandes_sah = response.json()
            _logger.info("commandes_sah commandes_sah %s",commandes_sah)
            for commande in commandes_sah:      
                id_order = commande['Id']
                commandes_odoo = self.env['sale.order'].search([('id_order_sh','=',id_order)])
                client_id = self.env['res.partner'].search([('id_client_sah','=',commande['Customer']['Id'])])
                Currency = self.env['res.currency'].search([('name','=',commande['Currency'])])
                methode_paiement = commande['PaymentMethod']
                methode_paiement_id=None
                if methode_paiement:
                    methode_paiement = self.env['methode.paiement.sah'].search([('value','=',methode_paiement)])
                    if len(methode_paiement) ==1:
                        methode_paiement_id=methode_paiement
                # vendeur_id = self.env['res.users'].search([('id_vendeur_sah','=',commande['Seller']['Id'])])


                if not commandes_odoo and client_id:
                    order = commandes_odoo.create({
                        "id_order_sh":commande['Id'],
                        "name":commande['OrderRefCode'],
                        "partner_id":client_id.id,
                        "currency_id":Currency.id, 
                        "vdi":client_id.vdi_id.id or False,
                        "methode_paiement_id":methode_paiement_id.id if methode_paiement_id else None,
                    })
                    if order:
                        paiement_sah = commande['Payments']
                        if paiement_sah:
                            paiement_vals=[]
                            for p in paiement_sah:
                                mtp = self.env['methode.paiement.sah'].search([('code','=',p['Method'])])
                                self.env['paiement.sah'].sudo().create({
                                    'name':p['Name'],  
                                    'methode': mtp.id if mtp else None,  
                                    'montant': p['Amount'],   
                                    'numero_transaction': p['TransactionNumber'], 
                                    'date_paiement': datetime.strptime(str(p['PaymentAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['PaymentAt']!=None else None,
                                    'date_echeance':datetime.strptime(str(p['DueAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['DueAt']!=None else None,
                                    'date_validation': datetime.strptime(str(p['ValidatedAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['ValidatedAt']!=None else None,
                                    'order_id': order.id,
                                })
                                order.methode_paiement_id = mtp.id if mtp else order.methode_paiement_id
                        for elt in commande['Products']:
                            p=self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])])
                            if p:
                                self.env['sale.order.line'].create({
                                "id_order_line_sh":elt["Id"],
                                "name":p.name,
                                "order_id":order.id,
                                'product_id':p.product_variant_id.id,
                                'product_template_id':p.id,
                                'product_uom_qty': elt['Quantity'],
                                'price_unit': elt['UnitPriceExcltax'], 
                                'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                                })

                elif commandes_odoo:
                    commandes_odoo.write({ 
                        "name":commande['OrderRefCode'], 
                        "partner_id":client_id.id, 
                        "currency_id":Currency.id, 
                        "vdi":client_id.vdi_id.id or False,
                        "methode_paiement_id":methode_paiement_id.id if methode_paiement_id else None,
                    })
                    paiement_sah = commande['Payments']
                    
                    if paiement_sah:
                        paiement_vals=[]
                        if commandes_odoo.paiement_ids:
                            for p in paiement_sah:
                                for pc in commandes_odoo.paiement_ids:
                                    mtp = self.env['methode.paiement.sah'].search([('code','=',p['Method'])])
                                    if pc.name == p['Name'] or pc.methode == mtp:
                                        pc.sudo().write({
                                            'montant': p['Amount'],   
                                            'numero_transaction': p['TransactionNumber'],  
                                            'date_paiement': datetime.strptime(str(p['PaymentAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['PaymentAt']!=None else None,
                                            'date_echeance':datetime.strptime(str(p['DueAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['DueAt']!=None else None,
                                            'date_validation': datetime.strptime(str(p['ValidatedAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['ValidatedAt']!=None else None,
                                            })
                                    else:
                                        self.env['paiement.sah'].sudo().create({
                                            'name':p['Name'],  
                                            'methode': mtp.id if mtp else None,  
                                            'montant': p['Amount'],   
                                            'numero_transaction': p['TransactionNumber'],  
                                            'date_paiement': datetime.strptime(str(p['PaymentAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['PaymentAt']!=None else None,
                                            'date_echeance':datetime.strptime(str(p['DueAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['DueAt']!=None else None,
                                            'date_validation': datetime.strptime(str(p['ValidatedAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['ValidatedAt']!=None else None,
                                            'order_id': commandes_odoo.id,
                                        })
                                    commandes_odoo.methode_paiement_id = mtp.id if mtp else commandes_odoo.methode_paiement_id, 
                        else:
                            for p in paiement_sah:
                                mtp = self.env['methode.paiement.sah'].search([('code','=',p['Method'])])
                                self.env['paiement.sah'].sudo().create({
                                    'name':p['Name'],  
                                    'methode': mtp.id if mtp else None,  
                                    'montant': p['Amount'],   
                                    'numero_transaction': p['TransactionNumber'],  
                                    'date_paiement': datetime.strptime(str(p['PaymentAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['PaymentAt']!=None else None,
                                    'date_echeance':datetime.strptime(str(p['DueAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['DueAt']!=None else None,
                                    'date_validation': datetime.strptime(str(p['ValidatedAt']), "%Y-%m-%dT%H:%M:%S.%f") if p['ValidatedAt']!=None else None,
                                    'order_id': commandes_odoo.id,
                                })
                                commandes_odoo.methode_paiement_id = mtp.id if mtp else commandes_odoo.methode_paiement_id, 
                    for elt in commande['Products']:
                        p=self.env['product.template'].search([('produit_sah_id','=',elt['ProductId'])])
                        if p:
                            j=0
                            for l in commandes_odoo.order_line:
                                if l.id_order_line_sh==elt["Id"]:
                                    l.write({'product_uom_qty': elt['Quantity'],'price_unit': elt['UnitPriceExcltax'], 'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])] })
                                    j+=1
                            if j==0:
                                self.env['sale.order.line'].create({
                                "id_order_line_sh":elt["Id"],
                                "name":p.name,
                                "order_id":commandes_odoo.id,
                                'product_id':p.product_variant_id.id,
                                'product_template_id':p.id,
                                'product_uom_qty': elt['Quantity'],
                                'price_unit': elt['UnitPriceExcltax'], 
                                'tax_id': [(6, 0, [self._get_or_create_tax(elt['TaxRate'])])],
                                })
        else:
            _logger.info(f"Erreur {response.status_code}: {response.text}")
       
            
    def _get_or_create_tax(self, tax_rate):
        # Recherche la taxe par son montant
        tax = self.env['account.tax'].search([('amount', '=', tax_rate)], limit=1)
        if not tax:
            tax = self.env['account.tax'].create({
                'name': f'Taxe {tax_rate}%',
                'amount': tax_rate,
            })
        
        return tax.id


