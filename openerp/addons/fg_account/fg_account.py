# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time


class sale_order(osv.osv):
    _inherit = 'fg_sale.order'
    _columns = {
        'bill_line': fields.one2many('fg_account.rbill.line', 'rbill_id','收款明细', readonly=True),
    }

class fg_account_rbill_line(osv.osv):
    _name = 'fg_account.rbill.line'
    _description = '收款单明细'
    
    _columns = {
        'name':fields.related('rbill_id', 'name', type='char', string='单号'),
        'rbill_id': fields.many2one('fg_account.rbill', '收款单', required=True, ondelete='cascade', select=True),
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
    }

class fg_account_rbill(osv.osv):
    _name = 'fg_account.rbill'
    _description = '收款单'
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'date_issue': fields.date('收款日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        'user_id': fields.many2one('res.users', '制单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '审核人', select=True, readonly=True),
        'bill_line': fields.one2many('fg_account.rbill.line', 'rbill_id', '收款单', readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True), 
    }
    


