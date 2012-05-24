# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time


class sale_order(osv.osv):
    _inherit = 'fg_sale.order'
    _columns = {\
        'unpaid':fields.float('未核销金额', digits=(10, 2), readonly=True),
        'rbill_line': fields.one2many('fg_account.rbill.line', 'rbill_id','收款明细', readonly=True),
    }

class fg_account_rbill_line(osv.osv):
    _name = 'fg_account.rbill.line'
    _description = '收款单明细'
    
    _columns = {
        'name':fields.related('rbill_id', 'name', type='char', string='单号', readonly=True),
        'partner_id':fields.related('rbill_id', 'partner_id', type='many2one', relation='res.partner', string='客户'),
        'rbill_id': fields.many2one('fg_account.rbill', '收款单', required=True, ondelete='cascade', select=True),
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
        'amount':fields.float('单据未核销金额', digits=(10, 2), readonly=True),
        'paid':fields.float('已核销金额', digits=(10, 2)),
        'unpaid':fields.float('未核销金额', digits=(10, 2), readonly=True),
        'note':fields.text('附注'),
    }
    
    def onchange_order_id(self, cr, uid, ids, order_id):
        if not order_id:
            return {'value': {'amount': 0, 'paid':0, 'unpaid':0}}
        
        order_obj = self.pool.get('fg_sale.order')
        orders = order_obj.browse(cr, uid, [order_id])
        if orders:
            return {'value': {'amount': orders[0]['unpaid'], 'paid':orders[0]['unpaid'], 'unpaid':0}}
    
    def onchange_paid(self, cr, uid, ids, order_id, paid):
        order_obj = self.pool.get('fg_sale.order')
        orders = order_obj.browse(cr, uid, [order_id])
        if orders:
            if paid > orders[0]['unpaid']:
                raise osv.except_osv('核销金额错误', '核销金额不允许大于订单金额.')
            
            return {'value': {'amount': orders[0]['unpaid'], 'unpaid':(orders[0]['unpaid']-paid)}}
    
    def _write_readonly(self, vals):
        if vals.get('order_id'):
            order_obj = self.pool.get('fg_sale.order')
            orders = order_obj.browse(cr, uid, [vals.get('order_id')])
            if orders:
                vals['amount'] = orders[0]['unpaid']
                vals['unpaid'] = orders[0]['unpaid']-vals.get('paid', 0)
        
        return vals
    
    def write(self, cr, uid, ids, vals, context=None):
        vs = self._write_readonly(vals)
        return super(fg_account_rbill_line, self).write(cr, uid, ids, vs, context=context)
    
    def create(self, cr, uid, vals, context=None):
        vs = self._write_readonly(vals)
        
        return super(fg_account_rbill_line, self).create(cr, uid, vs, context=context)
    
class fg_account_rbill(osv.osv):
    _name = 'fg_account.rbill'
    _description = '收款单'
    
    def _paid_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for bill in self.browse(cr, uid, ids, context=context):
            res[bill.id] = { 'paid_all':0.0 }
            amount = 0
            for line in bill.bill_line:
                #todo: got to decide which one to add. subtotal_amount or, discount_amount
                amount = amount + line.paid
            res[bill.id]['paid_all'] = amount
        return res
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'date_issue': fields.date('收款日期', required=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        'user_id': fields.many2one('res.users', '制单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '审核人', select=True, readonly=True),
        'payment': fields.selection([('cash','现金'),('bank','银行转账')], '结算方式', states={'draft': [('readonly', False)]}),
        'amount':fields.float('收款金额', digits=(10, 2)),
        'paid_all':fields.function(_paid_all, string='已核销金额', store=False, multi='sums'),
        'bill_line': fields.one2many('fg_account.rbill.line', 'rbill_id', '收款单', readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True), 
        'state': fields.selection([('draft', '未审核'), ('done', '已审核'), ('cancel','已取消')], '收款单状态', readonly=True, select=True),
        'note':fields.text('附注'),
    }
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    def button_review(self, cr, uid, ids, context=None):
        #set confirming
        bills = self.browse(cr, uid, ids, context)
        for bill in bills:
            
        
        
        return True
    
    _defaults = {
        'date_issue': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')
    
    def create(self, cr, uid, vals, context=None):
        #
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_account.rbill')
        id = super(fg_account_rbill, self).create(cr, uid, vals, context)
        return id
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('paid_all')>vals.get('amount'):
            raise osv.except_osv('金额不足', '所有核销的金额大于收款金额.')
        
        return super(fg_account_rbill, self).write(cr, uid, ids, vals, context=context)


