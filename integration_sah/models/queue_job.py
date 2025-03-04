#  Copyright 2020 VentorTech OU
#  License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import re
from odoo import models, fields, api, _
from odoo.addons.queue_job.job import FAILED
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class QueueJob(models.Model):
    _inherit = 'queue.job'
    _removal_interval = 15

   
    commande_sah_id = fields.Many2one(comodel_name='commande.sah', string='Commande SAH')


    def _set_integration(self):
        for rec in self:
            _logger.info("11111111111111111")
            odoo_model = rec.records[:1]
            _logger.info("222222222 %s",odoo_model)
            value = False
            if odoo_model and hasattr(odoo_model, '_get_integration_id_for_job'):

                _logger.info("33333333333")
                value = odoo_model.exists()._get_integration_id_for_job()

            rec.commande_sah_id = value

    @api.model_create_multi
    def create(self, vals_list):
        records = super(QueueJob, self).create(vals_list)

        _logger.info("444444444")
        records._set_integration()

        _logger.info("555555555")
        return records