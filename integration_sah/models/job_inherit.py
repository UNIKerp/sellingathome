from odoo import models, api, fields,_
import requests
import logging
_logger = logging.getLogger(__name__)

class JobEXT(models.Model):
    _inherit = "queue.job"


  
    def write(self,vals):
        res = super(JobEXT, self).write(vals)
        if self.method_name == "creation_produit_odoo_sah":
           
            self.retry = 1
            _logger.info('========================================= %s',self.retry)
        return res