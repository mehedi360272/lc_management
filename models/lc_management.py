from odoo import models, fields, api, _

class LetterOfCredit(models.Model):
    _name = 'lc.management'
    _description = 'Letter of Credit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', default="New")
    lc_name = fields.Char(string='LC Number', required=True)
    lc_type = fields.Many2one('lc.type', string="LC Type")

    partner_id = fields.Many2one('res.partner', string="Vendor", required=True)
    bank_id = fields.Many2one('res.partner', string="Issuing Bank", required=True)
    adv_bank = fields.Many2one('res.partner', string="Advising Bank", required=True)

    currency = fields.Selection([
        ('usd', 'USD'),
        ('bdt', 'BDT')
    ], string="Currency Type")

    lc_amount = fields.Float(string="Amount in FC", required=True)
    dollar_rate = fields.Float(string="FC Rate in BDT", required=True)
    bdt_amount = fields.Float(string="Amount in BDT", compute='_compute_bdt_amount', store=True)

    @api.depends('lc_amount', 'dollar_rate')
    def _compute_bdt_amount(self):
        for record in self:
            record.bdt_amount = record.lc_amount * record.dollar_rate if record.lc_amount and record.dollar_rate else 0.0

    margin_amount = fields.Float(string="Margin (%)", required=True)
    open_date = fields.Date(string="Opening Date", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True)

    po_ids = fields.One2many('purchase.order', 'lc_id', string="Linked Purchase Orders")
    bill_ids = fields.One2many('account.move', 'lc_id', string="Vendor Bills")
    landed_cost_ids = fields.One2many('stock.landed.cost', 'lc_id', string="Landed Costs")

    document = fields.Many2many('ir.attachment', string='Attachments')

    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('open', 'Open'),
        ('closed', 'Closed')
    ], default='draft', string="Status")

    def action_approve(self):
        for rec in self:
            if rec.name == 'New':
                rec.name = self.env['ir.sequence'].next_by_code('lc.management.sequence') or 'New'
            rec.status = 'approved'

    def action_mark_as_open(self):
        self.status = 'open'

    def action_close(self):
        self.status = 'closed'

    count_po = fields.Integer(string="PO Count", compute="_compute_counts")
    count_bill = fields.Integer(string="Bill Count", compute="_compute_counts")
    count_landed_cost = fields.Integer(string="Landed Cost Count", compute="_compute_counts")
    x_count_receipts = fields.Integer(string="Receipts", compute="_compute_counts")

    @api.depends('po_ids', 'bill_ids', 'landed_cost_ids')
    def _compute_counts(self):
        for rec in self:
            rec.count_po = len(rec.po_ids)
            rec.count_bill = len(rec.bill_ids)
            rec.count_landed_cost = len(rec.landed_cost_ids)

            # Receipt count
            receipt_pickings = self.env['stock.picking'].search_count([
                ('picking_type_id.code', '=', 'incoming'),
                ('purchase_id.lc_id', '=', rec.id)
            ])
            rec.x_count_receipts = receipt_pickings

    def action_view_purchase_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'view_mode': 'list,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', self.po_ids.ids)],
            'context': {'default_lc_id': self.id},
        }

    def action_view_vendor_bills(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.bill_ids.ids)],
            'context': {'default_lc_id': self.id},
        }

    def action_view_landed_costs(self):
        self.ensure_one()
        return {
            'name': 'Landed Costs',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.landed.cost',
            'view_mode': 'list,form',
            'domain': [('lc_id', '=', self.id)],
            'context': {'default_lc_id': self.id},
            'target': 'current',
        }

    def action_view_incoming_pickings(self):
        picking_ids = self.env['stock.picking'].search([
            ('picking_type_id.code', '=', 'incoming'),
            ('purchase_id.lc_id', '=', self.id),
        ])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incoming Shipments',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('id', 'in', picking_ids.ids)],
            'context': {'default_lc_id': self.id},
        }


    def action_create_purchase_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Purchase Order',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_lc_id': self.id,
            },
        }

    def action_create_landed_cost(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Landed Cost',
            'res_model': 'stock.landed.cost',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_lc_id': self.id,
            }
        }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    lc_id = fields.Many2one('lc.management', string="Letter of Credit")

    def _create_picking(self):
        res = super()._create_picking()
        for picking in self.picking_ids:
            picking.lc_id = self.lc_id.id
        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    lc_id = fields.Many2one('lc.management', string="Letter of Credit")

class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    lc_id = fields.Many2one('lc.management', string="Letter of Credit")

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    lc_id = fields.Many2one('lc.management', string="Letter of Credit")
