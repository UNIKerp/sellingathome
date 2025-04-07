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



    def action_post(self):
        res = super().action_post()
        for move in self:
            move.action_invoice_sent()

    # def action_post(self):
    #     # Disabled by default to avoid breaking automated action flow
    #     action_invoice_sent()
    #     if (
    #         not self.env.context.get('disable_abnormal_invoice_detection', True)
    #         and self.filtered(lambda m: m.abnormal_amount_warning or m.abnormal_date_warning)
    #     ):
    #         wizard = self.env['validate.account.move'].create({
    #             'move_ids': [Command.set(self.ids)],
    #         })
    #         return {
    #             'name': _("Confirm Entries"),
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'validate.account.move',
    #             'res_id': wizard.id,
    #             'view_mode': 'form',
    #             'target': 'new',
    #         }
    #     if self:
    #         self._post(soft=False)
    #     if autopost_bills_wizard := self._show_autopost_bills_wizard():
    #         return autopost_bills_wizard
    #     return False
