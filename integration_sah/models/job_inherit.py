from odoo import models, api, fields,_
import requests


class JobEXT(models.Model):
    _inherit = "queue.job"

    product_job = fields.Char()

    # @api.model
    # def create(self,vals):
    #     res = super(JobEXT, self).create(vals)
    #     if res:
    #         res.retry = 1
    #     return res