# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"



    # def action_post(self):
    #     _logger.info('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
    #     res = super().action_post()
    #     _logger.info("hhhhhhhhhhhhhhhhhhh%s",res)
    #     for move in res:
    #         _logger.info('mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm %s',move)
    #         move.action_invoice_sent()
    #         move.action_print_pdf()
    #         _logger.info('okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')

    def action_post(self):
        # Disabled by default to avoid breaking automated action flow
    
        
        if (
            not self.env.context.get('disable_abnormal_invoice_detection', True)
            and self.filtered(lambda m: m.abnormal_amount_warning or m.abnormal_date_warning)
        ):
            wizard = self.env['validate.account.move'].create({
                'move_ids': [Command.set(self.ids)],
            })
            return {
                'name': _("Confirm Entries"),
                'type': 'ir.actions.act_window',
                'res_model': 'validate.account.move',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
            }
        if self:
            self._post(soft=False)
        if autopost_bills_wizard := self._show_autopost_bills_wizard():
            return autopost_bills_wizard
        for move in self:
            _logger.info('Traitement de la facture : %s', move.name)
            move.action_invoice_sent()    # Prépare et envoie l'email au client
            move.action_print_pdf() 
        return False
