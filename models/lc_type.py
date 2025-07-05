from odoo import models, fields, _

class LetterOfCredit(models.Model):
    _name = 'lc.type'
    _description = 'Letter of Credit Type'

    name = fields.Char(string='LC Type', required=True)